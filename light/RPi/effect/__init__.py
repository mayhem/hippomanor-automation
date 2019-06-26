import abc


class Effect(object):

    def __init__(self, led_art, name):
        self.led_art = led_art
        self.effect_name = name

    @property
    def name(self):
        return self.effect_name

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def set_color(self, color):
        pass

    @abc.abstractmethod
    def loop(self):
        pass

