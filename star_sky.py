import asyncio
import time
import curses
import random
import os


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(5):
            await asyncio.sleep(0)


def draw(canvas):
    star_symbols = ['*', ':', '+', '.']
    (col_max, row_max) = os.get_terminal_size(0)
    canvas.border()
    curses.curs_set(False)
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
