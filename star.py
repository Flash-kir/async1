import asyncio
import time
import curses


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    star = blink(canvas, 5, 20)
    while True:
        star.send(None)
        canvas.refresh()
        time.sleep(0.5)
        star.send(None)
        canvas.refresh()
        time.sleep(0.5)
        star.send(None)
        canvas.refresh()
        time.sleep(0.5)
        star.send(None)
        canvas.refresh()
        time.sleep(0.5)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
