import copy
import os
from piece import *
import sys

class Board:
    """
    Class that represents the BoxShogi board
    """

    # The BoxShogi board is 5x5
    BOARD_SIZE = 5

    def __init__(self):
        self._board = self._initEmptyBoard()
        self.initGame()

    def create_pieces(self):
        #Initializes each piece (interactive)
        piece_types = [Drive, Shield, Relay, Governance, Notes, Preview]
        sides = ["lower", "UPPER"]

        for side in sides:
            for piece_type in piece_types:
                piece = piece_type(side)
                self.add_to_board(piece)

    def add_to_board(self, piece):
        self._board[piece.position[0]][piece.position[1]] = piece.label
        self.backend_board[piece.position[0]][piece.position[1]] = piece
        if piece.side == "lower":
            self.lower_pieces.append(piece)
        else:
            self.upper_pieces.append(piece)

    def remove_from_board(self, piece):
        self._board[piece.position[0]][piece.position[1]] = "__"
        self.backend_board[piece.position[0]][piece.position[1]] = "__"
        if piece.side == "lower":
            self.lower_pieces.remove(piece)
        else:
            self.upper_pieces.remove(piece);

    def _initEmptyBoard(self):
        #Makes board array
        board = [["__" for _ in range(5)] for _ in range(5)]
        self.backend_board = [["__" for _ in range(5)] for _ in range(5)]

        return board
    def initGame(self):
        self.upper_captures = []
        self.lower_captures = []
        self.upper_pieces = []
        self.lower_pieces = []
        self.gameOver = False
        self.curTurn = "lower"
        self.moveCounter = 0
        #Hashmap that reference each label to its class
        self.piece_map = {
            'd': lambda: Drive("lower"),
            'D': lambda: Drive("UPPER"),
            's': lambda: Shield("lower"),
            'S': lambda: Shield("UPPER"),
            'r': lambda: Relay("lower"),
            'R': lambda: Relay("UPPER"),
            'g': lambda: Governance("lower"),
            'G': lambda: Governance("UPPER"),
            'n': lambda: Notes("lower"),
            'N': lambda: Notes("UPPER"),
            'p': lambda: Preview("lower"),
            'P': lambda: Preview("UPPER"),
            '+G': lambda: Promoted_Governance("UPPER"),
            '+R': lambda: Promoted_Relay("UPPER"),
            '+P': lambda: Promoted_Preview("UPPER"),
            '+N': lambda: Promoted_Notes("UPPER"),
            '+g': lambda: Promoted_Governance("lower"),
            '+r': lambda: Promoted_Relay("lower"),
            '+p': lambda: Promoted_Preview("lower"),
            '+n': lambda: Promoted_Notes("lower")
        }


    def switchTurns(self):
        if self.curTurn == "lower":
            self.curTurn = "UPPER"
        else:
            self.curTurn = "lower"

    def tie_game(self):
        self.printState()
        print("\nTie game.  Too many moves.")
        sys.exit()

    def filter_instruction(self, instruction):
        #determine what instruction it is and call appropriate function
        if len(instruction) == 4 and instruction[0] == "move" and instruction[3] == "promote":
            self.make_move(instruction[1], instruction[2], True)
        elif len(instruction) == 3 and instruction[0] == "move":
            self.make_move(instruction[1], instruction[2], False)
        elif len(instruction) == 3 and instruction[0] == "drop":
            self.make_drop(instruction[1], instruction[2])
        self.switchTurns()

    def make_turn(self):
        #interactive only
        self.printState()
        check, checkmate, final_move_list, king_pos = self.is_check(False)
        if checkmate:
            print(self.curTurn + " player is in checkmate!")
            if self.curTurn == "LOWER":
                print("UPPER player wins.")
            else:
                print("LOWER player wins.")
            sys.exit()
        elif check:
            print(self.curTurn + " player is in check!")
            print("Available moves: ")
            for move in final_move_list:
                print(move)

        print("")
        print(self.curTurn + ">", end = " ")
        userInput = input()
        instruction = userInput.split(" ")
        self.filter_instruction(instruction)


    def setup_initial_pieces(self, initial_pieces):
        for piece_info in initial_pieces:
            position = self.convert_coordinates(piece_info['position'])
            piece_type = piece_info['piece']
            piece = self.piece_map[piece_type]()
            piece.setPosition(*position)
            self.add_to_board(piece)

    def setup_captured_pieces(self, upper_captures, lower_captures):
        self.upper_captures = upper_captures
        self.lower_captures = lower_captures

    def process_moves(self, moves):
        #process moves in file mode and check if it's checkmate after finish reading file
        for i in range(0, len(moves)):
            if i == len(moves) - 1:
                print(self.curTurn + " player action: " + moves[i])
            instruction = moves[i].split(" ")
            self.filter_instruction(instruction)

        check, checkmate, final_move_list, king_pos = self.is_check(False)
        #checks for tie game
        if i == 399:
            if checkmate:
                self.printState()
                winner = "UPPER" if self.curTurn == "lower" else "lower"
                print(f"\n{winner} player wins.  Checkmate.")
                sys.exit()
            else:
                self.tie_game()
        self.printState()

        if checkmate:
            winner = "UPPER" if self.curTurn == "lower" else "lower"
            print(f"{winner} player wins.  Checkmate.")
            sys.exit()

        if check:
            print(f"\n{self.curTurn} player is in check!")
            print("Available moves: ")
            self.print_can_move_list(final_move_list)

        print(f"\n{self.curTurn}> ", end="")
        sys.exit()

    def file_mode_init(self, hashmap):
        self.setup_initial_pieces(hashmap['initialPieces'])
        self.setup_captured_pieces(hashmap['upperCaptures'], hashmap['lowerCaptures'])
        moves = hashmap['moves']
        self.process_moves(moves)



    def illegal_move(self):
        self.printState()
        print("")
        winner = "lower" if self.curTurn == "UPPER" else "UPPER"
        print(f"\n{winner} player wins.  Illegal move.")
        sys.exit()


    def convert_coordinates(self, coord):
        file_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}

        rank = int(coord[1]) - 1
        file = coord[0]

        file_index = file_to_index[file]

        return (file_index, rank)

    def convert_coordinates_to_string(self, coord):
        index_to_file = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}
        return index_to_file[coord[0]] + str(coord[1] + 1)

    def try_move_king(self, king):
        # Check if the king can move to any of the valid positions called after king is in check
        # can use recursive backtracking to make it more efficient and save space
        valid_moves = []
        king_position = king.position

        for move in king.can_move_to(king_position, self._board):
            if king.check_in_bounds(move):
                # Simulate the move on a temporary board
                temp_board = copy.deepcopy(self._board)
                temp_board[king_position[0]][king_position[1]] = "__"
                temp_board[move[0]][move[1]] = king.label

                # Check if the king would be in check in the new position
                if not self.is_king_in_check_at_position(move, temp_board):
                    valid_moves.append(move)

        return valid_moves

    def capture_piece(self, curPiece, potential_pos):
        self.remove_from_board(curPiece)
        curPiece.setPosition(potential_pos[0], potential_pos[1])
        if self.backend_board[potential_pos[0]][potential_pos[1]] != "__":
            captured_piece = self.backend_board[potential_pos[0]][potential_pos[1]]
            if captured_piece.side == "UPPER":
                self.lower_captures.append(captured_piece.label[-1].lower())
            else:
                self.upper_captures.append(captured_piece.label[-1].upper())
        self.add_to_board(curPiece)

    def make_move(self, original_pos, potential_pos, bool_promote):
        self.moveCounter += 1
        #convert coordinates from string format to coordinate format (ex. A5 -> (0, 4))
        original_pos = self.convert_coordinates(original_pos)
        potential_pos = self.convert_coordinates(potential_pos)
        curPiece = self.backend_board[original_pos[0]][original_pos[1]]

        #Check that piece can't take own piece
        target_piece = self.backend_board[potential_pos[0]][potential_pos[1]]
        if target_piece != "__" and target_piece.side == curPiece.side:
            self.illegal_move()
            return

        #check that promoted piece can't be promoted again
        if curPiece.label[0] == "+" and bool_promote:
            self.illegal_move()

        #check if move is valid
        if self.curTurn == "upper":
            behind_piece = self.backend_board[original_pos[0]][original_pos[1]-1]
        else:
            behind_piece = self.backend_board[original_pos[0]+1][original_pos[1]+1]


        if type(curPiece) != str and curPiece.isValid(curPiece.position, potential_pos, self._board) and (behind_piece != "__" and behind_piece.isValid()):
            #not nessacarily capture everytime maybe should've named it better
            self.capture_piece(curPiece, potential_pos)

            # Automatically promote Preview piece if it reaches the furthest row
            if isinstance(curPiece, Preview) and ((curPiece.side == "lower" and potential_pos[1] == 4) or (
                    curPiece.side == "UPPER" and potential_pos[1] == 0)):
                bool_promote = True

            #promote piece if it's in the promotion zone
            if bool_promote:
                a = self.make_promotion(curPiece)
                if not a:
                    self._board[potential_pos[0]][potential_pos[1]] = "__"
                    self._board[original_pos[0]][original_pos[1]] = curPiece.label
                    self.illegal_move()

        else:
            self.illegal_move()

    def make_drop(self, label, potential_pos):
        self.moveCounter += 1
        potential_pos = self.convert_coordinates(potential_pos)

        if label.lower() == 'p':
            pawn_label = 'p' if self.curTurn == "lower" else 'P'
            # Iterate through the column at the potential position's row
            for piece in self.backend_board[potential_pos[0]]:
                # Check for an unpromoted pawn in the same column
                if piece != "__" and piece.label == pawn_label:
                    self.illegal_move()
                    return

        promotion_zone_row = 4 if self.curTurn == "lower" else 0

        # Check if the drop is in the promotion zone for Preview pieces
        if label.lower() == 'p' and potential_pos[1] == promotion_zone_row:
            self.illegal_move()
            return

        label = label.lower() if self.curTurn == "lower" else label.upper()
        curPiece = self.piece_map[label]()
        captures_list = self.lower_captures if self.curTurn == "lower" else self.upper_captures

        # Check if the piece can be placed on the board
        if label in captures_list and self.backend_board[potential_pos[0]][potential_pos[1]] == "__":
            # Temporarily add the piece to check for checkmate conditions
            self.backend_board[potential_pos[0]][potential_pos[1]] = curPiece
            curPiece.setPosition(potential_pos[0], potential_pos[1])

            # Check for immediate checkmate by a pawn placement
            if curPiece.label.upper() == "P" and self.is_check(False)[1]:
                self.backend_board[potential_pos[0]][potential_pos[1]] = "__"
                self.illegal_move()
                return

            captures_list.remove(label)
            self.add_to_board(curPiece)
        else:
            self.illegal_move()

    def make_promotion(self, curPiece):
        newPiece = curPiece.promote(curPiece.position)
        if not newPiece:
            return False
        self.remove_from_board(curPiece)
        self.add_to_board(newPiece)
        return True

    def find_king(self, piece_list):
        for piece in piece_list:
            if piece.label.upper() == "D":
                return piece, piece.position


    def is_check_helper(self, king_position, piece_list):
        for piece in piece_list:
            if king_position in piece.can_move_to(piece.position, self._board):
                return True
        return False

    def is_check(self, switch):
        #tells us if user is in check or checkmate
        piece_list, other_list = (self.upper_pieces, self.lower_pieces) if self.curTurn == "lower" else (
        self.lower_pieces, self.upper_pieces)
        if switch:
            piece_list, other_list = other_list, piece_list

        king, king_position = self.find_king(other_list)
        can_move_list = []
        check = False
        checkmate = True
        threatening_pieces = []

        # Find all pieces that put the king in check
        for piece in piece_list:
            if king_position in piece.can_move_to(piece.position, self._board):
                check = True
                threatening_pieces.append(piece)

        # Try to move the king out of check
        for move in king.can_move_to(king_position, self._board):
            if king.check_in_bounds(move) and not self.is_check_helper(move, piece_list):
                piece = self.backend_board[move[0]][move[1]]
                if piece == "__" or piece.side != king.side:
                    can_move_list.append(move)

        # Check if any piece can block the attack or capture the threatening piece
        for piece in other_list:
            if piece.label != "D":  # Exclude the king itself
                for move in piece.can_move_to(piece.position, self._board):
                    for threat in threatening_pieces:
                        if move in threat.can_move_to(piece.position, self._board) or move == threat.position:
                            # checkmate = False
                            break

        king_pos = self.convert_coordinates_to_string(king_position)
        final_move_list = []
        new_board = copy.deepcopy(self._board)
        new_board[king_position[0]][king_position[1]] = "__"
        marker = "d" if self.curTurn == "lower" else "D"

        for move in can_move_list:
            new_board[move[0]][move[1]] = marker
            if not self.is_king_in_check_at_position(move, new_board):
                move_pos = self.convert_coordinates_to_string(move)
                final_move_list.append(f"move {king_pos} {move_pos}")

        final_move_list.sort()
        checkmate = not final_move_list

        return check, checkmate, final_move_list, king_position

    def print_can_move_list(self, list1):
        if list1:
            for move in list1:
                print(move)

    def is_king_in_check_at_position(self, king_position, board):
        if self.curTurn == "lower":
            opponent_pieces = self.upper_pieces
        else:
            opponent_pieces = self.lower_pieces

        # Check if any opponent piece can move to the king's position
        for piece in opponent_pieces:
            if king_position in piece.can_move_to(piece.position, board):
                return True  # The king is in check

        # No opponent piece can move to the king's position
        return False
    def printState(self):
        print(self)
        print("Captures UPPER: " + " ".join(self.upper_captures))
        print("Captures lower: " + " ".join(self.lower_captures))


    def __repr__(self):
        return self._stringifyBoard()

    def _stringifyBoard(self):
        """
        Utility function for printing the board
        """
        s = ''
        for row in range(len(self._board) - 1, -1, -1):
            s += '' + str(row + 1) + ' |'
            for col in range(0, len(self._board[row])):
                s += self._stringifySquare(self._board[col][row])
            s += os.linesep
        s += '    a  b  c  d  e' + os.linesep
        return s

    def _stringifySquare(self, sq):
        """
       	Utility function for stringifying an individual square on the board

        :param sq: Array of strings.
        """
        if type(sq) is not str or len(sq) > 2:
            raise ValueError('Board must be an array of strings like "", "P", or "+P"')
        if len(sq) == 0:
            return '__|'
        if len(sq) == 1:
            return ' ' + sq + '|'
        if len(sq) == 2:
            return sq + '|'
