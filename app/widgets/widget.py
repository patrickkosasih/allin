import pygame

from app.animations.anim_group import AnimGroup
from app.shared import *


class AutoRect(pygame.rect.Rect):
    """
    An extended version of Pygame's Rect class.
    An AutoRect has a settable unit, anchor, pivot, and parent rect that would make it easier to position widgets.
    """

    ALIGNMENT_FACTORS = {           # Aliases
        "topleft": (0, 0),          "tl": (0, 0),
        "midtop": (0.5, 0),         "mt": (0.5, 0),
        "topright": (1, 0),         "tr": (1, 0),
        "midleft": (0, 0.5),        "ml": (0, 0.5),
        "center": (0.5, 0.5),       "ctr": (0.5, 0.5),
        "midright": (1, 0.5),       "mr": (1, 0.5),
        "bottomleft": (0, 1),       "bl": (0, 1),
        "midbottom": (0.5, 1),      "mb": (0.5, 1),
        "bottomright": (1, 1),      "br": (1, 1),
    }

    def __init__(self, x, y, w, h, unit="px", anchor="topleft", pivot="topleft", parent_rect=None):
        """
        Parameters:

        :param x: X position
        :param y: Y position
        :param w: Width
        :param h: Height

        :param unit: The unit of x, y, w, and h. Possible units:
                       px: Pixels (default).
                       %:  A fraction of the display's dimensions in percentage.

        :param anchor: The anchor/origin of the rect on the parent rect. Possible anchors: See `ALIGNMENT_FACTORS`.
                         e.g. When the anchor is set to "center", then the position's (0, 0) would be located in the
                         center of the screen / parent rect.

        :param pivot: The pivot of the rect. Possible anchors: See `ALIGNMENT_FACTORS`.
                        e.g. When the pivot is set to "bottomright", then the rect's bottom right corner would be placed
                        in the given x and y positions.

        :param parent_rect: The parent rect.
        """

        parent_rect = parent_rect if parent_rect else pygame.Rect(0, 0, *pygame.display.get_window_size())

        if unit == "%":
            w, h = elementwise_mult(parent_rect.size, (w / 100, h / 100))

        super().__init__(0, 0, w, h)

        """
        Extended attributes
        """
        self.parent_rect = parent_rect
        self.global_rect = None

        self._unit = unit
        self._anchor = anchor
        self._pivot = pivot

        """
        Initialize position
        """
        self.set_pos(x, y)

    def __repr__(self):
        x, y, w, h = self
        return f"<AutoRect({x}, {y}, {w}, {h}, {self._unit=}, {self._anchor=}, {self._pivot=})>"

    def set_pos(self, x, y, unit=None, anchor=None, pivot=None):
        """
        Set the position of the rect.

        :param x: X position.
        :param y: Y position.
        :param unit: Temporarily override the rect's unit.
        :param anchor: Temporarily override the rect's anchor.
        :param pivot: Temporarily override the rect's pivot.
        """

        unit = unit if unit else self._unit
        anchor = anchor if anchor else self._anchor
        pivot = pivot if pivot else self._pivot

        """
        Set the original Rect position (where the anchor and pivot are in the top right)
        """
        if unit == "px":
            self.x, self.y = x, y
        elif unit == "%":
            self.x, self.y = elementwise_mult(self.parent_rect.size, (x / 100, y / 100))
        else:
            raise ValueError("invalid unit: " + unit)

        """
        Validate anchor and pivot 
        """
        if anchor not in AutoRect.ALIGNMENT_FACTORS:
            raise ValueError("invalid anchor: " + anchor)
        elif pivot not in AutoRect.ALIGNMENT_FACTORS:
            raise ValueError("invalid pivot: " + pivot)

        """
        Align the position according to the anchor and pivot

        Pos = Original pos + (Anchor alignment factors * Parent rect size) - (Pivot alignment factors * Dimensions)
        """
        anchor_offset = Vector2(*elementwise_mult(AutoRect.ALIGNMENT_FACTORS[anchor], self.parent_rect.size))
        pivot_offset = Vector2(*elementwise_mult(AutoRect.ALIGNMENT_FACTORS[pivot], self.size))

        self.x, self.y = Vector2(self.topleft) + anchor_offset - pivot_offset

        """
        Set global rect
        """
        self.global_rect = self.move(*self.parent_rect.topleft)

    def get_pos(self, unit=None, anchor=None, pivot=None) -> Vector2:
        """
        Returns the rect's position with the specified unit relative to the specified anchor and pivot.
        If the unit/anchor/pivot is not specified, then the rect's attribute is used instead.
        """

        unit = unit if unit else self._unit
        anchor = anchor if anchor else self._anchor
        pivot = pivot if pivot else self._pivot

        anchor_offset = Vector2(*elementwise_mult(AutoRect.ALIGNMENT_FACTORS[anchor], self.parent_rect.size))
        pivot_offset = Vector2(*elementwise_mult(AutoRect.ALIGNMENT_FACTORS[pivot], self.size))
        pos = Vector2(self.topleft) - anchor_offset + pivot_offset

        if unit == "%":
            pos.x = pos.x * self.parent_rect.w / 100
            pos.y = pos.y * self.parent_rect.h / 100

        return pos

    @property
    def aspect_ratio(self):
        return self.w / self.h


class Widget(pygame.sprite.Sprite):
    """
    Base class for all widgets (GUI elements/Pygame sprites of the Allin game).
    """

    def __init__(self, *rect_args, parent: "Widget" = None, groups=()):
        """
        Parameters:

        :param rect_args: Non-keyword arguments of the __init__ method of this class are read as arguments for the
                          AutoRect of the widget.

        :param parent: The parent widget of this widget.
        :param groups: A tuple of the sprite groups the new widget is part of.
        """

        super().__init__(*groups)

        self._rect = AutoRect(*rect_args, parent_rect=parent.rect if parent else None)
        self._image = pygame.Surface(self._rect.size, pygame.SRCALPHA)

        self.parent = parent
        self.component_group = pygame.sprite.Group()
        self.anim_group = AnimGroup()

    def update(self, dt):
        self.anim_group.update(dt)
        self.component_group.update(dt)

    def set_pos(self, x, y, unit=None, anchor=None, pivot=None):
        self._rect.set_pos(x, y, unit, anchor, pivot)
        # TODO When the position of a widget is changed, update the global rect of the widget's children
        #  (and their children, and so on).

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect.update(*rect)

    @property
    def image(self):
        return self._image
