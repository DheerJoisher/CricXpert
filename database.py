# database.py
import sqlite3

def create_db():
    conn = sqlite3.connect('tournament_manager.db')  # Creates the DB file
    cursor = conn.cursor()

    # Create tournaments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date_created TEXT
        )
    ''')

    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            tournament_id INTEGER,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')

    # Create players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')

    # Create matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team1_id INTEGER,
            team2_id INTEGER,
            date DATETIME NOT NULL,
            score_team1 INTEGER,
            score_team2 INTEGER,
            tournament_id INTEGER,
            FOREIGN KEY (team1_id) REFERENCES teams(id),
            FOREIGN KEY (team2_id) REFERENCES teams(id),
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')

    # Create score table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY,
            match_id INTEGER,
            player_id INTEGER,
            runs INTEGER,
            wickets INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')

    # Create scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            runs INTEGER DEFAULT 0,
            balls INTEGER DEFAULT 0,
            wickets INTEGER DEFAULT 0,
            PRIMARY KEY (match_id, player_id),  -- Composite Primary Key
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')

    # Create Overs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS overs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            over_number INTEGER NOT NULL,
            ball_number INTEGER NOT NULL,
            runs INTEGER DEFAULT 0,
            wickets BOOLEAN DEFAULT 0,
            bowler_id INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (bowler_id) REFERENCES players(id)
        )
    ''')

    conn.commit()  # Save changes to the database
    conn.close()   # Close the connection

# Call this function to create the database when the app starts
create_db()
