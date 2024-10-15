import random

from app.scenes.scene import Scene
from app.shared import load_image
from app.widgets.basic.button import CircularButton, Button
from online.client.client_comms import ClientComms

from online.packets import MessagePacket


class MultiplayerMenuScene(Scene):
    def __init__(self, app):
        # super().__init__(app, "multiplayer")
        super().__init__(app)

        ClientComms.connect()

        self.back_button = CircularButton(self, 1.5, 1.5, 4, "%h", "tl", "tl",
                                          command=self.back,
                                          icon=load_image("assets/sprites/menu icons/back.png"),
                                          icon_size=0.8)

        self.test_button = Button(self, 0, 0, 20, 20, "%", "ctr", "ctr",
                                  command=self.test_send_thing,
                                  text_str="oi oi oi")

    def test_send_thing(self):
        ClientComms.send_packet(MessagePacket(message=f"heyyy..... GIVE ME FISH {random.randrange(1000000)}"))

    def back(self):
        self.app.change_scene_anim("mainmenu")
