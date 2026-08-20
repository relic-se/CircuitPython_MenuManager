# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense
"""
Example for `pico_synth_sandbox Rev2
<https://github.com/relic-se/pico_synth_sandbox-hardware/releases/tag/Rev2>`_ by @relic-se.
"""

import adafruit_debouncer
import board
import digitalio
import rotaryio
import ulab.numpy as np
from adafruit_character_lcd import character_lcd

import relic_menumanager.character_lcd

lcd_rs = digitalio.DigitalInOut(board.GP7)
lcd_en = digitalio.DigitalInOut(board.GP6)
lcd_d4 = digitalio.DigitalInOut(board.GP22)
lcd_d5 = digitalio.DigitalInOut(board.GP26)
lcd_d6 = digitalio.DigitalInOut(board.GP27)
lcd_d7 = digitalio.DigitalInOut(board.GP28)

COLUMNS = 16
ROWS = 2

lcd = character_lcd.Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, COLUMNS, ROWS
)


def item_title(item: relic_menumanager.Item) -> str:
    return type(item).__name__


menu = relic_menumanager.character_lcd.Menu(
    lcd,
    COLUMNS,
    ROWS,
    "Menu",
    (
        relic_menumanager.Action(item_title, lambda: print("Hello World")),
        relic_menumanager.Group(
            "Simple",
            (
                relic_menumanager.Number(item_title),
                relic_menumanager.Bool(item_title),
                relic_menumanager.Time(item_title),
                relic_menumanager.List(item_title, ("ASDF", "QWER", "UIOP")),
                relic_menumanager.Char(item_title),
            ),
        ),
        relic_menumanager.Group(
            "Complex",
            (
                relic_menumanager.String(item_title, length=COLUMNS),
                relic_menumanager.Waveform(
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


button_pins = (
    digitalio.DigitalInOut(board.GP13),
    digitalio.DigitalInOut(board.GP18),
)
buttons = []
for pin in button_pins:
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    buttons.append(adafruit_debouncer.Debouncer(pin))
buttons = tuple(buttons)

encoders = (
    rotaryio.IncrementalEncoder(board.GP12, board.GP11),
    rotaryio.IncrementalEncoder(board.GP17, board.GP16),
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
            elif isinstance(menu.selected.current_item, relic_menumanager.Group):
                menu.select()

        encoder_position[i] = position
