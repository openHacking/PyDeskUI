from tkinter import *
from tkinter import ttk

# reference: https://tkdocs.com/tutorial/

## 01 test pop up
# tkinter._test()

## 02 hello world 
# root = Tk()
# ttk.Button(root,text="Hello World").grid()
# root.mainloop()

# 03 real example,convert a distance in feet to the equivalent distance in meters
def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

root = Tk()
root.title("Feet to Meters")

mainFrame = ttk.Frame(root,padding='3 3 12 12')