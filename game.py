from enum import IntEnum


class TileType(IntEnum):
    V = 0  # vacant
    X = 1  # cross
    O = 2  # circle


BOARD_SIZE = 3
TILE_ICONS = {TileType.V: "-", TileType.X: "X", TileType.O: "O"}


class InvalidMoveError(ValueError): ...


class GameMove:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


class GameEngine:
    def __init__(self):
        self.board = [[TileType.V for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = TileType.X
        self.last_move: GameMove | None = None
        self.is_draw = False
        self.is_win = False

    def evaluate_board(self):
        last_move_row = self.last_move.row
        last_move_col = self.last_move.col

        # scan top-down ray crossing last move
        td_ray_leng = 0
        td_ray_full = True
        td_r = 0
        td_c = last_move_col
        while td_r in range(BOARD_SIZE):
            if self.board[td_r][td_c] != self.turn:
                td_ray_full = False
                break
            td_ray_leng += 1
            td_r += 1

        # scan top left - bottom right ray crossing last move
        tlbr_ray_leng = 0
        tlbr_ray_full = True
        tlbr_r = last_move_row
        tlbr_c = last_move_col
        while tlbr_r in range(1, BOARD_SIZE) and tlbr_c in range(1, BOARD_SIZE):
            tlbr_r -= 1
            tlbr_c -= 1
        while tlbr_r in range(BOARD_SIZE) and tlbr_c in range(BOARD_SIZE):
            if self.board[tlbr_r][tlbr_c] != self.turn:
                tlbr_ray_full = False
                break
            tlbr_ray_leng += 1
            tlbr_r += 1
            tlbr_c += 1

        # scan top right - bottom left ray crossing last move
        trbl_ray_leng = 0
        trbl_ray_full = True
        trbl_r = last_move_row
        trbl_c = last_move_col
        while trbl_r in range(1, BOARD_SIZE) and trbl_c in range(1, BOARD_SIZE):
            trbl_r -= 1
            trbl_c += 1
        while trbl_r in range(BOARD_SIZE) and trbl_c in range(BOARD_SIZE):
            if self.board[trbl_r][trbl_c] != self.turn:
                trbl_ray_full = False
                break
            trbl_ray_leng += 1
            trbl_r += 1
            trbl_c -= 1

        # scan left-right ray crossing last move
        lr_ray_leng = 0
        lr_ray_full = True
        lr_r = last_move_row
        lr_c = 0
        while lr_c in range(BOARD_SIZE):
            if self.board[lr_r][lr_c] != self.turn:
                lr_ray_full = False
                break
            lr_ray_leng += 1
            lr_c += 1

        # need to be at least board size length to win
        td_ray_win = td_ray_full and td_ray_leng >= BOARD_SIZE
        tlbr_ray_win = tlbr_ray_full and tlbr_ray_leng >= BOARD_SIZE
        trbl_ray_win = trbl_ray_full and trbl_ray_leng >= BOARD_SIZE
        lr_ray_win = lr_ray_full and lr_ray_leng >= BOARD_SIZE

        # check if any of the rays are winning
        if any([td_ray_win, tlbr_ray_win, trbl_ray_win, lr_ray_win]):
            self.is_win = True
            return

        # check if one or less tile is open
        vacant_tiles = 0
        for r in self.board:
            for c in r:
                if c == TileType.V:
                    vacant_tiles += 1
        # check it?
        if vacant_tiles <= 1:
            self.is_draw = True
            return

    def swap_turn(self):
        self.turn = TileType.X if self.turn == TileType.O else TileType.O

    def is_valid_move(self, move: GameMove):
        if move.row not in range(BOARD_SIZE) or move.col not in range(BOARD_SIZE):
            return False
        if self.board[move.row][move.col] != TileType.V:
            return False
        return True

    def make_move(self, move: GameMove):
        self.board[move.row][move.col] = self.turn
        self.last_move = move
        self.evaluate_board()
        if self.is_win or self.is_draw:
            return
        self.swap_turn()


class GameAI:
    def __init__(self, engine: GameEngine):
        self.engine = engine


class GameUI:
    def __init__(self, engine: GameEngine):
        self.engine = engine

    def draw(self):
        print(f"  {[str(i) for i in range(BOARD_SIZE)]}")
        for i, r in enumerate(self.engine.board):
            print(f"{i} {[TILE_ICONS[t] for t in r]}")

    def pick_tile(self):
        row_input = int(input("r: "))
        col_input = int(input("c: "))
        return row_input, col_input


class Game:
    def __init__(self, engine: GameEngine, ai: GameAI, ui: GameUI):
        self.engine = engine
        self.ai = ai
        self.ui = ui

    def start(self):
        self.ui.draw()
        while True:
            move_row, move_col = self.ui.pick_tile()
            move = GameMove(row=move_row, col=move_col)
            if not self.engine.is_valid_move(move=move):
                print("invalid move")
                continue
            self.engine.make_move(move=move)
            self.ui.draw()
            if self.engine.is_draw:
                print("draw!")
                break
            if self.engine.is_win:
                print("win!")
                break


if __name__ == "__main__":
    engine = GameEngine()
    ai = GameAI(engine=engine)
    ui = GameUI(engine=engine)
    game = Game(engine=engine, ai=ai, ui=ui)
    game.start()
