# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: Unlicense

import relic_menumanager

menu = relic_menumanager.Menu(
    "Menu",
    (
        relic_menumanager.Action("Action 1", lambda: print("Hello World!")),
        relic_menumanager.Action("Action 2", lambda: print("Hello World, again!")),
    ),
)
menu.select()  # Prints "Hello World!" in REPL
menu.next()  # Navigate from "Action 1" to "Action 2"
menu.select()  # Prints "Hello World, again!" in REPL
