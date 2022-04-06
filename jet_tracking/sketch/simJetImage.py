import numpy as np
from tools.imGen import read_noise, jet_display


class SimulatedImage(object):
    def __init__(self, context, signals):
        self.context = context
        self.signals = signals
        self.jet_im = []
        self.x_size = 500
        self.y_size = 500
        self.pix_per_mm = 1000
        self.jet_location = 0
        self.motor_position = 0
        self.gen_image()
        self.make_connections()

    def make_connections(self):
        self.signals.changeReadPosition.connect(
            self.update_motor_position)

    def update_motor_position(self, p):
        self.motor_position = p

    def gen_image(self):
        self.jet_im = np.full((self.y_size, self.x_size), 0, dtype=np.uint8)
        self.jet_im = jet_display(self.jet_im, self.motor_position, self.context.jet_center, self.pix_per_mm, self.x_size)
        self.jet_im = read_noise(self.jet_im, 10, 4)



