from typing import T

import pygame

from app.shared import *
from app.widgets.basic.button import CircularButton
from app.widgets.widget import Widget, WidgetComponent


DEFAULT_BASE_COLOR = (150, 150, 150, 111)
DEFAULT_BUTTON_COLOR = (111, 111, 111, 200)
DEFAULT_LABEL_COLOR = (255, 255, 255)


class NumberPicker(Widget):
    """
    The number picker is a widget that enables the user to adjust/input a numerical value by clicking the minus and
    plus buttons.
    """

    def __init__(self, parent, *rect_args,
                 min_value=1, max_value=10, default_value=1, step=1,
                 base_color=DEFAULT_BASE_COLOR, button_color=DEFAULT_BUTTON_COLOR, label_color=DEFAULT_LABEL_COLOR,
                 format_func: Callable[[int or float], str] = str,
                 call_on_change: Callable[[], None] = lambda: None):

        """
        Parameters:

        :param parent: The parent scene/widget.
        :param rect_args: AutoRect arguments for the widget's positioning.

        :param min_value: The number picker's minimum value.
        :param max_value: The number picker's maximum value.
        :param default_value: The number picker's default value on its creation.
        :param step: The increment/decrement of the number picker when clicking the plus/minus button.

        :param base_color: The number picker's base/background color
        :param button_color: The plus and minus buttons' color.
        :param label_color: The number label's color.

        :param format_func: A function that converts the integer or float value of the number picker into a string that
                            is shown in the number picker's label.
        :param call_on_change: A function that is called everytime the value of the number picker changes.
        """

        super().__init__(parent, *rect_args)

        self._value = default_value

        self._min_value = min_value
        self._max_value = max_value
        self._step = step

        self._base_color = base_color
        self._button_color = button_color
        self._label_color = label_color

        self.format_func = format_func
        self.call_on_change = call_on_change

        """
        Components
        """
        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        draw_rounded_rect(self.base.image, self.base.rect, base_color)

        self.label = WidgetComponent(self, 0, 0, 100, 75, "%", "ctr", "ctr")

        self.update_label()

        self.minus_button = CircularButton(self, 0, 0, 50, "%", "ml", "ml",
                                           icon=load_image("assets/sprites/misc/minus.png"), icon_size=0.9,
                                           color=button_color, command=self.minus_click)

        self.plus_button = CircularButton(self, 0, 0, 50, "%", "mr", "mr",
                                          icon=load_image("assets/sprites/misc/plus.png"), icon_size=0.9,
                                          color=button_color, command=self.plus_click)

    def update_label(self):
        self.label.image = FontSave.get_font(4).render(self.format_func(self._value), True, self._label_color)
        self.label.set_pos(0, 0)

    def minus_click(self):
        if (new_val := self.value - self._step) >= self._min_value:
            self.value = new_val
            self.call_on_change()

    def plus_click(self):
        if (new_val := self.value + self._step) <= self._max_value:
            self.value = new_val
            self.call_on_change()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.update_label()


class ItemPicker(NumberPicker):
    """
    The item picker is an extension of the number picker that enables the user pick something from a list of items
    instead of picking a number between a number range. The said item can be of any data type, from strings, tuples,
    numbers, class instances, and more.
    """

    def __init__(self, parent, *rect_args,
                 items: list[T], default_index: int = 0,
                 format_func: Callable[[T], str] = str,
                 **kwargs):

        self._items = items

        super().__init__(parent, *rect_args,
                         min_value=0, max_value=len(items), default_value=default_index, step=1,
                         format_func=format_func, **kwargs)

    def update_label(self):
        self.label.image = FontSave.get_font(4).render(self.format_func(self.selected_item), True, self._label_color)
        self.label.set_pos(0, 0)

    def plus_click(self):
        self._value += 1
        self._value %= len(self._items)
        self.call_on_change()
        self.update_label()

    def minus_click(self):
        self._value -= 1
        self._value %= len(self._items)
        self.call_on_change()
        self.update_label()

    @property
    def selected_item(self):
        return self._items[self._value]

    @selected_item.setter
    def selected_item(self, value):
        if value in self._items:
            self._value = self._items.index(value)
            self.update_label()
        else:
            raise ValueError(f"the given item does not exist in the items list: {value}")
