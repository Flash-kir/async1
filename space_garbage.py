from curses_tools import draw_frame
import asyncio
from obstacles import Obstacle
from curses_tools import get_frame_size


obstacles = []


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    frame_rows, frame_columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(
        0,
        column,
        frame_rows,
        frame_columns,
    )
    obstacles.append(obstacle)

    while True:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        if row > rows_number:
            obstacles.remove(obstacle)
        if obstacle not in obstacles:
            return
        obstacle.row += speed
        row += speed
