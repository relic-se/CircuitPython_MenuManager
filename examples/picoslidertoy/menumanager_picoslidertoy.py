# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense
"""
Example for `picoslidertoy <https://github.com/todbot/picoslidertoy>`_ by @todbot.
"""

import board
import busio
import displayio
import ulab.numpy as np

from adafruit_displayio_ssd1306 import SSD1306
from touchslider import TouchSlider, TouchWheelRotary

from relic_menumanager import *
from relic_menumanager.synthio import *
from relic_menumanager.displayio import Menu as DisplayioMenu

WIDTH = 128
HEIGHT = 64

displayio.release_displays()

i2c = busio.I2C(scl=board.GP15, sda=board.GP14, frequency=1000000)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=64)


def item_title(item: Item) -> str:
    return type(item).__name__


menu = DisplayioMenu(
    WIDTH,
    HEIGHT,
    "picoslidertoy Menu",
    (
        Action(item_title, lambda: print("Hello World")),
        Group(
            "Simple Items",
            (
                Number(item_title),
                Bool(item_title),
                Time(item_title),
                List(item_title, ("ASDF", "QWER", "UIOP")),
                Char(item_title),
            ),
        ),
        Group(
            "Complex Items",
            (
                String(item_title, length=8),
                Waveform(
                    item_title,
                    (
                        (
                            "Sine",
                            lambda: np.array(
                                np.sin(np.linspace(0, 2 * np.pi, WIDTH, endpoint=False)) * 32767,
                                dtype=np.int16,
                            ),
                        ),
                        ("Saw", lambda: np.linspace(32767, -32767, num=WIDTH, dtype=np.int16)),
                        (
                            "Triangle",
                            lambda: np.concatenate(
                                (
                                    np.linspace(-32767, 32767, num=WIDTH // 2, dtype=np.int16),
                                    np.linspace(32767, -32767, num=WIDTH // 2, dtype=np.int16),
                                )
                            ),
                        ),
                        (
                            "Square",
                            lambda: np.concatenate(
                                (
                                    np.full(WIDTH // 2, 32767, dtype=np.int16),
                                    np.full(WIDTH // 2, -32767, dtype=np.int16),
                                )
                            ),
                        ),
                    ),
                ),
                AREnvelope(item_title),
                ADSREnvelope(item_title),
                LFO(item_title),
                Filter(item_title),
                Mix(item_title),
                Tune(item_title),
                Patch(item_title),
            ),
        ),
    ),
)

display.root_group = menu.group

wheelX = TouchWheelRotary((board.GP7, board.GP8, board.GP9))
wheelY = TouchWheelRotary((board.GP10, board.GP11, board.GP12), step_size=0.15)

wheelX.on_increment = lambda: menu.next()
wheelX.on_decrement = lambda: menu.previous()
wheelX.on_right_press = lambda: menu.select()
wheelX.on_left_press = lambda: menu.exit()

wheelY.on_increment = lambda: menu.increment()
wheelY.on_decrement = lambda: menu.decrement()
wheelY.on_right_press = lambda: menu.increment()
wheelY.on_left_press = lambda: menu.decrement()

faderC = TouchSlider((board.GP3, board.GP2, board.GP26))

while True:
    wheelX.update()
    wheelY.update()

    if (pos := faderC.pos) is not None:
        menu.value = 1 - pos
