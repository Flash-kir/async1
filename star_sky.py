import asyncio
import time
import curses
import random
import os
from itertools import cycle
from curses_tools import draw_frame
from curses_tools import get_frame_size
from curses_tools import read_controls
from space_garbage import fly_garbage
from physics import update_speed
from space_garbage import obstacles
from explosion import explode
from game_scenario import get_garbage_delay_tics

coroutines = []
game_year = 1957


async def increase_game_years(canvas):
    (col_max, row_max) = os.get_terminal_size(0)
    global game_year
    while True:
        draw_frame(canvas, 0, 0, str(game_year) + ' ' + str(len(obstacles)))
        await sleep(range(6))
        game_year += 1


async def sleep(tics=1):
    for i in tics:
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(range(offset_tics[0]))

        canvas.addstr(row, column, symbol)
        await sleep(range(offset_tics[1]))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(range(offset_tics[2]))

        canvas.addstr(row, column, symbol)
        await sleep(range(offset_tics[3]))


async def game_over(canvas):
    with open('frames/game_over.txt', "r") as garbage_file:
        frame = garbage_file.read()

    (col_max, row_max) = os.get_terminal_size(0)
    word_height, word_width = get_frame_size(frame)

    row = row_max/2 - round(word_height/2)
    col = col_max/2 - round(word_width/2)

    while True:
        draw_frame(
            canvas,
            row,
            col,
            frame
        )
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, cols_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += cols_speed

    symbol = '-' if cols_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row - 1 and 1 < column < max_column - 1:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += cols_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles.remove(obstacle)
                await explode(canvas, row, column)
                return


async def animate_spaceship(canvas, start_row, start_column, frames):
    last_frame = ''
    row_direction = col_direction = 0
    (col_max, row_max) = os.get_terminal_size(0)
    row = start_row
    col = start_column
    row_speed = column_speed = 0
    for frame in cycle(frames):
        if last_frame:
            draw_frame(
                canvas,
                row,
                col,
                last_frame,
                negative=True
            )

        row_direction, col_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(
                                        row_speed,
                                        column_speed,
                                        row_direction,
                                        col_direction
                                    )

        start_row += row_speed
        start_column += column_speed

        ship_height, ship_width = get_frame_size(frame)

        row = start_row - round(ship_height/2)
        col = start_column - round(ship_width/2)

        if space_pressed and game_year >= 2020:
            coroutines.append(
                fire(
                    canvas,
                    row,
                    start_column,
                )
            )

        if row == 0 or row == row_max - ship_height:
            start_row -= row_speed
            row -= row_speed
        if col == 0 or col == col_max - ship_width:
            start_column -= column_speed
            col -= column_speed

        draw_frame(
            canvas,
            row,
            col,
            frame)
        last_frame = frame
        await asyncio.sleep(0)
        for obstacle in obstacles:
            if obstacle.has_collision(row, col, ship_height, ship_width):
                obstacles.remove(obstacle)
                await explode(canvas, row + ship_height/2, col + ship_width/2)
                draw_frame(
                    canvas,
                    row,
                    col,
                    frame,
                    negative=True
                )
                coroutines.append(game_over(canvas))
                return


def load_space_ship_frame(file_path):
    with open(file_path, "r") as my_file:
        file_contents = my_file.read()
    return file_contents


async def fill_orbit_with_garbage(canvas):
    garbage_frames_path = 'frames/garbage/'
    garbage_frame_names = os.listdir(garbage_frames_path)
    while True:
        random_frame = garbage_frames_path + random.choice(garbage_frame_names)
        (col_max, row_max) = os.get_terminal_size(0)
        with open(random_frame, "r") as garbage_file:
            frame = garbage_file.read()
        column = random.randint(1, col_max - 2)
        delay = get_garbage_delay_tics(game_year)
        if delay:
            coroutines.append(
                fly_garbage(canvas, column=column, garbage_frame=frame)
            )
        else:
            delay = 1
        await sleep(range(delay))


def draw(canvas):
    space_ship_frame_1 = load_space_ship_frame('frames/rocket_frame_1.txt')
    space_ship_frame_2 = load_space_ship_frame('frames/rocket_frame_2.txt')
    frames = [
        space_ship_frame_1,
        space_ship_frame_1,
        space_ship_frame_2,
        space_ship_frame_2,
    ]

    star_symbols = ['*', ':', '+', '.']
    (col_max, row_max) = os.get_terminal_size(0)
    canvas.nodelay(True)
    curses.curs_set(False)

    space_ship_corutine = animate_spaceship(
        canvas,
        round(row_max/2),
        round(col_max/2),
        frames
    )

    coroutines.append(increase_game_years(canvas))
    coroutines.append(space_ship_corutine)
    coroutines.append(fill_orbit_with_garbage(canvas))

    for a in range(200):
        star_row = random.randint(1, row_max - 2)
        star_col = random.randint(1, col_max - 2)
        star_symbol = random.choice(star_symbols)
        offset_tics = [
            random.randint(10, 20),
            random.randint(1, 8),
            random.randint(3, 15),
            random.randint(1, 8),
        ]
        coroutines.append(
            blink(
                canvas,
                star_row,
                star_col,
                offset_tics,
                symbol=star_symbol
            )
        )

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
