#! coding: utf-8

import sys
import json
import os
import threading

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

def read_settings():
    settings_filename = os.path.join(__path__, 'default_settings.json')
    settings_filename = os.path.normpath(settings_filename)
    with open(settings_filename) as f:
        settings_obj = json.load(f)
    return settings_obj

setting_data = read_settings()
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

        try:
            self.api = tweepy.API(auth)
            # threading.Thread(target=self.tweetmain, args=(text, edit)).start()
            self.tweetmain(text, edit)
        except:
            sublime.error_message('Error! Enter your consumer_key, consumer_secret, access_token, access_token_secret in default_settings')

    def tweetmain(self, text, edit):
        if len(text) > 2:
            HEAD = text[:2]
            OPR = text[2]
            op = len(HEAD) + len(OPR)

            if HEAD == 'tl' and OPR == ':':
                timeline = self.get_my()
                for tweet in timeline:
                    self.view.insert(edit, 0, tweet)
                self.view.insert(edit, 0, "\n")

            elif HEAD == 'mt' and OPR == ':':
                timeline = self.get_user_timeline()
                for tweet in timeline:
                    self.view.insert(edit, 0, tweet)
                self.view.insert(edit, 0, "\n")

            elif HEAD == 'rp' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    in_reply_to_status_id = text[op:firstarg]
                    sublime.message_dialog(self.tweet(text[firstarg+1:], in_reply_to_status_id))

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

            elif HEAD == 'rt' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    tweet_id = text[op:firstarg]
                    sublime.message_dialog(self.retweet(tweet_id))

            elif HEAD == 'fv' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    tweet_id = text[op:firstarg]
                    sublime.message_dialog(self.favorite(tweet_id))

            elif HEAD == 'dl' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    tweet_id = text[op:firstarg]
                    sublime.message_dialog(self.destroy_tweet(tweet_id))

            elif HEAD == 'cf' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    user_id = text[op:firstarg]
                    sublime.message_dialog(self.create_friend(user_id))

            elif HEAD == 'df' and OPR == ':':
                firstarg = text.find(',')
                if firstarg != -1:
                    user_id = text[op:firstarg]
                    sublime.message_dialog(self.destroy_friend(user_id))

            elif HEAD == 'il' and OPR == ':':
                lists = self.friendship_incoming()
                for val in lists:
                    self.view.insert(edit, 0, val)
                self.view.insert(edit, 0, "\n")

            elif OPR == ':':
                sublime.message_dialog("Command not found\n")

            else:
                sublime.message_dialog(self.tweet(text))

        elif len(text) == 0:
            timeline = self.get_my()
            for tweet in timeline:
                self.view.insert(edit, 0, tweet)
            self.view.insert(edit, 0, "\n")

        else:
            pass
            # sublime.message_dialog(self.tweet(text))

    def tweet_detail(self, tweet_id):
        return self.api.get_status(tweet_id)

    def tweet(self, text, reply_id = None):
        self.api.update_status(status = text, in_reply_to_status_id = reply_id)
        if reply_id == None:
            return "Updated status\n"
        else:
            return "Updated status(reply)\n"

    def destroy_tweet(self, tweet_id):
        try:
            self.api.destroy_status(tweet_id)
            return "Destroyed status\n"
        except:
            return "Error (destroy tweet)\n"

    def retweet(self, tweet_id):
        try:
            self.api.retweet(tweet_id)
            return "Retweeted\n"
        except:
            return "Error (retweet)\n"

    def favorite(self, tweet_id):
        favorited = self.tweet_detail(tweet_id).favorited
        if not favorited:
            return self.create_fav(tweet_id)
        else:
            return self.destroy_fav(tweet_id)

    def create_fav(self, tweet_id):
        try:
            self.api.create_favorite(tweet_id)
            return "Created favorite\n"
        except:
            return "Error (create favorite)\n"

    def destroy_fav(self, tweet_id):
        try:
            self.api.destroy_favorite(tweet_id)
            return "Destroyed favorite\n"
        except:
            return "Error (destroy favorite)\n"

    def get_timeline(self, public_tweets):
        timeline = []
        for tweet in public_tweets:
            timeline.append(str(tweet.id) + ", @" + tweet.user.screen_name +
                "\n" + tweet.text + "\n" +
                "RT: " + str(tweet.retweet_count) + ", " +
                "fav: " + str(tweet.favorite_count) + "\n")
        timeline.reverse()
        return timeline

    def get_list(self):
        Lists = self.api.lists_all()
        listids = []
        for val in Lists:
            string = val.full_name + ", " + val.name + "\n"
            string = string.replace('/', ',')
            listids.append(string)
        return listids

    def get_my(self):
        public_tweets = self.api.home_timeline()
        return self.get_timeline(public_tweets)

    def get_list_timeline(self, screen_name, listid):
        public_tweets = self.api.list_timeline(owner_screen_name=screen_name,
            slug=listid)
        return self.get_timeline(public_tweets)

    def create_friend(self, user_id):
        try:
            self.api.create_friendship(user_id)
            return "Created friend\n"
        except:
            return "Error (create friend)\n"

    def destroy_friend(self, user_id):
        try:
            self.api.destroy_friendship(user_id)
            return "Destroyed friend\n"
        except:
            return "Error (destroy friend)\n"

    def get_user_timeline(self, screen_name=''):
        public_tweets = self.api.user_timeline(screen_name=self.api.me().screen_name)
        return self.get_timeline(public_tweets)

    def friendship_incoming(self):
        Lists = self.api.friendships_incoming()
        listids = []
        for val in Lists:
            listids.append(str(val) + "\n")
        return listids
