from tkinter import *
from tkinter import ttk

# reference: https://tkdocs.com/tutorial/
# record https://tkdocs.com/tutorial/firstexample.html

## 01 test pop up
# tkinter._test()

## 02 hello world 
# root = Tk()
# ttk.Button(root,text="Hello World").grid()
# root.mainloop()

# 03 real example,convert a distance in feet to the equivalent distance in meters
class FeetToMeters:
    def __init__(self,root):
        # set title
        root.title("Feet to Meters")

        # create content frame
        mainFrame = ttk.Frame(root,padding='3 3 12 12')
        mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))

        # The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        # set feet input
        self.feet = StringVar()
        feet_entry = ttk.Entry(mainFrame,width=7,textvariable=feet)
        feet_entry.grid(column=2,row=1,sticky=(W,E))

        # set meter label,to calculated result
        self.meters = StringVar()
        ttk.Label(mainFrame,textvariable=self.meters).grid(column=2,row=2,sticky=(W,E))

        # set calculate button
        ttk.Button(mainFrame,text="Calculate",command=self.calculate).grid(column=3,row=3,sticky=W)

        # set feet/is equivalent to/meters label
        ttk.Label(mainFrame,text="feet").grid(column=3,row=1,sticky=W)
        ttk.Label(mainFrame,text="is equivalent to").grid(column=1,row=2,sticky=E)
        ttk.Label(mainFrame,text="meters").grid(column=3,row=2,sticky=W)

        # set padding
        for child in mainFrame.winfo_children():
            child.grid_configure(padx=5,pady=5)

        # auto focus feet input
        feet_entry.focus()
        # bind keyboard Enter,trigger calculate
        root.bind("<Return>",self.calculate)

    def calculate(self,*args):
        try:
            value = float(self.feet.get())
            self.meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
        except ValueError:
            pass

# sets up the main application window
root = Tk()
# init function
FeetToMeters(root)
# necessary for everything to appear onscreen and allow users to interact with it.
root.mainloop()

