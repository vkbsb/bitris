import cocos
from cocos.director import director
from pyglet import gl

# Defining a new layer type...
class Square(cocos.layer.Layer):
    """Square (color, c, y, size=50) : A layer drawing a square at (x,y) of
    given color and size"""
    def __init__(self, color, x, y, size=50):
        super( Square, self ).__init__()

        self.x = x
        self.y = y
        self.size = size
        self.layer_color = color
        self.bitNum = 0
        self.label = cocos.text.Label('0',
                                 font_name='Times New Roman',
                                 font_size=20,
                                 anchor_x='center', anchor_y='center')
        self.label.element.color = (0, 0, 0, 150)
        self.label.position = size/2, size/2
        self.add(self.label)

    def setBitNumber(self, num):
        self.label.element.text = str(num)
        self.bitNum = num

    def isBitOn(self):
        if(self.label.element.color == (255, 255, 255, 255)):
            return False
        return True

    def isPointInside(self, x, y):
        if(x < self.x + self.size and x > self.x):
            if(y < self.y + self.size and y > self.y):
                return True
        return False

    def draw(self):
        super(Square,self).draw()

        gl.glColor4f(*self.layer_color)
        x, y = self.x, self.y
        w = x+self.size; h=y+self.size
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( x, y )
        gl.glVertex2f( x, h )
        gl.glVertex2f( w, h )
        gl.glVertex2f( w, y )
        gl.glEnd()
        gl.glColor4f(1,1,1,1)

        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f( x, y )
        gl.glVertex2f( w, y )
        gl.glVertex2f( w, h )
        gl.glVertex2f( x, h )
        gl.glEnd()

class BitPattern(cocos.layer.Layer):
    # colors = [
    #     (255, 255, 255, 255),
    #     (128, 0, 128, 255),
    #     (0, 0, 255, 255),
    #     (0, 255, 255, 255),
    #     (0, 255, 0, 255),
    #     (255, 255, 0, 255),
    #     (255, 102, 0, 255),
    #     (255, 0, 0, 255)
    # ]

    colors = [
        (255, 213, 213, 255),
        (255, 170, 170, 255),
        (255, 128, 128, 255),
        (255, 85, 85, 255),
        (255, 0, 0, 255),
        (170, 0, 0, 255),
        (128, 0, 0, 255),
        (85, 0, 0, 220)
    ]

    def Color4B24F(self, color4B):
        return map(lambda x: x/255.0, color4B)

    def __init__(self, numBits):
        super(BitPattern, self).__init__()
        w,h = director.get_window_size()
        bitSize = w/numBits
        self.bits = [ Square(self.Color4B24F(BitPattern.colors[i]), i*bitSize, 0, bitSize) for i in range(0,numBits) ]
        for i in range(0, numBits):
            self.bits[i].setBitNumber(i)
            self.add(self.bits[i])
        self.position = 0, h-bitSize

    def toggleBit(self, bitNum):
        self.bits[bitNum].layer_color = (0, 0, 0, 0)
        self.bits[bitNum].label.element.color = (255, 255, 255, 255)

    def handleClick(self, x, y):
        for i in range(0, len(self.bits)):
            x_in_node = x-self.x
            y_in_node = y-self.y
            if self.bits[i].isPointInside(x_in_node, y_in_node):
                self.toggleBit(i)