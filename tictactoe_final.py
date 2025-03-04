from tkinter import *
import numpy as np
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('Tic_Tac_Toe.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                player1_name TEXT,
                player2_name TEXT,
                player1_score INTEGER DEFAULT 0,
                player2_score INTEGER DEFAULT 0
                )''')
conn.commit()

size_of_board = 600
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 50
symbol_X_color = '#EE4035'
symbol_O_color = '#0492CF'
Green_color = '#7BC043'

class Tic_Tac_Toe():
    # ------------------------------------------------------------------
    # Initialization Functions:
    # ------------------------------------------------------------------
    def __init__(self):
        self.window = Tk()
        self.window.title('Tic-Tac-Toe')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        # Input from user in form of clicks
        self.window.bind('<Button-1>', self.click)

        self.player_X_turns = True
        self.board_status = np.zeros(shape=(3, 3))

        self.player_X_starts = True
        self.reset_board = False
        self.gameover = False
        self.tie = False
        self.X_wins = False
        self.O_wins = False

        self.player1_name = None
        self.player2_name = None

        self.create_login_interface()

    def mainloop(self):
        self.window.mainloop()

    def create_login_interface(self):
        self.login_window = Toplevel(self.window)
        self.login_window.title("Player Login")

        label_player1 = Label(self.login_window, text="Player 1 (X) Name:")
        label_player1.grid(row=0, column=0)
        self.entry_player1 = Entry(self.login_window)
        self.entry_player1.grid(row=0, column=1)

        label_player2 = Label(self.login_window, text="Player 2 (O) Name:")
        label_player2.grid(row=1, column=0)
        self.entry_player2 = Entry(self.login_window)
        self.entry_player2.grid(row=1, column=1)

        button_start_game = Button(self.login_window, text="Start Game", command=self.start_game)
        button_start_game.grid(row=2, columnspan=2)

    def start_game(self):
        self.player1_name = self.entry_player1.get()
        self.player2_name = self.entry_player2.get()
        
        # Insert player names into the database if they don't exist
        cursor.execute('''INSERT OR IGNORE INTO players (player1_name, player2_name) VALUES (?, ?)''', (self.player1_name, self.player2_name))
        conn.commit()
        
        self.login_window.destroy()

        self.initialize_board()

    def initialize_board(self):
        for i in range(2):
            self.canvas.create_line((i + 1) * size_of_board / 3, 0, (i + 1) * size_of_board / 3, size_of_board)

        for i in range(2):
            self.canvas.create_line(0, (i + 1) * size_of_board / 3, size_of_board, (i + 1) * size_of_board / 3)

    def play_again(self):
        self.initialize_board()
        self.player_X_starts = not self.player_X_starts
        self.player_X_turns = self.player_X_starts
        self.board_status = np.zeros(shape=(3, 3))

    def draw_O(self, logical_position):
        logical_position = np.array(logical_position)
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_oval(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                outline=symbol_O_color)

    def draw_X(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                fill=symbol_X_color)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] + symbol_size,
                                grid_position[0] + symbol_size, grid_position[1] - symbol_size, width=symbol_thickness,
                                fill=symbol_X_color)

    def display_gameover(self):

        if self.X_wins:
            text = f'Winner: {self.player1_name} (X)'
        elif self.O_wins:
            text = f'Winner: {self.player2_name} (O)'
        else:
            text = 'It\'s a tie'

        self.canvas.delete("all")
        self.canvas.create_text(size_of_board / 2, size_of_board / 3, font="cmr 60 bold", fill='black', text=text)

        # Update scores in SQLite database
        if self.X_wins:
            cursor.execute('''UPDATE players SET player1_score = player1_score + 1 WHERE player1_name = ?''', (self.player1_name,))
            conn.commit()
        elif self.O_wins:
            cursor.execute('''UPDATE players SET player2_score = player2_score + 1 WHERE player2_name = ?''', (self.player2_name,))
            conn.commit()

        self.reset_board = True

    def convert_logical_to_grid_position(self, logical_position):
        logical_position = np.array(logical_position, dtype=int)
        return (size_of_board / 3) * logical_position + size_of_board / 6

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        return np.array(grid_position // (size_of_board / 3), dtype=int)

    def is_grid_occupied(self, logical_position):
        if self.board_status[logical_position[0]][logical_position[1]] == 0:
            return False
        else:
            return True

    def is_winner(self, player):

        player = -1 if player == 'X' else 1

        # Three in a row
        for i in range(3):
            if self.board_status[i][0] == self.board_status[i][1] == self.board_status[i][2] == player:
                return True
            if self.board_status[0][i] == self.board_status[1][i] == self.board_status[2][i] == player:
                return True

        # Diagonals
        if self.board_status[0][0] == self.board_status[1][1] == self.board_status[2][2] == player:
            return True

        if self.board_status[0][2] == self.board_status[1][1] == self.board_status[2][0] == player:
            return True

        return False

    def is_tie(self):

        r, c = np.where(self.board_status == 0)
        tie = False
        if len(r) == 0:
            tie = True

        return tie

    def is_gameover(self):
        self.X_wins = self.is_winner('X')
        if not self.X_wins:
            self.O_wins = self.is_winner('O')

        if not self.O_wins:
            self.tie = self.is_tie()

        gameover = self.X_wins or self.O_wins or self.tie

        return gameover

    def click(self, event):
        grid_position = [event.x, event.y]
        logical_position = self.convert_grid_to_logical_position(grid_position)

        if not self.reset_board:
            if self.player_X_turns:
                if not self.is_grid_occupied(logical_position):
                    self.draw_X(logical_position)
                    self.board_status[logical_position[0]][logical_position[1]] = -1
                    self.player_X_turns = not self.player_X_turns
            else:
                if not self.is_grid_occupied(logical_position):
                    self.draw_O(logical_position)
                    self.board_status[logical_position[0]][logical_position[1]] = 1
                    self.player_X_turns = not self.player_X_turns

            # Check if game is concluded
            if self.is_gameover():
                self.display_gameover()
        else:  # Play Again
            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False


game_instance = Tic_Tac_Toe()
game_instance.mainloop()
