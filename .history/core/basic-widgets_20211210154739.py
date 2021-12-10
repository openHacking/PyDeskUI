# Basic Widgets,reference https://tkdocs.com/tutorial/widgets.html

from tkinter import *
from tkinter import ttk

root = Tk()

root.title("Basic Widgets")

# create content frame
mainFrame = ttk.Frame(root,padding='3 3 12 12')
mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))

# The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)


root.mainloop()