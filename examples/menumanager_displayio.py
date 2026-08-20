# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import adafruit_debouncer
import adafruit_displayio_ssd1306
import board
import busio
import digitalio
import displayio
import ulab.numpy as np

import relic_menumanager
import relic_menumanager.displayio

WIDTH = 128
HEIGHT = 64

displayio.release_displays()

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)


def item_title(item: relic_menumanager.Item) -> str:
    return type(item).__name__


menu = relic_menumanager.displayio.Menu(
    WIDTH,
    HEIGHT,
    "displayio Menu",
    (
        relic_menumanager.Action(item_title, lambda: print("Hello World")),
        relic_menumanager.Group(
            "Simple Items",
            (
                relic_menumanager.Action("Return", lambda: menu.exit()),
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
                relic_menumanager.Action("Return", lambda: menu.exit()),
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

button_pins = (
    digitalio.DigitalInOut(board.GP2),
    digitalio.DigitalInOut(board.GP3),
    digitalio.DigitalInOut(board.GP4),
    digitalio.DigitalInOut(board.GP5),
)
buttons = []
for pin in button_pins:
    pin.direction = digitalio.Direction.INPUT
    buttons.append(adafruit_debouncer.Debouncer(pin))
buttons = tuple(buttons)

while True:
    for button in buttons:
        button.update()

    if buttons[0].fell:
        if isinstance(menu.selected, relic_menumanager.Group):
            menu.previous()
        else:
            menu.decrement()
    if buttons[1].fell:
        if isinstance(menu.selected, relic_menumanager.Group):
            menu.next()
        else:
            menu.increment()
    if buttons[2].fell:
        if not menu.select():
            menu.exit()
    if buttons[3].fell:
        menu.exit()
