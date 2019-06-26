import effect


class SolidEffect(effect.Effect):

    NAME = "solid"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)
        self.color = (255, 255, 255)
        self.done = False


    def setup(self):
        self.done = False


    def set_color(self, color):
        pass

        self.color = color
        self.done = False


    def loop(self):
        if not self.done:
            self.led_art.set_color(self.color)
            self.led_art.show()

        self.done = True
