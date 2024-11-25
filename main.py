import tkinter as tk
from tkcalendar import Calendar
from tkinter import simpledialog, messagebox
import sqlite3

class TournamentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tournament Manager")
        self.root.geometry("600x400")

        # Create the database if not exists
        create_db()

        self.create_widgets()
        self.load_tournaments()

    def create_widgets(self):
        # Button to create a new tournament
        self.create_button = tk.Button(self.root, text="Create New Tournament", command=self.create_tournament)
        self.create_button.pack(pady=10)

        # Listbox to display existing tournaments
        self.tournament_list = tk.Listbox(self.root)
        self.tournament_list.pack(fill=tk.BOTH, expand=True)

        # Bind event to listbox selection
        self.tournament_list.bind("<Double-1>", self.tournament_selected)

    def create_tournament(self):
        # Prompt user for tournament name
        tournament_name = simpledialog.askstring("Tournament Name", "Enter the name of the tournament:")
        if tournament_name:
            # Insert into the database
            self.add_tournament_to_db(tournament_name)
            self.load_tournaments()

    def add_tournament_to_db(self, name):
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tournaments (name, date_created) VALUES (?, datetime('now'))", (name,))
        conn.commit()
        conn.close()

    def load_tournaments(self):
        # Clear the list
        self.tournament_list.delete(0, tk.END)

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM tournaments")
        tournaments = cursor.fetchall()
        conn.close()

        for tournament in tournaments:
            self.tournament_list.insert(tk.END, tournament[0])

    def tournament_selected(self, event):
        # Get the selected tournament
        selected_tournament = self.tournament_list.get(tk.ACTIVE)
        self.show_tournament_details(selected_tournament)

    def show_tournament_details(self, tournament_name):
        # New window to manage selected tournament
        new_window = tk.Toplevel(self.root)
        new_window.title(f"Managing {tournament_name}")

        # Button to add teams
        self.add_team_button = tk.Button(new_window, text="Add Team", command=lambda: self.add_team(new_window, tournament_name))
        self.add_team_button.pack(pady=10)

        # Button to manage players
        self.manage_players_button = tk.Button(new_window, text="Manage Players", command=lambda: self.manage_players(new_window, tournament_name))
        self.manage_players_button.pack(pady=10)

        # Button to schedule a match
        self.schedule_match_button = tk.Button(new_window, text="Schedule Match and Enter Result", command=lambda: self.schedule_match(new_window, tournament_name))
        self.schedule_match_button.pack(pady=10)

        # Button to view scheduled matches
        self.view_matches_button = tk.Button(new_window, text="View Matches", command=lambda: self.view_matches(tournament_name))
        self.view_matches_button.pack(pady=10)

        # Button to view points table
        self.points_table_button = tk.Button(new_window, text="View Points Table", command=lambda: self.view_points_table(tournament_name))
        self.points_table_button.pack(pady=10)

    def add_team(self, window, tournament_name):
        team_name = simpledialog.askstring("Team Name", "Enter the name of the team:")
        if team_name:
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament_name,))
            tournament_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO teams (name, tournament_id, points) VALUES (?, ?, ?)", (team_name, tournament_id, 0))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Team {team_name} added successfully!")
            window.destroy()

    def manage_players(self, window, tournament_name):
        # Get tournament ID from name
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament_name,))
        tournament_id = cursor.fetchone()[0]

        # New window to manage players
        player_window = tk.Toplevel(window)
        player_window.title(f"Manage Players for {tournament_name}")

        # Listbox to show players
        self.player_listbox = tk.Listbox(player_window)
        self.player_listbox.pack(fill=tk.BOTH, expand=True)

        # Load teams to choose where to add players
        cursor.execute("SELECT id, name FROM teams WHERE tournament_id = ?", (tournament_id,))
        teams = cursor.fetchall()

        self.team_combobox = tk.StringVar()
        team_dropdown = tk.OptionMenu(player_window, self.team_combobox, *[team[1] for team in teams])
        team_dropdown.pack(pady=10)

        # Button to add players
        self.add_player_button = tk.Button(player_window, text="Add Player", command=lambda: self.add_player(tournament_id))
        self.add_player_button.pack(pady=10)

        # Button to display players in the selected team
        self.view_players_button = tk.Button(player_window, text="View Players", command=lambda: self.view_players(tournament_id))
        self.view_players_button.pack(pady=10)

    def add_player(self, tournament_id):
        player_name = simpledialog.askstring("Player Name", "Enter the name of the player:")
        if player_name:
            team_name = self.team_combobox.get()
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            # Get team ID
            cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team_name, tournament_id))
            team_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO players (name, team_id) VALUES (?, ?)", (player_name, team_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Player {player_name} added to team {team_name}!")

    def view_players(self, tournament_id):
        self.player_listbox.delete(0, tk.END)  # Clear the listbox
        team_name = self.team_combobox.get()
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        # Get team ID
        cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team_name, tournament_id))
        team_id = cursor.fetchone()[0]

        # Get players in the selected team
        cursor.execute("SELECT name FROM players WHERE team_id = ?", (team_id,))
        players = cursor.fetchall()
        conn.close()

        for player in players:
            self.player_listbox.insert(tk.END, player[0])

    def schedule_match(self, window, tournament_name):
        # Create a new window to schedule the match
        schedule_window = tk.Toplevel(window)
        schedule_window.title(f"Schedule Match for {tournament_name}")

        # Load teams to choose from
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM teams WHERE tournament_id = (SELECT id FROM tournaments WHERE name = ?)", (tournament_name,))
        teams = cursor.fetchall()
        conn.close()

        self.team1_combobox = tk.StringVar()
        self.team2_combobox = tk.StringVar()

        team1_dropdown = tk.OptionMenu(schedule_window, self.team1_combobox, *[team[1] for team in teams])
        team1_dropdown.pack(pady=10)

        team2_dropdown = tk.OptionMenu(schedule_window, self.team2_combobox, *[team[1] for team in teams])
        team2_dropdown.pack(pady=10)

        # Calendar for date selection
        tk.Label(schedule_window, text="Select Match Date:").pack()
        self.match_date_calendar = Calendar(schedule_window, date_pattern="yyyy-mm-dd")
        self.match_date_calendar.pack(pady=10)

        # Entry for time selection
        tk.Label(schedule_window, text="Enter Match Time (HH:MM 24-hour):").pack()
        self.match_time_entry = tk.Entry(schedule_window)
        self.match_time_entry.pack(pady=5)
        self.match_time_entry.insert(0, "HH:MM")

        # Button to save the match
        self.schedule_button = tk.Button(schedule_window, text="Enter Result", command=lambda: self.save_match(tournament_name, schedule_window))
        self.schedule_button.pack(pady=10)



    def save_and_refresh_match(self, tournament_name, schedule_window):
        # Save match and then refresh the matches list
        self.save_match(tournament_name)
        self.view_matches(tournament_name)  # Refresh the list of matches after saving
        schedule_window.destroy()  # Close the scheduling window

    def save_match(self, tournament_name, schedule_window):
        team1_name = self.team1_combobox.get()
        team2_name = self.team2_combobox.get()
        match_date = self.match_date_calendar.get_date()
        match_time = self.match_time_entry.get()

        if not team1_name or not team2_name or not match_date or not match_time:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        # Get tournament ID
        cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament_name,))
        tournament_id = cursor.fetchone()[0]

        # Get team IDs
        cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team1_name, tournament_id))
        team1_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team2_name, tournament_id))
        team2_id = cursor.fetchone()[0]

        # Combine date and time for match schedule
        match_datetime = f"{match_date} {match_time}:00"

        # Insert match data
        cursor.execute("""
        INSERT INTO matches (team1_id, team2_id, date, tournament_id)
        VALUES (?, ?, ?, ?)
        """, (team1_id, team2_id, match_datetime, tournament_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Match scheduled between {team1_name} and {team2_name} on {match_datetime}!")

        # Now you can call the result input method and pass the necessary details
        self.show_match_result_input(tournament_name, schedule_window, team1_id, team2_id, match_datetime)


    def view_matches(self, tournament_name):
        # Retrieve scheduled matches from the database
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        # Query to fetch match details for the selected tournament
        cursor.execute("""
        SELECT t1.name AS team1_name, t2.name AS team2_name, m.date 
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        WHERE m.tournament_id = (SELECT id FROM tournaments WHERE name = ?)
        """, (tournament_name,))

        matches = cursor.fetchall()
        conn.close()

        # Create a new window to display the scheduled matches
        match_window = tk.Toplevel(self.root)
        match_window.title(f"Scheduled Matches for {tournament_name}")

        # Check if there are no scheduled matches
        if not matches:
            tk.Label(match_window, text="No matches scheduled yet.").pack(pady=20)
            return

        # Display the matches
        for match in matches:
            team1_name = match[0]
            team2_name = match[1]
            match_date = match[2]

            # Format the date and time to a more readable format
            formatted_date = match_date.replace("T", " at ")

            # Display match info
            match_info = f"{team1_name} vs {team2_name} on {formatted_date}"
            tk.Label(match_window, text=match_info).pack(pady=5)

    def view_points_table(self, tournament_name):
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT name, points FROM teams
        WHERE tournament_id = (SELECT id FROM tournaments WHERE name = ?)
        ORDER BY points DESC
        """, (tournament_name,))
        points = cursor.fetchall()
        conn.close()

        points_window = tk.Toplevel(self.root)
        points_window.title(f"Points Table for {tournament_name}")

        for team, points in points:
            tk.Label(points_window, text=f"{team}: {points} points").pack()

    def update_points(self, team1_id, team2_id, result):
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        if result == 'team1':
            # Team 1 wins, update Team 1 points
            cursor.execute("UPDATE teams SET points = points + 2 WHERE id = ?", (team1_id,))
            cursor.execute("UPDATE teams SET points = points WHERE id = ?", (team2_id,))  # Team 2 gets 0 points
        elif result == 'team2':
            # Team 2 wins, update Team 2 points
            cursor.execute("UPDATE teams SET points = points + 2 WHERE id = ?", (team2_id,))
            cursor.execute("UPDATE teams SET points = points WHERE id = ?", (team1_id,))  # Team 1 gets 0 points
        else:
            # Draw, both teams get 1 point
            cursor.execute("UPDATE teams SET points = points + 1 WHERE id = ?", (team1_id,))
            cursor.execute("UPDATE teams SET points = points + 1 WHERE id = ?", (team2_id,))

        conn.commit()
        conn.close()

        # Reload the points table
        self.load_points_table()

    def show_match_result_input(self, tournament_name, schedule_window, team1_id, team2_id, match_datetime):
        result_window = tk.Toplevel(schedule_window)
        result_window.title("Enter Match Result")

        # Dropdown to select the result
        result_var = tk.StringVar()
        result_var.set("draw")  # Default to draw

        result_label = tk.Label(result_window, text="Select Match Result:")
        result_label.pack(pady=10)

        result_dropdown = tk.OptionMenu(result_window, result_var, "team1", "team2", "draw")
        result_dropdown.pack(pady=10)

        # Button to save the result
        save_button = tk.Button(result_window, text="Save Result", command=lambda: self.save_match_result(tournament_name, team1_id, team2_id, result_var.get(), match_datetime))
        save_button.pack(pady=10)


    def save_match_result(self, tournament_name, team1_id, team2_id, result, match_datetime):
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        if result == "team1":
            cursor.execute("UPDATE teams SET points = points + 2 WHERE id = ?", (team1_id,))
            cursor.execute("UPDATE teams SET points = points WHERE id = ?", (team2_id,))  # Team 2 gets 0 points
        elif result == "team2":
            cursor.execute("UPDATE teams SET points = points + 2 WHERE id = ?", (team2_id,))
            cursor.execute("UPDATE teams SET points = points WHERE id = ?", (team1_id,))  # Team 1 gets 0 points
        else:
            # Draw, both teams get 1 point
            cursor.execute("UPDATE teams SET points = points + 1 WHERE id = ?", (team1_id,))
            cursor.execute("UPDATE teams SET points = points + 1 WHERE id = ?", (team2_id,))

        conn.commit()
        conn.close()

        # Reload the points table
        self.load_points_table()

        # Notify the user
        messagebox.showinfo("Success", "Match result updated successfully!")


    def load_points_table(self):
        # Clear the points table list
        self.points_table_list.delete(0, tk.END)

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT teams.name, teams.points 
            FROM teams
            JOIN tournaments ON teams.tournament_id = tournaments.id
            WHERE tournaments.name = ?
            ORDER BY teams.points DESC
        """, (self.selected_tournament_name,))
        teams = cursor.fetchall()
        conn.close()

        for team in teams:
            self.points_table_list.insert(tk.END, f"{team[0]} - {team[1]} points")

# Database setup
def create_db():
    conn = sqlite3.connect('tournament_manager.db')
    cursor = conn.cursor()

    # Create tournaments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_created TEXT NOT NULL
    )
    """)

    # Create teams table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tournament_id INTEGER NOT NULL,
        points INTEGER DEFAULT 0,
        FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
    )
    """)

    # Create players table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team_id INTEGER NOT NULL,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    )
    """)

    # Create matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1_id INTEGER NOT NULL,
        team2_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        tournament_id INTEGER NOT NULL,
        FOREIGN KEY(team1_id) REFERENCES teams(id),
        FOREIGN KEY(team2_id) REFERENCES teams(id),
        FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentManagerApp(root)
    root.mainloop()
