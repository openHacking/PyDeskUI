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

################################################ Label text
label = ttk.Label(mainFrame, text='Full name:')

# Displaying Text
resultsContents = StringVar()
label['textvariable'] = resultsContents
resultsContents.set('Label text')

# place to grid
label.grid(column=1,row=1,sticky=(W,E))

################################################ Label image
labelImage = ttk.Label(mainFrame, text='Full name:')

# Displaying Images
image = PhotoImage(file='./core/assets/img/logo.png')
labelImage['image'] = image

# place to grid
labelImage.grid(column=2,row=1,sticky=(W,E))

################################################ Button
def submitForm():
    print('submit')
button = ttk.Button(mainFrame, text='Button', command=submitForm)

# place to grid
button.grid(column=1,row=2,sticky=(W,E))


root.mainloop()