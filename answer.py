from parse import parse
import queries


def answer(question):
    char1, char2, stage = parse(question)
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


# for testing
if __name__ == '__main__':
    question = ''
    while question != 'q':
        question = input('Enter a question: ')
        print(answer(question))