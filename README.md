# Multiplayer Hangman Game

A fun and interactive multiplayer Hangman game built with Python and Pygame. Play solo or challenge your friends in an exciting word-guessing adventure!

## Features

- Single-player mode
- Multiplayer mode with lobby system
- Multiple word categories
- Interactive GUI with Pygame
- Sound effects for correct and incorrect guesses

## Requirements

- Python 3.7+
- Pygame

## Installation

1. Clone the repository:
git clone https://github.com/Moon-Elf/Hangman.git


2. Install the required dependencies:
pip install pygame


## How to Play

1. Run the game:
python client.py

2. From the main menu, choose:
- "Play" for single-player mode
- "Create Lobby" to host a multiplayer game
- "Join Lobby" to join an existing multiplayer game

3. In single-player mode:
- Select a word category
- Guess letters by clicking on the on-screen keyboard
- Try to guess the word before the hangman is fully drawn!

4. In multiplayer mode:
- As the host, wait for players to join and then start the game
- As a player, wait for the host to start the game
- Take turns guessing letters

## Project Structure

- `client.py`: Main game client with GUI and game logic
- `server.py`: Game server for multiplayer functionality
- `singleplayer.py`: Single-player game mode

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
