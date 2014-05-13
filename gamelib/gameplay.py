import cocos
from cocos.scenes.transitions import *
import cocos.particle_systems
import cocos.actions
from cocos.director import director
import pattern
import random
from vfx import *

def createLabel(msg, fontsize = 18, color = (255, 0, 0, 255)):
    errormsg = cocos.text.Label(msg,
                        font_name='Nokia Cellphone',
                         font_size=fontsize,
                         anchor_x='center', anchor_y='center')
    errormsg.element.color = color
    return errormsg

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events
    BitPatternSize = 8
    def __init__(self):
        super(GamePlay, self).__init__()
        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = createLabel('Hello, World!', 32, (255, 255, 255, 255))
        (w,h) = director.get_window_size()
        self.w = w
        self.h = h
        self.label.position = w/2, h-32
        self.add(self.label)
        self.bitSize = w/GamePlay.BitPatternSize
        self.resetGame()
        self.schedule(self.update)

    def resetGame(self):
        self.currentTarget = 0
        self.stackHeight = 0
        self.successCounter = 0
        self.isAnimating = False
        self.score = 0
        self.isGameOver = False
        self.generateNextPattern()

    def generateNextPattern(self):
        if self.isGameOver:
            return
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
        cl = cocos.layer.ColorLayer(255,255,255,255, w, self.bitSize)
        cl.position = 0, self.stackHeight
        #cl.do(cocos.actions.FadeIn(0.2))
        self.add(cl, 1)
        self.stackHeight += self.bitSize

    def handleError(self, node):
        node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))
        self.addWhiteLine()
        self.isAnimating = False
        self.generateNextPattern()

    def handleSuccess(self, node):
        self.isAnimating = False
        self.generateNextPattern()
        node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))

    def showMessage(self, msg, color=(0, 0, 0, 255), isError = True):
        """
        This function is useful for showing the message on screen. If the isError value is
        True, we call the handleError once the FadeIn happens, Else we call handleSuccess.
        """
        #We want to prevent any updates going on while we are showing the message.
        self.isAnimating = True
        #create a white layer that fades in
        (w,h) = director.get_window_size()
        cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
        cl.position = 0, self.bitpattern.y
        if isError == True:
            cl.do(cocos.actions.FadeIn(0.2) + cocos.actions.Delay(1.5) + cocos.actions.CallFuncS(self.handleError))
        else:
            cl.do(cocos.actions.FadeIn(0.2) + cocos.actions.Delay(1.5) + cocos.actions.CallFuncS(self.handleSuccess))

        #text label on top of white text.
        errormsg = createLabel(msg, 32, color)
        errormsg.position = w/2, self.bitSize/2-5
        errormsg.do(cocos.actions.Delay(0.2) + cocos.actions.Blink(2, 1) + cocos.actions.FadeOut(0.5))
        cl.add(errormsg)
        self.add(cl)

    def showResults(self):
        #TODO: figure out if we want to transition to a different scene or in this scene.
        s = cocos.scene.Scene()
        director.replace(TurnOffTilesTransition(s))

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

        if(self.stackHeight > self.h - self.bitSize):
            print "GameOver"
            self.isGameOver = True
            self.bitpattern.stop()
            self.unschedule(self.update)
            errormsg = createLabel("Fatal: too many errors")
            errormsg.position = self.w/2, self.h/2
            self.add(errormsg, 2)
            errormsg = createLabel("Program Terminated")
            errormsg.position = self.w/2, self.h/2-25
            self.add(errormsg, 2)
            errormsg.do(cocos.actions.Delay(0.2) + cocos.actions.Blink(2, 1))
            self.do(cocos.actions.Delay(1.5) + cocos.actions.CallFunc(self.showResults))


        elif self.isPatternFinished():
            #increment the score / successcounter
            self.successCounter += 1
            self.score += (self.BitPatternSize - self.bitpattern.getNumBitsOn())
            #remove the old bit pattern.
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("SUCCESS!", (0, 255, 0, 255), False)
            #add a couple of explosions for effect.
            explosion = SuccessExplosion()
            explosion.position = (self.bitSize, self.bitpattern.y + self.bitSize/2)
            self.add(explosion)
            explosion = SuccessExplosion()
            explosion.position = (self.w - self.bitSize, self.bitpattern.y + self.bitSize/2)
            self.add(explosion)

    def update_text(self, x, y):
        self.label.element.text = "" + str(x)  + "," + str(y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.isGameOver:
            #TODO: switch to results screen.
            pass
        else:
            self.posx, self.posy = director.get_virtual_coordinates(x, y)
            #make the bits toggle when the mouse is clicked.
            self.bitpattern.handleClick(x, y)