# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

from relic_menumanager import Menu, Action

menu = Menu(
    "Menu",
    (
        Action("Action 1", lambda: print("Hello World!")),
        Action("Action 2", lambda: print("Hello World, again!")),
    ),
)
menu.select()  # Prints "Hello World!" in REPL
menu.next()  # Navigate from "Action 1" to "Action 2"
menu.select()  # Prints "Hello World, again!" in REPL
