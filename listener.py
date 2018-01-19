from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API

from answer import answer

from pprint import pprint
import json


class SmashListener(StreamListener):

    def make_api(self, auth):
        self.api = API(auth)
        # self.api.update_status('Online!')

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        tweet_id = data['id_str']
        screen_name = data['user']['screen_name']
        if 'text' in data and ' vs' in data['text']:
            try:
                ans = answer(' '.join(data['text'].split()[1:]))
                self.api.update_status('@' + screen_name + ' ' + ans, in_reply_to_status_id=tweet_id)
                print(ans)
            except:
                self.api.update_status('@' + screen_name + " Sorry, an internal error occurred. Check your spelling and keep in mind I'm still in beta!",
                    in_reply_to_status_id=tweet_id)
                print('Error')
        else:
            print('Other')
        print()
        
    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    with open('local/keys.txt', 'r') as f:
        keys = [l.split('=')[1].strip() for l in f]
    auth = OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    l = SmashListener()
    l.make_api(auth)
    stream = Stream(auth, l)
    stream.filter(track=['@ssbm_stats_bot'])