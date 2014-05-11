import cocos
import cocos.actions
from cocos.director import director
import pattern

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events

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
        self.bitSize = w/8
        self.stackHeight = 0
        self.bitpattern = pattern.BitPattern(8)
        self.moveBitPattern()
        self.add(self.bitpattern)
        self.schedule(self.update)

    def resetGame(self):
        self.stackHeight = 0

    def moveBitPattern(self):
        move = cocos.actions.MoveBy((0, -self.bitSize), 0.5)
        delay = cocos.actions.Delay(0.1)
        seq = cocos.actions.sequence(move, delay)
        self.bitpattern.do(cocos.actions.Repeat(seq))

    def update(self, dt):
        if self.bitpattern.y <= self.stackHeight:
            self.bitpattern.stop()
            (w,h) = director.get_window_size()
            cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
            cl.position = 0, self.stackHeight
            cl.do(cocos.actions.FadeIn(0.2))
            self.add(cl)
            self.stackHeight += self.bitSize
            self.remove(self.bitpattern)
            self.bitpattern = None


    def update_text(self, x, y):
        self.label.element.text = "" + str(x)  + "," + str(y)

    def on_mouse_motion(self, x, y, dx, dy):
        """Called when the mouse moves over the app window with no button pressed

        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        """
        self.update_text(x, y)


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Called when the mouse moves over the app window with some button(s) pressed

        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.update_text(x, y)


    def on_mouse_press(self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
        (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.posx, self.posy = director.get_virtual_coordinates(x, y)
        self.update_text(x, y)
        self.bitpattern.handleClick(x, y)