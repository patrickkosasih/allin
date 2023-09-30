import pygame

from app.shared import Layer


SPRITE_PATHS = {
    "D": "assets/sprites/dealer buttons/d.png",
    "SB": "assets/sprites/dealer buttons/sb.png",
    "BB": "assets/sprites/dealer buttons/bb.png"
}


class DealerButton(pygame.sprite.Sprite):
    def __init__(self, pos, diameter, button_type="D"):
        super().__init__()

        button_type = button_type.upper()
        if button_type not in SPRITE_PATHS:
            raise ValueError(f"invalid button type: {button_type}")

        self.image = pygame.transform.smoothscale(pygame.image.load(SPRITE_PATHS[button_type]), 2 * (diameter,))
        self.rect = self.image.get_rect(center=pos)
        self.layer = Layer.DEALER_BUTTON if button_type == "D" else Layer.BLINDS_BUTTON
