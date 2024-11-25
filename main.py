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

        # Initialize toss_winner_combobox before using it
        self.toss_winner_combobox = tk.StringVar()  # Initialize the combobox variable

        # Display live score
        self.team1_score = 0
        self.team2_score = 0
        self.current_overs = 0
        self.current_balls = 0

        self.score_label = tk.Label(scoring_window, text="Score: 0/0 Overs: 0.0")
        self.score_label.pack(pady=10)

        # Label for toss winner
        tk.Label(scoring_window, text="Select Toss Winner:").pack(pady=5)

        # Dropdown for toss winner
        teams = [matches[match_index][1], matches[match_index][2]]
        toss_winner_dropdown = tk.OptionMenu(scoring_window, self.toss_winner_combobox, *teams)
        toss_winner_dropdown.pack(pady=5)

        # Label and radiobuttons for toss decision
        tk.Label(scoring_window, text="Choose Toss Decision:").pack(pady=5)

        self.toss_decision = tk.StringVar()
        tk.Radiobutton(scoring_window, text="Bat", variable=self.toss_decision, value="Bat").pack(anchor=tk.W)
        tk.Radiobutton(scoring_window, text="Bowl", variable=self.toss_decision, value="Bowl").pack(anchor=tk.W)

        # Save Toss Details Button
        self.save_toss_button = tk.Button(
            scoring_window, text="Save Toss Details",
            command=lambda: self.save_toss_details(match_id)
        )
        self.save_toss_button.pack(pady=10)

        # Player list for score updates
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        # Get players from both teams
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
        player_dropdown = tk.OptionMenu(scoring_window, self.player_combobox, *[f"{player[1]} ({player[2]})" for player in players])
        player_dropdown.pack(pady=10)

        # Input fields for runs and wickets
        tk.Label(scoring_window, text="Add Runs:").pack()
        self.runs_entry = tk.Entry(scoring_window)
        self.runs_entry.pack(pady=5)

        tk.Label(scoring_window, text="Add Wickets:").pack()
        self.wickets_entry = tk.Entry(scoring_window)
        self.wickets_entry.pack(pady=5)

        # Buttons to update score
        self.add_score_button = tk.Button(scoring_window, text="Update Score", command=lambda: self.update_score(match_id, players))
        self.add_score_button.pack(pady=10)

        # Live scorecard display
        self.scorecard_text = tk.Text(scoring_window, height=15, width=50)
        self.scorecard_text.pack(pady=10)

        self.update_scorecard_display(match_id)

        # Check if toss details are already saved
        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT toss_winner_team_id, toss_decision FROM matches WHERE id = ?", (match_id,))
        toss_details = cursor.fetchone()
        conn.close()

        if toss_details and toss_details[0]:
            # Reopen the connection and fetch toss details
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM teams WHERE id = ?", (toss_details[0],))
            toss_winner_team_name = cursor.fetchone()[0]
            conn.close()

            tk.Label(scoring_window, text=f"Toss Winner: {toss_winner_team_name}, Elected to {toss_details[1]}").pack(pady=5)


    def save_toss_details(self, match_id):
        toss_winner = self.toss_winner_combobox.get()
        toss_decision = self.toss_decision.get()

        if not toss_winner or not toss_decision:
            messagebox.showerror("Error", "Please select toss winner and decision!")
            return

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM teams WHERE name = ?", (toss_winner,))
        toss_winner_team_id = cursor.fetchone()[0]

        cursor.execute("UPDATE matches SET toss_winner_team_id = ?, toss_decision = ? WHERE id = ?", (toss_winner_team_id, toss_decision, match_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Toss details saved successfully!")
        def update_score(self, match_id, players):
            player_name = self.player_combobox.get()
            runs = self.runs_entry.get()
            wickets = self.wickets_entry.get()

            if not player_name or not runs or not wickets:
                messagebox.showerror("Error", "Please fill all fields!")
                return

            # Find player ID
            player_index = [f"{player[1]} ({player[2]})" for player in players].index(player_name)
            player_id = players[player_index][0]

            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            # Insert the score data into the database
            cursor.execute("INSERT INTO scores (match_id, player_id, runs, wickets) VALUES (?, ?, ?, ?)", 
                           (match_id, player_id, int(runs), int(wickets)))
            conn.commit()

            # Update team total scores
            cursor.execute("""
            UPDATE teams 
            SET total_runs = (SELECT SUM(runs) FROM scores WHERE match_id = ? AND player_id IN 
                              (SELECT id FROM players WHERE team_id IN (SELECT id FROM teams WHERE match_id = ?)))
            WHERE id = ?
            """, (match_id, match_id, team_id))

            conn.commit()
            conn.close()

            # Refresh the scorecard display
            self.update_scorecard_display(match_id)

            messagebox.showinfo("Success", "Score updated successfully!")


    def update_scorecard_display(self, match_id):
        self.scorecard_text.delete(1.0, tk.END)

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        cursor.execute("""
        SELECT players.name, scores.runs, scores.balls, scores.wickets
        FROM scores
        JOIN players ON scores.player_id = players.id
        WHERE scores.match_id = ?
        """, (match_id,))
        scores = cursor.fetchall()
        conn.close()

        # Display the scorecard for each player
        for score in scores:
            self.scorecard_text.insert(tk.END, f"Player: {score[0]} Runs: {score[1]} Balls: {score[2]} Wickets: {score[3]}\n")


    def view_scores(self, match_id):
        """
        View scores for a specific match.

        Args:
            match_id (int): ID of the match.
        """
        try:
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            cursor.execute("""
            SELECT players.name, scores.runs, scores.balls, scores.wickets
            FROM scores
            JOIN players ON scores.player_id = players.id
            WHERE scores.match_id = ?
            """, (match_id,))
            scores = cursor.fetchall()

            conn.close()

            # Display scores (you can integrate this into the UI as needed)
            for score in scores:
                print(f"Player: {score[0]}, Runs: {score[1]}, Balls: {score[2]}, Wickets: {score[3]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scores: {e}")
        player_index = [f"{player[1]} ({player[2]})" for player in players].index(player)
        player_id = players[player_index][0]

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO scores (match_id, player_id, runs, wickets) VALUES (?, ?, ?, ?)", (match_id, player_id, runs, wickets))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Score updated successfully!")
        self.update_scorecard_display(match_id)

    def update_scorecard_display(self, match_id):
        self.scorecard_text.delete(1.0, tk.END)

        conn = sqlite3.connect('tournament_manager.db')
        cursor = conn.cursor()

        cursor.execute("""
        SELECT players.name, scores.runs, scores.balls, scores.wickets 
        FROM scores 
        JOIN players ON scores.player_id = players.id 
        WHERE scores.match_id = ?
        """, (match_id,))
        scores = cursor.fetchall()
        conn.close()

        # Display scorecard
        for score in scores:
            self.scorecard_text.insert(tk.END, f"Player: {score[0]} Runs: {score[1]} Balls: {score[2]} Wickets: {score[3]}\n")

    def view_scores(self, match_id):
        """
        View scores for a specific match.

        Args:
            match_id (int): ID of the match.
        """
        try:
            conn = sqlite3.connect('tournament_manager.db')
            cursor = conn.cursor()

            cursor.execute("""
            SELECT players.name, scores.runs, scores.balls, scores.wickets
            FROM scores
            JOIN players ON scores.player_id = players.id
            WHERE scores.match_id = ?
            """, (match_id,))
            scores = cursor.fetchall()

            conn.close()

            # Display scores (you can integrate this into the UI as needed)
            for score in scores:
                print(f"Player: {score[0]}, Runs: {score[1]}, Balls: {score[2]}, Wickets: {score[3]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scores: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentManagerApp(root)
    root.mainloop()
