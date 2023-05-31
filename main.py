import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
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
        self.moveList = ['down', 'left', 'up', 'right']
        self.addRandBlock()
        self.addRandBlock()

    def setBoard(self, boardString):
        boardList = list(map(int, boardString.split(' ')))
        if len(boardList) != 16:
            raise ValueError("Invalid board string. It must contain 16 space-separated integers.")
        self.board = [boardList[i:i + self.size] for i in range(0, len(boardList), self.size)]
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
        # Initialize rotated as a copy of the original board
        rotated = [row[:] for row in board]
        for c in range(count):
            # Now rotated gets overwritten here if count > 0
            rotated = [[0 for i in range(self.size)] for i in range(self.size)]
            for row in range(self.size):
                for col in range(self.size):
                    rotated[self.size - col - 1][row] = board[row][col]
            board = rotated

        return rotated

    def makeMove(self, moveDir):
        # Check if the game is already over
        if self.gameOver():
            return False

        board = self.board

        # Set how many rotations based on the move
        rotateCount = self.moveList.index(moveDir)
        moved = False

        # Rotate board to orient the board downwards
        if rotateCount:
            board = self.rotateBoard(board, rotateCount)

        # make an array to track merged tiles
        merged = [[0 for i in range(self.size)] for i in range(self.size)]

        for row in range(self.size - 1):
            for col in range(self.size):

                currentTile = board[row][col]
                nextTile = board[row + 1][col]

                # go to next tile if current tile is empty
                if not currentTile:
                    continue

                # if next position is empty, move all tiles down
                if not nextTile:
                    for x in range(row + 1):
                        board[row - x + 1][col] = board[row - x][col]
                    board[0][col] = 0
                    moved = True
                    continue
                # if tile was merged already, go to next tile
                if merged[row][col]:
                    continue

                if currentTile == nextTile:
                    # if three consecutive tiles of same value, dont merge first two
                    if (row < self.size - 2 and nextTile == board[row + 2][col]):
                        continue

                    # merge tiles and set new value, shift all other tiles down
                    board[row + 1][col] *= 2
                    for x in range(row):
                        board[row - x][col] = board[row - x - 1][col]
                    board[0][col] = 0

                    # mark tile as merged and add appropriate score
                    merged[row + 1][col] = 1
                    self.score += self.scoreBonus(currentTile)
                    moved = True

        # return board to original orientation
        if rotateCount:
            board = self.rotateBoard(board, 4 - rotateCount)

        self.board = board

        # if tiles were moved, increment number of moves and add a random block
        if moved:
            self.numMoves += 1
            self.addRandBlock()
            return True
        else:
            return False

    def addRandBlock(self, val=None):
        """
        Places a random tile (either 2 or 4) on the board
        tile = 4: 10 percent chance
        tile = 2: 90 percent chance
        """
        avail = self.availableSpots()

        if avail:
            (row, column) = avail[random.randint(0, len(avail) - 1)]

            if random.randint(0, 9) == 9:
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

        for move in self.moveList:
            board = self.rotateBoard(copy.deepcopy(self.board), self.moveList.index(move))

            for row in range(self.size - 1):
                for col in range(self.size):

                    currentTile = board[row][col]
                    nextTile = board[row + 1][col]

                    # go to next tile if current tile is empty
                    if not currentTile:
                        continue

                    # if next position is empty, we can move
                    if not nextTile:
                        return False

                    if currentTile == nextTile:
                        # if three consecutive tiles of same value, dont merge first two
                        if (row < self.size - 2 and nextTile == board[row + 2][col]):
                            continue

                        # if current and next tile are same, we can merge, so return false
                        return False

        return True


def mcts_strategy(game, num_simulations):
    # Store the average score for each move
    average_scores = {move: 0 for move in game.moveList}

    for move in average_scores.keys():
        total_score = 0
        num_valid_simulations = 0
        for _ in range(num_simulations):
            # Create a copy of the game
            game_copy = copy.deepcopy(game)

            # Save the original board for comparison
            original_board = copy.deepcopy(game_copy.board)
            game_copy.makeMove(move)

            # Check if the move was valid (the board changed)
            if original_board == game_copy.board:
                continue

            num_valid_simulations += 1

            # Continue making random moves until the game is over
            num_moves = 0
            while not game_copy.gameOver():
                # Use simple heuristics to guide random move selection
                top_row = game_copy.board[0]
                bottom_row = game_copy.board[-1]
                left_col = [row[0] for row in game_copy.board]
                right_col = [row[-1] for row in game_copy.board]

                if all(top_val >= bottom_val for top_val, bottom_val in zip(top_row, bottom_row)) and all(
                        left_val >= right_val for left_val, right_val in zip(left_col, right_col)):
                    random_move = random.choice(['up', 'left'])
                elif all(top_val >= bottom_val for top_val, bottom_val in zip(top_row, bottom_row)) and all(
                        right_val >= left_val for right_val, left_val in zip(right_col, left_col)):
                    random_move = random.choice(['up', 'right'])
                elif all(bottom_val >= top_val for bottom_val, top_val in zip(bottom_row, top_row)) and all(
                        left_val >= right_val for left_val, right_val in zip(left_col, right_col)):
                    random_move = random.choice(['down', 'left'])
                elif all(bottom_val >= top_val for bottom_val, top_val in zip(bottom_row, top_row)) and all(
                        right_val >= left_val for right_val, left_val in zip(right_col, left_col)):
                    random_move = random.choice(['down', 'right'])
                else:
                    random_move = random.choice(game_copy.moveList)

                valid_move = game_copy.makeMove(random_move)
                if not valid_move:
                    break

            # Add the final score to the total
            total_score += game_copy.score

        # Calculate the average score for this move
        average_scores[move] = total_score / num_valid_simulations if num_valid_simulations > 0 else 0

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


# Prompt the user to choose the URL or enter a custom one.
url_choice = input("""Please enter:
1) For 'https://www.astrill.com/coupon-code'
2) For 'https://www.getastr.com/coupon-code'
3) To enter a custom URL: 
""")

# Validate the user's input and save the chosen URL.
if url_choice == '1':
    chosen_url = "https://www.astrill.com/coupon-code"
elif url_choice == '2':
    chosen_url = "https://www.getastr.com/coupon-code"
elif url_choice == '3':
    chosen_url = input("Please enter your custom URL: ")
else:
    print("Invalid choice! Please enter either '1', '2', or '3'.")
    exit()

# Prompt the user to choose the WebDriver.
driver_choice = input("""Please choose the WebDriver to use (make sure the browser is installed):
1) For 'Chrome'
2) For 'Firefox'
3) For 'Edge'
4) For 'Safari'
""")

# Validate the user's input and create a WebDriver instance accordingly.
if driver_choice == '1':
    driver = webdriver.Chrome()
elif driver_choice == '2':
    driver = webdriver.Firefox()
elif driver_choice == '3':
    driver = webdriver.Edge()
elif driver_choice == '4':
    driver = webdriver.Safari()
else:
    print("Invalid choice! Please enter a number between '1' and '4'.")
    exit()

# Navigate to the chosen URL.
driver.get(chosen_url)

# Wait for page to load. Increase as necessary if load times are longer.
time.sleep(1)

game = Engine()
while True:
    # Get the HTML of the page
    time.sleep(0.1)
    html = driver.page_source

    game_over_elements = driver.find_elements("css selector", "div.game-message.game-over")

    if game_over_elements:
        # game is over, restart it
        restart_button = driver.find_element("css selector", "a.restart-button")
        restart_button.click()
        time.sleep(1)

    # Parse the HTML and decide on the best move
    game_container_html = get_game_container(html)
    board_state = get_board_state(game_container_html)
    game.setBoard(board_state)

    # best_move = solve_2048_game(board_state)
    best_move = mcts_strategy(game, 130)

    print(board_state)
    print(best_move)

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
