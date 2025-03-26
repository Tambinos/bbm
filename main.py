import ttkbootstrap as tb
from tkinter import StringVar, IntVar
from tkinter.ttk import Combobox, Entry, Button, LabelFrame, Label, Treeview
from neo4j import GraphDatabase


class LeagueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("League Manager")
        self.root.geometry("700x700")
        self.style = tb.Style("superhero")  # Modern dark theme

        # Neo4j setup
        self.uri = "neo4j://localhost:7687"
        self.user = "neo4j"
        self.password = "password"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

        self.create_widgets()
        self.update_team_list()
        self.update_division_table()

    def create_widgets(self):
        for widget in root.winfo_children():
            widget.destroy()
        # Main Container Frame
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # TEAM CREATION SECTION
        team_frame = LabelFrame(main_frame, text="Create Team", padding=10)
        team_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        Label(team_frame, text="Team Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.team_name_entry = Entry(team_frame, width=25)
        self.team_name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(team_frame, text="Division:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.division_var = StringVar()
        self.division_combobox = Combobox(team_frame, textvariable=self.division_var, values=["Swiss", "NBA"], width=22)
        self.division_combobox.grid(row=1, column=1, padx=5, pady=5)

        Button(team_frame, text="Create Team", command=self.create_team, bootstyle="success").grid(row=2, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=10)

        # PLAYER CREATION SECTION
        player_frame = LabelFrame(main_frame, text="Create Player", padding=10)
        player_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        Label(player_frame, text="Player Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.player_name_entry = Entry(player_frame, width=25)
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(player_frame, text="Team:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.team_var = StringVar()
        self.team_combobox = Combobox(player_frame, textvariable=self.team_var, width=22)
        self.team_combobox.grid(row=1, column=1, padx=5, pady=5)

        Button(player_frame, text="Create Player", command=self.create_player, bootstyle="primary").grid(row=2,
                                                                                                         column=0,
                                                                                                         columnspan=2,
                                                                                                         pady=10)

        # MATCH CREATION SECTION
        match_frame = LabelFrame(main_frame, text="Create Match", padding=10)
        match_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        Label(match_frame, text="Team 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.team1_var = StringVar()
        self.team1_combobox = Combobox(match_frame, textvariable=self.team1_var, width=22)
        self.team1_combobox.grid(row=0, column=1, padx=5, pady=5)

        Label(match_frame, text="Team 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.team2_var = StringVar()
        self.team2_combobox = Combobox(match_frame, textvariable=self.team2_var, width=22)
        self.team2_combobox.grid(row=1, column=1, padx=5, pady=5)

        Label(match_frame, text="Score 1:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.score1_var = IntVar()
        self.score1_entry = Entry(match_frame, textvariable=self.score1_var, width=10)
        self.score1_entry.grid(row=2, column=1, padx=5, pady=5)

        Label(match_frame, text="Score 2:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.score2_var = IntVar()
        self.score2_entry = Entry(match_frame, textvariable=self.score2_var, width=10)
        self.score2_entry.grid(row=3, column=1, padx=5, pady=5)

        Button(match_frame, text="Create Match", command=self.create_match, bootstyle="danger").grid(row=4, column=0,
                                                                                                     columnspan=2,
                                                                                                     pady=10)

        # DIVISION TABLE & RADIO BUTTONS
        standings_frame = LabelFrame(main_frame, text="League Standings", padding=10)
        standings_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.selected_division = StringVar(value="NBA")  # Default selection

        radio_frame = tb.Frame(standings_frame)
        radio_frame.pack(pady=5)

        tb.Radiobutton(radio_frame, text="Swiss", variable=self.selected_division, value="Swiss",
                       command=self.update_division_table).pack(side="left", padx=5)
        tb.Radiobutton(radio_frame, text="NBA", variable=self.selected_division, value="NBA",
                       command=self.update_division_table).pack(side="left", padx=5)

        self.division_table = Treeview(standings_frame, columns=("Team", "Wins", "Losses"), show="headings")
        self.division_table.heading("Team", text="Team")
        self.division_table.heading("Wins", text="Wins")
        self.division_table.heading("Losses", text="Losses")
        self.division_table.pack(fill='both', expand=True)
        self.delete_team_button = Button(standings_frame, text="Delete Team", command=self.delete_team,
                                         bootstyle="danger")
        self.delete_team_button.pack(pady=5)
        self.division_table.bind("<Double-1>", self.on_double_click_edit)

    def update_team_list(self):
        teams = self.get_team_names()
        self.team_combobox["values"] = teams
        self.team1_combobox["values"] = teams
        self.team2_combobox["values"] = teams

    def get_team_names(self):
        with self.driver.session() as session:
            result = session.run("MATCH (t:Team) RETURN t.name AS name")
            return [record["name"] for record in result]

    def create_team(self):
        name = self.team_name_entry.get()
        division = self.division_var.get()
        with self.driver.session() as session:
            session.run("CREATE (t:Team {name: $name, division: $division, wins: 0, losses: 0})", name=name,
                        division=division)
        self.update_team_list()
        self.update_division_table()

    def create_player(self):
        name = self.player_name_entry.get()
        team = self.team_var.get()
        with self.driver.session() as session:
            session.run("MATCH (t:Team {name: $team}) CREATE (p:Player {name: $name})-[:BELONGS_TO]->(t)", name=name,
                        team=team)

    def create_match(self):
        team1 = self.team1_var.get()
        team2 = self.team2_var.get()
        score1 = self.score1_var.get()
        score2 = self.score2_var.get()

        if not team1 or not team2 or team1 == team2:
            print("Invalid match setup!")  # Add proper UI error handling
            return

        if score1 > score2:
            winner, loser = team1, team2
        elif score2 > score1:
            winner, loser = team2, team1
        else:
            winner, loser = None, None  # Handle draws if needed

        with self.driver.session() as session:
            # Create the match node and relationships
            if winner and loser:
                session.run("""
                    MATCH (tW:Team {name: $winner}), (tL:Team {name: $loser})
                    CREATE (m:Match {score1: $score1, score2: $score2})
                    CREATE (m)-[:WINNER]->(tW)
                    CREATE (m)-[:LOSER]->(tL)
                """, winner=winner, loser=loser, score1=score1, score2=score2)

                # Update win/loss counts only for matches where both teams are in the same division
                session.run("""
                    MATCH (tW:Team {name: $winner})-[:WINNER]->(m:Match)-[:LOSER]->(tL:Team {name: $loser})
                    WHERE tW.division = tL.division
                    SET tW.wins = COALESCE(tW.wins, 0) + 1
                    SET tL.losses = COALESCE(tL.losses, 0) + 1
                """, winner=winner, loser=loser)

        self.update_division_table()

    def update_division_table(self):
        division = self.selected_division.get()
        self.division_table.delete(*self.division_table.get_children())

        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Team {division: $division})
                OPTIONAL MATCH (t)<-[:WINNER]-(m:Match)-[:LOSER]->(opponent:Team)
                WHERE opponent.division = $division
                OPTIONAL MATCH (t)<-[:LOSER]-(m2:Match)-[:WINNER]->(opponent2:Team)
                WHERE opponent2.division = $division
                WITH t, 
                     COUNT(DISTINCT m) AS wins, 
                     COUNT(DISTINCT m2) AS losses
                RETURN t.name AS team, wins, losses 
                ORDER BY wins DESC
            """, division=division)

            for record in result:
                self.division_table.insert("", "end", values=(record["team"], record["wins"], record["losses"]))

    def delete_team(self):
        selected_item = self.division_table.selection()
        if not selected_item:
            print("No team selected!")
            return

        team_name = self.division_table.item(selected_item, "values")[0]
        with self.driver.session() as session:
            # Delete all matches where the team is involved
            session.run("""
                MATCH (m:Match)-[:WINNER|LOSER]->(t:Team {name: $team_name})
                DETACH DELETE m
            """, team_name=team_name)

            # Delete the team itself
            session.run("""
                MATCH (t:Team {name: $team_name})
                DETACH DELETE t
            """, team_name=team_name)

        self.division_table.delete(selected_item)
        self.update_division_table()

    def on_double_click_edit(self, event):
        item = self.division_table.identify_row(event.y)
        if not item:
            return

        column = self.division_table.identify_column(event.x)
        if column != "#1":
            return

        col_index = int(column[1:]) - 1
        # Get the bounding box of the cell (for reference, not used in grid)
        x, y, width, height = self.division_table.bbox(item, col_index)
        team_name = self.division_table.item(item, "values")[0]

        # Create the entry widget
        self.edit_entry = Entry(self.division_table)
        self.edit_entry.grid(row=self.division_table.index(item), column=col_index, sticky="nsew")  # Use grid

        self.edit_entry.insert(0, team_name)
        self.edit_entry.focus()

        # Bind the events for saving or discarding the changes
        self.edit_entry.bind("<Return>", lambda e: self.save_team_name_edit(item, team_name))
        self.edit_entry.bind("<FocusOut>", lambda e: self.save_team_name_edit(item, team_name))

        # Configure grid to expand with cell
        self.division_table.grid_columnconfigure(col_index, weight=1)
        self.division_table.grid_rowconfigure(self.division_table.index(item), weight=1)

    def save_team_name_edit(self, item, old_name):
        new_name = self.edit_entry.get()
        self.edit_entry.destroy()

        with self.driver.session() as session:
            session.run("""
                MATCH (t:Team {name: $old_name})
                SET t.name = $new_name
            """, old_name=old_name, new_name=new_name)

            session.run("""
                MATCH (m:Match)-[r:WINNER|LOSER]->(t:Team {name: $new_name})
                SET r.team = $new_name
            """, new_name=new_name)
        self.__init__(root)


if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = LeagueApp(root)
    root.mainloop()