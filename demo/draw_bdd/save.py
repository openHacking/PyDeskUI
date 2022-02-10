from PIL import ImageGrab
import os

def save_image(root,widget):
    root.update()
    x=root.winfo_rootx()+widget.winfo_x()
    y=root.winfo_rooty()+widget.winfo_y()

    x1=x+widget.winfo_width()
    y1=y+widget.winfo_height()
    offset = 4
    ImageGrab.grab().crop((x + offset,y + offset,x1 - offset,y1 - offset)).save(os.getcwd() + "\\bdd.png", "PNG")