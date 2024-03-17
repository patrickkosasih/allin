from typing import Type

from app.scenes.scene import Scene
from app.shared import *
from app.widgets.basic.number_picker import NumberPicker
from app.widgets.widget import Widget, WidgetComponent
from app.widgets.basic.panel import Panel


DEFAULT_ENTRY_BG_COLOR = (20, 20, 20, 128)
DEFAULT_ENTRY_FG_COLOR = (255, 255, 255)


class FormEntry(Widget):
    """
    Form entries are elements of the form panel which has a representing text and an input widget.
    """

    # Widget types
    NO_WIDGET = 0
    NUMBER_PICKER = 1
    SWITCH = 2
    SLIDER = 3

    def __init__(self, parent: "FormPanel", *rect_args,
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

        self.input_widget = None

    def set_input_widget(self, widget_type: int, **widget_kwargs):
        if self.input_widget:
            del self.input_widget

        match widget_type:
            case FormEntry.NO_WIDGET:
                self.input_widget = None

            case FormEntry.NUMBER_PICKER:
                self.input_widget = NumberPicker(self, -self.horizontal_margin, 0, 25, 75, "%", "mr", "mr",
                                                 **widget_kwargs)

            # TODO Coming soon switch/checkbox and slider inputs

    def get_entry_data(self):
        if type(self.input_widget) is NumberPicker:
            return self.input_widget.value


class FormHeader(Widget):
    def __init__(self, parent: "FormPanel", *rect_args, header_text: str, color=DEFAULT_ENTRY_FG_COLOR):
        super().__init__(parent, *rect_args)

        self.image = FontSave.get_font(self.rect.h, "px").render(header_text, True, color)

    def set_input_widget(self, widget_type: int, **widget_kwargs):
        pass


class FormPanel(Panel):
    """
    The form panel is an extension of the `Panel` class that is used to create a container for multiple input widgets.
    """

    def __init__(self, parent: "Widget" or Scene, *rect_args, panel_unit="%",
                 entry_height=10, entry_horizontal_margin=2, **kwargs):

        super().__init__(parent, *rect_args, panel_unit=panel_unit, **kwargs)

        if panel_unit == "%":
            entry_height = self.rect.h * entry_height / 100  # Convert % into px

        self.entry_height = entry_height
        self.entry_hz_margin = entry_horizontal_margin

        self.entry_dict = {}  # {field name: entry widget}

    def add_entry(self, field_name: str, label_text: str = "", **entry_kwargs) -> FormEntry:
        if field_name in self.entry_dict:
            raise ValueError(f"field name already exists: {field_name}")

        w = self.rect.w - 2 * self._outer_margin
        h = self.entry_height

        entry = FormEntry(self, 0, 0, w, h, "px", "tl", "tl",
                          entry_label_text=label_text, horizontal_margin=self.entry_hz_margin,
                          **entry_kwargs)

        self.add_scrollable(entry)
        self.entry_dict[field_name] = entry

        return entry

    def add_header(self, header_text: str) -> FormHeader:
        w = self.rect.w - 2 * self._outer_margin
        h = self.entry_height

        header = FormHeader(self, 0, 0, w, h, "px", "tl", "tl", header_text=header_text)
        self.add_scrollable(header)

        self._next_row_y += self._inner_margin

        return header

    def get_form_data(self) -> dict:
        return {field: entry.get_entry_data() for field, entry in self.entry_dict.items()}
