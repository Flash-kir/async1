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
    star1 = blink(canvas, 5, 20)
    star2 = blink(canvas, 6, 21)
    star3 = blink(canvas, 7, 22)
    star4 = blink(canvas, 8, 23)
    star5 = blink(canvas, 9, 24)

    coroutines = [star1, star2, star3, star4, star5]

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.5)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
