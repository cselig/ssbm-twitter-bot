"""Database handles retrieving information from the database."""

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
            select
                stage,
                sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100 as percent_win,
                sum(1) as total_games
            from (
                select
                    stage,
                    case
                        when winner_id = p1_id then p1_char
                        else p2_char
                    end as winner_char
                    from
                        games
                    where(p1_char = ? and p2_char = ? or
                        p1_char = ? and p2_char = ?)
                        and stage in ('Final Destination', 'Pokemon Stadium', 'Battlefield', 'Dreamland', "Yoshi's Story", 'Fountain of Dreams')
                )
            group by
                stage
            order by
                percent_win desc
            limit 1''', 
                (char1, char1, char2, char2, char1))

        best_stage, win_percent, total_games = c.fetchone()

        return best_stage, win_percent, total_games


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
            select
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from (
            select
                case
                    when winner_id = p1_id then p1_char
                    when winner_id = p2_id then p2_char
                end as winner_char
                from
                    games
                where
                    (p1_char = ? and p2_char = ?
                    or p1_char = ? and p2_char = ?)
                    and stage = ?
            )
            ''', (char1, char1, char2, char2, char1, stage))

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
            select
                (sum(case when winner_char = ? then 1 else 0 end) * 1.0 / sum(1) * 100) as percent_win, 
                sum(1) as total_games
            from (
            select
                case
                    when winner_id = p1_id then p1_char
                    when winner_id = p2_id then p2_char
                end as winner_char
                from
                    games
                where
                    p1_char = ? and p2_char = ?
                    or p1_char = ? and p2_char = ?
                )
            ''', (char1, char1, char2, char2, char1))
        
        win_percent, total_games = c.fetchone() 

        return win_percent, total_games
