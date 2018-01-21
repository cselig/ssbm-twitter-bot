from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API

from pprint import pprint
import json
import queries


# Program flow:
#   listener -> answer -> parse -> query
class SmashListener(StreamListener):

    # probably want to figure out how to roll this up into the superclass init method
    def setup(self, api_auth):
        self.api = API(api_auth)
        # self.api.update_status('Online!')

        self.char_aliases = self.make_aliases('data/char_aliases.txt')
        # self.tag_aliases = self.make_aliases('data/tag_aliases.txt')
        self.stage_aliases = self.make_aliases('data/stage_aliases.txt')


    # create aliases out of file with following format
    #   {canon name}:{list of aliases, comma sep, lower}
    # Used to create aliases for tags, stages, and characters
    def make_aliases(self, path):
        aliases = {}
        with open(path, 'r') as f:
            headers = next(f)
            for l in f:
                name = l.split(':')[0]
                aliases_list = l.split(':')[1].strip().split(',')
                for a in aliases_list:
                    aliases[a] = name
        return aliases


    def on_data(self, raw_data):
        data = json.loads(raw_data)
        tweet_id = data['id_str']
        screen_name = data['user']['screen_name']
        if 'text' in data and ' vs' in data['text']:
            try:
                print('question: ' + data['text'])
                # TODO: better way to remove mentions
                ans = self.answer(' '.join(data['text'].split()[1:]))
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


    def answer(self, question):
        char1, char2, stage = self.parse(question)
        if stage:
            c = queries.query_chars_stage(char1, char2, stage)
            win_percent, total = c.fetchone()
            return '%s vs %s on %s:\n%s has won %s%% of %s games' % \
                    (char1, char2, stage, char1, str(int(win_percent)), str(total))
        else:
            c = queries.query_chars(char1, char2)
            win_percent, total = c.fetchone() 
            return '%s vs %s:\n%s has won %s%% of %s games' % \
                    (char1, char2, char1, str(int(win_percent)), str(total))


    def parse(self, question):
        q_split = question.split()
        stage_fl = False
        stage = ''

        if ' on ' in question:
            on_index = q_split.index('on')
            stage_fl = True
            stage_list = question.split()[on_index + 1:]
            if len(stage_list) == 2:
                stage = stage_list[0] + ' ' + stage_list[1]
            else:
                stage = stage_list[0]

        if 'vs' in question:
            if 'vs.' in question:
                vs_index = q_split.index('vs.')
            else:
                vs_index = q_split.index('vs')
            char1_list = q_split[:vs_index]
            if len(char1_list) == 2:
                char1 = char1_list[0] + ' ' + char1_list[1]
            else:
                char1 = char1_list[0]
            if stage_fl:
                char2_list = q_split[vs_index + 1:on_index]
            else:
                char2_list = q_split[vs_index + 1:]

            if len(char2_list) == 2:
                char2 = char2_list[0] + ' ' + char2_list[1]
            else:
                char2 = char2_list[0]

        if char1.lower() in self.char_aliases:
            char1 = self.char_aliases[char1.lower()]
        if char2.lower() in self.char_aliases:
            char2 = self.char_aliases[char2.lower()]

        if stage.lower() in self.stage_aliases:
            stage = self.stage_aliases[stage.lower()]

        # TODO: get rid of this
        if stage != "Yoshi's Story": 
            stage = stage.title()

        return char1.title(), char2.title(), stage


if __name__ == '__main__':
    with open('local/keys.txt', 'r') as f:
        keys = [l.split('=')[1].strip() for l in f]
    auth = OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    l = SmashListener()
    l.setup(auth)
    stream = Stream(auth, l)
    # TODO: better way to listen for mentions? 
    stream.filter(track=['@ssbm_stats_bot'])
