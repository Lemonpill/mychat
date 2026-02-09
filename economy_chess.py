from enum import IntEnum
import string


BRD_SIZE = 8
DIR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]


class PieceType(IntEnum):
    BLANK = 0
    KING = 1
    QUEEN = 2
    ROOK = 3
    BISHOP = 4
    KNIGHT = 5
    PAWN = 6


class Color(IntEnum):
    WHITE = 1
    BLACK = -1


"""
◼◻
♔♕♖♗♘♙
♚♛♜♝♞♟
"""
SQUARE_UI = {1: "◻", -1: "◼"}
PIECE_UI = {
    -(PieceType.KING): "♔",
    PieceType.KING: "♚",
    -(PieceType.QUEEN): "♕",
    PieceType.QUEEN: "♛",
    -(PieceType.ROOK): "♖",
    PieceType.ROOK: "♜",
    -(PieceType.BISHOP): "♗",
    PieceType.BISHOP: "♝",
    -(PieceType.KNIGHT): "♘",
    PieceType.KNIGHT: "♞",
    -(PieceType.PAWN): "♙",
    PieceType.PAWN: "♟",
}


class GameMove:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, value):
        if self.row != value.row or self.col != value.col:
            return False
        return True

    def __repr__(self):
        return f"{self.row}-{self.col}"


class GameEngine:
    def __init__(self):
        self.board = [[PieceType.BLANK for _ in range(BRD_SIZE)] for _ in range(BRD_SIZE)]
        self.color = Color.WHITE
        self._setup_board()

    def _setup_board(self):
        self.board[7] = [-1 * p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]
        self.board[6] = [-1 * PieceType.PAWN for _ in range(BRD_SIZE)]
        # self.board[1] = [PieceType.PAWN for _ in range(BRD_SIZE)]
        self.board[0] = [p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]

    def _valid_king_moves(self, row: int, col: int):
        moves: list[GameMove] = []
        for r_off, c_off in DIR_OFFSETS:
            nxt_r = row + r_off
            nxt_c = col + c_off
            if nxt_r not in range(BRD_SIZE) or nxt_c not in range(BRD_SIZE):
                continue
            if self.board[nxt_r][nxt_c] > 0 and self.color < 0 or self.board[nxt_r][nxt_c] < 0 and self.color > 0:
                continue
            m = GameMove(row=nxt_r, col=nxt_c)
            moves.append(m)
        return moves

    def _valid_queen_moves(self, row: int, col: int):
        moves = []
        cur_p = self.board[row][col]
        for r_off, c_off in DIR_OFFSETS:
            nxt_r = row + r_off
            nxt_c = col + c_off
            while nxt_r in range(BRD_SIZE) and nxt_c in range(BRD_SIZE):
                nxt_p = self.board[nxt_r][nxt_c]
                if nxt_p > 0 and cur_p < 0 or nxt_p < 0 and cur_p > 0:
                    m = GameMove(row=nxt_r, col=nxt_c)
                    moves.append(m)
                    break
                elif nxt_p > 0 and cur_p > 0 or nxt_p < 0 and cur_p < 0:
                    break
                m = GameMove(row=nxt_r, col=nxt_c)
                moves.append(m)
                nxt_r += 1
                nxt_c += 1
        return moves

    def _valid_moves(self) -> list[GameMove]:
        moves = []
        for r in range(BRD_SIZE):
            for c in range(BRD_SIZE):
                s = self.board[r][c]
                if self.color > 0 and s < 0 or self.color < 0 and s > 0:
                    continue
                match abs(s):
                    case PieceType.KING:
                        moves += self._valid_king_moves(row=r, col=c)
                    case PieceType.QUEEN:
                        moves += self._valid_queen_moves(row=r, col=c)
        return moves


class GameUI:
    def __init__(self):
        pass

    def draw_board(self, board: list[list[PieceType]]):
        c_hdr = [string.ascii_lowercase[x].upper() for x in range(BRD_SIZE)]
        print(" " + " ".join(c_hdr))
        for r in range(BRD_SIZE):
            c_pcs = []
            for c in range(BRD_SIZE):
                p = board[r][c]
                if p in PIECE_UI:
                    c_pcs.append(PIECE_UI[p])
                else:
                    p_sgn = 1 if (r + c) % 2 else -1
                    c_pcs.append(SQUARE_UI[p_sgn])
            print(str(r + 1) + " ".join(c_pcs))

    def user_move(self):
        coordinate = input("move: ")
        row = int(coordinate[1]) - 1
        col = string.ascii_uppercase.index(coordinate[0])
        return GameMove(row=row, col=col)


if __name__ == "__main__":
    engine = GameEngine()
    ui = GameUI()
    ui.draw_board(engine.board)
    user_move = ui.user_move()
    print(engine._valid_moves())
