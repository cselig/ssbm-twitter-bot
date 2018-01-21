# Examples of valid question format:
#   Marth vs Fox on Final destination
#   Sheik vs Peach


def make_aliases(path):
    aliases = {}
    with open(path, 'r') as f:
        headers = next(f)
        for l in f:
            name = l.split(':')[0]
            aliases_list = l.split(':')[1].strip().split(',')
            for a in aliases_list:
                aliases[a] = name
    return aliases


char_aliases = make_aliases('data/char_aliases.txt')
# tag_aliases = make_aliases('data/tag_aliases.txt')


def parse(question):
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

    if char1.lower() in char_aliases:
        char1 = char_aliases[char1.lower()]
    if char2.lower() in char_aliases:
        char2 = char_aliases[char2.lower()]

    return char1.title(), char2.title(), stage.title()
