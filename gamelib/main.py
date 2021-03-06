'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data
import mainmenu
import cocos
from gamelib import Inventory

def main():
    print "Hello from your game's main()"
    print data.load('sample.txt').read()
        # director init takes the same arguments as pyglet.window
    cocos.director.director.init(320, 480)

    # if Inventory.data['userdata']['IsFirstRun']:
    #     #TODO: take them through the story.
    #
    # else:
    # We create a new layer, an instance of HelloWorld
    hello_layer = mainmenu.MainMenu() #gameplay.GamePlay()

    # A scene that contains the layer hello_layer
    main_scene = cocos.scene.Scene (hello_layer)

    # And now, start the application, starting with main_scene
    cocos.director.director.run (main_scene)
