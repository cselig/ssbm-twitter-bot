"""Database handles retrieving information from the database."""

from sqlalchemy import create_engine, select
from sqlalchemy.sql import text

class Database:
    """A Database interfaces with the database of ssbm stats.

    Args:
        db_path (str): The local path of the saved database. This current implementation expects
            a sqlite3 database with the schema specified in schema.txt.
    """

    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///' + db_path)

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
        query = text('''
            select
                stage,
                sum(case when winner_char = :char1 then 1 else 0 end) * 100.0 / sum(1) as win_percent,
                sum(1) as total_games
            from
                games_v
            where
                (p1_char = :char1 and p2_char = :char2
                or p2_char = :char1 and p1_char = :char2)
                and stage is not null
            group by
                stage
            order by
                2 desc
            limit 1
        ''')
        stage, win_percent, total_games = self.engine.execute(query, char1=char1, char2=char2).fetchone()
        return stage, win_percent, total_games

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
        query = text('''
            select
                sum(case when winner_char = :char1 then 1 else 0 end) * 100.0 / sum(1) as win_percent,
                sum(1) as total_games
            from
                games_v
            where
                (p1_char = :char1 and p2_char = :char2
                or p2_char = :char1 and p1_char = :char2)
                and stage = :stage
        ''')
        win_percent, total_games = self.engine.execute(query, char1=char1, char2=char2, stage=stage).fetchone()
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
        query = text('''
            select
                sum(case when winner_char = :char1 then 1 else 0 end) * 100.0 / sum(1) as win_percent,
                sum(1) as total_games
            from
                games_v
            where
                p1_char = :char1 and p2_char = :char2
                or p2_char = :char1 and p1_char = :char2
        ''')
        win_percent, total_games = self.engine.execute(query, char1=char1, char2=char2).fetchone()
        return win_percent, total_games
