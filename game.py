from enum import IntEnum


BOARD_SIZE = 3


class TileNotVacantError(ValueError): ...


class TileNotOnBoardError(ValueError): ...


class TileType(IntEnum):
    V = 0  # vacant
    O = 2  # circle
    X = 1  # cross


class GameEngine:
    def __init__(self):
        self.board = [[TileType.V for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = TileType.X
        self.last_move: tuple[int, int] = None
        self.done = False

    def evaluate(self):
        last_move_row = self.last_move[0]
        last_move_col = self.last_move[1]

        # scan vertical ray from last move
        vert_ray_tiles = []
        curr_r = 0
        curr_c = last_move_col
        while curr_r in range(BOARD_SIZE) and curr_c in range(BOARD_SIZE):
            vert_ray_tiles.append(self.board[curr_r][curr_c])
            curr_r += 1

        print(vert_ray_tiles)

    def move(self, tile: tuple[int, int]):
        r = tile[0]
        c = tile[1]
        if r not in range(BOARD_SIZE) or c not in range(BOARD_SIZE):
            raise TileNotOnBoardError
        if self.board[r][c] != TileType.V:
            raise TileNotVacantError
        self.board[r][c] = self.turn
        self.turn = TileType.X if self.turn == TileType.O else TileType.O
        self.last_move = tile


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
            try:
                self.engine.move((int(col_input), int(row_input)))
            except (TileNotOnBoardError, TileNotVacantError):
                print("make a valid move")


if __name__ == "__main__":
    engine = GameEngine()
    ai = GameAI(engine=engine)
    ui = GameUI(engine=engine)
    game = Game(engine=engine, ai=ai, ui=ui)
    game.start()
