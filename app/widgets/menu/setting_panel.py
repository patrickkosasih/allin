from typing import Type

from app.scenes.scene import Scene
from app.shared import *
from app.widgets.basic.number_picker import NumberPicker, ItemPicker
from app.widgets.basic.slider import Slider
from app.widgets.basic.toggle_switch import ToggleSwitch
from app.widgets.widget import Widget, WidgetComponent
from app.widgets.basic.panel import Panel


DEFAULT_ENTRY_BG_COLOR = (20, 20, 20, 128)
DEFAULT_ENTRY_FG_COLOR = (255, 255, 255)


class SettingEntry(Widget):
    """
    Setting fields are elements of the setting panel which has a representing text and an input widget.
    """

    # Widget types
    NO_WIDGET = 0
    NUMBER_PICKER = 1
    ITEM_PICKER = 2
    SLIDER = 3
    TOGGLE_SWITCH = 4

    def __init__(self, parent: "SettingPanel", *rect_args,
                 entry_label_text: str = "", horizontal_margin=2,
                 entry_base_color=DEFAULT_ENTRY_BG_COLOR,
                 entry_label_scale=0.6,
                 entry_label_color=DEFAULT_ENTRY_FG_COLOR):

        super().__init__(parent, *rect_args)

        self.horizontal_margin = horizontal_margin

        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        draw_rounded_rect(self.base.image, self.base.rect, color=entry_base_color)

        self.label = WidgetComponent(self, horizontal_margin, 0, 50, 100, "%", "ml", "ml")
        self.label.image = (FontSave.get_font(self.rect.height * entry_label_scale, "px").
                            render(entry_label_text, True, entry_label_color))

        self.input_widget: None or NumberPicker or ItemPicker or Slider or ToggleSwitch
        self.input_widget = None

    def set_input_widget(self, widget_type: int, **widget_kwargs):
        if self.input_widget:
            del self.input_widget

        match widget_type:
            case SettingEntry.NO_WIDGET:
                self.input_widget = None

            case SettingEntry.NUMBER_PICKER:
                self.input_widget = NumberPicker(self, -self.horizontal_margin, 0, 25, 75, "%", "mr", "mr",
                                                 **widget_kwargs)

            case SettingEntry.ITEM_PICKER:
                self.input_widget = ItemPicker(self, -self.horizontal_margin, 0, 30, 75, "%", "mr", "mr",
                                               **widget_kwargs)

            case SettingEntry.SLIDER:
                self.input_widget = Slider(self, -self.horizontal_margin, 0, 50, 75, "%", "mr", "mr",
                                           **widget_kwargs)

            case SettingEntry.TOGGLE_SWITCH:
                self.input_widget = ToggleSwitch(self, -self.horizontal_margin, 0, 100, 50, ("%", "%h"), "mr", "mr",
                                                 **widget_kwargs)

            case _:
                raise ValueError(f"invalid widget type code: {widget_type}")

    def get_entry_data(self):
        if type(self.input_widget) is NumberPicker or type(self.input_widget) is ItemPicker:
            return self.input_widget.value
        elif type(self.input_widget) is Slider:
            return self.input_widget.current_value
        elif type(self.input_widget) is ToggleSwitch:
            return self.input_widget.state


class SettingHeader(Widget):
    def __init__(self, parent: "SettingPanel", *rect_args, header_text: str, color=DEFAULT_ENTRY_FG_COLOR):
        super().__init__(parent, *rect_args)

        self.image = FontSave.get_font(self.rect.h, "px").render(header_text, True, color)

    def set_input_widget(self, widget_type: int, **widget_kwargs):
        pass


class SettingPanel(Panel):
    """
    The setting panel is an extension of the `Panel` class that is able to contain multiple rows of entries usually used
    to configure something.
    """

    def __init__(self, parent: "Widget" or Scene, *rect_args, panel_unit="%",
                 entry_horizontal_margin=5, **kwargs):

        super().__init__(parent, *rect_args, panel_unit=panel_unit, **kwargs)

        self.entry_hz_margin = entry_horizontal_margin

        self.entry_dict = {}  # {field name: entry widget}

    def add_entry(self, field_name: str, label_text: str = "", **entry_kwargs) -> SettingEntry:
        if field_name in self.entry_dict:
            raise ValueError(f"field name already exists: {field_name}")

        entry = SettingEntry(self, *self.next_pack_rect, "px", "tl", "tl",
                             entry_label_text=label_text, horizontal_margin=self.entry_hz_margin,
                             **entry_kwargs)

        self.add_scrollable(entry)
        self.entry_dict[field_name] = entry

        return entry

    def add_header(self, header_text: str, font_scale=1.0) -> SettingHeader:
        x, y, w, h = self.next_pack_rect
        h *= font_scale

        header = SettingHeader(self, x, y, w, h, "px", "tl", "tl", header_text=header_text)
        self.add_scrollable(header)

        self._next_row_y += self._inner_margin

        return header

    def get_setting_data(self) -> dict:
        return {field: entry.get_entry_data() for field, entry in self.entry_dict.items()}
