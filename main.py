import tkinter as tk
import random
import pygame
import time
import os


class SnakeLadderLudo:
    def __init__(self, root, mode):
        self.root = root
        self.mode = mode
        self.root.title("Unconventional Snake, Ladder & Ludo Game")

        self.board_frame = tk.Frame(root)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.log_frame = tk.Frame(root)
        self.log_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.canvas = tk.Canvas(self.board_frame, width=600, height=600)
        self.canvas.pack()

        self.move_log_text = tk.Text(self.log_frame, width=40, height=20)
        self.move_log_text.pack()

        # Tag configs for colored logs
        self.move_log_text.insert("1.0", "3. Yellow dots are powerups(gives one extra turn)\n")
        self.move_log_text.insert("1.0", "2. Green lines are ladders 🪜 \n")
        self.move_log_text.insert("1.0", "1. Red lines are snakes 🐍\n")
        self.move_log_text.insert("1.0", "======= Game Rules =======\n")
        self.move_log_text.tag_config("player1", foreground="blue")
        self.move_log_text.tag_config("player2", foreground="red")
        self.move_log_text.tag_config("ai", foreground="green")
        self.move_log_text.tag_config("snake", foreground="orange")
        self.move_log_text.tag_config("ladder", foreground="purple")
        self.move_log_text.tag_config("power", foreground="gold")



        if mode == "Human vs Human":
            self.players = {1: 1, 2: 1}
            colors = ["blue", "red"]
        else:
            self.players = {1: 1, 2: 1}
            colors = ["blue", "green"]  # AI is green

        self.player_tokens = {}
        for idx, color in enumerate(colors, start=1):
            self.player_tokens[idx] = self.canvas.create_oval(10 + (idx - 1) * 40, 560, 40 + (idx - 1) * 40, 590,
                                                              fill=color)

        self.current_player = 1
        self.turn_counter = 0

        self.snakes = {98: 78, 95: 75, 93: 73, 87: 24, 64: 60, 62: 19, 56: 53, 49: 11, 47: 26, 16: 6}
        self.ladders = {2: 38, 7: 14, 8: 31, 15: 26, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 78: 98}
        self.power_ups = {10: "extra_turn", 30: "skip_opponent", 50: "double_dice", 70: "teleport"}

        self.create_board()
        self.draw_snakes_and_ladders()

        pygame.mixer.init()

        self.roll_button = tk.Button(root, text="Roll Dice", command=self.roll_dice)
        self.roll_button.pack(side=tk.LEFT, padx=10)

        self.dice_label = tk.Label(root, text="Roll: ")
        self.dice_label.pack(side=tk.LEFT, padx=10)

    def create_board(self):
        cell_size = 60
        self.positions = {}
        for row in range(10):
            for col in range(10):
                x1 = col * cell_size
                y1 = (9 - row) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                pos = row * 10 + col + 1 if row % 2 == 0 else row * 10 + (10 - col)
                self.canvas.create_text(x1 + 30, y1 + 30, text=str(pos), font=("Arial", 10, "bold"))
                self.positions[pos] = (x1 + 15, y1 + 15)
                if pos in self.power_ups:
                    self.canvas.create_oval(x1 + 20, y1 + 20, x1 + 40, y1 + 40, fill="gold", outline="black")

    def draw_snakes_and_ladders(self):
        self.canvas.delete("snake_or_ladder")
        for start, end in self.ladders.items():
            self.draw_connection(start, end, "green", ladder=True)
        for start, end in self.snakes.items():
            self.draw_connection(start, end, "red", ladder=False)

    def draw_connection(self, start, end, color, ladder=True):
        if start not in self.positions or end not in self.positions:
            return
        x1, y1 = self.positions[start]
        x2, y2 = self.positions[end]
        arrow = tk.LAST if ladder else tk.FIRST
        self.canvas.create_line(x1 + 15, y1 + 15, x2 + 15, y2 + 15, fill=color, width=4,
                                arrow=arrow, arrowshape=(16, 20, 6), tags="snake_or_ladder")

    def roll_dice(self):
        dice_value = random.randint(1, 6)
        self.dice_label.config(text=f"Roll: {dice_value}")
        self.play_sound("744984__aalorv__dice-rolls-d12.wav")
        self.move_player(dice_value)

    def move_player(self, steps):
        player = self.current_player
        original_pos = self.players[player]
        self.players[player] += steps
        if self.players[player] > 100:
            self.players[player] = 100

        msg_tag = "player1" if player == 1 else "ai" if self.mode == "Human vs AI" and player == 2 else "player2"
        message = f"{'AI' if msg_tag == 'ai' else f'Player {player}'} rolled {steps} , moved from {original_pos} to {self.players[player]}"
        event_message = ""

        # Snake
        if self.players[player] in self.snakes:
            bitten_pos = self.players[player]
            self.players[player] = self.snakes[bitten_pos]
            message += f" — bitten by a snake 🐍! Slides to {self.players[player]}"
            event_message += "  🐍 Snake bite!\n"
            self.move_log_text.insert(tk.END, message + "\n", msg_tag)
            self.move_log_text.insert(tk.END, event_message, "snake")

        # Ladder
        elif self.players[player] in self.ladders:
            climbed_pos = self.players[player]
            self.players[player] = self.ladders[climbed_pos]
            message += f" — climbed a ladder 🪜! Climbs to {self.players[player]}"
            event_message += "  ⬆ 🪜Climbed a ladder!\n"
            self.move_log_text.insert(tk.END, message + "\n", msg_tag)
            self.move_log_text.insert(tk.END, event_message, "ladder")

        else:
            self.move_log_text.insert(tk.END, message + "\n", msg_tag)

        # Power-up
        if self.players[player] in self.power_ups:
            power = self.power_ups[self.players[player]]
            self.apply_power_up(player, power)
            self.move_log_text.insert(tk.END, f"  ⚡ Power-up: {power}\n", "power")

        self.move_log_text.yview(tk.END)
        self.update_player_position(player)

        if self.players[player] == 100:
            winner = "AI" if (self.mode == "Human vs AI" and player == 2) else f"Player {player}"
            self.dice_label.config(text=f"{winner} Wins!")
            self.play_sound("337049__shinephoenixstormcrow__320655__rhodesmas__level-up-01.mp3")
            self.roll_button.config(state="disabled")
            if not hasattr(self, "restart_button"):
                self.restart_button = tk.Button(self.root, text="Restart Game", command=self.restart_game)
                self.restart_button.pack(pady=10)
            return

        self.turn_counter += 1
        if self.turn_counter % 3 == 0:
            self.randomize_snakes_and_ladders()

        if self.power_ups.get(self.players[player]) != "extra_turn":
            self.current_player = 1 if self.current_player == 2 else 2

        if self.mode == "Human vs AI":
            if self.current_player == 2:
                self.roll_button.config(state="disabled")
                self.root.after(1000, self.ai_turn)
            else:
                self.roll_button.config(state="normal")

    def ai_turn(self):
        if self.players[2] < 100:
            dice_value = random.randint(1, 6)
            self.dice_label.config(text=f"AI rolled: {dice_value}")
            self.move_player(dice_value)

    def apply_power_up(self, player, power):
        if power == "extra_turn":
            pass
        elif power == "skip_opponent":
            self.current_player = player
        elif power == "double_dice":
            self.move_player(random.randint(1, 6))
        elif power == "teleport":
            self.players[player] = random.randint(1, 100)
            if self.players[player] in self.snakes:
                self.players[player] = self.snakes[self.players[player]]
            if self.players[player] in self.ladders:
                self.players[player] = self.ladders[self.players[player]]

    def update_player_position(self, player):
        if self.players[player] not in self.positions:
            return
        x, y = self.positions[self.players[player]]
        x += 0 if player == 1 else 20
        self.canvas.coords(self.player_tokens[player], x, y, x + 20, y + 20)

    def randomize_snakes_and_ladders(self):
        self.snakes.clear()
        self.ladders.clear()
        while len(self.snakes) < 5:
            head = random.randint(20, 99)
            tail = random.randint(1, head - 10)
            if head not in self.snakes and head not in self.ladders:
                self.snakes[head] = tail
        while len(self.ladders) < 5:
            bottom = random.randint(1, 79)
            top = random.randint(bottom + 10, 100)
            if bottom not in self.snakes and bottom not in self.ladders:
                self.ladders[bottom] = top
        self.draw_snakes_and_ladders()

    def play_sound(self, sound_file):
        if os.path.exists(sound_file):
            try:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"Error playing sound {sound_file}: {e}")
        else:
            print(f"Sound file {sound_file} not found.")

    def restart_game(self):
        self.root.destroy()
        show_start_menu()


def start_game(mode):
    start_window.destroy()
    root = tk.Tk()
    game = SnakeLadderLudo(root, mode)
    root.mainloop()


def show_start_menu():
    global start_window
    start_window = tk.Tk()
    start_window.title("Select Game Mode")
    tk.Label(start_window, text="Choose Game Mode", font=("Arial", 16)).pack(pady=10)
    tk.Button(start_window, text="Human👨 vs Human👨", command=lambda: start_game("Human vs Human"), width=20).pack(pady=5)
    tk.Button(start_window, text="Human👨 vs AI🤖", command=lambda: start_game("Human vs AI"), width=20).pack(pady=5)
    start_window.mainloop()


# Launch
show_start_menu()
