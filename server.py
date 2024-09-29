import socket
import threading
import random
import json

HOST = '127.0.0.1'
PORT = 65432
MAX_WRONG_GUESSES = 7
word_categories = {
    "Animals": ["ELEPHANT", "GIRAFFE", "PENGUIN", "TIGER", "DOLPHIN"],
    "Countries": ["BRAZIL", "JAPAN", "AUSTRALIA", "FRANCE", "CANADA"],
    "Fruits": ["APPLE", "BANANA", "ORANGE", "STRAWBERRY", "PINEAPPLE"],
    "Sports": ["FOOTBALL", "TENNIS", "BASKETBALL", "SWIMMING", "VOLLEYBALL"]
}

class GameSession:
    def __init__(self, host):
        self.players = [host]
        self.player_names = {}
        self.host = host
        self.game_started = False
        self.category = None
        self.word = None
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.current_player = 0
        self.winner = None

    def add_player(self, player_id, name):
        self.players.append(player_id)
        self.player_names[player_id] = name

    def is_ready_to_start(self):
        return len(self.players) >= 2

    def start_game(self, category):
        self.game_started = True
        self.category = category
        self.word = random.choice(word_categories[category])

    def guess(self, letter):
        self.guessed_letters.add(letter)
        is_correct = letter in self.word
        if not is_correct:
            self.wrong_guesses = min(self.wrong_guesses + 1, MAX_WRONG_GUESSES)
        self.current_player = (self.current_player + 1) % len(self.players)
        print(f"Turn passed to player {self.current_player}")  # Debug print
        return is_correct


    def is_game_over(self):
        return self.wrong_guesses >= 7 or all(letter in self.guessed_letters for letter in self.word)

    def get_game_state(self):
        return {
            "word": "".join(letter if letter in self.guessed_letters else "_" for letter in self.word),
            "guessed_letters": list(self.guessed_letters),
            "wrong_guesses": self.wrong_guesses,
            "current_player": self.current_player,
            "game_over": self.is_game_over(),
            "winner": self.winner,
            "category": self.category,
            "current_player_name": self.player_names[self.players[self.current_player]]
        }

class Server:
    def __init__(self):
        self.lobbies = {}

    def create_lobby(self, host, name):
        lobby_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        self.lobbies[lobby_code] = GameSession(host)
        self.lobbies[lobby_code].add_player(host, name)
        return lobby_code

    def join_lobby(self, lobby_code, player, name):
        if lobby_code in self.lobbies:
            self.lobbies[lobby_code].add_player(player, name)
            return True
        return False

    def handle_client(self, conn, addr):
        print(f"New connection from {addr}")
        player_id = addr[1]

        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                message = json.loads(data)
                response = self.process_message(message, player_id)
                conn.sendall(json.dumps(response).encode())

            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break

        print(f"Connection from {addr} closed")
        conn.close()

    def process_message(self, message, player_id):
        action = message.get('action')

        if action == 'create_lobby':
            lobby_code = self.create_lobby(player_id, message['name'])
            return {'status': 'success', 'lobby_code': lobby_code}

        elif action == 'join_lobby':
            lobby_code = message['lobby_code']
            if self.join_lobby(lobby_code, player_id, message['name']):
                return {'status': 'success', 'lobby_code': lobby_code}
            else:
                return {'status': 'error', 'message': 'Invalid lobby code'}

        elif action == 'check_lobby_status':
            lobby_code = message['lobby_code']
            game = self.lobbies[lobby_code]
            return {
                'status': 'success',
                'player_count': len(game.players),
                'players': list(game.player_names.values()),
                'ready_to_start': game.is_ready_to_start(),
                'game_started': game.game_started
            }

        elif action == 'start_game':
            lobby_code = message['lobby_code']
            game = self.lobbies[lobby_code]
            if player_id == game.host and game.is_ready_to_start():
                return {'status': 'success'}
            else:
                return {'status': 'error', 'message': 'Not authorized to start the game'}

        elif action == 'set_category':
            lobby_code = message['lobby_code']
            category = message['category']
            game = self.lobbies[lobby_code]
            game.start_game(category)
            return {'status': 'success'}

        elif action == 'guess':
            lobby_code = message['lobby_code']
            letter = message['letter']
            game = self.lobbies[lobby_code]
            
            if game.players[game.current_player] != player_id:
                return {'status': 'error', 'message': 'Not your turn'}

            is_correct = game.guess(letter)
            game.current_player = (game.current_player + 1) % len(game.players)
            
            if all(letter in game.guessed_letters for letter in game.word):
                game.winner = game.player_names[player_id]
            
            return {'status': 'success', 'game_state': game.get_game_state()}


        elif action == 'get_game_state':
            lobby_code = message['lobby_code']
            game = self.lobbies[lobby_code]
            return {'status': 'success', 'game_state': game.get_game_state()}

        return {'status': 'error', 'message': 'Invalid action'}

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()
