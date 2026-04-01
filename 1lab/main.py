import copy


class Piece:
    """Базовый класс для всех шахматных фигур."""

    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol

    def possible_moves(self, pos, board):
        raise NotImplementedError

    def __repr__(self):
        return self.symbol


class Pawn(Piece):
    """Пешка."""

    def __init__(self, color):
        super().__init__(color, 'P' if color == 'white' else 'p')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        nx, ny = x + direction, y
        if 0 <= nx < 8 and board[nx][ny] is None:
            moves.append((nx, ny))
            if x == start_row and board[x + 2 * direction][y] is None:
                moves.append((x + 2 * direction, y))

        for dy in (-1, 1):
            nx, ny = x + direction, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[nx][ny]
                if target and target.color != self.color:
                    moves.append((nx, ny))
        return moves


class Rook(Piece):
    """Ладья."""

    def __init__(self, color):
        super().__init__(color, 'R' if color == 'white' else 'r')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for step in range(1, 8):
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                else:
                    if board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                    break
        return moves


class Knight(Piece):
    """Конь."""

    def __init__(self, color):
        super().__init__(color, 'N' if color == 'white' else 'n')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                       (1, 2), (1, -2), (-1, 2), (-1, -2)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[nx][ny]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves


class Bishop(Piece):
    """Слон."""

    def __init__(self, color):
        super().__init__(color, 'B' if color == 'white' else 'b')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for step in range(1, 8):
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                else:
                    if board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                    break
        return moves


class Queen(Piece):
    """Ферзь."""

    def __init__(self, color):
        super().__init__(color, 'Q' if color == 'white' else 'q')

    def possible_moves(self, pos, board):
        return Rook.possible_moves(self, pos, board) + Bishop.possible_moves(self, pos, board)


class King(Piece):
    """Король."""

    def __init__(self, color):
        super().__init__(color, 'K' if color == 'white' else 'k')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board[nx][ny]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))
        return moves


# ========== НОВЫЕ ФИГУРЫ ==========

class Camel(Piece):
    """Верблюд — ходит как конь, но на (3,1) клетки."""

    def __init__(self, color):
        super().__init__(color, 'C' if color == 'white' else 'c')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((3, 1), (3, -1), (-3, 1), (-3, -1),
                       (1, 3), (1, -3), (-1, 3), (-1, -3)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[nx][ny]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves


class Guard(Piece):
    """Стражник — ходит как король, но только по диагонали."""

    def __init__(self, color):
        super().__init__(color, 'G' if color == 'white' else 'g')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[nx][ny]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves


class Jumper(Piece):
    """Попрыгунчик — ходит на 2 клетки по вертикали/горизонтали."""

    def __init__(self, color):
        super().__init__(color, 'J' if color == 'white' else 'j')

    def possible_moves(self, pos, board):
        x, y = pos
        moves = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[nx][ny]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves


class ChessBoard:
    """Шахматная доска."""

    def __init__(self, mode='classic'):
        self.board = [[None] * 8 for _ in range(8)]
        self.turn = 'white'
        self.history = []
        self.mode = mode
        self.setup()

    def setup(self):
        if self.mode == 'classic':
            self._setup_classic()
        else:
            self._setup_extended()

    def _setup_classic(self):
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece_class in enumerate(pieces):
            self.board[0][i] = piece_class('black')
            self.board[7][i] = piece_class('white')
        for i in range(8):
            self.board[1][i] = Pawn('black')
            self.board[6][i] = Pawn('white')

    def _setup_extended(self):
        white_pieces = [Rook, Knight, Guard, Camel, King, Jumper, Bishop, Rook]
        black_pieces = [Rook, Knight, Guard, Camel, King, Jumper, Bishop, Rook]

        for i, piece_class in enumerate(white_pieces):
            self.board[7][i] = piece_class('white')
        for i, piece_class in enumerate(black_pieces):
            self.board[0][i] = piece_class('black')

        for i in range(8):
            self.board[6][i] = Pawn('white')
            self.board[1][i] = Pawn('black')

    def display(self, highlight_moves=None, threats=None, check_highlight=None):
        """Отображение доски."""
        print("\n  a  b  c  d  e  f  g  h")
        for i in range(8):
            row = 8 - i
            print(row, end=" ")
            for j in range(8):
                piece = self.board[i][j]
                if highlight_moves and (i, j) in highlight_moves:
                    print(" ·", end=" ")
                elif threats and (i, j) in threats:
                    print(" X", end=" ")
                elif check_highlight and (i, j) == check_highlight:
                    print(" +", end=" ")
                elif piece:
                    print(f" {piece.symbol}", end=" ")
                else:
                    print(" .", end=" ")
            print(row)
        print("  a  b  c  d  e  f  g  h")

    def get_piece_at(self, pos):
        x, y = pos
        return self.board[x][y]

    def move(self, from_pos, to_pos):
        piece = self.get_piece_at(from_pos)
        if not piece or piece.color != self.turn:
            return False

        possible = piece.possible_moves(from_pos, self.board)
        if to_pos not in possible:
            return False

        captured = self.get_piece_at(to_pos)
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = None

        if self.is_check(self.turn):
            self.board[from_pos[0]][from_pos[1]] = piece
            self.board[to_pos[0]][to_pos[1]] = captured
            return False

        self.history.append((copy.deepcopy(self.board), self.turn))
        self.turn = 'black' if self.turn == 'white' else 'white'
        return True

    def undo(self):
        if not self.history:
            return False
        self.board, self.turn = self.history.pop()
        return True

    def is_check(self, color):
        king_pos = None
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color == color and isinstance(piece, King):
                    king_pos = (i, j)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color != color:
                    if king_pos in piece.possible_moves((i, j), self.board):
                        return True
        return False

    def threats_to(self, color):
        threats = []
        king_pos = None
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color == color and isinstance(piece, King):
                    king_pos = (i, j)
                    break
            if king_pos:
                break

        if not king_pos:
            return threats

        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color != color:
                    if king_pos in piece.possible_moves((i, j), self.board):
                        threats.append(king_pos)
                        break
        return threats


def choose_mode():
    print("\n" + "=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В ШАХМАТЫ!")
    print("=" * 60)
    print("\nВыберите режим игры:")
    print("1. Классические шахматы")
    print("2. Расширенные шахматы (с новыми фигурами)")
    print("\nНовые фигуры:")
    print("  C/c Верблюд — ходит как конь, но на (3,1) клетки")
    print("  G/g Стражник — ходит как король, но только по диагонали")
    print("  J/j Попрыгунчик — ходит на 2 клетки по вертикали/горизонтали")

    while True:
        choice = input("\nВведите 1 или 2: ").strip()
        if choice == '1':
            return 'classic'
        elif choice == '2':
            return 'extended'
        else:
            print("Неверный выбор. Попробуйте снова.")


def main():
    mode = choose_mode()
    board = ChessBoard(mode)
    selected = None

    print("\n" + "=" * 60)
    print("ИГРА НАЧАЛАСЬ!")
    print("=" * 60)
    print("\nОБОЗНАЧЕНИЯ ФИГУР:")
    print("-" * 60)
    print("БЕЛЫЕ ФИГУРЫ (заглавные буквы):")
    print("  P = Пешка (ходит вперед на 1 клетку, на 2 с начальной позиции, бьет по диагонали)")
    print("  R = Ладья (ходит по горизонтали и вертикали на любое расстояние)")
    print("  N = Конь (ходит буквой 'Г': 2 клетки в одну сторону, 1 в другую)")
    print("  B = Слон (ходит по диагонали на любое расстояние)")
    print("  Q = Ферзь (ходит как ладья + слон)")
    print("  K = Король (ходит на 1 клетку в любом направлении)")
    
    if mode == 'extended':
        print("\nДОПОЛНИТЕЛЬНЫЕ ФИГУРЫ (только в расширенном режиме):")
        print("  C = Верблюд (ходит как конь, но на 3 клетки в одну сторону и 1 в другую)")
        print("  G = Стражник (ходит как король, но только по диагонали)")
        print("  J = Попрыгунчик (ходит на 2 клетки по вертикали или горизонтали)")
    
    print("\nЧЁРНЫЕ ФИГУРЫ (строчные буквы):")
    print("  p = пешка")
    print("  r = ладья")
    print("  n = конь")
    print("  b = слон")
    print("  q = ферзь")
    print("  k = король")
    
    if mode == 'extended':
        print("  c = верблюд")
        print("  g = стражник")
        print("  j = попрыгунчик")
    
    print("\n" + "-" * 60)
    print("КОМАНДЫ:")
    print("  a2a3      - сделать ход (например, a2a3)")
    print("  select a2 - подсветить возможные ходы фигуры")
    print("  undo      - откатить последний ход")
    print("  quit      - выйти из игры")
    print("=" * 60)

    while True:
        check_pos = None
        if board.is_check(board.turn):
            threats = board.threats_to(board.turn)
            check_pos = threats[0] if threats else None

        board.display(
            threats=board.threats_to(board.turn),
            check_highlight=check_pos
        )

        if selected:
            piece = board.get_piece_at(selected)
            if piece and piece.color == board.turn:
                moves = piece.possible_moves(selected, board.board)
                board.display(
                    highlight_moves=moves,
                    threats=board.threats_to(board.turn),
                    check_highlight=check_pos
                )

        cmd = input(
            f"\n{board.turn}'s turn. "
            "Enter move (a2a3), 'select a2', 'undo', or 'quit': "
        ).strip().lower()

        if cmd == 'quit':
            print("\nСпасибо за игру!")
            break
        elif cmd == 'undo':
            if board.undo():
                selected = None
                print("Ход отменён")
            else:
                print("Нечего отменять")
            continue
        elif cmd.startswith('select'):
            try:
                _, pos = cmd.split()
                x = 8 - int(pos[1])
                y = ord(pos[0]) - ord('a')
                if 0 <= x < 8 and 0 <= y < 8:
                    selected = (x, y)
                else:
                    print("Неверная позиция")
            except (ValueError, IndexError):
                print("Неверная команда. Пример: select a2")
            continue
        elif len(cmd) == 4:
            try:
                fx, fy = 8 - int(cmd[1]), ord(cmd[0]) - ord('a')
                tx, ty = 8 - int(cmd[3]), ord(cmd[2]) - ord('a')
                if board.move((fx, fy), (tx, ty)):
                    selected = None
                else:
                    print("Неверный ход")
            except (ValueError, IndexError):
                print("Неверная команда. Пример: a2a3")
        else:
            print("Команды: a2a3, select a2, undo, quit")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
