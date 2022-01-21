import os
from tkinter import *
from tkinter import ttk
import subprocess
# from button import CustomButton

# reference https://stackoverflow.com/a/34466743
class CustomButton(Label):

    def __init__(self, *args, **kwargs):
        # TODO: Create a Frame for border https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/

        # Create a Frame for border
        border_color = Frame(root, background="red")
        
        Label.__init__(self)
        
        # Label Widget inside the Frame
        label = Label(border_color, text="This is a Label widget", bd=0)
        
        # Place the widgets with border Frame
        label.pack(padx=1, pady=1)

        
        self.bind("<Enter>", self.changeBGEnter)
        self.bind("<Leave>", self.changeBGLeave)
        self.bind("<Button-1>",kwargs.get('handleClick',self.handleClickDefault) )

        self.background = kwargs.get('background',"#1890ff")
        self.hoverBackground = kwargs.get('hoverBackground',"#40a9ff")
        self.foreground = kwargs.get('foreground',"#fff")
        self.fontsize = kwargs.get('fontsize',14) 
        self.fontfamily = kwargs.get('fontfamily',"微软雅黑") 
        self.text = kwargs.get('text',"Button") 
        self.width = kwargs.get('width',30) 
        self.padx = kwargs.get('padx',10) 
        self.pady = kwargs.get('pady',10) 
        self.relief = kwargs.get('relief','solid') 
        self.borderwidth = kwargs.get('borderwidth',1) 
        self.anchor = kwargs.get('anchor','center') 
        self.justify = kwargs.get('justify','center') 

        self.config(
            anchor=self.anchor,  # Where to anchor the text in the widget
            justify=self.justify,
            background=self.background,
            foreground=self.foreground,
            font=(self.fontfamily, self.fontsize),
            text=self.text,
            relief=self.relief,
            width=self.width,
            padx=self.padx,
            pady=self.pady,
            borderwidth=self.borderwidth
        )

    def changeBGEnter(self,event):
        self.config(background=self.hoverBackground,foreground=self.foreground)

    def changeBGLeave(self, event):
        self.config(background=self.background,foreground=self.foreground)
    
    def handleClickDefault(self, event):
        print('click')


class Win:
    def __init__(self,root):
        # set title
        root.title("test button")

        # screen width
        sw = root.winfo_screenwidth()
        # screen height
        sh = root.winfo_screenheight()
        # frame width
        ww = 380
        # frame height
        wh = 180
        x = (sw-ww) / 2
        y = (sh-wh) / 2 - 20

        root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))
        root.resizable(False, False)
        root.config(background="white")
        
        # create content frame
        mainFrame = ttk.Frame(root,padding='20 20 20 20')
        mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))
        # The columnconfigure/rowconfigure bits tell Tk that the frame should expand to fill any extra space if the window is resized.
        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        # default button style
        defaultButton = CustomButton(root, text="button one",handleClick=self.useClassic)
        defaultButton.grid(column=0, row=0, columnspan=2, sticky=(N, W), padx=5,pady=20)

        # custom button style
        customButton = CustomButton(root, text="button two",foreground='#1a1a1a',hoverBackground="#ede9e5",background='#fcfbfa',handleClick=self.useDefault)
        customButton.grid(column=0, row=1, columnspan=2, sticky=(N, W), padx=5,pady=20)

        # Create a Frame for border
        # border_color = Frame(root, background="red")
        
        
        # border_color.grid(column=0, row=2, columnspan=2, sticky=(N, W), padx=5,pady=20)
        # border_color.pack(padx=40, pady=40)

        # frame = ttk.Frame(root, width = 202, height = 32, back, highlightcolor="red", highlightthickness=1, bd=0)
        # l = Entry(frame, borderwidth=0, relief="flat", highlightcolor="green")
        # # l.place(width=200, height=30)
        # frame.grid(column=0, row=2, columnspan=2, sticky=(N, W), padx=5,pady=20)
    # exec bat
    def useClassic(self,*args):

        print('click one')

    def useDefault(self,*args):

        print('click two')

# sets up the main application window
root = Tk()
# init function
Win(root)
# necessary for everything to appear onscreen and allow users to interact with it.
root.mainloop()
