import sys
from utils import parseTestCase
from board import *
def main():
    """
    Main function to read terminal input
    """
    if sys.argv[1] == '-f':
        dict1 = parseTestCase(sys.argv[2])
        board = Board()
        board.initGame()
        board.file_mode_init(dict1)


    if sys.argv[1] == '-i':
        board = Board()
        board.create_pieces()
        while not board.gameOver:
            board.make_turn()

if __name__ == "__main__":
    main()