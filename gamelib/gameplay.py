import cocos
import cocos.particle_systems
import cocos.actions
from cocos.director import director
import pattern
import random

def removePattern(node):
    node.kill()

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events
    BitPatternSize = 8
    def __init__(self):
        super(GamePlay, self).__init__()
        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = cocos.text.Label('Hello, World!',
                                 font_name='Nokia Cellphone',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')

        (w,h) = director.get_window_size()
        self.w = w
        self.h = h
        self.label.position = w/2, h-32
        self.add(self.label)
        self.bitSize = w/GamePlay.BitPatternSize
        self.stackHeight = 0
        self.currentTarget = 0
        self.isAnimating = False
        self.generateNextPattern()
        self.schedule(self.update)

    def resetGame(self):
        self.stackHeight = 0

    def generateNextPattern(self):
        self.currentTarget = random.randrange(0, 10) #TODO change limit based on level
        self.label.element.text = "Target: " + str(self.currentTarget)
        self.bitpattern = pattern.BitPattern(GamePlay.BitPatternSize)
        self.add(self.bitpattern)
        move = cocos.actions.MoveBy((0, -self.bitSize), 0.5)
        delay = cocos.actions.Delay(1) #TODO change delay based on level.
        seq = cocos.actions.sequence(move, delay)
        self.bitpattern.do(cocos.actions.Repeat(seq))

    def isPatternFailed(self):
        return self.currentTarget & self.bitpattern.getValue() != self.currentTarget

    def isPatternFinished(self):
        return self.currentTarget ^ self.bitpattern.getValue() == 0

    def addWhiteLine(self):
        #add the white block at the bottom of screen.
        (w,h) = director.get_window_size()
        cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
        cl.position = 0, self.stackHeight
        cl.do(cocos.actions.FadeIn(0.5))
        self.add(cl)
        self.stackHeight += self.bitSize

    def handleError(self, node):
        node.do(cocos.actions.Delay(0.5) + cocos.actions.CallFuncS(self.remove))
        self.addWhiteLine()
        self.isAnimating = False
        self.generateNextPattern()

    def handleSuccess(self, node):
        print "Successful"
        self.isAnimating = False
        self.generateNextPattern()
        node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))

    def showMessage(self, msg, color=(0, 0, 0, 255), callback = None):
        self.isAnimating = True

        #create a white layer that fades in
        (w,h) = director.get_window_size()
        cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
        cl.position = 0, self.bitpattern.y
        if callback == None:
            cl.do(cocos.actions.FadeIn(0.5) + cocos.actions.Delay(1) + cocos.actions.CallFuncS(self.handleError))
        else:
            cl.do(cocos.actions.FadeIn(0.5) + cocos.actions.Delay(1) + cocos.actions.CallFuncS(self.handleSuccess))

        #text label on top of white text.
        errormsg = cocos.text.Label(msg,
                             font_name='Nokia Cellphone',
                             font_size=32,
                             anchor_x='center', anchor_y='center')
        errormsg.position = w/2, self.bitSize/2-5
        errormsg.element.color = color
        errormsg.do(cocos.actions.Delay(0.5) + cocos.actions.Blink(2, 1))
        cl.add(errormsg)

        self.add(cl)

    def update(self, dt):
        #if we are animating something we do not want the update checks.
        if self.isAnimating:
            return

        #if the required number cannot be achieved
        if self.isPatternFailed():
            #remove the current pattern
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("ERROR", (255, 0, 0, 255))
            return

        # when the pattern has reached bottom of screen.
        if self.bitpattern.y <= self.stackHeight:
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("TIMEOUT!!", (255, 0, 0, 255))

        if(self.stackHeight > self.h-self.bitSize):
            print "GameOver"
            self.unschedule(self.update)

        elif self.isPatternFinished():
            #TODO show possitive prompt on screen
            self.bitpattern.stop()
            self.remove(self.bitpattern)
            self.isAnimating = True
            self.showMessage("SUCCESS!", (0, 255, 0, 255), 1)
            explosion = cocos.particle_systems.Explosion()
            explosion.position = self.w/2, self.h/2
            explosion.total_particles = 10
            explosion.life = 1.0
            explosion.life_var = 0.5
            explosion.start_color = cocos.particle.Color(1, 1, 1, 1)
            explosion.start_color_var = cocos.particle.Color(0, 0, 0, 0)
            explosion.end_color = cocos.particle.Color(1, 1, 1, 0)
            explosion.end_color_var = cocos.particle.Color(0, 0, 0, 0)
            explosion.do(cocos.actions.Delay(2) + cocos.actions.CallFuncS(self.remove))
            self.add(explosion)


    def update_text(self, x, y):
        self.label.element.text = "" + str(x)  + "," + str(y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.posx, self.posy = director.get_virtual_coordinates(x, y)
        #make the bits toggle when the mouse is clicked.
        self.bitpattern.handleClick(x, y)