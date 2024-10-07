#!/usr/bin/env python3

import sys
import asyncio

from shutil import which
from widgets import Widget, Button

import config


async def print_bar(bar: Widget, bar_in: asyncio.StreamWriter):
    async for value in bar:
        bar_in.write(value.encode())
        await bar_in.drain()
        print(value, flush=True, file=sys.stderr)


async def process_input(bar_out: asyncio.StreamReader):
    while True:
        line = await bar_out.readline()
        id = int(line.strip().decode())

        Button.callbacks[id]()


async def main() -> int:
    fonts = []
    for font in config.fonts:
        fonts.extend(("-f", font))

    lemonbar_path = which("lemonbar")
    if lemonbar_path is None:
        print("lemonbar isn't found!", file=sys.stderr)
        return 1

    lemonbar = await asyncio.subprocess.create_subprocess_exec(
        lemonbar_path,
        "-g", "1920x30+0+0", *fonts,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)

    input_task = asyncio.create_task(print_bar(config.bar, lemonbar.stdin))
    output_task = asyncio.create_task(process_input(lemonbar.stdout))

    await asyncio.gather(input_task, output_task)
    await lemonbar.wait()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
