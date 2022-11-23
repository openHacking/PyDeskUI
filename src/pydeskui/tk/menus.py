# reference: https://tkdocs.com/tutorial/menus.html

from tkinter import *
root = Tk()
# menu = Menu(root)

###################################### Menubars
# Creating a Menubar
win = Toplevel(root)
menubar = Menu(win)
win['menu'] = menubar

# Adding Menus
menu_file = Menu(menubar)
menu_edit = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_edit, label='Edit')

# Adding Menu Items
def newFile():
    print('new file')
def openFile():
    print('open file')
def closeFile():
    print('close file')
menu_file.add_command(label='New', command=newFile)
menu_file.add_command(label='Open...', command=openFile)
menu_file.add_separator() # Separators
menu_file.add_command(label='Close', command=closeFile)

# Submenus
# menu_recent = Menu(menu_file)
# menu_file.add_cascade(menu=menu_recent, label='Open Recent')
# for f in recent_files:
#     menu_recent.add_command(label=os.path.basename(f), command=lambda f=f: openFile(f))

############################################ Contextual Menus
# for i in ('One', 'Two', 'Three'):
#     menu.add_command(label=i)
# if (root.tk.call('tk', 'windowingsystem') == 'aqua'):
#     root.bind('<2>', lambda e: menu.post(e.x_root, e.y_root))
#     root.bind('<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
# else:
#     root.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))
root.mainloop()
