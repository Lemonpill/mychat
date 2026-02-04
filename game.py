import json
import colorama
from enum import IntEnum
from openai import OpenAI


class TileType(IntEnum):
    V = 0  # vacant
    X = 1  # cross
    O = 2  # circle


BOARD_SIZE = 3
TILE_ICONS = {
    TileType.V: "□",
    TileType.X: "⧆",
    TileType.O: "⧇",
}


class InvalidMoveError(ValueError): ...


class GameMove:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


class GameEngine:
    def __init__(self):
        self.board = [[TileType.V for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.last_move: GameMove | None = None
        self.is_over: bool = False
        self.is_draw: bool = False
        self.turn = TileType.X

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
            self.is_over = True
            return

        # no moves + no win = draw
        vacant_tiles = 0
        for r in self.board:
            for c in r:
                if c == TileType.V:
                    vacant_tiles += 1
        if not vacant_tiles:
            self.is_over = self.is_draw = True
            return

    def swap_turns(self):
        self.turn = TileType.X if self.turn == TileType.O else TileType.O

    def is_legal_move(self, move: GameMove):
        if move.row not in range(BOARD_SIZE) or move.col not in range(BOARD_SIZE):
            return False
        if self.board[move.row][move.col] != TileType.V:
            return False
        return True

    def make_move(self, move: GameMove):
        self.board[move.row][move.col] = self.turn
        self.last_move = move
        self.evaluate_board()
        if not self.is_over:
            self.swap_turns()


class GameAI:
    def __init__(self, client: OpenAI):
        self.system_chat = {"role": "system", "content": 'you must return json containing best move coordinate in tic-tac-toe based on board representation and turn provided. example: {"r": 0, "c": 2}'}
        self.client = client

    def suggest_move(self, board: str, turn: TileType):
        messages = [self.system_chat, {"role": "user", "content": f"board: {board}\nturn: {turn.value}"}]
        resp = self.client.chat.completions.create(model="gpt-5", messages=messages)
        resp_text_raw = resp.choices[0].message.content
        resp_text = resp_text_raw.replace("```json\n", "").replace("\n```", "")
        resp_dict = json.loads(resp_text)
        return int(resp_dict.get("r")), int(resp_dict.get("c"))


class GameUI:
    def __init__(self):
        pass

    def dump_board(self, board: list[list[TileType]]):
        text = "\n"
        for r in range(BOARD_SIZE):
            if r == 0:
                header = " ".join([str(i) for i in range(BOARD_SIZE)])
                text += f"  {header}\n"
            row = " ".join([TILE_ICONS[t] for t in board[r]])
            text += f"{r} {row}\n"
        return text

    def draw_board(self, board: list[list[TileType]]):
        text = self.dump_board(board=board)
        print(text)
        print(colorama.Style.RESET_ALL)

    def draw_error(self, text: str):
        print(colorama.Fore.RED + f"\n{text}\n")
        print(colorama.Style.RESET_ALL)

    def draw_alert(self, text: str):
        print(colorama.Fore.YELLOW + f"\n{text}\n")
        print(colorama.Style.RESET_ALL)

    def move_input(self):
        row_input = int(input("r: "))
        col_input = int(input("c: "))
        return row_input, col_input


class Game:
    def __init__(self, engine: GameEngine, ai: GameAI, ui: GameUI):
        self.engine = engine
        self.ai = ai
        self.ui = ui
        self.ai_turn = TileType.O

    def start(self):
        # first draw
        self.ui.draw_board(board=self.engine.board)

        # main game loop
        while True:
            ai_move = self.ai_turn == self.engine.turn

            # process inputs
            if ai_move:
                # ai input
                try:
                    move_row, move_col = self.ai.suggest_move(board=self.ui.dump_board(board=self.engine.board), turn=self.engine.turn)
                except Exception as e:
                    self.ui.draw_error(f"input error: {e}")
                    break
            else:
                # human input
                try:
                    move_row, move_col = self.ui.move_input()
                except Exception as e:
                    self.ui.draw_error(f"input error: {e}")
                    continue
                if move_row < 0 or move_col < 0:
                    break

            # validate selected coordinates
            move = GameMove(row=move_row, col=move_col)
            if not self.engine.is_legal_move(move=move):
                self.ui.draw_error(f"invalid move: r={move.row} c={move.col}")
                if ai_move:
                    break
                else:
                    continue

            # update board state
            self.engine.make_move(move=move)

            # redraw board state
            self.ui.draw_board(board=self.engine.board)

            # stop on win / draw
            if self.engine.is_over and not self.engine.is_draw:
                self.ui.draw_alert("game over")
                break
            elif self.engine.is_draw:
                self.ui.draw_alert("game draw")
                break


if __name__ == "__main__":
    engine = GameEngine()
    ai = GameAI(client=OpenAI())
    ui = GameUI()
    game = Game(engine=engine, ai=ai, ui=ui)
    game.start()
