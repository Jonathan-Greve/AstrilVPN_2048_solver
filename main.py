import numpy as np
from bs4 import BeautifulSoup

# Define possible moves
MOVES = ['up', 'down', 'left', 'right']

# Function to calculate score after a move
def score_board(board, move):
    # Create a copy of the board to manipulate
    board_copy = board.copy()
    if move == 'up':
        for j in range(4):
            column = board_copy[:, j]
            column = column[column != 0]  # remove zeros
            for i in range(len(column) - 1):
                if column[i] == column[i + 1]:  # merge tiles
                    column[i] *= 2
                    column[i + 1] = 0
            column = column[column != 0]  # remove zeros
            board_copy[:, j] = np.pad(column, (0, 4 - len(column)), 'constant')
    elif move == 'down':
        for j in range(4):
            column = board_copy[:, j][::-1]
            column = column[column != 0]  # remove zeros
            for i in range(len(column) - 1):
                if column[i] == column[i + 1]:  # merge tiles
                    column[i] *= 2
                    column[i + 1] = 0
            column = column[column != 0]  # remove zeros
            board_copy[:, j] = np.pad(column[::-1], (4 - len(column), 0), 'constant')
    elif move == 'left':
        for i in range(4):
            row = board_copy[i, :]
            row = row[row != 0]  # remove zeros
            for j in range(len(row) - 1):
                if row[j] == row[j + 1]:  # merge tiles
                    row[j] *= 2
                    row[j + 1] = 0
            row = row[row != 0]  # remove zeros
            board_copy[i, :] = np.pad(row, (0, 4 - len(row)), 'constant')
    elif move == 'right':
        for i in range(4):
            row = board_copy[i, :][::-1]
            row = row[row != 0]  # remove zeros
            for j in range(len(row) - 1):
                if row[j] == row[j + 1]:  # merge tiles
                    row[j] *= 2
                    row[j + 1] = 0
            row = row[row != 0]  # remove zeros
            board_copy[i, :] = np.pad(row[::-1], (4 - len(row), 0), 'constant')
    return np.sum(board_copy - board)

# Function to decide the next move
def decide_move(board):
    scores = {move: score_board(board, move) for move in MOVES}
    best_move = max(scores, key=scores.get)
    return best_move

# Function to convert space separated string into 4x4 numpy array and solve the game
def solve_2048_game(input_string):
    input_list = list(map(int, input_string.split()))
    board = np.array(input_list).reshape(4, 4)
    return decide_move(board)

def get_game_container(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the game-container div
    game_container = soup.find('div', class_='game-container')

    return str(game_container) if game_container else None


def get_board_state(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Create a 4x4 matrix to represent the board
    board = [[0] * 4 for _ in range(4)]

    # Find all the tiles
    tiles = soup.find_all(class_=lambda x: x and x.startswith('tile tile-'))

    for tile in tiles:
        classes = tile.get('class')
        # Find the tile value and position
        for cls in classes:
            if cls.startswith('tile-') and not 'position' in cls and not 'new' in cls:
                value_string = cls.split('-')[1]
                if value_string.isdigit():  # Check if the string can be converted to an integer
                    value = int(value_string)
                else:
                    continue  # Skip this class if it does not contain a valid integer
            elif cls.startswith('tile-position-'):
                position = cls.split('-')[2:]
                row = int(position[0]) - 1
                col = int(position[1]) - 1

        # Update the board - swap row and col here
        board[col][row] = value

    # Flatten the board to a single list and convert to strings
    board = [str(cell) for row in board for cell in row]

    return ' '.join(board)


html = ''''''  # Your HTML string goes here

# Extract the game-container div from the full HTML
game_container_html = get_game_container(html)

# Now pass the extracted game-container div to your existing get_board_state function
if game_container_html:
    board_state = get_board_state(game_container_html)
    print(board_state)
    print(solve_2048_game(board_state))
else:
    print("No game-container found.")




