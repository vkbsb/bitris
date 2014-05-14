import cocos
from cocos.director import director

class Results(cocos.layer.Layer):
    def __init__(self, dic = ['test', 1, 'test2', 3]):
        super(Results, self).__init__()
        (w,h) = director.get_window_size()
        i = 0
        for key in xrange(len(dic)/2):
            keymsg = cocos.text.Label(dic[i],
                        font_name='Nokia Cellphone',
                         font_size=18,
                         anchor_x='right', anchor_y='center')
            keymsg.position = w/2, h - (i+5)*10

            valuemsg =  cocos.text.Label(str(dic[i+1]),
                        font_name='Nokia Cellphone',
                         font_size=18,
                         anchor_x='left', anchor_y='center')
            valuemsg.position = w/2, h - (i+5)*10

            i += 2
            self.add(keymsg)
            self.add(valuemsg)