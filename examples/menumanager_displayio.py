# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import board
import busio
import displayio
import ulab.numpy as np
from adafruit_debouncer import Debouncer
from adafruit_displayio_ssd1306 import SSD1306
from digitalio import DigitalInOut, Pull

from relic_menumanager import *
from relic_menumanager.displayio import Displayio_Menu
from relic_menumanager.synthio import *

WIDTH = 128
HEIGHT = 64

displayio.release_displays()

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=64)


def item_title(item: Item) -> str:
    return type(item).__name__


menu = Displayio_Menu(
    WIDTH,
    HEIGHT,
    "displayio Menu",
    (
        Action(item_title, lambda: print("Hello World")),
        Group(
            "Simple Items",
            (
                Action("Return", lambda: menu.exit()),
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
                Action("Return", lambda: menu.exit()),
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

button_pins = (
    DigitalInOut(board.GP2),
    DigitalInOut(board.GP3),
    DigitalInOut(board.GP4),
    DigitalInOut(board.GP5),
)
buttons = []
for pin in button_pins:
    pin.switch_to_input(pull=Pull.UP)
    buttons.append(Debouncer(pin))
buttons = tuple(buttons)

while True:
    for button in buttons:
        button.update()

    if buttons[0].fell:
        if isinstance(menu.selected, Group):
            menu.previous()
        else:
            menu.decrement()
    if buttons[1].fell:
        if isinstance(menu.selected, Group):
            menu.next()
        else:
            menu.increment()
    if buttons[2].fell:
        if not menu.select():
            menu.exit()
    if buttons[3].fell:
        menu.exit()
