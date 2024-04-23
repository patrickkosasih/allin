from typing import Type

from app.animations.animation import Animation


class AnimGroup:
    """
    An animation group is used to store multiple animations into one group. The update method of an animation group is
    then called every game tick which updates all the ongoing animations. When an animation is finished playing, it gets
    removed from the animation group.
    """

    def __init__(self):
        self.animations: list[Animation] = []  # Currently running animations

    def add(self, animation: Animation):
        self.animations.append(animation)

    def reset(self, anim_type: Type or None = None):
        """
        Remove all the animations on the animation group. If `anim_type` is specified, then only the animations of the
        specified type/class is removed.
        """
        if anim_type:
            for anim in self.animations:
                if type(anim) is anim_type:
                    self.animations.remove(anim)

        else:
            self.animations = []

    def update(self, dt):
        """
        Run the update method of all the animations of this group.
        """
        for animation in self.animations:
            animation.update(dt)

            if animation.finished:
                self.animations.remove(animation)
