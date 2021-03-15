from tkinter import Tk, Canvas, Label, Menu, OUTSIDE
import configparser

import paho.mqtt.client as mqtt


class WindowDraggable():
    def __init__(self, label):
        self.label = label
        label.bind('<ButtonPress-1>', self.StartMove)
        label.bind('<ButtonRelease-1>', self.StopMove)
        label.bind('<B1-Motion>', self.OnMotion)

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self,event):
        x = (event.x_root - self.x)
        y = (event.y_root - self.y)
        master.geometry("+%s+%s" % (x, y))


def init_config(path):
    config.optionxform = str
    config.read(path)


def on_message(client, userdata, message):
    temp.config(text=conf['general']['pred']
                    +str(message.payload.decode("utf-8"))
                    +conf['general']['post'])


def activate_menu(event):
    posx =  event.x_root
    posy =  event.y_root
    menu = Menu(master, tearoff = 0)
    menu.add_command(label = 'Quit', command = quit)
    menu.tk_popup(posx, posy)


def quit():
    master.quit()
    master.destroy()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    path = './settings.ini'
    init_config(path)
    conf = {}
    for section in config.sections():
        conf.update({section.lower():dict(config[section])})
    master = Tk()
    master.overrideredirect(1)
    master.geometry('%sx%s+%s+%s' % (conf['general']['width'],
                                    conf['general']['height'],
                                    conf['general']['posx'],
                                    conf['general']['posy']))

    w = Canvas(master, highlightthickness=0, relief='ridge')
    w.pack()
    temp = Label(w, text='',
                    font=(conf['general']['font'],
                    int(conf['general']['size'])),
                    bg=conf['general']['bgcolor'],
                    fg=conf['general']['color'])
    temp.place(bordermode=OUTSIDE,
                height=conf['general']['height'],
                width=conf['general']['width'])
    if conf['general']['draggable'] == '1':
        WindowDraggable(temp)
    temp.bind("<Button-3>", activate_menu)

    try:
        client = mqtt.Client()
        client.on_message=on_message
        client.username_pw_set(username=conf['mqtt']['username'],
                               password=conf['mqtt']['password'])
        client.connect(conf['mqtt']['ip'],
                        int(conf['mqtt']['port']),
                        int(conf['mqtt']['timeout']))
        client.subscribe(conf['mqtt']['topic'])
        client.loop_start()
    except:
        temp.config(text='No signal')

    master.mainloop()
