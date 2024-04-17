import asyncio
import time
import curses
import random
import os
from itertools import cycle
from curses_tools import draw_frame
from curses_tools import get_frame_size
from curses_tools import read_controls


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(random.randint(10, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(random.randint(1, 8)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(random.randint(3, 15)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(random.randint(1, 8)):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row - 1 and 1 < column < max_column - 1:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, frames):
    last_frame = ''
    row_direction = col_direction = 0
    (col_max, row_max) = os.get_terminal_size(0)
    row = start_row
    col = start_column
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

        start_row += row_direction
        start_column += col_direction

        ship_height, ship_width = get_frame_size(frame)

        row = start_row - round(ship_height/2)
        col = start_column - round(ship_width/2)
        if row == 0 or row == row_max - ship_height:
            start_row -= row_direction
            row -= row_direction
        if col == 0 or col == col_max - ship_width:
            start_column -= col_direction
            col -= col_direction

        draw_frame(
            canvas,
            row,
            col,
            frame)
        last_frame = frame
        await asyncio.sleep(0)


def load_space_ship_frame(file_path):
    with open(file_path, "r") as my_file:
        file_contents = my_file.read()
    return file_contents


def draw(canvas):
    space_ship_frame_1 = load_space_ship_frame('frames/rocket_frame_1.txt')
    space_ship_frame_2 = load_space_ship_frame('frames/rocket_frame_2.txt')
    frames = [space_ship_frame_1, space_ship_frame_2]

    star_symbols = ['*', ':', '+', '.']
    (col_max, row_max) = os.get_terminal_size(0)
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)

    space_ship_corutine = animate_spaceship(
        canvas,
        round(row_max/2),
        round(col_max/2),
        frames
    )

    fire_corutine = fire(
        canvas,
        round(row_max/2),
        round(col_max/2)
    )

    while True:
        try:
            fire_corutine.send(None)
            canvas.refresh()
            time.sleep(0.1)
        except StopIteration:
            break

    coroutines = [space_ship_corutine]
    for a in range(200):
        star_row = random.randint(1, row_max - 2)
        star_col = random.randint(1, col_max - 2)
        star_symbol = random.choice(star_symbols)
        coroutines.append(
            blink(
                canvas,
                star_row,
                star_col,
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
