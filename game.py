from enum import IntEnum


BOARD_SIZE = 3


class TileNotVacantError(ValueError): ...


class TileNotOnBoardError(ValueError): ...


class TileType(IntEnum):
    V = 0  # vacant
    O = 2  # circle
    X = 1  # cross
    
class GameMove:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


class GameEngine:
    def __init__(self):
        self.board = [[TileType.V for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = TileType.X
        self.last_move: GameMove | None = None
        self.done = False

    def evaluate(self):
        last_move_row = self.last_move.row
        last_move_col = self.last_move.col

        # scan top-down crossing last move
        td_ray_tiles = []
        td_r = 0
        td_c = last_move_col
        while td_r in range(BOARD_SIZE):
            td_ray_tiles.append(self.board[td_r][td_c])
            td_r += 1

        print(td_ray_tiles)
        
        lr_ray_tiles = []
        lr_r = last_move_row
        lr_c = 0
        while lr_c in range(BOARD_SIZE):
            lr_ray_tiles.append(self.board[lr_r][lr_c])
            lr_c += 1
        
        print(lr_ray_tiles)
        

    def make_move(self, move: GameMove):
        r = move.row
        c = move.col
        if r not in range(BOARD_SIZE) or c not in range(BOARD_SIZE):
            raise TileNotOnBoardError
        if self.board[r][c] != TileType.V:
            raise TileNotVacantError
        self.board[r][c] = self.turn
        self.last_move = move
        self.evaluate()
        self.turn = TileType.X if self.turn == TileType.O else TileType.O


class GameAI:
    def __init__(self, engine: GameEngine):
        self.engine = engine


class GameUI:
    def __init__(self, engine: GameEngine):
        self.engine = engine

    def draw(self):
        tile_ui = {TileType.V: "-", TileType.X: "X", TileType.O: "O"}
        print(f"  {[str(i) for i in range(BOARD_SIZE)]}")
        for i, r in enumerate(self.engine.board):
            print(f"{i} {[tile_ui[t] for t in r]}")


class Game:
    def __init__(self, engine: GameEngine, ai: GameAI, ui: GameUI):
        self.engine = engine
        self.ai = ai
        self.ui = ui

    def start(self):
        while True:
            self.ui.draw()
            col_input = input("c: ")
            row_input = input("r: ")
            if not all([col_input, row_input]):
                break
            move = GameMove(row=int(row_input), col=int(col_input))
            try:
                self.engine.make_move(move=move)
            except (TileNotOnBoardError, TileNotVacantError):
                print("make a valid move")


if __name__ == "__main__":
    engine = GameEngine()
    ai = GameAI(engine=engine)
    ui = GameUI(engine=engine)
    game = Game(engine=engine, ai=ai, ui=ui)
    game.start()
