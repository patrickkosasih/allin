"""
app/app_timer.py

The app timer module is used to schedule function calls.

Instead of running a new thread, The scheduling of function calls are done synchronously to the main thread. This is
done by updating the timer groups (the global `default_group` and other local timer groups) every game tick.
"""

from typing import Callable


class Timer:
    """
    The Timer class is used to schedule a function to be called in a set time interval.

    Every tick, the `time_left` attribute of timers are subtracted by the delta time of that tick. Once they reach zero,
    the function is run.
    """

    def __init__(self, delay: float, func: Callable, args=(), group: None or "TimerGroup" = None):
        """
        Params:

        :param delay: How many seconds until the function is called.
        :param func: The function to run.
        :param args: The arguments to pass in the run function.
        :param group: Which timer group to put the timer in. If set to None then the timer would be automatically placed
                      in the global `default_group`, updated in the game's main loop.
        """

        self.time_left = delay
        self.func = func
        self.args = args

        self.group = group if group else default_group
        self.group.add(self)

    def update(self, dt: float):
        """
        Subtract the time left by the current tick's delta time. Once the time left reaches zero, the function is run
        and the timer is removed from its group.
        """

        self.time_left -= dt

        if self.time_left <= 0:
            self.func(*self.args)
            self.group.remove(self)


class Sequence:
    """
    The Sequence class is used to create a sequence of function calls with set delays between them.
    """

    def __init__(self, sequence_list: list[Callable or int or float], group: None or "TimerGroup" = None):
        """
        Params:

        :param sequence_list: A list of functions and numbers (int or float) that make up the sequence of functions and
                              delays to be run. The sequencer iterates through the elements of the sequence list one by
                              one. A number represent the delay between functions in seconds.

        :param group: Which timer group to put the timer in. If set to None then the timer would be automatically placed
                      in the global `default_group`, updated in the game's main loop.
        """

        for x in sequence_list:
            if not (callable(x) or type(x) is int or type(x) is float):
                raise ValueError(f"invalid item in sequence list (must be either a function or a number): {x}")

        self.sequence_list = sequence_list
        self.group = group if group else default_group
        self.group.add(self)

        self.sequence_iter = iter(self.sequence_list)
        self.next_action_delay = 0.0

    def update(self, dt):
        """
        Subtract the `next_action_delay` (time left until the next action) by the current tick's delta time. Once the
        next action delay reaches zero, then the iterator goes to the next item on the list. If the item is a function,
        it is called, and if it's a number, it is added to the next action delay.

        Note that if there are more than one functions in a row in the sequence list, they are run on the same tick.
        """

        self.next_action_delay -= dt

        while self.next_action_delay <= 0:
            try:
                action: Callable or int or float
                action = next(self.sequence_iter)
            except StopIteration:
                self.group.remove(self)
                break

            if callable(action):
                action()
            else:
                self.next_action_delay += action


class TimerGroup:
    """
    Timer groups are used to group timers and sequences. Timers and sequences can be added, removed, and updated in the
    timer group altogether, and once a timer or sequence is finished running, they are removed from the group (by the
    timers and sequences themselves).
    """

    def __init__(self):
        self.timers: list[Timer or Sequence] = []

    def new_timer(self, delay: float, func: Callable, args=()) -> Timer:
        return Timer(delay, func, args, group=self)

    def add(self, timer: Timer or Sequence) -> None:
        """
        Add a timer or sequence to the timer group. Each timer/sequence can only be bound to one anim group, so if the
        timer/sequence is already in another group, then that timer/sequence is removed from its previous group.
        """

        if timer.group and timer.group is not self:
            timer.group.remove(timer)

        timer.group = self

        self.timers.append(timer)

    def remove(self, timer: Timer or Sequence) -> None:
        """
        Remove a timer or sequence from the timer group.
        """
        self.timers.remove(timer)

    def update(self, dt: float) -> None:
        """
        Update all the timers and sequences in the timer group.
        """
        for x in self.timers:
            x.update(dt)


default_group = TimerGroup()
