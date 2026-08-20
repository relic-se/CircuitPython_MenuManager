# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense
"""
Example for `picoslidertoy <https://github.com/todbot/picoslidertoy>`_ by @todbot.
"""

import adafruit_displayio_ssd1306
import board
import busio
import displayio
import touchslider
import ulab.numpy as np

import relic_menumanager
import relic_menumanager.displayio

WIDTH = 128
HEIGHT = 64

displayio.release_displays()

i2c = busio.I2C(scl=board.GP15, sda=board.GP14, frequency=1000000)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)


def item_title(item: relic_menumanager.Item) -> str:
    return type(item).__name__


menu = relic_menumanager.displayio.Menu(
    WIDTH,
    HEIGHT,
    "picoslidertoy Menu",
    (
        relic_menumanager.Action(item_title, lambda: print("Hello World")),
        relic_menumanager.Group(
            "Simple Items",
            (
                relic_menumanager.Number(item_title),
                relic_menumanager.Bool(item_title),
                relic_menumanager.Time(item_title),
                relic_menumanager.List(item_title, ("ASDF", "QWER", "UIOP")),
                relic_menumanager.Char(item_title),
            ),
        ),
        relic_menumanager.Group(
            "Complex Items",
            (
                relic_menumanager.String(item_title, length=8),
                relic_menumanager.Waveform(
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
                relic_menumanager.AREnvelope(item_title),
                relic_menumanager.ADSREnvelope(item_title),
                relic_menumanager.LFO(item_title),
                relic_menumanager.Filter(item_title),
                relic_menumanager.Mix(item_title),
                relic_menumanager.Tune(item_title),
                relic_menumanager.Patch(item_title),
            ),
        ),
    ),
)

display.root_group = menu.group

wheelX = touchslider.TouchWheelRotary((board.GP7, board.GP8, board.GP9))
wheelY = touchslider.TouchWheelRotary((board.GP10, board.GP11, board.GP12), step_size=0.15)

wheelX.on_increment = lambda: menu.next()
wheelX.on_decrement = lambda: menu.previous()
wheelX.on_right_press = lambda: menu.select()
wheelX.on_left_press = lambda: menu.exit()

wheelY.on_increment = lambda: menu.increment()
wheelY.on_decrement = lambda: menu.decrement()
wheelY.on_right_press = lambda: menu.increment()
wheelY.on_left_press = lambda: menu.decrement()

faderC = touchslider.TouchSlider((board.GP3, board.GP2, board.GP26))

while True:
    wheelX.update()
    wheelY.update()

    if (pos := faderC.pos) is not None:
        menu.value = 1 - pos
