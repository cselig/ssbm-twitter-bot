import sqlite3

conn = sqlite3.connect('data/ssbm.db')

# player char vs. player char on a certain stage
def query_players_chars_stage(p1, p2, p1_char, p2_char, stage):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win,
            sum(1) as total_games
        from(
            select *
            from sets join games using(setid)
            where (p1_tag = ? and p2_tag = ? and p1_char = ? and p2_char =?) or
                (p1_tag = ? and p2_tag = ? and p1_char = ? and p2_char = ?)
        )
        where stage = ?''', 
        (p1, p1, p2, p1_char, p2_char, p2, p1, p2_char, p1_char, stage))

    return c


# player char vs. player char 
def query_players_chars(p1, p2, p1_char, p2_char):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win,
            sum(1) as total_games
        from(
            select *
            from sets join games using(setid)
            where (p1_tag = ? and p2_tag = ? and p1_char = ? and p2_char =?) or
                (p1_tag = ? and p2_tag = ? and p1_char = ? and p2_char = ?)
        )
        where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')''', 
        (p1, p1, p2, p1_char, p2_char, p2, p1, p2_char, p1_char))

    return c


# player vs. player on a certain stage
def query_players_stage(p1, p2, stage):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win,
            sum(1) as total_games
        from(
            select *
            from sets join games using(setid)
            where (p1_tag = ? and p2_tag = ? or
                p1_tag = ? and p2_tag = ?)
        )
        where stage = ?''', 
        (p1, p1, p2, p2, p1, stage))

    return c


# player vs. player
def query_players(p1, p2):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win,
            sum(1) as total_games
        from(
            select *
            from sets join games using(setid)
            where (p1_tag = ? and p2_tag = ? or
                p1_tag = ? and p2_tag = ?)
        )
        where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')''', 
        (p1, p1, p2, p2, p1))

    return c


# return row for each legal stage
def query_chars_all_stages(char1, char2):
    c = conn.cursor()

    c.execute('''
        SELECT 
            stage,
            (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
            sum(1) as total_games
        from(
            select 
                *, 
                (case when games.winner = p1_tag then p1_char 
                when games.winner = p2_tag then p2_char end) as winner_char
            from sets join games using(setid)
            where (p1_char = ? and p2_char = ? or 
                p1_char = ? and p2_char = ?)
            ) 
            where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
            group by stage''', 
            (char1, char1, char2, char2, char1))

    return c


# char vs. char on certain stage
def query_chars_stage(char1, char2, stage):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
            sum(1) as total_games
        from(
            select 
                *, 
                (case when games.winner = p1_tag then p1_char 
                when games.winner = p2_tag then p2_char end) as winner_char
            from sets join games using(setid)
            where (p1_char = ? and p2_char = ? or 
                p1_char = ? and p2_char = ?)
            ) 
            where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
            and stage = ?''', 
            (char1, char1, char2, char2, char1, stage))

    return c


# char vs. char 
def query_chars(char1, char2):
    c = conn.cursor()

    c.execute('''
        SELECT 
            (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
            sum(1) as total_games
        from(
            select 
                *, 
                (case when games.winner = p1_tag then p1_char 
                when games.winner = p2_tag then p2_char end) as winner_char
            from sets join games using(setid)
            where (p1_char = ? and p2_char = ? or 
                p1_char = ? and p2_char = ?)
            ) 
            where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')''', 
            (char1, char1, char2, char2, char1))

    return c