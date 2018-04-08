"""Queries handles retrieving information from the database."""

# TODO: there's gotta be a better way

import sqlite3

class Database:
    """A Database interfaces with the database of ssbm stats.

    Args:
        db_path (str): The local path of the saved database. This current implementation expects
            a sqlite3 database with the schema specified in schema.txt.
    """

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def query_best_stage_counterpick(self, char1, char2):
        """Returns the best stage to select against when playing char1 against char2.

        Args:
            char1 (str): The character of the player selecting the stage.
            char2 (str): The character of the opponent.

        Returns:
            (str, float, int): A tuple of the best stage, the win percentage of char1 against
                char2 on the stage, and the total number of games recorded between char1 and char2
                on that stage.
        """
        c = self.conn.cursor()

        c.execute('''
            SELECT 
                stage,
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from(
                select 
                    *, 
                    case
                        when games.winner = p1_tag then p1_char
                        when games.winner = p2_tag then p2_char end as winner_char
                from sets join games using(setid)
                where (p1_char = ? and p2_char = ? or 
                    p1_char = ? and p2_char = ?)
                ) 
            where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
            group by stage
            order by percent_win desc
            limit 1''', 
                (char1, char1, char2, char2, char1))

        best_stage, win_percent, total_games = c.fetchone()

        return best_stage, win_percent, total_games


    # player char vs. player char on a certain stage
    def query_players_chars_stage(self, p1, p2, p1_char, p2_char, stage):
        c = self.conn.cursor()

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
    def query_players_chars(self, p1, p2, p1_char, p2_char):
        c = self.conn.cursor()

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
    def query_players_stage(self, p1, p2, stage):
        c = self.conn.cursor()

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
    def query_players(self, p1, p2):
        c = self.conn.cursor()

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
    def query_chars_all_stages(self, char1, char2):
        c = self.conn.cursor()

        c.execute('''
            SELECT 
                stage,
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from(
                select 
                    *, 
                    case
                        when games.winner = p1_tag then p1_char
                        when games.winner = p2_tag then p2_char end as winner_char
                from sets join games using(setid)
                where (p1_char = ? and p2_char = ? or 
                    p1_char = ? and p2_char = ?)
                ) 
                where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
                group by stage''', 
                (char1, char1, char2, char2, char1))

        return c


    def query_chars_stage(self, char1, char2, stage):
        """Returns the win percentage of char1 against char2 on the specified stage.

        Args:
            char1 (str): The first character. 
            char2 (str): The second character.

        Returns:
            (float, int): The percentage of games won by char1 against char2 on the specified stage
                and the total number of recorded games played on that stage between char1 and
                char2.
        """
        c = self.conn.cursor()

        c.execute('''
            SELECT 
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from(
                select 
                    *, 
                    case
                        when games.winner = p1_tag then p1_char
                        when games.winner = p2_tag then p2_char end as winner_char
                from sets join games using(setid)
                where (p1_char = ? and p2_char = ? or 
                    p1_char = ? and p2_char = ?)
                ) 
                where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
                and stage = ?''', 
                (char1, char1, char2, char2, char1, stage))

        win_percent, total_games = c.fetchone()

        return win_percent, total_games


    def query_chars(self, char1, char2):
        """Returns the win percentage of char1 against char2.
        Args:
            char1 (str): The first character.
            char2 (str): The second character.

        Returns:
            (float, int): The win percentage of char1 against char2 and the total number of games
                between char1 and char2.
        """
        c = self.conn.cursor()

        c.execute('''
            SELECT 
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from(
                select 
                    *, 
                    case
                        when games.winner = p1_tag then p1_char
                        when games.winner = p2_tag then p2_char end as winner_char
                from sets join games using(setid)
                where (p1_char = ? and p2_char = ? or 
                    p1_char = ? and p2_char = ?)
                ) 
                where stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')''', 
                (char1, char1, char2, char2, char1))
        
        win_percent, total_games = c.fetchone() 

        return win_percent, total_games