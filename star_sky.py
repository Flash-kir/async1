import asyncio
import time
import curses
import random
import os


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


def draw(canvas):
    star_symbols = ['*', ':', '+', '.']
    (col_max, row_max) = os.get_terminal_size(0)
    canvas.border()
    curses.curs_set(False)

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

    coroutines = []
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
