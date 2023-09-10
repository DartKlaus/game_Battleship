from random import randint # из модуля random импортируем метод randint, который возвращает случайное целое число


class Dot: # класс точка, где присутствуют 2 атрибута х, у. Возвращает экземпляр класса в строковом виде 'Dot(x, y)'
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# классы исключения
class BoardException(Exception):
    pass

class OutBoard(BoardException):
    def __str__(self):
        return 'Сделайте выстрел в пределах доски!'

class AlreadyBoard(BoardException):
    def __str__(self):
        return 'По этим координатам уже был выстрел!'

class WrongShip(BoardException):
    pass


class Ship: # класс корабля с атрибутами: конец корабля, длинна, направление
    def __init__(self, s_end, s_len, direction):
        self.s_end = s_end
        self.s_len = s_len
        self.direction = direction
        self.hp = s_len

    @property # декоратор, обеспечивающий инкапсуляцию
    def dots(self): # метод класса, создающий список из координат расставленных кораблей
        ship_dots = []
        for i in range(self.s_len):
            cur_x = self.s_end.x
            cur_y = self.s_end.y

            if self.direction == 0:
                cur_x += i

            elif self.direction == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot): # метод класса проверяющий координаты выстрела с координатами кораблей
        return shot in self.dots


class Board: # класс доски с атрибутами: видна/не видна доска, размер доски
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid # когда атрибут hid равен False, доска видна

        self.count = 0 # количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)] # матрица игрового поля

        self.busy = [] # список всех занятых точек на доске
        self.ships = [] # список координат кораблей

    def __str__(self): # метод вывода из консоли игрового поля
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d): # метод проверки точки, находится ли она в пределах доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False): # метод обводящий контуром корабли
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship): # метод добавления корабля на игровое поле
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise WrongShip()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d): # метод выстрела по игровому полю
        if self.out(d): # исключение при наборе координат вне диапазона
            raise OutBoard()

        if d in self.busy: # исключение при наборее координат по уже занятым клеткам
            raise AlreadyBoard()

        self.busy.append(d)

        for ship in self.ships: # при попадании по кораблю запускается цикл вплоть до уничтожения корабля
            if d in ship.dots:
                ship.hp -= 1
                self.field[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "." # если выстрел происходит мимо
        print("Мимо!")
        return False

    def begin(self): # метод обнуления списка занятых клеток, для того, сохранять в него выстрелы игрока
        self.busy = []


class Player: # класс игрок с атрибутами доски самого игрока и противника
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self): # метод с возвращением ошибки при его вызове
        raise NotImplementedError()

    def move(self): # метод хода с бесконечным циклом
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player): # класс ИИ от родительского класса игрока
    def ask(self): # метод с использованием функции случайного числа
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player): # класс пользователя
    def ask(self): # метод с бесконечным циклом, который возвращает Dot(x, y)
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game: # класс игры
    def __init__(self, size=6): # метод с атрибутом размера доски
        self.size = size
        pl = self.random_board() # доска пользователя
        co = self.random_board() # доска ИИ
        co.hid = True # атрибут hid равен True, соответственно скрывает доску ИИ

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def hello(self): # метод приветствия с выводом из консоли инструкций к игре
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
    def try_board(self): # метод генерации доски с кораблями
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for s_len in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), s_len, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShip:
                    pass
        board.begin()
        return board

    def random_board(self): # метод с бесконечным циклом, где пытаемся создать доску без ошибок
        board = None
        while board is None:
            board = self.try_board()
        return board

    def loop(self): # метод игрового цикла с бесконечным циклом
        num = 0 # переменная для понимая, чей ход
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat: # если выстрел пользователя или ИИ попадает по кораблю, то переменная num откатывается
                num -= 1

            if self.ai.board.count == 7: # если число уничтоженных кораблей равно 7, то побеждает пользователь
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7: # аналогично для ИИ
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self): # метод старта игры
        self.hello()
        self.loop()


g = Game() # вызов класса
g.start() # использование метода start из класса Game, то есть вызов игры
