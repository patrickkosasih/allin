"""
app/app_timer.py

The app timer is used to schedule a function to be run in a time interval (e.g. run function `x` after 5 seconds).

Instead of running a new thread, The function call of timers remains synchronous to the main thread. This is done by
calling the `update_timers(dt)` function in the main loop of the app, which updates all existing timers by subtracting
their remaining time (`time_left`) by the delta time (dt) of the last tick. Once the remaining time has reached zero,
the scheduled function is called.
"""

from typing import Callable


timers = []


class Timer:
    def __init__(self, delay: float, func: Callable, args=()):
        self.time_left = delay
        self.func = func
        self.args = args

        timers.append(self)

    def update(self, dt: float):
        self.time_left -= dt

        if self.time_left <= 0:
            self.func(*self.args)
            timers.remove(self)


def update_timers(dt: float):
    for x in timers:
        x.update(dt)
