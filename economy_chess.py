from enum import IntEnum, Enum
import string


DIR_N = (-1, 0)
DIR_NE = (-1, 1)
DIR_E = (0, 1)
DIR_SE = (1, 1)
DIR_S = (1, 0)
DIR_SW = (1, -1)
DIR_W = (0, -1)
DIR_NW = (-1, -1)

DIR_RKFL: list[tuple[int, int]] = [DIR_N, DIR_E, DIR_S, DIR_W]
DIR_DGNL: list[tuple[int, int]] = [DIR_NE, DIR_SE, DIR_SW, DIR_NW]
BRD_SIZE = 8


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
    def __init__(self, src_row: int, src_col: int, tgt_row: int, tgt_col: int):
        self.src_row = src_row
        self.src_col = src_col
        self.tgt_row = tgt_row
        self.tgt_col = tgt_col

    def __eq__(self, value):
        src_match = self.src_row == value.src_row and self.src_col == value.src_col
        tgt_match = self.tgt_row == value.tgt_row and self.tgt_col == value.tgt_col
        if src_match and tgt_match:
            return True
        return False

    def __repr__(self):
        return f"{self.src_row}-{self.src_col} -> {self.tgt_row}-{self.tgt_col}"


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

    def _is_blank_square(self, row: int, col: int):
        return not self.board[row][col]

    def _is_enemy_square(self, row: int, col: int):
        cond_a = self.color > 0 and self.board[row][col] < 0
        cond_b = self.color < 0 and self.board[row][col] > 0
        return any([cond_a, cond_b])

    def _is_valid_square(self, row: int, col: int):
        return row in range(BRD_SIZE) and col in range(BRD_SIZE)

    def _is_legal_square(self, row: int, col: int):
        if not self._is_valid_square(row=row, col=col):
            return False
        nxt_blank = self._is_blank_square(row=row, col=col)
        nxt_enemy = self._is_enemy_square(row=row, col=col)
        return nxt_blank or nxt_enemy

    def _valid_king_moves(self, row: int, col: int):
        moves: list[GameMove] = []
        for r_off, c_off in DIR_RKFL + DIR_DGNL:
            nxt_r = row + r_off
            nxt_c = col + c_off
            if not self._is_valid_square(row=nxt_r, col=nxt_c):
                continue
            m = GameMove(src_row=row, src_col=col, tgt_row=nxt_r, tgt_col=nxt_c)
            if self._is_blank_square(row=m.tgt_row, col=m.tgt_col):
                moves.append(m)
            else:
                if self._is_enemy_square(row=m.tgt_row, col=m.tgt_col):
                    moves.append(m)
                break
        return moves

    def _valid_queen_moves(self, row: int, col: int):
        moves: list[GameMove] = []
        for r_off, c_off in DIR_RKFL + DIR_DGNL:
            nxt_r = row + r_off
            nxt_c = col + c_off
            while self._is_valid_square(row=nxt_r, col=nxt_c):
                m = GameMove(src_row=row, src_col=col, tgt_row=nxt_r, tgt_col=nxt_c)
                if self._is_blank_square(row=nxt_r, col=nxt_c):
                    moves.append(m)
                else:
                    if self._is_enemy_square(row=nxt_r, col=nxt_c):
                        moves.append(m)
                    break
                nxt_r += r_off
                nxt_c += c_off
        return moves

    def _valid_moves(self) -> list[GameMove]:
        moves = []
        for r in range(BRD_SIZE):
            for c in range(BRD_SIZE):
                s_enemy = self._is_enemy_square(row=r, col=c)
                s_blank = self._is_blank_square(row=r, col=c)
                if not s_blank and s_enemy:
                    continue
                match abs(self.board[r][c]):
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
        return int(input("move: "))

    def move_text(self, board: list[list[PieceType]], move: GameMove):
        col_t = string.ascii_uppercase[move.tgt_col]
        row_t = move.tgt_row + 1
        src_p = board[move.src_row][move.src_col]
        mov_t = f"{PIECE_UI[src_p]}->{col_t}{row_t}"
        tgt_p = board[move.tgt_row][move.tgt_col]
        mov_t += f"x{PIECE_UI[tgt_p]}" if tgt_p in PIECE_UI else ""
        return mov_t


if __name__ == "__main__":
    engine = GameEngine()
    ui = GameUI()
    ui.draw_board(engine.board)
    for i, m in enumerate(engine._valid_moves()):
        m_txt = ui.move_text(board=engine.board, move=m)
        print(f"{i}: {m_txt}")
