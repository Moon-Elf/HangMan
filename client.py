import pygame
import sys
import random
import string
import socket
import json
import threading
from singleplayer import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Hangman")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# Load hangman images
hangman_images = [pygame.image.load(f"hangman{i}.png") for i in range(7)]

# Load sounds
correct_sound = pygame.mixer.Sound("correct.wav")
wrong_sound = pygame.mixer.Sound("wrong.wav")
win_sound = pygame.mixer.Sound("win.wav")
lose_sound = pygame.mixer.Sound("lose.wav")

# Network setup
HOST = '127.0.0.1'
PORT = 65432

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class NetworkClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    def send(self, data):
        self.socket.sendall(json.dumps(data).encode())
        return json.loads(self.socket.recv(1024).decode())

client = NetworkClient()

def main_menu():
    play_button = Button(300, 150, 200, 50, "Play", WHITE, BLACK)
    create_lobby_button = Button(300, 225, 200, 50, "Create Lobby", WHITE, BLACK)
    join_lobby_button = Button(300, 300, 200, 50, "Join Lobby", WHITE, BLACK)
    exit_button = Button(300, 375, 200, 50, "Exit", WHITE, BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    play_single_player()
                elif create_lobby_button.is_clicked(event.pos):
                    create_lobby()
                elif join_lobby_button.is_clicked(event.pos):
                    join_lobby()
                elif exit_button.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        play_button.draw(screen)
        create_lobby_button.draw(screen)
        join_lobby_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()

def play_single_player():
    category = choose_category()
    word = random.choice(word_categories[category])
    guessed_letters = set()
    wrong_guesses = 0

    keyboard = create_keyboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key in keyboard:
                    if key.is_clicked(event.pos) and key.text not in guessed_letters:
                        letter = key.text
                        guessed_letters.add(letter)
                        if letter not in word:
                            wrong_guesses += 1
                            wrong_sound.play()
                        else:
                            correct_sound.play()

        screen.fill(WHITE)
        
        # Draw hangman
        screen.blit(hangman_images[min(wrong_guesses, MAX_WRONG_GUESSES)], (50, 50))

        # Draw word
        word_surface = large_font.render(" ".join(letter if letter in guessed_letters else "_" for letter in word), True, BLACK)
        screen.blit(word_surface, (300, 300))

        # Draw keyboard
        for key in keyboard:
            if key.text in guessed_letters:
                key.color = GRAY
            key.draw(screen)

        # Draw category
        category_surface = font.render(f"Category: {category}", True, BLACK)
        screen.blit(category_surface, (50, 20))

        # Check win/lose conditions
        if all(letter in guessed_letters for letter in word):
            win_surface = large_font.render("You Win!", True, GREEN)
            screen.blit(win_surface, (300, 200))
            win_sound.play()
            pygame.display.flip()
            pygame.time.wait(3000)
            break
        elif wrong_guesses >= MAX_WRONG_GUESSES:
            lose_surface = large_font.render(f"You Lose! The word was {word}", True, RED)
            screen.blit(lose_surface, (200, 200))
            lose_sound.play()
            pygame.display.flip()
            pygame.time.wait(3000)
            break

        pygame.display.flip()

def choose_category():
    categories = list(word_categories.keys())
    buttons = []
    for i, category in enumerate(categories):
        buttons.append(Button(300, 150 + i * 75, 200, 50, category, WHITE, BLACK))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        return button.text

        screen.fill(BLACK)
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()

def create_lobby():
    player_name = get_player_name()
    response = client.send({'action': 'create_lobby', 'name': player_name})
    if response['status'] == 'success':
        lobby_code = response['lobby_code']
        host_waiting_room(lobby_code, player_name)

def host_waiting_room(lobby_code, player_name):
    clock = pygame.time.Clock()
    start_button = Button(300, 400, 200, 50, "Start Game", WHITE, BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    response = client.send({'action': 'start_game', 'lobby_code': lobby_code})
                    if response['status'] == 'success':
                        category = choose_category()
                        client.send({'action': 'set_category', 'lobby_code': lobby_code, 'category': category})
                        play_multiplayer_game(lobby_code, player_name)
                        return

        response = client.send({'action': 'check_lobby_status', 'lobby_code': lobby_code})
        if response['status'] == 'success':
            player_count = response['player_count']
            players = response['players']

            screen.fill(BLACK)
            code_surface = large_font.render(f"Lobby Code: {lobby_code}", True, WHITE)
            screen.blit(code_surface, (250, 100))
            count_surface = font.render(f"Players: {player_count}", True, WHITE)
            screen.blit(count_surface, (350, 150))

            for i, player in enumerate(players):
                player_surface = font.render(player, True, WHITE)
                screen.blit(player_surface, (350, 200 + i * 30))

            if player_count >= 2:
                start_button.draw(screen)
            else:
                waiting_surface = font.render("Waiting for more players...", True, WHITE)
                screen.blit(waiting_surface, (250, 400))

        pygame.display.flip()
        clock.tick(30)

def join_lobby():
    lobby_code = ""
    player_name = get_player_name()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(lobby_code) == 6:
                    response = client.send({'action': 'join_lobby', 'lobby_code': lobby_code, 'name': player_name})
                    if response['status'] == 'success':
                        player_waiting_room(lobby_code, player_name)
                        return
                    else:
                        lobby_code = ""
                elif event.key == pygame.K_BACKSPACE:
                    lobby_code = lobby_code[:-1]
                elif event.unicode.isalnum() and len(lobby_code) < 6:
                    lobby_code += event.unicode.upper()

        screen.fill(BLACK)
        prompt_surface = font.render("Enter Lobby Code:", True, WHITE)
        screen.blit(prompt_surface, (300, 250))
        code_surface = large_font.render(lobby_code, True, WHITE)
        screen.blit(code_surface, (350, 300))
        pygame.display.flip()

def player_waiting_room(lobby_code, player_name):
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        response = client.send({'action': 'check_lobby_status', 'lobby_code': lobby_code})
        if response['status'] == 'success':
            if response['game_started']:
                play_multiplayer_game(lobby_code, player_name)
                return

            screen.fill(BLACK)
            code_surface = large_font.render(f"Lobby Code: {lobby_code}", True, WHITE)
            screen.blit(code_surface, (250, 100))
            count_surface = font.render(f"Players: {response['player_count']}", True, WHITE)
            screen.blit(count_surface, (350, 150))

            for i, player in enumerate(response['players']):
                player_surface = font.render(player, True, WHITE)
                screen.blit(player_surface, (350, 200 + i * 30))

            waiting_surface = font.render("Waiting for host to start the game...", True, WHITE)
            screen.blit(waiting_surface, (200, 400))

        pygame.display.flip()
        clock.tick(30)

def play_multiplayer_game(lobby_code, player_name):
    keyboard = create_keyboard()
    
    while True:
        response = client.send({'action': 'get_game_state', 'lobby_code': lobby_code})
        game_state = response['game_state']
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state['current_player_name'] == player_name:
                    for key in keyboard:
                        if key.is_clicked(event.pos) and key.text not in game_state['guessed_letters']:
                            response = client.send({'action': 'guess', 'lobby_code': lobby_code, 'letter': key.text})
                            if response['status'] == 'success':
                                game_state = response['game_state']
                                if key.text in game_state['word']:
                                    correct_sound.play()
                                else:
                                    wrong_sound.play()

        screen.fill(WHITE)
        
        # Draw hangman
        screen.blit(hangman_images[min(game_state['wrong_guesses'], len(hangman_images) - 1)], (50, 50))

        # Draw word
        word_surface = large_font.render(" ".join(game_state['word']), True, BLACK)
        screen.blit(word_surface, (300, 300))

        # Draw keyboard
        for key in keyboard:
            if key.text in game_state['guessed_letters']:
                key.color = GRAY
            else:
                key.color = WHITE
            key.draw(screen)

        # Draw current player and category
        current_player_surface = font.render(f"Current player: {game_state['current_player_name']}", True, BLUE)
        screen.blit(current_player_surface, (50, 20))
        category_surface = font.render(f"Category: {game_state['category']}", True, BLACK)
        screen.blit(category_surface, (50, 60))

        # Draw game over message
        if game_state['game_over']:
            if game_state['winner']:
                win_surface = large_font.render(f"{game_state['winner']} Wins!", True, GREEN)
                screen.blit(win_surface, (300, 200))
                win_sound.play()
            else:
                lose_surface = large_font.render("Game Over! No one guessed the word.", True, RED)
                screen.blit(lose_surface, (200, 200))
                lose_sound.play()

        pygame.display.flip()

        if game_state['game_over']:
            pygame.time.wait(3000)
            break

def create_keyboard():
    keyboard = []
    for i, letter in enumerate(string.ascii_uppercase):
        x = 100 + (i % 13) * 50
        y = 400 + (i // 13) * 50
        keyboard.append(Button(x, y, 40, 40, letter, WHITE, BLACK))
    return keyboard

def get_player_name():
    name = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 15:
                    name += event.unicode

        screen.fill(BLACK)
        prompt_surface = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_surface, (300, 250))
        name_surface = large_font.render(name, True, WHITE)
        screen.blit(name_surface, (300, 300))
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
