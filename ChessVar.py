#Author: Christopher Lopez
#GitHub username: Lopezc2
#Date: 12/8/2024
#Description: Chess board game that plays in fog of war style
#             No check, checkmate, castling, en passant, and/or pawn promotion

class ChessVar:

    def __init__(self):
        """Initializes the game"""
        self._player_1 = "WHITE"
        self._player_2 = "BLACK"
        self._board = [ #initializes board
             ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], #A8-H8
             ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], #A7-H7
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], #A6-H6
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], #A5-H5
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], #A4-H4
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], #A3-H3
             ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], #A2-H2
             ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']  #A1-H1
        ]
        self._turn = self._player_1 #Initiates white as starting turn
        self._game_state = "UNFINISHED"

    def make_move(self, start_pos, end_pos):
        """
        Moves pieces and checks if kings are still in play
        Rules: Cannot go on a space with an ally piece
               Cannot go on/pass an enemy piece exception of knights and capturing
               Invalid movement notifies and recalls action
        """
        if self._game_state != "UNFINISHED":
            return False #If game is not unfinished, continue making moves

        start_row, start_column = self._board_positions(start_pos) #Converts notation
        end_row, end_column = self._board_positions(end_pos)

        piece = self._board[start_row][start_column] #The piece being moved
        target = self._board[end_row][end_column] #The target of the piece

        if self._turn == self._player_1 and piece.islower(): #White can't move black pieces
            return False
        if self._turn == self._player_2 and piece.isupper(): #Black can't move white pieces
            return False

        move_piece = { #Movement for pieces
            'p': self._move_pawn,
            'r': self._move_rook,
            'n': self._move_knight,
            'b': self._move_bishop,
            'q': self._move_queen,
            'k': self._move_king
            }

        if piece.lower() not in move_piece:
            return False #Invalid piece type

        if not move_piece[piece.lower()](start_row, start_column, end_row, end_column, piece):
            return False #Invalid move for piece

        #Attacking pieces
        if target == ' ' or (piece.isupper() and target.islower()) or (piece.islower() and target.isupper()):
            self._board[end_row][end_column] = piece #Move the piece to target
            self._board[start_row][start_column] = ' ' #piece's start position becomes empty
        else:
            return False #Cannot move to a square containing an ally

        #Check if kings are alive after move is made
        white_king_alive = False
        black_king_alive = False

        for row in self._board:
            if 'k' in row: #Check if black king exists
                black_king_alive = True
            if 'K' in row: #Check if white king exists
                white_king_alive = True

        if not white_king_alive: #If white king is false
            self._game_state = "BLACK_WON"
        if not black_king_alive: #If black king is false
            self._game_state = "WHITE_WON"
        else:
            if self._turn == self._player_1: #Switches from White's turn to black
                self._turn = self._player_2
            else:
                self._turn = self._player_1 #If it's black's turn switches to white
        return True

    def _board_positions(self, pos):
        """Marks each position with notations"""
        column, row = pos[0], pos[1] #Split positions between column and rows
        column_pos = {'a':0, 'b':1, 'c':2, 'd':3,'e':4, 'f':5, 'g':6, 'h':7}
        column_index = column_pos[column] #Convert column letters
        row_index = 8 - int(row) #convert row index in reverse
        return row_index, column_index

    def _move_pawn(self, start_row, start_column, end_row, end_column, piece):
        """
        Pawn (p): Vertically - Two possible at start, one anytime, takes pieces one space diagonally
        """
        if piece.isupper(): #Direction based on color
            movement = -1 #White
        else:
            movement = 1 #Black

        #Forward
        if start_column == end_column and self._board[end_row][end_column] == ' ':
            #One space
            if start_row + movement == end_row:
                return True

            #Two spaces at start
            starting_row = 6 if piece.isupper() else 1
            if start_row == starting_row and start_row + (2 * movement) == end_row:
                return self._board[start_row + movement][start_column] == ' '
            return True

        #Diagonal
        if (start_column - end_column == 1 or end_column - start_column == 1) and start_row + movement == end_row:
            #Can only capture if opponent piece is there
            if self._board[end_row][end_column] != ' ' and self._board[end_row][end_column].islower() != piece.islower():
                return True
        return False #If move is invalid

    def _move_rook(self, start_row, start_column, end_row, end_column, piece):
        """
        Rook (r): Vertical and horizontal
        """
        #Moves Horizontal or vertical
        if start_row == end_row or start_column == end_column:
            #Movement direction (positive = forward/right, negative = down/left)
            movement = (1 if end_row > start_row else -1) if start_row != end_row else (1 if end_column > start_column else -1)

            #steps for loop
            step_row = start_row + (movement if start_row != end_row else 0)
            step_column = start_column + (movement if start_column != end_column else 0)

            #Loop through each square along path
            while step_row != end_row or step_column != end_column:
                #If piece is in the way, move is invalid
                if self._board[step_row][step_column] != ' ':
                    return False

                #Updates steps depending on movement
                step_row += (movement if start_row != end_row else 0)
                step_column += (movement if start_column != end_column else 0)

            #If no problems, valid move
            return True
        #If not horizontal or vertical, invalid
        return False

    def _move_knight(self, start_row, start_column, end_row, end_column, piece):
        """
        Knight (n): Two spaces horizontal/vertical one space to the side
        """
        #row and column difference
        row_diff = start_row - end_row
        column_diff = start_column - end_column

        #Moves in L shape, 2 squares and 1 over
        if ((row_diff == 2 or row_diff == -2) and (column_diff == 1 or column_diff == -1)) or\
            ((row_diff == 1 or row_diff == 1) and (column_diff == 2 or column_diff == -2)):
            return True

    def _move_bishop(self, start_row, start_column, end_row, end_column, piece):
        """
        Bishop (b): Diagonally
        """
        if (start_row - end_row == start_column - end_column) or (start_row - end_row == end_column - start_column):
            #Determine movement direction for rows and columns
            movement_row = 1 if end_row > start_row else -1
            movement_column = 1 if end_column > start_column else -1

            #steps for loop
            step_row = start_row + movement_row
            step_column = start_column + movement_column

            #Loop through each square
            while step_row != end_row and step_column != end_column:
                #If piece is in the way, move is invalid
                if self._board[step_row][step_column] != ' ':
                    return False
                #updates steps
                step_row += movement_row
                step_column += movement_column
                return True
        #If move is not diagonal, it's invalid
        return False

    def _move_queen(self, start_row, start_column, end_row, end_column, piece):
        """
        Queen (q): Moves in same directions as rook and bishop
        """
        #Uses the rook and bishop movement functions for itself
        if self._move_rook(start_row, start_column, end_row, end_column, piece) or\
            self._move_bishop(start_row, start_column, end_row, end_column, piece):
            return True

    def _move_king(self, start_row, start_column, end_row, end_column, piece):
        """
            King (k): One space in any direct
        """
        #Moves one square in any direction
        row_diff = start_row - end_row
        column_diff = start_column - end_column
        #valid move if the movement is 1 or -2
        if ((row_diff == 1 or row_diff == -1 or row_diff == 0) and
                (column_diff == 1 or column_diff == -1 or column_diff == 0)):
            return True

    def get_game_state(self):
        """Checks if game is in progress or if there is a winner"""
        return self._game_state

    def get_board(self, perspective):
        """
        Retrieves the board and flips depending on player color
        when retrieving board, opposite side pieces return as * (fog of war)
        """
        fog = [['*' for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for column in range(8):
                piece = self._board[row][column]
                if perspective == "white":
                    if piece.islower(): #Hides lower case letters (black pieces)
                        fog[row][column] = '*'
                    else:
                        fog[row][column] = piece
                elif perspective == "black":
                    if piece.isupper(): #Hides uppercase letters (White pieces)
                        fog[row][column] = '*'
                    else:
                        fog[row][column] = piece
                if perspective == "audience":
                    fog[row][column] = piece
        for row in fog:
            print(' '.join(map(str,row)))
        return fog

def main():

    game = ChessVar()
    game.make_move('a2','a4')
    game.make_move('c7','c5')
    game.make_move('b1','a3')
    game.make_move('d8','a5')
    game.make_move('e2','e3')
    game.make_move('a5','d2')
    game.make_move('c2','c4')
    game.make_move('b8', 'c6')
    game.make_move('f1', 'd3')
    game.make_move('a7','a5')
    game.make_move('a1','b1')
    game.make_move('d2', 'e1')
    print(game.get_game_state())
    game.get_board("audience")

if __name__ == "__main__":
    main()


