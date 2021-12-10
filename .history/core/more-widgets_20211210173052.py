# Basic Widgets,reference https://tkdocs.com/tutorial/morewidgets.html

from tkinter import *
from tkinter import ttk

root = Tk()

root.title("More Widgets")

# create content frame
mainFrame = ttk.Frame(root,padding='3 3 12 12')
mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))

# The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)


################################################ Listbox


choices = ["apple", "orange", "banana"]
choicesvar = StringVar(value=choices)
l = Listbox(mainFrame, listvariable=choicesvar)

# add more item
choices.append("peach")
choicesvar.set(choices)



def updateDetails(s):
    print('select',l.get(s))

l.bind("<<ListboxSelect>>", lambda e: updateDetails(l.curselection()))

# place to grid
l.grid(column=0,row=0,sticky=(W,E))

root.mainloop()


