# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense
"""
Example for `pico_synth_sandbox Rev2
<https://github.com/relic-se/pico_synth_sandbox-hardware/releases/tag/Rev2>`_ by @relic-se.
"""

import board
from digitalio import DigitalInOut, Pull
from rotaryio import IncrementalEncoder
import ulab.numpy as np

from adafruit_debouncer import Debouncer
from adafruit_character_lcd.character_lcd import Character_LCD_Mono

from relic_menumanager import *
from relic_menumanager.synthio import *
from relic_menumanager.character_lcd import Menu as LCDMenu

lcd_rs = DigitalInOut(board.GP7)
lcd_en = DigitalInOut(board.GP6)
lcd_d4 = DigitalInOut(board.GP22)
lcd_d5 = DigitalInOut(board.GP26)
lcd_d6 = DigitalInOut(board.GP27)
lcd_d7 = DigitalInOut(board.GP28)

COLUMNS = 16
ROWS = 2

lcd = Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, COLUMNS, ROWS
)


def item_title(item: Item) -> str:
    return type(item).__name__


menu = LCDMenu(
    lcd,
    COLUMNS,
    ROWS,
    "Menu",
    (
        Action(item_title, lambda: print("Hello World")),
        Group(
            "Simple",
            (
                Number(item_title),
                Bool(item_title),
                Time(item_title),
                List(item_title, ("ASDF", "QWER", "UIOP")),
                Char(item_title),
            ),
        ),
        Group(
            "Complex",
            (
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
    DigitalInOut(board.GP13),
    DigitalInOut(board.GP18),
)
buttons = []
for pin in button_pins:
    pin.switch_to_input(pull=Pull.UP)
    buttons.append(Debouncer(pin))
buttons = tuple(buttons)

encoders = (
    IncrementalEncoder(board.GP12, board.GP11),
    IncrementalEncoder(board.GP17, board.GP16),
)
encoder_position = []
for encoder in encoders:
    encoder_position.append(encoder.position)

while True:
    for i, encoder in enumerate(encoders):
        position = encoder.position
        buttons[i].update()

        if position > encoder_position[i]:
            for j in range(position - encoder_position[i]):
                menu.next() if not i else menu.increment()
        elif position < encoder_position[i]:
            for j in range(encoder_position[i] - position):
                menu.previous() if not i else menu.decrement()
        if buttons[i].rose:
            if not i:
                menu.exit()
            elif isinstance(menu.selected.current_item, Group):
                menu.select()

        encoder_position[i] = position
