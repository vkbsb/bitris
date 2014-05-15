import cocos
from powerups import PowerUpIndicator
from vfx import *
from cocos.director import director
from gamelib import Inventory

class MainMenu(cocos.layer.Layer):
    def __init__(self):
        super(MainMenu, self).__init__()

        self.infoShown = 0
        (w, h) = director.get_window_size()
        #create the menu for powerups.
        menu = cocos.menu.Menu()
        positions = []
        itemSize = w/3
        self.arr = [ 'AutoByte', 'BitAndOrder', 'ByteBlast' ]
        for i in xrange(3):
            positions.append((w/2-itemSize/2 + i*itemSize/2, h/2-itemSize))
        i = 0
        for position in positions:
            pup = Inventory.data['gameconfig'][self.arr[i]]
            costLabel = createLabel("<>" + str(pup['cost']), 18, (0, 0, 255, 255))
            costLabel.position = position[0]-itemSize/2 + i*itemSize/2, h/2 - itemSize/4
            self.add(costLabel)
            i += 1

        pup = Inventory.data['gameconfig'][self.arr[self.infoShown]]
        self.infoLabel = createLabel(pup['info'], 15, (0, 0, 255, 255))
        self.infoLabel.position = w/2, h/2 - itemSize/2
        self.add(self.infoLabel)

        layout_func = cocos.menu.fixedPositionMenuLayout(positions)
        l = []
        l.append(cocos.menu.ImageMenuItem('AutoByte.png', self.abClicked))
        l.append(cocos.menu.ImageMenuItem('BitAndOrder.png', self.baoClicked))
        l.append(cocos.menu.ImageMenuItem('ByteBlast.png', self.bbClicked))
        menu.create_menu(l, None, cocos.menu.zoom_out(), cocos.menu.shake(), layout_func)
        menu.scale = 2
        menu.position = 0, h/2
        self.add(menu)

    def updateInfoLabel(self):
        pup = Inventory.data['gameconfig'][self.arr[self.infoShown]]
        self.infoLabel.element.text = pup['info']

    #TODO: buy the powerup when the current info shown is same as the one clicked.
    def abClicked(self):
        self.infoShown = 0
        self.updateInfoLabel()

    def baoClicked(self):
        self.infoShown = 1
        self.updateInfoLabel()

    def bbClicked(self):
        self.infoShown = 2
        self.updateInfoLabel()