from enum import IntEnum


BRD_SIZE = 8


class PieceType(IntEnum):
    BLANK = 0
    KING = 1
    QUEEN = 2
    ROOK = 3
    BISHOP = 4
    KNIGHT = 5
    PAWN = 6


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


class GameEngine:
    def __init__(self):
        self.board = [[PieceType.BLANK for _ in range(BRD_SIZE)] for _ in range(BRD_SIZE)]
        self._setup_board()

    def _setup_board(self):
        self.board[0] = [-1 * p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]
        self.board[1] = [-1 * PieceType.PAWN for _ in range(BRD_SIZE)]
        self.board[6] = [PieceType.PAWN for _ in range(BRD_SIZE)]
        self.board[7] = [p for p in [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]]


class GameUI:
    def __init__(self):
        pass

    def draw_board(self, board: list[list[PieceType]]):
        for r in range(BRD_SIZE):
            c_pcs = []
            for c in range(BRD_SIZE):
                p = board[r][c]
                if p in PIECE_UI:
                    c_pcs.append(PIECE_UI[p])
                else:
                    p_sgn = 1 if (r + c) % 2 else -1
                    c_pcs.append(SQUARE_UI[p_sgn])
            print(" ".join(c_pcs))


if __name__ == "__main__":
    engine = GameEngine()
    ui = GameUI()
    ui.draw_board(engine.board)
