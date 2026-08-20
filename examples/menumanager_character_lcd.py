# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import board
import ulab.numpy as np
from adafruit_character_lcd.character_lcd import Character_LCD_Mono
from adafruit_debouncer import Debouncer
from digitalio import DigitalInOut, Pull

from relic_menumanager import *
from relic_menumanager.character_lcd import Character_LCD_Menu
from relic_menumanager.synthio import *

lcd_rs = DigitalInOut(board.GP0)
lcd_en = DigitalInOut(board.GP1)
lcd_d7 = DigitalInOut(board.GP2)
lcd_d6 = DigitalInOut(board.GP3)
lcd_d5 = DigitalInOut(board.GP4)
lcd_d4 = DigitalInOut(board.GP5)
lcd_backlight = DigitalInOut(board.GP6)

COLUMNS = 16
ROWS = 2

lcd = Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, COLUMNS, ROWS, lcd_backlight
)


def item_title(item: Item) -> str:
    return type(item).__name__


menu = Character_LCD_Menu(
    lcd,
    COLUMNS,
    ROWS,
    "CharLCD Menu",
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
                String(item_title, length=COLUMNS),
                Waveform(
                    item_title,
                    (
                        (
                            "Sine",
                            lambda: np.array(
                                np.sin(np.linspace(0, 2 * np.pi, COLUMNS, endpoint=False)) * 32767,
                                dtype=np.int16,
                            ),
                        ),
                        ("Saw", lambda: np.linspace(32767, -32767, num=COLUMNS, dtype=np.int16)),
                        (
                            "Triangle",
                            lambda: np.concatenate(
                                (
                                    np.linspace(-32767, 32767, num=COLUMNS // 2, dtype=np.int16),
                                    np.linspace(32767, -32767, num=COLUMNS // 2, dtype=np.int16),
                                )
                            ),
                        ),
                        (
                            "Square",
                            lambda: np.concatenate(
                                (
                                    np.full(COLUMNS // 2, 32767, dtype=np.int16),
                                    np.full(COLUMNS // 2, -32767, dtype=np.int16),
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
