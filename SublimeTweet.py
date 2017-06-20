# coding: utf-8

import sys
import json
import os
import threading

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)


def read_settings():
    settings_filename = os.path.join(__path__, 'settings.json')
    settings_filename = os.path.normpath(settings_filename)
    with open(settings_filename) as f:
        settings_obj = json.load(f)
    return settings_obj

setting_data = read_settings()
for path in setting_data['site_packages_path']:
    site_packages_path = path
    sys.path.append(site_packages_path)

from tweepy import OAuthHandler, API
import sublime
import sublime_plugin


def parse_command(cmd_text):
    if len(cmd_text) < 3:
        return ('get_timeline')
    elif cmd_text[2] != ':':
        return ('update_status', cmd_text)
    cmd = cmd_text[:2]

    if cmd == 'tl':
        return ('get_timeline', None)
    elif cmd == 'mt':
        username = cmd_text[3:]
        return ('get_mytimeline', username)
    elif cmd == 'rp':
        cmd_list = cmd_text[3:].split(',')
        return ('reply', cmd_list[1], cmd_list[0])
    elif cmd == 'll':
        return ('list_list', None)
    elif cmd == 'lt':
        cmd_list = cmd_text[3:].split(',')
        return ('list_timeline', cmd_list)
    elif cmd == 'rt':
        cmd_list = cmd_text[3:].split(',')
        return ('retweet', cmd_list[0])
    elif cmd == 'fv':
        cmd_list = cmd_text[3:].split(',')
        return ('favorite', cmd_list[0])
    elif cmd == 'dl':
        cmd_list = cmd_text[3:].split(',')
        return ('delete', cmd_list[0])
    elif cmd == 'cf':
        cmd_list = cmd_text[3:].split(',')
        return ('create_friend', cmd_list[0])
    elif cmd == 'df':
        cmd_list = cmd_text[3:].split(',')
        return ('destroy_friend', cmd_list[0])
    elif cmd == 'il':
        return ('follow_request_list', None)

    return None


class TweetCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        selection = self.view.sel()[0]
        text = self.view.substr(selection)
        consumer_key = setting_data['consumer_key']
        consumer_secret = setting_data['consumer_secret']
        access_token = setting_data['access_token']
        access_token_secret = setting_data['access_token_secret']

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        try:
            self.api = API(auth)
            self.tweetmain(text, edit)
        except Exception:
            sublime.error_message(('Error! Enter your consumer_key, consumer_s'
                                   'ecret, access_token, access_token_secret i'
                                   'n default_settings'))

    def tweetmain(self, text, edit):
        cmd = parse_command(text)
        if cmd:
            if cmd[0] == 'get_timeline':
                timeline = self.get_my()
                for tweet in timeline:
                    self.view.insert(edit, 0, tweet)
                self.view.insert(edit, 0, "\n")
            elif cmd[0] == 'update_status':
                threading.Thread(target=self.tweet, kwargs={
                                 "text": cmd[1]}).start()
            elif cmd[0] == 'get_mytimeline':
                timeline = self.get_user_timeline(screen_name=cmd[1])
                for tweet in timeline:
                    self.view.insert(edit, 0, tweet)
                self.view.insert(edit, 0, "\n")
            elif cmd[0] == 'reply':
                threading.Thread(target=self.tweet, kwargs={
                                 "text": cmd[1], "reply_id": cmd[2]}).start()
            elif cmd[0] == 'favorite':
                threading.Thread(target=self.favorite, kwargs={
                                 "tweet_id": cmd[1]}).start()
            elif cmd[0] == 'delete':
                threading.Thread(target=self.destroy_tweet, kwargs={
                                 "tweet_id": cmd[1]}).start()
            elif cmd[0] == 'list_list':
                lists = self.get_list()
                for val in lists:
                    self.view.insert(edit, 0, val)
                self.view.insert(edit, 0, "\n")
            elif cmd[0] == 'list_timeline':
                timeline = []
                screen_name = cmd[1][0]
                listid = cmd[1][1]
                timeline = self.get_list_timeline(screen_name, listid)
                for tweet in timeline:
                    self.view.insert(edit, 0, tweet)
                self.view.insert(edit, 0, "\n")
            elif cmd[0] == 'retweet':
                threading.Thread(target=self.retweet, kwargs={
                                 "tweet_id": cmd[1]}).start()
            elif cmd[0] == 'create_friend':
                threading.Thread(target=self.create_friend, kwargs={
                                 "screen_name": cmd[1]}).start()
            elif cmd[0] == 'destroy_friend':
                threading.Thread(target=self.destroy_friend, kwargs={
                                 "screen_name": cmd[1]}).start()
            elif cmd[0] == 'follow_request_list':
                lists = self.friendship_incoming()
                for val in lists:
                    self.view.insert(edit, 0, val)
                self.view.insert(edit, 0, "\n")
            else:
                sublime.message_dialog("Command not implemented\n")
        else:
            sublime.message_dialog("Command not found\n")

        reply = "^@[a-zA-Z0-9\_]*"
        retweet = "^RT @[a-zA-Z0-9\_]*:"
        self.view.add_regions('Reply',
                              self.view.find_all(reply),
                              "invalid",
                              "",
                              sublime.DRAW_SQUIGGLY_UNDERLINE)
        self.view.add_regions('Retweet',
                              self.view.find_all(retweet),
                              "invalid",
                              "",
                              sublime.DRAW_SQUIGGLY_UNDERLINE)

    def tweet_detail(self, tweet_id):
        return self.api.get_status(tweet_id)

    def tweet(self, text, reply_id=None):
        self.api.update_status(status=text, in_reply_to_status_id=reply_id)
        if not reply_id:
            sublime.message_dialog("Updated status\n")
        else:
            sublime.message_dialog("Updated status(reply)\n")

    def destroy_tweet(self, tweet_id):
        try:
            self.api.destroy_status(tweet_id)
            sublime.message_dialog("Destroyed status\n")
        except Exception:
            sublime.message_dialog("Error (destroy tweet)\n")

    def retweet(self, tweet_id):
        try:
            self.api.retweet(tweet_id)
            sublime.message_dialog("Retweeted\n")
        except Exception:
            sublime.message_dialog("Error (retweet)\n")

    def favorite(self, tweet_id):
        favorited = self.tweet_detail(tweet_id).favorited
        if not favorited:
            sublime.message_dialog(self.create_fav(tweet_id))
        else:
            sublime.message_dialog(self.destroy_fav(tweet_id))

    def create_fav(self, tweet_id):
        try:
            self.api.create_favorite(tweet_id)
            return "Created favorite\n"
        except Exception:
            return "Error (create favorite)\n"

    def destroy_fav(self, tweet_id):
        try:
            self.api.destroy_favorite(tweet_id)
            return "Destroyed favorite\n"
        except Exception:
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
        public_tweets = self.api.list_timeline(
            owner_screen_name=screen_name, slug=listid)
        return self.get_timeline(public_tweets)

    def create_friend(self, screen_name):
        try:
            user_id = self.api.get_user(screen_name=screen_name).id
        except Exception:
            sublime.message_dialog("Error (user not found or other issue)")

        try:
            self.api.create_friendship(user_id)
            sublime.message_dialog("Created friend\n")
        except Exception:
            sublime.message_dialog("Error (create friend)\n")

    def destroy_friend(self, screen_name):
        try:
            user_id = self.api.get_user(screen_name=screen_name).id
        except Exception:
            sublime.message_dialog("Error (user not found or other issue)")

        try:
            self.api.destroy_friendship(user_id)
            sublime.message_dialog("Destroyed friend\n")
        except Exception:
            sublime.message_dialog("Error (destroy friend)\n")

    def get_user_timeline(self, screen_name=''):
        public_tweets = self.api.user_timeline(
            screen_name=self.api.me().screen_name)
        return self.get_timeline(public_tweets)

    def friendship_incoming(self):
        Lists = self.api.friendships_incoming()
        listids = []
        for val in Lists:
            listids.append(str(val) + "\n")
        return listids
