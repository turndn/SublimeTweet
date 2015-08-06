#! coding: utf-8

import sys
import json
import os

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

def read_default_settings():
    default_settings_filename = os.path.join(__path__, 'default_settings.json')
    default_settings_filename = os.path.normpath(default_settings_filename)
    with open(default_settings_filename) as f:
        settings_obj = json.load(f)
    return settings_obj

setting_data = read_default_settings()
site_packages_path = setting_data['site_packages_path']
sys.path.append(site_packages_path)
import tweepy

import sublime, sublime_plugin

class TweetCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		selection = self.view.sel()[0]
		text = self.view.substr(selection)
		consumer_key = setting_data['consumer_key']
		consumer_secret = setting_data['consumer_secret']
		access_token = setting_data['access_token']
		access_token_secret = setting_data['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		self.api = tweepy.API(auth)

		if len(text) > 1:
			HEAD = text[0]
			OPR = text[1]
			if HEAD == 't' and OPR == ':':
				timeline = self.get_time_line()
				for tweet in timeline:
					self.view.insert(edit, 0, tweet)
				self.view.insert(edit, 0, "\n")
			elif HEAD == 'r' and OPR == ':':
				endpoint = text.find(',')
				if endpoint != -1:
					in_reply_to_status_id = text[2:endpoint]
					self.view.insert(edit, 0, self.tweet(text[endpoint+1:], in_reply_to_status_id))
			else:
				self.view.insert(edit, 0, self.tweet(text))


	def tweet(self, text, reply_id = None):
		self.api.update_status(status = text, in_reply_to_status_id = reply_id)
		return "finish"

	def get_time_line(self):
		public_tweets = self.api.home_timeline()
		timeline = []
		for tweet in public_tweets:
			timeline.append(str(tweet.id) + ": @" + tweet.user.screen_name + " " + tweet.text + "\n")
		timeline.reverse()
		return timeline
