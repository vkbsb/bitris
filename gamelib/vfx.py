from cocos.particle_systems import *
from cocos.particle import *
from cocos.actions import *

class SuccessExplosion(Explosion):
    def __init__(self, start_color=Color(0, 1, 0, 1), end_color=Color(1,1,1,0)):
        super(SuccessExplosion, self).__init__()
        self.total_particles = 10
        self.life = 1.0
        self.life_var = 0.5
        self.start_color = start_color
        self.start_color_var = Color(0, 0, 0, 0)
        self.end_color = end_color
        self.end_color_var = Color(0, 0, 0, 0)
        self.do(Delay(2) + CallFunc(self.kill))