import cocos
import cocos.actions
from cocos.director import director
import pattern
import random

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events
    BitPatternSize = 8
    def __init__(self):
        super(GamePlay, self).__init__()
        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = cocos.text.Label('Hello, World!',
                                 font_name='Times New Roman',
                                 font_size=32,
                                 anchor_x='center', anchor_y='center')

        (w,h) = director.get_window_size()
        self.label.position = w/2, h-32
        self.add(self.label)
        self.bitSize = w/GamePlay.BitPatternSize
        self.stackHeight = 0
        self.currentTarget = 0
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

    def update(self, dt):
        #if the required number cannot be achieved or when the pattern has reached bottom of screen.
        if  self.isPatternFailed() or self.bitpattern.y <= self.stackHeight:
            self.bitpattern.stop()
            (w,h) = director.get_window_size()
            cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
            cl.position = 0, self.stackHeight
            cl.do(cocos.actions.FadeIn(0.2))
            self.add(cl)
            #TODO show error prompt on screen.
            self.stackHeight += self.bitSize
            self.remove(self.bitpattern)
            if(self.stackHeight > h-self.bitSize):
                print "GameOver"
                self.unschedule(self.update)
            else:
                self.generateNextPattern()

        elif self.isPatternFinished():
            #TODO show possitive prompt on screen
            self.bitpattern.stop()
            self.remove(self.bitpattern)
            self.generateNextPattern()


    def update_text(self, x, y):
        self.label.element.text = "" + str(x)  + "," + str(y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.posx, self.posy = director.get_virtual_coordinates(x, y)
        #make the bits toggle when the mouse is clicked.
        self.bitpattern.handleClick(x, y)