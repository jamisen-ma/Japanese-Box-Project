BOARD_SIZE = 5
class Piece:
    """
    Class that represents a BoxShogi piece
    """
    def __init__(self, side, label):
        self.side = side
        self.set_label(label)

    def __repr__(self):
        return self.label

    def set_label(self, label):
        #sets the letter that's diplayed on the board
        if self.side == "UPPER":
            self.label = label
        else:
            self.label = label.lower()

    def check_in_bounds(self, original_pos):
        if 0 <= original_pos[0] < BOARD_SIZE and 0 <= original_pos[1] < BOARD_SIZE :
            return True
        return False

    def check_not_same(self, original_pos, potential_pos):
        if original_pos == potential_pos:
            return False
        return True

    def setPosition(self, x, y):
        self.position = (x, y)


class Drive(Piece):
    def __init__(self, side):
        super().__init__(side, "D")
        self.setStartPosition()

    def setStartPosition(self):
        #sets the initial position of the piece (interactive)
        self.position = (0, 0) if self.side == "lower" else (4, 4)
        return self.position

    def isValid(self, original_pos, potential_pos, board):
        #Makes sure move is valid
        return self.check_in_bounds(original_pos) and \
            abs(potential_pos[0] - original_pos[0]) <= 1 and \
            abs(potential_pos[1] - original_pos[1]) <= 1

    def can_move_to(self, original_pos, board):
        # Define all possible moves the piece can make
        possible_moves = [
            (original_pos[0] - 1, original_pos[1]),
            (original_pos[0] + 1, original_pos[1]),
            (original_pos[0], original_pos[1] - 1),
            (original_pos[0], original_pos[1] + 1),
            (original_pos[0] - 1, original_pos[1] - 1),
            (original_pos[0] - 1, original_pos[1] + 1),
            (original_pos[0] + 1, original_pos[1] - 1),
            (original_pos[0] + 1, original_pos[1] + 1)
        ]
        valid_moves = [move for move in possible_moves if self.isValid(original_pos, move, board)]
        return valid_moves
    def promote(self, original_pos):
        return False

class Shield(Piece):
    def __init__(self, side):
        super().__init__(side, "S")
        self.setStartPosition()

    def setStartPosition(self):
        self.position = (1, 0) if self.side == "lower" else (3, 4)
        return self.position

    def promote(self, original_pos):
        return False

    def isValid(self, original_pos, potential_pos, board):
        if not self.check_in_bounds(original_pos) or not self.check_not_same(original_pos, potential_pos):
            return False

        x_diff = potential_pos[0] - original_pos[0]
        y_diff = potential_pos[1] - original_pos[1]

        if abs(x_diff) > 1 or abs(y_diff) > 1:
            return False

        if self.side == "lower" and (x_diff, y_diff) in [(-1, -1), (1, -1)]:
            return False
        elif self.side != "lower" and (x_diff, y_diff) in [(-1, 1), (1, 1)]:
            return False

        return True

    def can_move_to(self, original_pos, board):
        possible_moves = [
                (original_pos[0] - 1, original_pos[1]),
                (original_pos[0] + 1, original_pos[1]),
                (original_pos[0], original_pos[1] - 1),
                (original_pos[0], original_pos[1] + 1),
                (original_pos[0] + 1, original_pos[1] + 1),
                (original_pos[0] - 1, original_pos[1] + 1),
                (original_pos[0] + 1, original_pos[1] - 1),
                (original_pos[0] - 1, original_pos[1] - 1)
            ]
        valid_moves = [move for move in possible_moves if self.isValid(original_pos, move, board)]
        return valid_moves


class Relay(Piece):
    def __init__(self, side):
        super().__init__(side, "R")
        self.setStartPosition()
    def setStartPosition(self):
        self.position = (2, 0) if self.side == "lower" else (2, 4)
        return self.position

    def __repr__(self):
        return "R"

    def isValid(self, original_pos, potential_pos, board):
        if not self.check_in_bounds(original_pos) or not self.check_not_same(original_pos, potential_pos):
            return False

        x_diff = potential_pos[0] - original_pos[0]
        y_diff = potential_pos[1] - original_pos[1]

        # Common check for move distance greater than 1
        if abs(x_diff) > 1 or abs(y_diff) > 1:
            return False

        # Check for specific invalid moves based on the piece's side
        invalid_moves_lower = [(0, -1), (-1, 0), (1, 0)]
        invalid_moves_upper = [(0, 1), (-1, 0), (1, 0)]

        if (self.side == "lower" and (x_diff, y_diff) in invalid_moves_lower) or \
                (self.side != "lower" and (x_diff, y_diff) in invalid_moves_upper):
            return False

        return True

    def can_move_to(self, original_pos, board):
        # Define all possible moves the piece can make
        possible_moves = [
            (original_pos[0], original_pos[1] + 1),  # right,
            (original_pos[0], original_pos[1] - 1),  # left
            (original_pos[0] - 1, original_pos[1] - 1),  # up-left
            (original_pos[0] - 1, original_pos[1] + 1),  # up-right
            (original_pos[0] + 1, original_pos[1] - 1),  # down-left
            (original_pos[0] + 1, original_pos[1] + 1),  # down-right
        ]
        # Filter out the invalid moves, possible moves list could've been same for every piece
        valid_moves = [move for move in possible_moves if self.isValid(original_pos, move, board)]
        return valid_moves

    def promote(self, original_pos):
        shield = Promoted_Relay(self.side)
        shield.setPosition(original_pos[0], original_pos[1])
        return shield

class Governance(Piece):
    def __init__(self, side):
        super().__init__(side, "G")
        self.setStartPosition()

    def setStartPosition(self):
        self.position = (3, 0) if self.side == "lower" else (1, 4)
        return self.position

    def __repr__(self):
        return "G"

    def promote(self, original_pos):
        promoted_governance = Promoted_Governance(self.side)
        promoted_governance.setPosition(original_pos[0], original_pos[1])
        return promoted_governance

    def isClearPath(self, original_pos, potential_pos, board):
        # iteratively steps through each square between the two positions,
        # checking if each square is empty until it either reaches the potential position or encounters an obstruction.
        x_diff = potential_pos[0] - original_pos[0]
        y_diff = potential_pos[1] - original_pos[1]
        step_x = 1 if x_diff > 0 else -1
        step_y = 1 if y_diff > 0 else -1

        x, y = original_pos
        while (x, y) != potential_pos:
            x += step_x
            y += step_y
            if (x, y) == potential_pos:  # Reached potential position
                return True
            if board[x][y] != '__':  # If there's a piece in the way
                return False
        return True

    def isValid(self, original_pos, potential_pos, board):
        x_diff = potential_pos[0] - original_pos[0]
        y_diff = potential_pos[1] - original_pos[1]
        if self.check_in_bounds(original_pos) and abs(x_diff) == abs(y_diff):
            if self.check_not_same(original_pos, potential_pos) and self.isClearPath(original_pos, potential_pos, board):
                return True
        return False

    def can_move_to(self, original_pos, board):
        valid_moves = []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            x, y = original_pos
            while True:
                x += d[0]
                y += d[1]
                if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                    break
                if board[x][y] == '__':
                    valid_moves.append((x, y))
                else:
                    if self.side == "lower" and board[x][y].isupper():
                        valid_moves.append((x, y))
                    elif self.side == "UPPER" and board[x][y].islower():
                        valid_moves.append((x, y))
                    break  # Piece is in the way

        return valid_moves


class Notes(Piece):
    def __init__(self, side):
        super().__init__(side, "N")
        self.setStartPosition()
    def setStartPosition(self):
        self.position = (4, 0) if self.side == "lower" else (0, 4)
        return self.position

    def isValid(self, original_pos, potential_pos, board):
        if self.check_in_bounds(original_pos) and self.check_not_same(original_pos, potential_pos):
            x_diff = potential_pos[0] - original_pos[0]
            y_diff = potential_pos[1] - original_pos[1]
            if x_diff == 0 or y_diff == 0:
                return True
        return False

    def promote(self, original_pos):
        promoted_notes = Promoted_Notes(self.side)
        promoted_notes.setPosition(original_pos[0], original_pos[1])
        return promoted_notes

    def can_move_to(self, original_pos, board):
        valid_moves = []

        directions = [(-1, 0), (1,0), (0,1), (0,-1)]  # Straight directions
        for d in directions:
            x, y = original_pos
            while True:
                x += d[0]
                y += d[1]
                if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                    break  # Out of bounds
                if board[x][y] == '__':  # Empty square
                    valid_moves.append((x, y))
                else:
                    if self.side == "lower" and board[x][y].isupper():
                        valid_moves.append((x, y))
                    elif self.side == "UPPER" and board[x][y].islower():
                        valid_moves.append((x, y))
                    break  # Piece is in the way

        return valid_moves


class Preview(Piece):
    def __init__(self, side):
        super().__init__(side, "P")
        self.setStartPosition()
    def setStartPosition(self):
        self.position = (0, 1) if self.side == "lower" else (4, 3)
        return self.position

    def isValid(self, original_pos, potential_pos, board):
        if not self.check_in_bounds(original_pos) or not self.check_not_same(original_pos, potential_pos):
            return False

        y_diff = potential_pos[1] - original_pos[1]
        return (self.side == "lower" and y_diff == 1) or (self.side != "lower" and y_diff == -1)

    def promote(self, original_pos):
        shield = Promoted_Preview(self.side)
        shield.setPosition(original_pos[0], original_pos[1])
        return shield

    def can_move_to(self, original_pos, board):
        return [(original_pos[0], original_pos[1] + 1)]

class Promoted_Governance(Piece):
    def __init__(self, side):
        super().__init__(side, "+G")
        self.dummy_governance = Governance(side)
        self.dummy_drive = Drive(side)

    def isValid(self, original_pos, potential_pos, board):
        return Governance.isValid(self.dummy_governance, self.position, potential_pos, board) or Drive.isValid(self.dummy_drive, self.position, potential_pos, board)

    def can_move_to(self, original_pos, board):
        governance_moves = set(Governance.can_move_to(self.dummy_governance, self.position, board))
        drive_moves = set(Drive.can_move_to(self.dummy_drive, self.position, board))
        combined_moves = governance_moves.union(drive_moves)
        return list(combined_moves)



class Promoted_Notes(Piece):
    def __init__(self, side):
        super().__init__(side, "+N")
        self.dummy_notes = Notes(side)
        self.dummy_drive = Drive(side)

    def isValid(self, original_pos, potential_pos, board):
        return self.dummy_notes.isValid(original_pos, potential_pos, board) or self.dummy_drive.isValid(original_pos, potential_pos, board)

    def can_move_to(self, original_pos, board):
        notes_moves = set(self.dummy_notes.can_move_to(self.position, board))
        drive_moves = set(self.dummy_drive.can_move_to(self.position, board))
        combined_moves = notes_moves.union(drive_moves)
        return list(combined_moves)


class Promoted_Relay(Shield):
    def __init__(self, side):
        super().__init__(side)
        self.set_label("+R")

    def isValid(self, original_pos, potential_pos, board):
        return super().isValid(self.position, potential_pos, board)

    def can_move_to(self, original_pos, board):
        return super().can_move_to(self.position, board)


class Promoted_Preview(Shield):
    def __init__(self, side):
        super().__init__(side)
        self.set_label("+P")

    def isValid(self, original_pos, potential_pos, board):
        return super().isValid(self.position, potential_pos, board)

    def can_move_to(self, original_pos, board):
        return super().can_move_to(self.position, board)
