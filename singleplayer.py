import pygame
import sys
import random
import string

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

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

# Word categories
word_categories = {
    "Animals": ["ELEPHANT", "GIRAFFE", "PENGUIN", "TIGER", "DOLPHIN"],
    "Countries": ["BRAZIL", "JAPAN", "AUSTRALIA", "FRANCE", "CANADA"],
    "Fruits": ["APPLE", "BANANA", "ORANGE", "STRAWBERRY", "PINEAPPLE"],
    "Sports": ["FOOTBALL", "TENNIS", "BASKETBALL", "SWIMMING", "VOLLEYBALL"]
}

MAX_WRONG_GUESSES = len(hangman_images) - 1

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

def main_menu():
    play_button = Button(300, 150, 200, 50, "Play", WHITE, BLACK)
    exit_button = Button(300, 225, 200, 50, "Exit", WHITE, BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    category_menu()
                elif exit_button.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        play_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.flip()

def category_menu():
    buttons = []
    for i, category in enumerate(word_categories.keys()):
        buttons.append(Button(300, 150 + i * 75, 200, 50, category, WHITE, BLACK))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        play_game(button.text)

        screen.fill(BLACK)
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()

def play_game(category):
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
        elif wrong_guesses >= MAX_WRONG_GUESSES:
            lose_surface = large_font.render(f"You Lose! The word was {word}", True, RED)
            screen.blit(lose_surface, (200, 200))
            lose_sound.play()

        pygame.display.flip()

        if all(letter in guessed_letters for letter in word) or wrong_guesses >= MAX_WRONG_GUESSES:
            pygame.time.wait(3000)
            break

def create_keyboard():
    keyboard = []
    for i, letter in enumerate(string.ascii_uppercase):
        x = 100 + (i % 13) * 50
        y = 400 + (i // 13) * 50
        keyboard.append(Button(x, y, 40, 40, letter, WHITE, BLACK))
    return keyboard

if __name__ == "__main__":
    main_menu()
