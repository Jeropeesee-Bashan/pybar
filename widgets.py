import asyncio
import time
import sdbus
import pulsectl_asyncio

from abc import ABCMeta, abstractmethod
from collections.abc import (
    Iterable,
    Callable,
    AsyncIterator,
)
from typing import Optional
from contextlib import suppress

from upower import *


class Widget(metaclass=ABCMeta):
    @abstractmethod
    async def __aiter__(self) -> AsyncIterator[str]:
        pass


class Box(Widget, list):
    def __init__(
        self,
        children: Optional[Iterable[Widget]]=None,
        sep: str=''
    ):
        super(list, self).__init__()

        self._sep: str = sep
        self._queue = asyncio.Queue()

        if children is not None:
            self.extend(children)

    def append(self, widget: Widget, /):
        self._queue.put_nowait((0, len(self)))
        super().append(widget)

    def remove(self, widget: Widget, /):
        index = self.index(widget)
        self._queue.put_nowait((1, index))
        super().__delitem__(index)

    def insert(self, index: int, widget: Widget, /):
        self._queue.put_nowait((0, index))
        super().insert(index, widget)

    def pop(self, index: int=-1, /):
        self._queue.put_nowait((1, index))
        return super().pop(index)

    def extend(self, children: Iterable[Widget], /):
        for i in range(len(children)):
            self._queue.put_nowait((0, i))
        super().extend(children)

    def clear(self, /):
        for i in range(len(self) - 1, -1, -1):
            self._queue.put_nowait((1, i))
        super().clear()

    def __setitem__(self, index: int, widget: Widget, /):
        if index < 0:
            index = len(self) + index
        self._queue.put_nowait((1, index))
        self._queue.put_nowait((0, index))
        super().__setitem__(index, widget)

    def __delitem__(self, index: int, /):
        self._queue.put_nowait((1, index))
        super().__delitem__(index)

    async def __aiter__(self) -> AsyncIterator[str]:
        event = asyncio.Event()
        values: list[str] = []
        tasks: list[list[asyncio.Task]] = []

        async def update(index: int):
            async for value in self[index]:
                values[index] = value
                if all(v is not None for v in values):
                    event.set()

        async def process_queue(tg: asyncio.TaskGroup):
            while True:
                job, index = await self._queue.get()

                if job == 0:
                    task = tg.create_task(update(index))
                    if index >= len(tasks):
                        tasks.append([task])
                    else:
                        tasks[index].append(task)
                    values.insert(index, None)
                elif job == 1:
                    tasks[index][-1].cancel()
                    del values[index]
                elif job == 2:
                    break

                self._queue.task_done()

        async with asyncio.TaskGroup() as tg:
            queue_task = tg.create_task(process_queue(tg))
            while (values or not (
                tasks
                and all(all(t.done() for t in l) for l in tasks)
            )):
                await event.wait()
                await self._queue.join()
                try:
                    yield self._sep.join(values)
                except GeneratorExit:
                    for l in tasks:
                        for task in l:
                            task.cancel()
                    values.clear()
                    break
                event.clear()
            await self._queue.put((2, -1))


class Text(Widget):
    def __init__(
        self,
        value: str
    ):
        self._value = value.replace("%", "%%")

    async def __aiter__(self) -> AsyncIterator[str]:
        yield self._value


for letter, data in {
    "R": ("ColorSwap", None),
    "l": ("AlignLeft", None),
    "c": ("AlignCenter", None),
    "r": ("AlignRight", None),
    "O": ("Offset", "0"),
    "B": ("BColor", "-"),
    "F": ("FColor", "-"),
    "T": ("Font", "-"),
    "U": ("UColor", "-")
}.items():
    exec(f"""def __init__(
    self,
    child: Widget=None{"" if data[1] is None else ",\n    arg: str=\"{}\"".format(data[1])}
):{"" if data[1] is None else "\n    self._arg = arg"}
    if child is None:
        child = Text("")
    self._child: Box = Box([child])
    
async def __aiter__(self) -> AsyncIterator[str]:
    async for value in self._child:
        yield \"%{{{{{letter}{{0}}}}}}{{1}}\".format({"\"\"" if data[1] is None else "self._arg"}, value)""")

    def get_child(self) -> Widget:
        return self._child[0]

    def set_child(self, widget: Widget):
        self._child[0] = widget

    globals()[data[0]] = type(data[0], (Widget,), {
        "__init__": locals()["__init__"],
        "__aiter__": locals()["__aiter__"],
        "child": property(get_child, set_child)
    })


class Button(Widget):
    callbacks: list[Callable[[None], None]] = []
    used: dict[int, bool] = {}

    def __init__(
        self,
        child: Widget,
        callback: Callable[[None], None],
        button: str="1"
    ):
        self._button: str = button
        self._child = Box([child])
        try:
            index = Button.callbacks.index(callback)
        except ValueError:
            index = len(Button.callbacks)
            Button.callbacks.append(callback)
        self._id = index

    @property
    def child(self) -> Widget:
        return self._child[0]

    @child.setter
    def child(self, widget: Widget):
        self._child[0] = widget

    async def __aiter__(self) -> AsyncIterator[str]:
        async for value in self._child:
            yield "%{{A{0}:{1}:}}{2}%{{A}}".format(self._button,
                                                   self._id,
                                                   value)


class Clock(Widget):
    def __init__(
        self,
        show_secs: bool=False
    ):
        self._show_secs: bool = show_secs
        self._event = asyncio.Event()

    async def __aiter__(self) -> AsyncIterator[str]:
        async def sleep():
            delay = 1.0 if self._show_secs else 60.0 - float(tm.tm_sec)
            await asyncio.sleep(delay)
            self._event.set()

        self._event.set()
        while True:
            task = asyncio.create_task(sleep())
            await self._event.wait()
            if not task.done():
                task.cancel()

            with suppress(asyncio.CancelledError):
                await task

            tm = time.localtime()
            format = "%d.%m.%y %H:%M"
            if self._show_secs:
                format += ":%S"

            text = Text(time.strftime(format, tm))
            yield await anext(aiter(text))
            self._event.clear()

    def toggle(self):
        self._show_secs = not self._show_secs
        self._event.set()


class Battery(Widget):
    def __init__(
        self,
        dev: UPowerDevice,
        font_index: int=0
    ):
        self._dev = dev
        self._font_index = font_index

    async def __aiter__(self) -> AsyncIterator[str]:
        percentage = int(await self._dev.percentage)
        state = await self._dev.state
        type = await self._dev.type

        def level() -> int:
            if percentage <= 5:
                return 0
            elif percentage <= 25:
                return 1
            elif percentage <= 50:
                return 2
            elif percentage <= 75:
                return 3
            return 4

        def color() -> str:
            l = level()
            if l == 0:
                return "#ff0000"
            elif l == 1:
                return "#ef7d13"
            elif l == 2:
                return "#f7db00"
            elif l == 3:
                return "#a9f700"
            return "#25e817"

        def bat_icon() -> str:
            return chr(ord('\uf244') - level())

        def type_icon():
            if type == 2:
                if state in (1, 4):
                    return '\ue55b'
                else:
                    return '\uf1e6'
            elif type == 17:
                return '\uf025'
            return ''

        def result():
            return FColor(
                Box([
                    Box([
                        Font(
                            Box([
                                Text(bat_icon()),
                                Text(type_icon())
                            ]), str(self._font_index) if self._font_index > 0 else ''),
                        Font()
                    ]),
                    Text(str(percentage) + '%')
                ], ' '), color())

        yield await anext(aiter(result()))
    
        async for _, props, _ in self._dev.properties_changed:
            updated = False
            for prop, value in props.items():
                if prop == "Percentage":
                    percentage = int(value[1])
                    updated = True
                elif prop == "State":
                    state = int(value[1])
                    updated = True
            if updated:
                yield await anext(aiter(result()))


class BatteryBox(Widget):
    bus = sdbus.sd_bus_open_system()
    upower = UPower.new_proxy(UPOWER,
                              UPOWER_OBJECT,
                              bus)

    def __init__(self, font_index=0):
        self._font_index = font_index

    async def __aiter__(self) -> AsyncIterator[str]:
        batteries: dict[str, Battery] = {}
        box = Box(sep=' ')

        async def add_battery(path: str):
            dev = UPowerDevice.new_proxy(UPOWER, path, BatteryBox.bus)
            if await dev.type == 1:
                return
            bat = Battery(dev, self._font_index)
            batteries[path] = bat

            if len(box) > 0:
                box[-1] = box[-1][0]
            box.append(Box([bat, FColor()]))

        async def device_added():
            async for path in BatteryBox.upower.device_added:
                await add_battery(path)

        async def device_removed():
            async for path in BatteryBox.upower.device_removed:
                bat = batteries[path]
                if bat is box[-1][0]:
                    del box[-1]
                    if len(box) > 0:
                        box[-1] = Box([box[-1], FColor()])
                else:
                    box.remove(bat)

                del batteries[path]

        paths = await BatteryBox.upower.enumerate_devices()

        if not paths:
            return

        for path in await BatteryBox.upower.enumerate_devices():
            await add_battery(path)

        async with asyncio.TaskGroup() as tg:
            added_task = tg.create_task(device_added())
            removed_task = tg.create_task(device_removed())

            async for value in box:
                yield value


class Volume(Widget):
    def __init__(self,
        spawn_pavu: Optional[Callable[[None], None]]=None,
        font_index: int=0
    ):
        self._font_index: int = font_index
        self._spawn_pavu: Optional[Callable[[None], None]] = spawn_pavu
        self._color = "#1b998a"
        self._event = asyncio.Event()

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value
        self._event.set()

    async def __aiter__(self) -> AsyncIterator[str]:
        tasks = set()

        def volume_up():
            coro = pulse.volume_change_all_chans(sink, 0.01)
            tasks.add(asyncio.create_task(coro))

        def volume_down():
            coro = pulse.volume_change_all_chans(sink, -0.01)
            tasks.add(asyncio.create_task(coro))

        def result():
            volume = Box([
                FColor(
                    Box([
                        Box([
                            Font(Text('\uf028'), str(self._font_index) if self._font_index > 0 else ''),
                            Font()
                        ]),
                        Text(f"{round(sink.volume.value_flat * 100.0)}%")
            ], ' '), self._color), FColor()])

            pavu_button = volume
            if self._spawn_pavu is not None:
                pavu_button = Button(volume, self._spawn_pavu)

            volume_control = Button(
                Button(pavu_button, volume_up, "4"), volume_down, "5")

            return volume_control

        async def listen():
            nonlocal sink

            async for event in pulse.subscribe_events('sink'):
                sink = await pulse.sink_default_get()
                self._event.set()


        async with pulsectl_asyncio.PulseAsync("default-sink-volume") as pulse:
            try:
                sink = await pulse.sink_default_get()
            except:
                return

            self._event.set()
            task = asyncio.create_task(listen())
            while True:
                await self._event.wait()
                yield await anext(aiter(result()))
                self._event.clear()
                await asyncio.gather(*tasks)
                tasks.clear()
            await task
