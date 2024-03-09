from app.scenes.scene import Scene
from app.shared import *
from app.widgets.widget import Widget, WidgetComponent
from app.widgets.basic.panel import Panel


DEFAULT_BG_COLOR = (20, 20, 20, 128)
DEFAULT_FG_COLOR = (255, 255, 255)


class FormEntry(Widget):
    """
    Form entries are elements of the form panel which has a representing text and an input widget.
    """

    def __init__(self, parent: "Panel", *rect_args,
                 field_name="", base_color=DEFAULT_BG_COLOR, base_radius=-1,
                 text_scale=0.6, text_color=DEFAULT_FG_COLOR, text_margin=3):

        super().__init__(parent, *rect_args)

        self.base = WidgetComponent(self, 0, 0, 100, 100, "%", "ctr", "ctr")
        draw_rounded_rect(self.base.image, self.base.rect, color=base_color, r=base_radius)

        self.text = WidgetComponent(self, text_margin, 0, 50, 100, "%", "ml", "ml")
        self.text.image = FontSave.get_font(self.rect.height * text_scale, "px").render(field_name, True, text_color)


class FormPanel(Panel):
    """
    The form panel is an extension of the `Panel` class that is used to create a container for multiple input widgets.
    """

    def __init__(self, parent: "Widget" or Scene, *rect_args, panel_unit="%",
                 row_height=10, **kwargs):

        super().__init__(parent, *rect_args, panel_unit=panel_unit, **kwargs)

        """
        Convert % into px.
        """
        if panel_unit == "%":
            row_height = self.rect.h * row_height / 100

        self.row_height = row_height

    def add_entry(self, field_name: str, **row_kwargs):
        w = self.rect.w - 2 * self._outer_margin
        h = self.row_height

        row = FormEntry(self, 0, 0, w, h, "px", "tl", "tl", field_name=field_name, **row_kwargs)
        self.add_scrollable(row)

        return row
