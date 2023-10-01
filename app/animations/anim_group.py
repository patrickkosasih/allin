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

    def update(self, dt):
        """
        Run the update method of all the animations of this group.
        """
        for animation in self.animations:
            animation.update(dt)

            if animation.finished:
                self.animations.remove(animation)
