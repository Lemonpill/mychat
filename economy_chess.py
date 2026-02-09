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

DIRS_KNGT: list[tuple[int, int]] = [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)]
DIRS_RKFL: list[tuple[int, int]] = [DIR_N, DIR_E, DIR_S, DIR_W]
DIRS_DGNL: list[tuple[int, int]] = [DIR_NE, DIR_SE, DIR_SW, DIR_NW]

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
    def __init__(self, src_row: int, src_col: int, tgt_row: int, tgt_col: int, cap_row: int | None = None, cap_col: int | None = None):
        self.src_row = src_row
        self.src_col = src_col
        self.tgt_row = tgt_row
        self.tgt_col = tgt_col
        self.cap_row = cap_row
        self.cap_col = cap_col


class GameEngine:
    def __init__(self):
        self.board = [[PieceType.BLANK for _ in range(BRD_SIZE)] for _ in range(BRD_SIZE)]
        self.color = Color.WHITE
        self.enp_r: int | None = None
        self.enp_c: int | None = None
        self._setup_board()

    def _setup_board(self):
        self.board[7] = [-1 * p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]
        self.board[6] = [-1 * PieceType.PAWN for _ in range(BRD_SIZE)]
        self.board[1] = [PieceType.PAWN for _ in range(BRD_SIZE)]
        self.board[0] = [p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]

    def _is_blank(self, row: int, col: int):
        return not self.board[row][col]

    def _is_enemy(self, row: int, col: int):
        cond_a = self.color > 0 and self.board[row][col] < 0
        cond_b = self.color < 0 and self.board[row][col] > 0
        return any([cond_a, cond_b])

    def _is_valid(self, row: int, col: int):
        return row in range(BRD_SIZE) and col in range(BRD_SIZE)

    def _step_moves(self, row: int, col: int, dirs: list[tuple[int, int]]):
        moves: list[GameMove] = []
        for r_off, c_off in dirs:
            tgt_row = row + r_off
            tgt_col = col + c_off
            tgt_valid = self._is_valid(row=tgt_row, col=tgt_col)
            if not tgt_valid:
                continue
            tgt_enemy = self._is_enemy(row=tgt_row, col=tgt_col)
            tgt_blank = self._is_blank(row=tgt_row, col=tgt_col)
            if tgt_blank or tgt_enemy:
                m = GameMove(src_row=row, src_col=col, tgt_row=tgt_row, tgt_col=tgt_col)
                if tgt_enemy:
                    m.cap_row = tgt_row
                    m.cap_col = tgt_col
                moves.append(m)
        return moves

    def _slide_moves(self, row: int, col: int, dirs: list[tuple[int, int]]):
        moves: list[GameMove] = []
        for r_off, c_off in dirs:
            nxt_r = row + r_off
            nxt_c = col + c_off
            while self._is_valid(row=nxt_r, col=nxt_c):
                tgt_enemy = self._is_enemy(row=nxt_r, col=nxt_c)
                tgt_blank = self._is_blank(row=nxt_r, col=nxt_c)
                m = GameMove(src_row=row, src_col=col, tgt_row=nxt_r, tgt_col=nxt_c)
                if tgt_blank or tgt_enemy:
                    if tgt_enemy:
                        m.cap_row = nxt_r
                        m.cap_col = nxt_c
                    moves.append(m)
                if tgt_enemy or not tgt_blank:
                    break
                nxt_r += r_off
                nxt_c += c_off
        return moves

    def _king_moves(self, row: int, col: int):
        return self._step_moves(row=row, col=col, dirs=DIRS_RKFL + DIRS_DGNL)

    def _queen_moves(self, row: int, col: int):
        return self._slide_moves(row=row, col=col, dirs=DIRS_RKFL + DIRS_DGNL)

    def _rook_moves(self, row: int, col: int):
        return self._slide_moves(row=row, col=col, dirs=DIRS_RKFL)

    def _bishop_moves(self, row: int, col: int):
        return self._slide_moves(row=row, col=col, dirs=DIRS_DGNL)

    def _knight_moves(self, row: int, col: int):
        return self._step_moves(row=row, col=col, dirs=DIRS_KNGT)

    def _pawn_moves(self, row: int, col: int):
        moves: list[GameMove] = []
        is_initial = self.color > 0 and row == 1 or self.color < 0 and row == 6
        stp_t = 2 if is_initial else 1
        stp_dir = DIR_S if self.color > 0 else DIR_N
        stp_i = 1
        while stp_i <= stp_t:
            nxt_r = row + (stp_dir[0] * stp_i)
            nxt_c = col + (stp_dir[1] * stp_i)
            tgt_valid = self._is_valid(row=nxt_r, col=nxt_c)
            if not tgt_valid:
                break
            tgt_blank = self._is_blank(row=nxt_r, col=nxt_c)
            if not tgt_blank:
                break
            m = GameMove(src_row=row, src_col=col, tgt_row=nxt_r, tgt_col=nxt_c)
            moves.append(m)
            stp_i += 1
        atk_dir = [DIR_SW, DIR_SE] if self.color > 0 else [DIR_NW, DIR_NE]
        for d in atk_dir:
            atk_r = row + d[0]
            atk_c = col + d[1]
            if not self._is_valid(row=atk_r, col=atk_c):
                continue
            is_enpsn = atk_r == self.enp_r and atk_c == self.enp_c
            is_enemy = self._is_enemy(row=atk_r, col=atk_c)
            if not is_enemy and not is_enpsn:
                continue
            m = GameMove(src_row=row, src_col=col, tgt_row=atk_r, tgt_col=atk_c)
            if is_enemy:
                m.cap_row = atk_r
                m.cap_col = atk_c
            elif is_enpsn:
                m.cap_row = self.enp_r
                m.cap_col = self.enp_c
            moves.append(m)
        return moves

    def _pseudo_legal_moves(self) -> list[GameMove]:
        moves = []
        for r in range(BRD_SIZE):
            for c in range(BRD_SIZE):
                s_enemy = self._is_enemy(row=r, col=c)
                s_blank = self._is_blank(row=r, col=c)
                if s_blank or s_enemy:
                    continue
                match abs(self.board[r][c]):
                    case PieceType.KING:
                        moves += self._king_moves(row=r, col=c)
                    case PieceType.QUEEN:
                        moves += self._queen_moves(row=r, col=c)
                    case PieceType.ROOK:
                        moves += self._rook_moves(row=r, col=c)
                    case PieceType.BISHOP:
                        moves += self._bishop_moves(row=r, col=c)
                    case PieceType.KNIGHT:
                        moves += self._knight_moves(row=r, col=c)
                    case PieceType.PAWN:
                        moves += self._pawn_moves(row=r, col=c)
        return moves

    def make_move(self, move: GameMove):
        src_r, src_c = move.src_row, move.src_col
        tgt_r, tgt_c = move.tgt_row, move.tgt_col
        cap_r, cap_c = move.cap_row, move.cap_col
        move_piece = self.board[src_r][src_c]
        self.board[src_r][src_c] = PieceType.BLANK
        if cap_r is not None and cap_c is not None:
            self.board[cap_r][cap_c] = PieceType.BLANK
        if abs(move_piece) == PieceType.PAWN and abs(move.src_row - move.tgt_row) == 2:
            self.enp_r = (move.src_row + move.tgt_row) // 2
            self.enp_c = move.src_col
        else:
            self.enp_r = self.enp_c = None
        self.color = self.color * -1


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

    def _move_pos_text(self, board: list[list[PieceType]], row: int, col: int):
        col_t = string.ascii_uppercase[col]
        row_t = row + 1
        sqr = board[row][col]
        sqr_s = PIECE_UI[sqr] if sqr in PIECE_UI else ""
        return f"{sqr_s} {col_t}{row_t}"

    def move_text(self, board: list[list[PieceType]], move: GameMove):
        src_txt = self._move_pos_text(board=board, row=move.src_row, col=move.src_col)
        tgt_txt = self._move_pos_text(board=board, row=move.tgt_row, col=move.tgt_col)
        return f"{src_txt}>{tgt_txt}"


if __name__ == "__main__":
    engine = GameEngine()
    ui = GameUI()
    while True:
        ui.draw_board(engine.board)
        move_lst = engine._pseudo_legal_moves()
        move_map = {i: m for i, m in enumerate(move_lst)}
        for i, m in move_map.items():
            m_txt = ui.move_text(board=engine.board, move=m)
            print(f"{i}: {m_txt}")
        inp = ui.user_move()
        engine.make_move(move_map[inp])
