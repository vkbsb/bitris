import pyglet
import data
import inventory

#add the data folder to the fonts so that we get all .ttfs
pyglet.font.add_directory(data.data_dir)
pyglet.resource.path.append(data.data_dir)
pyglet.resource.reindex()

#laod the inventory into config.
Inventory = inventory.GameInventory()