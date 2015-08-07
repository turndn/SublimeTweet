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
for path in setting_data['site_packages_path']:
	site_packages_path = path
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

		if len(text) > 2:
			HEAD = text[:2]
			OPR = text[2]
			op = len(HEAD) + len(OPR)

			if HEAD == 'tl' and OPR == ':':
				timeline = self.get_my()
				for tweet in timeline:
					self.view.insert(edit, 0, tweet)
				self.view.insert(edit, 0, "\n")

			elif HEAD == 'rp' and OPR == ':':
				firstarg = text.find(',')
				if firstarg != -1:
					in_reply_to_status_id = text[op:firstarg]
					self.view.insert(edit, 0, self.tweet(text[firstarg+1:],
					 in_reply_to_status_id))

			elif HEAD == 'll' and OPR == ':':
				lists = self.get_list()
				for val in lists:
					self.view.insert(edit, 0, val)
				self.view.insert(edit, 0, "\n")

			elif HEAD == 'lt' and OPR == ':':
				timeline = []
				firstarg = text.find(',')
				if firstarg != -1 and len(text) > firstarg + 1:
					screen_name = text[op:firstarg]
					text = text[firstarg+1:]
					secondarg = text.find(',')
					if secondarg != -1:
						listid = text[:secondarg]
						timeline = self.get_list_timeline(screen_name, listid)
						for tweet in timeline:
							self.view.insert(edit, 0, tweet)
				self.view.insert(edit, 0, "\n")

			elif HEAD == 'rt' and OPR ==':':
				firstarg = text.find(',')
				if firstarg != -1:
					tweet_id = text[op:firstarg]
					self.view.insert(edit, 0, self.retweet(tweet_id))

			elif HEAD == 'fv' and OPR ==':':
				firstarg = text.find(',')
				if firstarg != -1:
					tweet_id = text[op:firstarg]
					self.view.insert(edit, 0, self.favorite(tweet_id))

			elif HEAD == 'dl' and OPR == ':':
				firstarg = text.find(',')
				if firstarg != -1:
					tweet_id = text[op:firstarg]
					self.view.insert(edit, 0, self.destroy_tweet(tweet_id))

			else :
				self.view.insert(edit, 0, self.tweet(text))

		elif len(text) == 0:
			timeline = self.get_my()
			for tweet in timeline:
				self.view.insert(edit, 0, tweet)
			self.view.insert(edit, 0, "\n")

		else :
			self.view.insert(edit, 0, self.tweet(text))

	def tweet_detail(self, tweet_id):
		return self.api.get_status(tweet_id)

	def tweet(self, text, reply_id = None):
		self.api.update_status(status = text, in_reply_to_status_id = reply_id)
		return "finish\n"

	def destroy_tweet(self, tweet_id):
		try:
			self.api.destroy_status(tweet_id)
			return "finish\n"
		except:
			return "error\n"

	def retweet(self, tweet_id):
		try:
			self.api.retweet(tweet_id)
			return "finish\n"
		except:
			return "error\n"

	def favorite(self, tweet_id):
		favorited = self.tweet_detail(tweet_id).favorited
		if not favorited:
			return self.create_fav(tweet_id)
		else:
			return self.destroy_fav(tweet_id)			

	def create_fav(self, tweet_id):
		try:
			self.api.create_favorite(tweet_id)
			return "finish\n"
		except:
			return "error\n"

	def destroy_fav(self, tweet_id):
		try:
			self.api.destroy_favorite(tweet_id)
			return "finish\n"
		except:
			return "error\n"

	def get_timeline(self, public_tweets):
		timeline = []
		for tweet in public_tweets:
			timeline.append(str(tweet.id) + ": @" + tweet.user.screen_name + 
				" " + tweet.text + "\n")
		timeline.reverse()
		return timeline

	def get_list(self):
		Lists = self.api.lists_all()
		listids = []
		for val in Lists:
			listids.append(val.full_name + ": " + val.name + "\n")
		return listids

	def get_my(self):
		public_tweets = self.api.home_timeline()
		return self.get_timeline(public_tweets)

	def get_list_timeline(self, screen_name, listid):
		public_tweets = self.api.list_timeline(owner_screen_name=screen_name, 
			slug=listid)
		return self.get_timeline(public_tweets)
