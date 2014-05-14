import cocos
from cocos.scenes.transitions import *
import cocos.particle_systems
import cocos.actions
import cocos.sprite
from cocos.director import director
import pattern
import results
from vfx import *
import data

def createLabel(msg, fontsize = 18, color = (255, 0, 0, 255)):
    errormsg = cocos.text.Label(msg,
                        font_name='Nokia Cellphone',
                         font_size=fontsize,
                         anchor_x='center', anchor_y='center')
    errormsg.element.color = color
    return errormsg


class PowerUpIndicator(cocos.sprite.Sprite):
    def __init__(self, image, callback):
        super(PowerUpIndicator, self).__init__(image)
        self.file_name = image
        self._count = 2
        self.callback = callback
        self.label = createLabel(str(self.count), 24)
        self.label.position = (-self.width/2, 10)
        self.label.element.color = (0, 0, 0, 118)
        self.label.element.anchor_x = 'right'
        self.add(self.label)

    def activate(self):
        if self.count > 0:
            self.do(cocos.actions.RotateBy(10, 0.1) + cocos.actions.RotateBy(-20, 0.1) + cocos.actions.RotateBy(10,0.1))
            self.count -= 1
            self.callback(self.file_name)

    def _set_count(self, c):
        self._count = c
        self.label.element.text = str(self._count)

    def _get_count(self):
        return self._count

    count = property(_get_count, _set_count, doc='indicates the number of powerups available')

    def _set_scale( self, s ):
        super(PowerUpIndicator, self)._set_scale(s)

        if hasattr(self, 'label'):
            self.label.position = (-self.width/2, -self.height/2)

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events
    BitPatternSize = 8
    def __init__(self):
        super(GamePlay, self).__init__()
        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = createLabel('Hello, World!', 20, (255, 255, 255, 255))
        (w,h) = director.get_window_size()
        self.w = w
        self.h = h
        self.label.position = w/2, h-20
        self.add(self.label)
        self.bitSize = w/GamePlay.BitPatternSize

        #score display
        self.scoreText = createLabel('Score: 8888', 10, (255, 255, 255, 255))
        self.scoreText.element.anchor_x = 'left'
        self.scoreText.position = 5, h-10
        self.add(self.scoreText)

        self.multiplierText = createLabel('x1', 10, (255, 255, 255, 255))
        self.multiplierText.element.anchor_x = 'left'
        self.multiplierText.position = 5, h-25
        self.add(self.multiplierText)

        self.resetGame()

        #we start with 0 as starting point.
        self.currentTarget = 0
        self.label.element.text = "Return: " + str(self.currentTarget)

        cl = cocos.layer.ColorLayer(255, 255, 255, 255, self.w, 72)
        self.add(cl)

        self.powerMenu = []
        self.powerMenu.append(PowerUpIndicator('AutoByte.png', self.activate_powerup))
        self.powerMenu.append(PowerUpIndicator('BitAndOrder.png', self.activate_powerup))
        self.powerMenu.append(PowerUpIndicator('ByteBlast.png', self.activate_powerup))
        itemSize = self.w/3
        for i in xrange(3):
            self.powerMenu[i].scale = 0.8
            self.powerMenu[i].position = itemSize/2 + i*itemSize, 72/2
            self.powerMenu[i].count = i #TODO load the numbers from inventory
            self.add(self.powerMenu[i])

        # #create the menu for powerups.
        # menu = cocos.menu.Menu()
        # positions = []
        # itemSize = self.w/3
        # for i in xrange(3):
        #     positions.append((itemSize/2 + i*itemSize, 48/2))
        # print positions
        # layout_func = cocos.menu.fixedPositionMenuLayout(positions)
        # l = []
        # l.append(cocos.menu.ImageMenuItem('AutoCorrect.png', self.resetGame))
        # l.append(cocos.menu.ImageMenuItem('BitAndOrder.png', self.resetGame))
        # l.append(cocos.menu.ImageMenuItem('BitBlast.png', self.resetGame))
        # menu.create_menu(l, cocos.menu.zoom_in(), cocos.menu.zoom_out(), cocos.menu.shake(), layout_func)
        # self.add(menu)

        self.schedule(self.update)

    def updateScoreText(self):
        self.scoreText.element.text = "Score: " + str(self.score)
        self.multiplierText.element.text = "x" + str(self.multiplier)

    def resetGame(self):
        self.currentTarget = 0
        self.stackHeight = 72
        self.multiplier = 1
        self.successCounter = 0
        self.isAnimating = False
        self.score = 0
        self.startMutation = False
        self.isGameOver = False
        self.genLimit = 10
        self.delayTime = 1
        self.maxMultiplier = 1
        self.updateScoreText()
        self.generateNextPattern()

    def generateNextPattern(self):
        if self.isGameOver:
            return
        self.currentTarget = random.randrange(0, self.genLimit)
        self.label.element.text = "Return: " + str(self.currentTarget)
        self.bitpattern = pattern.BitPattern(GamePlay.BitPatternSize)
        self.add(self.bitpattern)
        move = cocos.actions.MoveBy((0, -self.bitSize), 0.5)
        delay = cocos.actions.Delay(self.delayTime)
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
        self.multiplier = 1
        self.updateScoreText()

    def handleSuccess(self, node):
        self.isAnimating = False
        self.generateNextPattern()
        node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))
        # successcounter
        self.successCounter += 1
        self.multiplier += 1

        #track the max multiplier that the user had achieved during gameplay.
        if self.maxMultiplier < self.multiplier:
            self.maxMultiplier = self.multiplier

        #increment the genLimit by 10 every time the successCounter goes up.
        if(self.successCounter % 5 == 0):
            self.genLimit += 10

        #decrement the time for every 10 correct answers.
        if(self.successCounter % 10 == 0):
            self.delayTime -= 0.1
            #TODO decide when to shuffle the bits.
            if self.delayTime < 0.5:
                self.delayTime = 0.5

        self.updateScoreText()

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
        #TODO use same scene or different one for results
        print self.multiplier
        print self.score
        print self.successCounter
        r = results.Results(['Multiplier: ', self.maxMultiplier,
                             'Score: ', self.score,
                             'Success: ', self.successCounter,
                             '---------', '--------',
                             'CpuCycles: ', self.successCounter * self.maxMultiplier])
        s = cocos.scene.Scene(r)
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
            #increment the score
            self.score += self.multiplier * (self.BitPatternSize - self.bitpattern.getNumBitsOn())
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

    def activate_powerup(self, fname):
        #TODO implment the powerups.
        if fname == "AutoByte.png":
            print "AutoByte Launched"
        elif fname == "BitAndOrder.png":
            print "BitAndOrder Launched"
        elif fname == "ByteBlast.png":
            print "ByteBlater Launched"

    def on_mouse_motion(self, sx, sy, dx, dy):
        #handle the mouse over effect.
        for item in self.powerMenu:
            if item.contains(sx, sy):
                item.scale = 0.9
            else:
                item.scale = 0.8

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.isGameOver:
            pass
        else:
            #handle the mouse click to activate the powerup.
            for item in self.powerMenu:
                if item.contains(x, y):
                    item.activate()

            self.posx, self.posy = director.get_virtual_coordinates(x, y)
            #make the bits toggle when the mouse is clicked.
            self.bitpattern.handleClick(x, y)