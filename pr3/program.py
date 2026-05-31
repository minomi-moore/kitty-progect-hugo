"""
@mainpage Робот с запретными зонами
@author Замятина София
@date 14.05.2026

@page page1 - Страница 1
@section Характеристика программы
@subsection Описание программы
Программа реализует систему управления роботом на поле 100х100 с заданием запретных зон.
Начало движения - (1,1).Поддерживается высокоуровневое задание траектории с командами R, L,
U, D и командой B (откат на N шагов назад). На выход программа подает путь робота по
координатам (х,у)

@subsection Что может программа?
- Задание произвольного количества прямоугольных запретных зон
- Контроль выхода за границы поля
- Проверка столкновений с запретными зонами

@subsection Команды движения
R,N - движение вправо на N шагов
L,N - движение влево на N шагов
U,N - движение вверх на N шагов
D,N - движение вниз на N шагов
B - откат на один шаг назад (команда-отмена)

@page page2 - Страница 2
"""
import sys

#возврат точек запретной зоны
def post_zapret(x, y, w, h):
	"""
	@brief Формирование списка точек прямоугольной запретной зоны
	@details Функция создает список всех координах, входящих в прямоугольник с
		 левым верхним углом (х,у), шириной w и высотой h.

	@param x Координата X левого верхнего левого угла зоны
	@param y Координата Y левого верхнего левого угла зоны
	@param w Ширина зоны
	@param h Высота зоны

        @return Список кортежей (х,у) всех точек, входящих в запретную зону
	@code
	point = post_zapret(5,5,2,2)
	# Результат: [(5,5), (5,6), (6,5), (6,6)]
	@endcode

	@note пасхалко Дмитрию Борисовичу
	@warning Функция не проверяет выход за границы поля
	@todo Добавить проверку зон
	"""
    post_zapret_list = []
    for i in range(0, w):
        post_zapret_list.append((x+i, y))
        for k in range(1, h):
            post_zapret_list.append((x+i, y+k))
    return post_zapret_list


#вводим запретные зоны
def zapret_zona():
"""
@brief Ввод запретных зон с клавиатуры

@details Функция запрашивает у пользователя количество запретных зон,
         затем для каждой зоны вводит координаты левого верхнего угла,
         ширину и высоту. Все зоны объединяются в общий список.

@return Список всех запрещенных координат из всех зон

@note Ввод осуществляется последовательно: количество зон -> параметры каждой зоны
@warning Координаты и размеры зон не проверяются на корректность
@see post_zapret
"""
    print("Введите количество запретных зон: ")
    n = int(input())
    all_zones = []
    for _ in range(n):
        print("Введите координату левого верхнего угла зоны")
        print("X,Y")
        x = int(input())
        y = int(input())
        print("Введите ширину зоны")
        w = int(input())
        print("Введите высоту зоны")
        h = int(input())
        all_zones += post_zapret(x,y,w,h)
    return all_zones

#проверка зон
def prov(move_low,zapret):
"""
@brief Проверка попадания траектории в запретные зоны

@details Функция сравнивает каждую точку траектории движения робота
         с каждой точкой запретных зон. При первом же совпадении
         возвращает 0.

@param move_low Список координат траектории движения робота
@param zapret Список запрещенных координат

@return @retval 0 если есть попадание в запретную зону
        @retval 1 если запретные зоны не затронуты

@warning При длинных списках работает медленно (полный перебор)
@note Функция не изменяет исходные списки

@see low_level
"""
    for i in move_low:
        for j in zapret:
            if (i[0] == j[0] and i[1] == j[1]):
                return 0
    return 1

#проверка граней
def gran(start_pozicion):
"""
@brief Проверка выхода за границы поля

@details Функция проверяет, находятся ли координаты робота в пределах
         поля от 1 до 100 по x или по y. При выходе за границы программа
         завершается с сообщением об ошибке.

@param start_pozicion Текущие координаты робота [x, y]

@return Всегда возвращает True, если проверка пройдена

@note <3
"""
    if (start_pozicion[0] <= 0 or start_pozicion[0] > 100 or
                start_pozicion[1] <= 0 or start_pozicion[1] > 100):
                print("Выход за границу!")
                sys.exit(1)
    return True

#удаляем ненужные В
def count_b(move_high):
"""
@brief Удаление лишних команд B из программы движения

@details Функция оставляет только последнюю команду B в списке,
         так как только она имеет реальный эффект при выполнении.
         Все предыдущие команды B удаляются.

@param move_high Список высокоуровневых команд

@return Новый список команд без лишних B

@code
# Пример:
Вход: [['R',2], ['B',1], ['U',3], ['B',2]]
Выход: [['R',2], ['U',3], ['B',2]]
@endcode

@see high_level
"""

    cnt_B = 0
    new_move_high = []
    for i in move_high:
        if (i[0] == 'B'):
            cnt_B += 1
    last_B = -1
    if (cnt_B > 1):
        for i in range(len(move_high)-1,-1,-1):
            if (move_high[i][0] == 'B'):
                last_B = i
                break
    for i in range(len(move_high)):
        if (move_high[i][0] == 'B' and i != last_B):
            continue
        new_move_high.append(move_high[i])
    return new_move_high

#строим список с высокоуровневой прогой
def high_level():
"""
@brief Ввод высокоуровневой программы движения

@details Функция построчно считывает команды движения. Ввод продолжается
         до тех пор, пока пользователь не введет Enter.

@note Команды описаны на Странице 1
@return Список команд в формате [['буква', число], ...]

@warning При вводе неверной команды программа завершается

@see low_level
@see count_b
"""
    move_high = []
    print("Введите передвижения:")
    while (1):
        a = str(input())
        if (len(a) == 0):
            break
        if (a[0] not in "LRUDB"):
            print("Неверный формат ввода")
            break
        else:
            if(a == 'B'):
                move_high.append(['B',1])
            else:
                move_high.append(a.split(','))
    return move_high

#строим список низкоуровневой программы
def low_level(move_high):
"""
@brief Преобразование высокоуровневой программы в траекторию движения

@details Функция интерпретирует команды высокого уровня и генерирует
         список всех промежуточных координат, которые посещает робот.

@param move_high Список высокоуровневых команд

@return Список всех координат траектории (включая начальную точку)

@note Команда B инвертирует движение: R становится L, U становится D и т.д.
@warning Требуется предварительная очистка списка команд от лишних B

@see gran
@see high_level
@see count_b
"""
    start_pozicion = [1, 1]
    move_low = [start_pozicion.copy()]

    for i in range(len(move_high)):
        letter = move_high[i][0]
        number = int(move_high[i][1])
        if letter == "B":
            for j in range(i-1,max(0, i-number)-1, -1):
                back_letter = move_high[j][0]
                back_number = int(move_high[j][1])
                #Инверсия движения
                for _ in range(back_number):
                    if back_letter == "R":
                        start_pozicion[0] -= 1
                    elif back_letter == "L":
                        start_pozicion[0] += 1
                    elif back_letter == "U":
                        start_pozicion[1] += 1
                    elif back_letter == "D":
                        start_pozicion[1] -= 1

                    gran(start_pozicion)
                    move_low.append(start_pozicion.copy())
            continue
        if letter == 'R':
            for k in range(number):
                start_pozicion[0] += 1
                gran(start_pozicion)
                move_low.append(start_pozicion.copy())
        elif letter == 'L':
            for k in range(number):
                start_pozicion[0] -= 1
                gran(start_pozicion)
                move_low.append(start_pozicion.copy())
        elif letter == 'U':
            for k in range(number):
                start_pozicion[1] -= 1
                gran(start_pozicion)
                move_low.append(start_pozicion.copy())
        elif letter == 'D':
            for k in range(number):
                start_pozicion[1] += 1
                gran(start_pozicion)
                move_low.append(start_pozicion.copy())

    return move_low

"""
@section Основной блок выполнения программы

@subsection Последовательность работы:
1. Ввод запретных зон (функция zapret_zona)
2. Ввод высокоуровневой программы (функция high_level)
3. Очистка списка команд от лишних B (функция count_b)
4. Генерация траектории движения (функция low_level)
5. Проверка на столкновения с запретными зонами (функция prov)
6. Вывод результата или сообщение об ошибке

@note Начальная позиция (1,1) не выводится в результат

"""

zapret = zapret_zona()
move_high = high_level()
move_high = count_b(move_high)
move_low = low_level(move_high)
rez = move_low[1:]

rez_prov = prov(move_low,zapret)
if (rez_prov == 0):
    print("Вы попали в запретную зону!")
    sys.exit()

for i in rez:
    print(i)
