"""
app/app_timer.py

The app timer is used to schedule a function to be run in a time interval (e.g. run function `x` after 5 seconds).

Instead of running a new thread, The function call of timers remains synchronous to the main thread. This is done by
calling the `update_timers(dt)` function in the main loop of the app, which updates all existing timers by subtracting
their remaining time (`time_left`) by the delta time (dt) of the last tick. Once the remaining time has reached zero,
the scheduled function is called.
"""

from typing import Callable


class Timer:
    def __init__(self, delay: float, func: Callable, args=(), group: None or "TimerGroup" = None):
        self.time_left = delay
        self.func = func
        self.args = args

        self.group = group if group else default_group
        self.group.add(self)

    def update(self, dt: float):
        self.time_left -= dt

        if self.time_left <= 0:
            self.func(*self.args)
            self.group.remove(self)


class TimerGroup:
    def __init__(self):
        self.timers = []

    def new_timer(self, delay: float, func: Callable, args=()) -> Timer:
        return Timer(delay, func, args, group=self)

    def add(self, timer: Timer) -> None:
        if timer.group and timer.group is not self:
            timer.group.remove(timer)

        timer.group = self

        self.timers.append(timer)

    def remove(self, timer: Timer) -> None:
        self.timers.remove(timer)

    def update(self, dt: float) -> None:
        for x in self.timers:
            x.update(dt)


default_group = TimerGroup()
