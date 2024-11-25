import tkinter as tk
from tkcalendar import Calendar
from tkinter import simpledialog, messagebox
import sqlite3
from database import create_db


class TournamentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Tournament Manager")
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
        self.schedule_match_button = tk.Button(new_window, text="Schedule Match", command=lambda: self.schedule_match(new_window, tournament_name))
        self.schedule_match_button.pack(pady=10)

        # Button to manage scores
        self.manage_scores_button = tk.Button(new_window, text="Manage Scores", command=lambda: self.manage_scores(new_window, tournament_name))
        self.manage_scores_button.pack(pady=10)

    def add_team(self, window, tournament_name):
        team_name = simpledialog.askstring("Team Name", "Enter the name of the team:")
        if team_name:
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament_name,))
            tournament_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO teams (name, tournament_id) VALUES (?, ?)", (team_name, tournament_id))
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
        self.schedule_button = tk.Button(
            schedule_window,
            text="Schedule Match",
            command=lambda: self.save_match(tournament_name)
        )
        self.schedule_button.pack(pady=10)

    def save_match(self, tournament_name):
        """
        Saves the match schedule to the database.

        Args:
            tournament_name (str): Name of the tournament.
        """
        team1 = self.team1_combobox.get()
        team2 = self.team2_combobox.get()
        match_date = self.match_date_calendar.get_date()
        match_time = self.match_time_entry.get()

        if not team1 or not team2 or not match_date or not match_time:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        # Get tournament ID
        cursor.execute("SELECT id FROM tournaments WHERE name = ?", (tournament_name,))
        tournament_id = cursor.fetchone()[0]

        # Get team IDs
        cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team1, tournament_id))
        team1_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM teams WHERE name = ? AND tournament_id = ?", (team2, tournament_id))
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

        messagebox.showinfo("Success", f"Match scheduled between {team1} and {team2} on {match_datetime}!")

    def manage_scores(self, window, tournament_name):
        # Create a new window to manage scores
        score_window = tk.Toplevel(window)
        score_window.title(f"Manage Scores for {tournament_name}")

        # Load matches to choose from
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT matches.id, team1.name, team2.name, matches.date
        FROM matches
        JOIN teams AS team1 ON matches.team1_id = team1.id
        JOIN teams AS team2 ON matches.team2_id = team2.id
        WHERE matches.tournament_id = (SELECT id FROM tournaments WHERE name = ?)
        """, (tournament_name,))
        matches = cursor.fetchall()
        conn.close()

        self.match_combobox = tk.StringVar()
        match_dropdown = tk.OptionMenu(score_window, self.match_combobox, *[f"{match[1]} vs {match[2]} on {match[3]}" for match in matches])
        match_dropdown.pack(pady=10)

        # Button to open scoring panel
        self.open_scoring_panel_button = tk.Button(score_window, text="Open Scoring Panel", command=lambda: self.open_scoring_panel(score_window, matches))
        self.open_scoring_panel_button.pack(pady=10)

    def open_scoring_panel(self, match_window, matches):
        selected_match = self.match_combobox.get()
        if not selected_match:
            messagebox.showerror("Error", "Please select a match!")
            return

        # Find selected match ID
        match_index = [f"{match[1]} vs {match[2]} on {match[3]}" for match in matches].index(selected_match)
        match_id = matches[match_index][0]

        # Create scoring panel window
        scoring_window = tk.Toplevel(match_window)
        scoring_window.title(f"Scoring Panel: {selected_match}")
        scoring_window.geometry("600x600")  # Set window size

        # Initialize toss_winner_combobox before using it
        self.toss_winner_combobox = tk.StringVar()

        # Display live score
        self.team1_score = 0
        self.team2_score = 0
        self.current_overs = 0
        self.current_balls = 0

        score_frame = tk.Frame(scoring_window)
        score_frame.pack(pady=10)

        self.score_label = tk.Label(score_frame, text="Score: 0/0 Overs: 0.0", font=("Arial", 16))
        self.score_label.pack()

        # Toss Section
        toss_frame = tk.Frame(scoring_window)
        toss_frame.pack(pady=10, fill=tk.X)

        tk.Label(toss_frame, text="Select Toss Winner:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        teams = [matches[match_index][1], matches[match_index][2]]
        toss_winner_dropdown = tk.OptionMenu(toss_frame, self.toss_winner_combobox, *teams)
        toss_winner_dropdown.pack(side=tk.LEFT, padx=5)

        self.toss_decision = tk.StringVar()
        tk.Label(toss_frame, text="Decision:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(toss_frame, text="Bat", variable=self.toss_decision, value="Bat").pack(side=tk.LEFT)
        tk.Radiobutton(toss_frame, text="Bowl", variable=self.toss_decision, value="Bowl").pack(side=tk.LEFT)

        tk.Button(
            toss_frame, text="Save Toss Details",
            command=lambda: self.save_toss_details(match_id),
            bg="green", fg="white"
        ).pack(side=tk.LEFT, padx=10)

        # Player and Score Input Section
        input_frame = tk.Frame(scoring_window)
        input_frame.pack(pady=10, fill=tk.X)

        tk.Label(input_frame, text="Select Player:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT players.id, players.name, teams.name 
            FROM players 
            JOIN teams ON players.team_id = teams.id
            WHERE teams.id IN (
                SELECT team1_id FROM matches WHERE id = ?
                UNION
                SELECT team2_id FROM matches WHERE id = ?
            )
        """, (match_id, match_id))
        players = cursor.fetchall()
        conn.close()

        self.player_combobox = tk.StringVar()
        player_dropdown = tk.OptionMenu(input_frame, self.player_combobox, *[f"{player[1]} ({player[2]})" for player in players])
        player_dropdown.pack(side=tk.LEFT, padx=5)

        # Input for runs, wickets, extras
        runs_frame = tk.Frame(scoring_window)
        runs_frame.pack(pady=5, fill=tk.X)

        tk.Label(runs_frame, text="Runs:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.runs_entry = tk.Entry(runs_frame, width=5)
        self.runs_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(runs_frame, text="Wickets:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.wickets_entry = tk.Entry(runs_frame, width=5)
        self.wickets_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(runs_frame, text="Extras:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.extras_entry = tk.Entry(runs_frame, width=5)
        self.extras_entry.pack(side=tk.LEFT, padx=5)

        # Buttons to update scores
        action_frame = tk.Frame(scoring_window)
        action_frame.pack(pady=10, fill=tk.X)

        tk.Button(action_frame, text="Update Runs", command=lambda: self.update_score(match_id, players, "runs"), bg="blue", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(action_frame, text="Update Wickets", command=lambda: self.update_score(match_id, players, "wickets"), bg="red", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(action_frame, text="Add Extras", command=lambda: self.update_score(match_id, players, "extras"), bg="orange", fg="black").pack(side=tk.LEFT, padx=10)

        # Live scorecard display
        scorecard_frame = tk.Frame(scoring_window)
        scorecard_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(scorecard_frame, text="Live Scorecard:", font=("Arial", 14)).pack(pady=5)

        self.scorecard_text = tk.Text(scorecard_frame, height=15, width=60)
        self.scorecard_text.pack(pady=10)

        self.update_scorecard_display(match_id)
    
        def update_scorecard_display(self, match_id):
            """
            Update the scorecard display for the given match.
            """
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT players.name, score_details.runs, score_details.wickets, score_details.extras
                FROM score_details
                JOIN players ON score_details.player_id = players.id
                WHERE score_details.match_id = ?
            """, (match_id,))
            score_details = cursor.fetchall()
            conn.close()
    
            self.scorecard_text.delete(1.0, tk.END)
            for detail in score_details:
                self.scorecard_text.insert(tk.END, f"{detail[0]} - Runs: {detail[1]}, Wickets: {detail[2]}, Extras: {detail[3]}\n")

    def update_score(self, match_id, players, update_type):
        """
        Update the score for the match based on input type (runs, wickets, or extras).
        """
        try:
            if update_type == "runs":
                runs = int(self.runs_entry.get())
                self.team1_score += runs
                self.scorecard_text.insert(tk.END, f"Updated {runs} runs for {self.player_combobox.get()}.\n")
            elif update_type == "wickets":
                wickets = int(self.wickets_entry.get())
                self.scorecard_text.insert(tk.END, f"Recorded {wickets} wickets for {self.player_combobox.get()}.\n")
            elif update_type == "extras":
                extras = int(self.extras_entry.get())
                self.team1_score += extras
                self.scorecard_text.insert(tk.END, f"Added {extras} extras.\n")

            # Update overs
            self.current_balls += 1
            if self.current_balls == 6:
                self.current_overs += 1
                self.current_balls = 0

            # Update the score display
            self.score_label.config(text=f"Score: {self.team1_score}/{self.current_overs}.{self.current_balls}")
            self.update_scorecard_display(match_id)

        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter numeric values.")

        # Clear input fields
        self.runs_entry.delete(0, tk.END)
        self.wickets_entry.delete(0, tk.END)
        self.extras_entry.delete(0, tk.END)



if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentManagerApp(root)
    root.mainloop()
