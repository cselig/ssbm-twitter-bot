import json
import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from more_itertools import unique_everseen

from database import Database


# Program flow:
#   on_data -> answer -> parse -> query
class SmashListener(StreamListener):

    # probably want to figure out how to roll this up into the superclass init method
    def setup(self, api_auth):
        self.api = API(api_auth)
        logging_format = '%(asctime)-15s %(levelname)s %(module)s: %(message)s'
        logging.basicConfig(
            format=logging_format,
            # filename='logs/session_start_time=%s.log' % int(time.time()),
            level=logging.INFO
        )
        self.logger = logging.getLogger('logger')

        self.char_aliases, self.chars = self.make_aliases('data/char_aliases.txt')
        self.stage_aliases, self.stages = self.make_aliases('data/stage_aliases.txt')
        self.tag_aliases, self.tags = self.make_aliases('data/tag_aliases.txt')
        self.db = Database('/Users/cselig/data/melee/db/v2/ssbm.db')

        self.logger.info('Setup complete.')


    # create aliases out of file with following format
    #   {canon. name}:{list of aliases, comma sep, lower}
    # Used to create aliases for tags, stages, and characters
    def make_aliases(self, path):
        aliases = {}
        all_ = []
        with open(path, 'r') as f:
            next(f) # read out headers
            for l in f:
                name = l.split(':')[0]
                aliases_list = l.split(':')[1].strip().split(',')
                for a in aliases_list:
                    aliases[a] = name
                all_.append(name)
        return aliases, list(set(all_))


    # entry point for answering a tweet
    def on_data(self, raw_data):
        data = json.loads(raw_data)
        tweet_id = data['id_str']
        screen_name = data['user']['screen_name']
        if 'text' in data and ' vs' in data['text']:
            try:
                logging.info('Question: %s' % data['text'])
                # TODO: better way to remove mentions
                ans = self.answer(' '.join(data['text'].split()[1:]))
                self.api.update_status('@' + screen_name + ' ' + ans, in_reply_to_status_id=tweet_id)
                logging.info('Answered: %s' % ans)
            except:
                self.api.update_status('@' + screen_name + " Sorry, an internal error occurred. Check your spelling and keep in mind I'm still in beta!",
                    in_reply_to_status_id=tweet_id)
                logging.error('Error answering question: %s' % data['text'])
        else:
            logging.info('No question found: %s' % data['text'])
        

    def on_error(self, status):
        print(status)
        logging.error('Error status: ' + status)


    def answer(self, question):
        char_list, tag_list, stage, cp_fl = self.parse(question)
        if len(char_list) == 2 and len(tag_list) == 0 and not stage and not cp_fl:
            char1, char2 = char_list
            win_percent, total_games = self.db.query_chars(char1, char2)
            return '%s vs %s:\n%s has won %s%% of %s games' % \
                    (char1, char2, char1, str(int(win_percent)), str(total_games))
        if len(char_list) == 2 and len(tag_list) == 0 and not stage and cp_fl:
            char1, char2 = char_list
            best_stage, win_percent, total_games = self.db.query_best_stage_counterpick(char1, char2)
            return "%s's best counterpick vs %s is %s (%s%% win rate out of %s total games)" % \
                    (char1, char2, best_stage, str(int(win_percent)), str(total_games))
        if len(char_list) == 2 and len(tag_list) == 0 and stage and not cp_fl:
            char1, char2 = char_list
            win_percent, total_games = self.db.query_chars_stage(char1, char2, stage)
            return '%s vs %s on %s:\n%s has won %s%% of %s games' % \
                    (char1, char2, stage, char1, str(int(win_percent)), str(total_games))
        else:
            return "Sorry, I don't know how to answer that question."


    def parse(self, question):
        words = question.split()
        char_list = []
        tag_list = []
        stage = None
        cp_fl = False

        for i in range(0, len(words)):
            word = words[i].lower()
            next_word = words[i + 1].lower() if (i < len(words) - 1) else None

            if word in self.chars:
                char_list.append(word)
            elif word[-1] == 's' and word[:-1] in self.chars:
                char_list.append(word[:-1])
            elif word[-2:] == "'s" and word[:-2] in self.chars:
                char_list.append(word[:-2])
            elif word[-1] == 's' and word[:-1] in self.char_aliases:
                char_list.append(self.char_aliases[word[:-1]])
            elif word[-2:] == "'s" and word[:-2] in self.char_aliases:
                char_list.append(self.char_aliases[word[:-2]])
            elif next_word and word + ' ' + next_word in self.chars:
                char_list.append(word + ' ' + next_word)
            elif next_word and word + ' ' + next_word in self.char_aliases:
                char_list.append(self.char_aliases[word + ' ' + next_word])
            elif word in self.char_aliases:
                char_list.append(self.char_aliases[word])

            if word in self.tags:
                tag_list.append(word)
            elif word[:-1] in self.tags:
                tag_list.append(word[:-1])
            elif word[:-2] in self.tags:
                tag_list.append(word[:-2])
            elif next_word and word + ' ' + next_word in self.tags:
                tag_list.append(word + ' ' + next_word)
            elif next_word and word + ' ' + next_word in self.tag_aliases:
                tag_list.append(self.tag_aliases[word + ' ' + next_word])
            elif word in self.tag_aliases:
                tag_list.append(self.tag_aliases[word])

            # will grab the last stage found in the question
            if word in self.stages:
                stage = word
            elif next_word and word + ' ' + next_word in self.stages:
                stage_list = word + ' ' + next_word
            elif next_word and word + ' ' + next_word in self.stage_aliases:
                stage = self.stage_aliases[word + ' ' + next_word]
            elif word in self.stage_aliases:
                stage = self.stage_aliases[word]

            if word == 'counterpick' or word == 'counter' and next_word == 'pick':
                cp_fl = True

        # unique_everseen() is used to remove duplicates where a keyword contains its alias
        # example being "Yoshi's Story", which contains an alias "Yoshi's"
        return (
            list(unique_everseen([x.title() for x in char_list])),
            list(unique_everseen([x.title() for x in tag_list])),
            stage.title() if stage else None,
            cp_fl
        )


def main():
    with open('local/keys.txt', 'r') as f:
        keys = [l.split('=')[1].strip() for l in f]
    auth = OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    l = SmashListener()
    l.setup(auth)
    stream = Stream(auth, l)
    # TODO: better way to listen for mentions? 
    stream.filter(track=['@ssbm_stats_bot'])


if __name__ == '__main__':
    main()
