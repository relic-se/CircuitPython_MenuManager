# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: MIT

import ulab.numpy as np

from relic_menumanager import *

try:
    from typing import Callable
except ImportError:
    pass


class WaveformList(List):
    def __init__(
        self,
        title: str | Callable[[Item], str],
        items: tuple[str, Callable[[], np.ndarray]],
        on_update: Callable[[int, Item], None] = None,
    ):
        super().__init__(title, items, on_update=on_update)

    @property
    def label(self) -> str:
        return self._items[self.value][0]

    @property
    def data(self) -> np.ndarray:
        return self._items[self.value][1]()

    @data.setter
    def data(self, value: int) -> None:
        self._value = value


class Waveform(Group):
    waveform: WaveformList = None
    loop_start: Percentage = None
    loop_end: Percentage = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        items: tuple[str, Callable[[], np.ndarray]],
        on_waveform_update: Callable[[int, Item], None] = None,
        on_loop_start_update: Callable[[float, Item], None] = None,
        on_loop_end_update: Callable[[float, Item], None] = None,
    ):
        self.waveform = WaveformList(
            "Type",
            items,
            on_update=on_waveform_update,
        )

        self.loop_start = Percentage(
            "Loop Start",
            default=0.0,
        )
        self.loop_start.on_update = self._update_loop_start
        self._on_loop_start_update = on_loop_start_update

        self.loop_end = Percentage(
            "Loop End",
            default=1.0,
        )
        self.loop_end.on_update = self._update_loop_end
        self._on_loop_end_update = on_loop_end_update

        super().__init__(title, (self.waveform, self.loop_start, self.loop_end))

    def _update_loop_start(self, value: float, item: Item) -> None:
        if value > self.loop_end.value:
            self.loop_end.value = value
        if callable(self._on_loop_start_update):
            self._on_loop_start_update(value, item)

    def _update_loop_end(self, value: float, item: Item) -> None:
        if value < self.loop_start.value:
            self.loop_start.value = value
        if callable(self._on_loop_end_update):
            self._on_loop_end_update(value, item)


class AREnvelope(Group):
    attack_time: Time = None
    sustain_level: Number = None
    release_time: Time = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        on_attack_time_update: Callable[[float, Item], None] = None,
        on_sustain_level_update: Callable[[float, Item], None] = None,
        on_release_time_update: Callable[[float, Item], None] = None,
    ):
        self.attack_time = Time(
            title="Attack Time",
            on_update=on_attack_time_update,
        )
        self.sustain_level = Percentage(
            title="Sustain Level",
            step=0.05,
            on_update=on_sustain_level_update,
        )
        self.release_time = Time(
            title="Release Time",
            on_update=on_release_time_update,
        )
        super().__init__(title, (self.attack_time, self.sustain_level, self.release_time))


class ADSREnvelope(Group):
    attack_time: Time = None
    attack_level: Number = None
    decay_time: Time = None
    sustain_level: Number = None
    release_time: Time = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        on_attack_time_update: Callable[[float, Item], None] = None,
        on_attack_level_update: Callable[[float, Item], None] = None,
        on_decay_time_update: Callable[[float, Item], None] = None,
        on_sustain_level_update: Callable[[float, Item], None] = None,
        on_release_time_update: Callable[[float, Item], None] = None,
    ):
        self.attack_time = Time("Attack Time", on_update=on_attack_time_update)
        self.attack_level = Percentage(
            "Attack Level", default=1.0, step=0.05, on_update=on_attack_level_update
        )
        self.decay_time = Time("Decay Time", on_update=on_decay_time_update)
        self.sustain_level = Percentage(
            "Sustain Level", default=0.75, step=0.05, on_update=on_sustain_level_update
        )
        self.release_time = Time("Release Time", on_update=on_release_time_update)
        super().__init__(
            title,
            (
                self.attack_time,
                self.attack_level,
                self.decay_time,
                self.sustain_level,
                self.release_time,
            ),
        )


class LFO(Group):
    depth: Number = None
    rate: Number = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        on_depth_update: Callable[[float, Item], None] = None,
        on_rate_update: Callable[[float, Item], None] = None,
        on_delay_update: Callable[[float, Item], None] = None,
    ):
        self.depth = Number(
            title="Depth",
            step=0.01,
            maximum=0.5,
            smoothing=2.0,
            decimals=3,
            on_update=on_depth_update,
        )
        self.rate = Number(
            title="Rate",
            step=0.01,
            maximum=32.0,
            smoothing=2.0,
            append="hz",
            on_update=on_rate_update,
        )
        self.delay = Time(
            "Delay",
            step=0.05,
            minimum=0.0,
            maximum=2.0,
            on_update=on_delay_update,
        )
        super().__init__(title, (self.depth, self.rate, self.delay))


class Filter(Group):
    type: List = None
    frequency: Number = None
    resonance: Number = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        min_frequency: float = 0.0,
        max_frequency: float = 20000.0,
        min_resonance: float = 0.7071067811865475,
        max_resonance: float = 2.0,
        on_type_update: Callable[[int, Item], None] = None,
        on_frequency_update: Callable[[float, Item], None] = None,
        on_resonance_update: Callable[[float, Item], None] = None,
    ):
        self.type = List(
            title="Type",
            items=("Low Pass", "High Pass", "Band Pass"),
            on_update=on_type_update,
        )
        self.frequency = Number(
            title="Frequency",
            default=1.0,
            step=0.01,
            minimum=min_frequency,
            maximum=max_frequency,
            smoothing=3.0,
            decimals=0,
            append="hz",
            on_update=on_frequency_update,
        )
        self.resonance = Number(
            title="Resonance",
            default=0.0,
            step=0.01,
            minimum=min_resonance,
            maximum=max_resonance,
            smoothing=2.0,
            decimals=3,
            on_update=on_resonance_update,
        )
        super().__init__(
            title,
            (
                self.type,
                self.frequency,
                self.resonance,
            ),
        )


class Mix(Group):
    level: Number = None
    pan: Number = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        on_level_update: Callable[[float, Item], None] = None,
        on_pan_update: Callable[[float, Item], None] = None,
    ):
        self.level = Percentage(
            "Level",
            default=1.0,
            step=0.025,
            on_update=on_level_update,
        )
        self.pan = Number(
            "Pan",
            step=0.1,
            minimum=-1.0,
            on_update=on_pan_update,
        )
        super().__init__(
            title,
            (
                self.level,
                self.pan,
            ),
        )


class Tune(Group):
    coarse: Number = None
    fine: Number = None
    glide: Time = None
    bend: Number = None
    slew: Number = None
    slew_time: Time = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        on_coarse_update: Callable[[float, Item], None] = None,
        on_fine_update: Callable[[float, Item], None] = None,
        on_glide_update: Callable[[float, Item], None] = None,
        on_bend_update: Callable[[float, Item], None] = None,
        on_slew_update: Callable[[float, Item], None] = None,
        on_slew_time_update: Callable[[float, Item], None] = None,
    ):
        self.coarse = Number(
            "Coarse",
            default=0,
            step=1,
            minimum=-36,
            maximum=36,
            show_sign=True,
            decimals=0,
        )
        if callable(on_coarse_update):
            self.coarse.on_update = lambda value, item: on_coarse_update(value / 12, item)

        self.fine = Number(
            "Fine",
            default=0,
            step=5,
            minimum=-100,
            maximum=100,
            show_sign=True,
            decimals=3,
            append=" cents",
            on_update=on_fine_update,
        )
        if callable(on_fine_update):
            self.fine.on_update = lambda value, item: on_fine_update(value / 100, item)

        self.glide = Time(
            "Glide",
            step=0.05,
            minimum=0.0,
            maximum=2.0,
            on_update=on_glide_update,
        )

        self.bend = Number(
            "Bend",
            default=0,
            step=1,
            minimum=-24,
            maximum=24,
            show_sign=True,
            decimals=0,
        )
        if callable(on_bend_update):
            self.bend.on_update = lambda value, item: on_bend_update(value / 12, item)

        self.slew = Number(
            "Slew",
            default=0,
            step=10,
            minimum=-2400,
            maximum=2400,
            show_sign=True,
            decimals=0,
            append=" cents",
        )
        if callable(on_slew_update):
            self.slew.on_update = lambda value, item: on_slew_update(value / 1200, item)

        self.slew_time = Time(
            "Slew Time",
            step=0.05,
            minimum=0.0,
            maximum=2.0,
            on_update=on_slew_time_update,
        )

        super().__init__(
            title,
            (
                self.coarse,
                self.fine,
                self.glide,
                self.bend,
                self.slew,
                self.slew_time,
            ),
        )


class Patch(Group):
    patch: Number = None
    name: String = None

    def __init__(
        self,
        title: str | Callable[[Item], str],
        count: int = 16,
        on_patch_update: Callable[[int, Item], None] = None,
        on_name_update: Callable[[str, Item], None] = None,
    ):
        self.patch = Number(
            title="Patch",
            step=1,
            default=0,
            maximum=count - 1,
            loop=True,
            decimals=0,
            on_update=on_patch_update,
        )
        self.name = String(
            title="Name",
            on_update=on_name_update,
        )
        super().__init__(title, (self.patch, self.name))


class Sequence(Group):
    def __init__(
        self,
        title: str | Callable[[Item], str],
        length: int = 16,
        on_update: Callable[[tuple, Item], None] = None,
    ):
        self._length = length
        super().__init__(
            title,
            tuple(
                [
                    Bool(
                        title=str(i + 1),
                        labels=(" ", "*"),
                        on_update=self._handle_update,
                    )
                    for i in range(length)
                ]
            ),
        )
        self.on_update = on_update

    def _handle_update(self, value=None, item=None) -> None:
        if callable(self.on_update):
            self.on_update(self.value, self)

    def do_update(self) -> None:
        self._handle_update()

    @property
    def value(self) -> tuple:
        return tuple([i.value for i in self._items])

    @value.setter
    def value(self, value: tuple) -> None:
        if type(value) is tuple:
            for i in range(min(len(value), self._length)):
                self._items[i].value = bool(value[i])
            self.do_update()

    @property
    def label(self) -> str:
        return "".join([i.label for i in self._items])

    @property
    def length(self) -> int:
        return self._length

    @length.setter
    def length(self, value: int) -> None:
        self._length = max(value, 1)
        if len(self._items) > self._length:
            self._items = self._items[: self._length]
        elif len(self._items) < self._length:
            for i in range(len(self._items), self._length):
                self._items.append(
                    Bool(
                        title=str(i + 1),
                        labels=(" ", "*"),
                        on_update=self._handle_update,
                    )
                )
        self._index = self._index % self._length
