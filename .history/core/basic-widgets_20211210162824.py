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

button = ttk.Button(mainFrame, text='Button', default="active",command=submitForm)

# bind keyboard Enter,trigger submit
root.bind('<Return>', lambda e: button.invoke())
# place to grid
button.grid(column=1,row=2,sticky=(W,E))



################################################ Checkbutton
def metricChanged():
    print('checkbutton',measureSystem.get())

measureSystem = StringVar()
check = ttk.Checkbutton(mainFrame, text='Use Metric', 
	    command=metricChanged, variable=measureSystem,
	    onvalue='metric', offvalue='imperial')

# place to grid
check.grid(column=2,row=2,sticky=(W,E))



################################################ Radiobutton
phone = StringVar()
home = ttk.Radiobutton(mainFrame, text='Home', variable=phone, value='home')
office = ttk.Radiobutton(mainFrame, text='Office', variable=phone, value='office')
cell = ttk.Radiobutton(mainFrame, text='Mobile', variable=phone, value='cell')

# place to grid
home.grid(column=1,row=3,sticky=(W,E))
office.grid(column=2,row=3,sticky=(W,E))
cell.grid(column=3,row=3,sticky=(W,E))



################################################ Entry
username = StringVar()
name = ttk.Entry(mainFrame, textvariable=username)

# Watching for Changes
def it_has_been_written(*args):
    print('input',username.get())
username.trace_add("write", it_has_been_written)

# place to grid
name.grid(column=1,row=4,sticky=(W,E))

# password
password = StringVar()
passwd = ttk.Entry(mainFrame, textvariable=password, show="*")

# place to grid
passwd.grid(column=2,row=4,sticky=(W,E))



################################################ Combobox
countryvar = StringVar()
country = ttk.Combobox(mainFrame, textvariable=countryvar)

# Predefined Values
country['values'] = ('USA', 'Canada', 'Australia')

# get selected value
def selected(event):
    print('select',event.widget.get())

# bind selected event
country.bind('<<ComboboxSelected>>', selected)

# place to grid
country.grid(column=1,row=5,sticky=(W,E))



root.mainloop()


