import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import random
import copy

class Engine:

    def __init__(self):
        self.size = 4
        self.board = [[0 for i in range(self.size)] for i in range(self.size)]
        self.score = 0
        self.numMoves = 0
        self.moveList = ['down','left','up','right']
        self.addRandBlock()
        self.addRandBlock()

    def setBoard(self, boardString):
        boardList = list(map(int, boardString.split(' ')))
        if len(boardList) != 16:
            raise ValueError("Invalid board string. It must contain 16 space-separated integers.")
        self.board = [boardList[i:i+self.size] for i in range(0, len(boardList), self.size)]
        self.score = 0
        self.numMoves = 0

    def scoreBonus(self, val):
        """
        Returns the score to add when tile merged
        """
        score = {
            2: 4,
            4: 8,
            8: 16,
            16: 32,
            32: 64,
            64: 128,
            128: 256,
            256: 512,
            512: 1024,
            1024: 2048,
            2048: 4096,
            4096: 8192,
            8192: 16384,
            16384: 32768,
            32768: 65536,
            65536: 131072,
        }
        return score[val]

    def rotateBoard(self, board, count):
        """
        Rotate the board in order to make moves in different directions
        """
        for c in range(count):
            rotated = [[0 for i in range(self.size)] for i in range(self.size)]

            for row in range(self.size):
                for col in range(self.size):
                    rotated[self.size - col - 1][row] = board[row][col]

            board = rotated

        return rotated

    def makeMove(self, moveDir):
        """
        Shift the board to make the given move
        """
        # Check if the game is already over
        if self.gameOver():
            pass

        board = self.board

        # Set how many rotations based on the move
        rotateCount = self.moveList.index(moveDir)
        moved = False

        # Rotate board to orient the board downwards
        if rotateCount:
            board = self.rotateBoard(board, rotateCount)

        #make an array to track merged tiles
        merged = [[0 for i in range(self.size)] for i in range(self.size)]


        for row in range(self.size - 1):
            for col in range(self.size):

                currentTile = board[row][col]
                nextTile = board[row+1][col]

                #go to next tile if current tile is empty
                if not currentTile:
                    continue

                #if next position is empty, move all tiles down
                if not nextTile:
                    for x in range(row+1):
                        board[row-x+1][col] = board[row-x][col]
                    board[0][col] = 0
                    moved = True
                    continue
                #if tile was merged already, go to next tile
                if merged[row][col]:
                    continue

                if currentTile == nextTile:
                    #if three consecutive tiles of same value, dont merge first two
                    if (row < self.size - 2 and nextTile == board[row+2][col]):
                        continue

                    #merge tiles and set new value, shift all other tiles down
                    board[row+1][col] *= 2
                    for x in range(row):
                        board[row-x][col] = board[row-x-1][col]
                    board[0][col] = 0

                    #mark tile as merged and add appropriate score
                    merged[row+1][col] = 1
                    self.score += self.scoreBonus(currentTile)
                    moved = True

        #return board to original orientation
        if rotateCount:
            board = self.rotateBoard(board, 4 - rotateCount)

        self.board = board

        #if tiles were moved, increment number of moves and add a random block
        if moved:
            self.numMoves += 1
            self.addRandBlock()


    def addRandBlock(self, val=None):
        """
        Places a random tile (either 2 or 4) on the board
        tile = 4: 10 percent chance
        tile = 2: 90 percent chance
        """
        avail = self.availableSpots()

        if avail:
            (row, column) = avail[random.randint(0, len(avail) - 1)]

            if random.randint(0,9) == 9:
                self.board[row][column] = 4
            else:
                self.board[row][column] = 2


    def availableSpots(self):
        """
        Returns a list of all empty spaces on the board
        """
        spots = []
        for row in enumerate(self.board):
            for col in enumerate(row[1]):
                if col[1] == 0:
                    spots.append((row[0], col[0]))
        return spots

    def gameOver(self):
        """
        Returns True if no move can be made
        """
        if self.availableSpots():
            return False

        board = self.board
        for row in range(self.size):
            for col in range(self.size):
                if (row < self.size - 1 and board[row][col] == board[row+1][col]) \
                or (col < self.size - 1 and board[row][col] == board[row][col+1]):
                    return False
        return True

def mcts_strategy(game, num_simulations):
    # Store the average score for each move
    average_scores = {move: 0 for move in game.moveList}

    for move in average_scores.keys():
        total_score = 0
        for _ in range(num_simulations):
            # Create a copy of the game
            game_copy = copy.deepcopy(game)
            game_copy.makeMove(move)

            # Continue making random moves until the game is over
            while not game_copy.gameOver():
                random_move = random.choice(game_copy.moveList)
                game_copy.makeMove(random_move)

            # Add the final score to the total
            total_score += game_copy.score

        # Calculate the average score for this move
        average_scores[move] = total_score / num_simulations

    # Choose the move with the highest average score
    best_move = max(average_scores, key=average_scores.get)
    return best_move

# game = Engine()
# while not game.gameOver():
#     move = mcts_strategy(game, 20)  # Perform 100 simulations for each move

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

    # If board state doesn't change, return -1 to signify invalid move
    if np.array_equal(board, board_copy):
        return -1

    return np.sum(board_copy - board)

# Function to decide the next move
def decide_move(board):
    scores = {move: score_board(board, move) for move in MOVES}
    valid_moves = {move: score for move, score in scores.items() if score > -1}

    # If no valid moves, return None or you could raise an Exception
    if not valid_moves:
        return None

    best_move = max(valid_moves, key=valid_moves.get)
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


service = Service(r'C:\Users\jonag\Downloads\chromedriver_win32')
driver = webdriver.Chrome(service=service)

driver.get("https://www.astrill.com/coupon-code")

# Wait for page to load. Increase as necessary if load times are longer.
time.sleep(5)

game = Engine()
while True:
    # Get the HTML of the page
    time.sleep(0.5)
    html = driver.page_source

    # Parse the HTML and decide on the best move
    game_container_html = get_game_container(html)
    board_state = get_board_state(game_container_html)
    game.setBoard(board_state)

    # best_move = solve_2048_game(board_state)
    best_move = mcts_strategy(game, 200)

    print (board_state)
    print (best_move)

    # Make the move
    body = driver.find_element("tag name", 'body')
    if best_move == 'up':
        body.send_keys(Keys.UP)
    elif best_move == 'down':
        body.send_keys(Keys.DOWN)
    elif best_move == 'left':
        body.send_keys(Keys.LEFT)
    elif best_move == 'right':
        body.send_keys(Keys.RIGHT)

# Close the WebDriver instance
driver.quit()

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




