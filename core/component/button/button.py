from tkinter import *
from tkinter import ttk
# reference https://stackoverflow.com/a/34466743
class TxButton(Frame):
    def __init__(self,*args, **kwargs):

        # reference:How to change border color in Tkinter widget? https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/
        Frame.__init__(self)

        self.background = kwargs.get('background',"#1890ff")
        self.hoverBackground = kwargs.get('hoverBackground',"#40a9ff")
        self.foreground = kwargs.get('foreground',"#fff")
        self.fontsize = kwargs.get('fontsize',12) 
        self.fontfamily = kwargs.get('fontfamily',"Microsoft YaHei") 
        self.text = kwargs.get('text',"Primary Button")
        self.width = kwargs.get('width',0) # default width, fit content 
        self.height = kwargs.get('height',0) # default height, fit content 
        self.padx = kwargs.get('padx',10) 
        self.pady = kwargs.get('pady',10) 
        self.relief = kwargs.get('relief','solid') 
        self.borderwidth = kwargs.get('borderwidth',1) 
        self.anchor = kwargs.get('anchor','center') 
        self.justify = kwargs.get('justify','center')
        self.borderColor = kwargs.get('borderColor','#fff')
        self.borderRadius = kwargs.get('borderRadius',4)

        # Label Widget inside the Frame
        label = Label(self)

        self.label = label
        
        # Place the widgets with border Frame
        label.grid(padx=self.borderwidth, pady=self.borderwidth)

        # set Frame style
        self.config(background=self.borderColor)

        label.bind("<Enter>", self.changeBGEnter)
        label.bind("<Leave>", self.changeBGLeave)
        label.bind("<Button-1>",kwargs.get('handleClick',self.handleClickDefault) )

        # set Label style
        label.config(
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
            borderwidth=0
        )

        # add border radius, https://github.com/ParthJadhav/Tkinter-Designer/issues/31#issuecomment-862535324
        
    def changeBGEnter(self,event):
        self.label.config(background=self.hoverBackground,foreground=self.foreground)

    def changeBGLeave(self, event):
        self.label.config(background=self.background,foreground=self.foreground)
    
    def handleClickDefault(self, event):
        print('click')

from tkinter import *
import tkinter as tk
import tkinter.font as font

class RoundedButton(tk.Canvas):
  def __init__(self, parent, border_radius, padding, color, text='', command=None):
    tk.Canvas.__init__(self, parent, borderwidth=0,
                       relief="flat", highlightthickness=0, bg=parent["bg"])
    self.command = command
    font_size = 16
    self.font = font.Font(size=font_size, family='Helvetica', weight="bold")
    self.id = None
    height = font_size+(2*padding)
    width = self.font.measure(text)+(4*padding)
    width = width if width >= 80 else 80

    if border_radius > 0.5*width:
      print("Error: border_radius is greater than width.")
      return None

    if border_radius > 0.5*height:
      print("Error: border_radius is greater than height.")
      return None

    rad = 2*border_radius

    def shape():
      self.create_arc((0, rad, rad, 0),
                      start=90, extent=90, fill=color, outline=color)
      self.create_arc((width-rad, 0, width,
                        rad), start=0, extent=90, fill=color, outline=color)
      self.create_arc((width, height-rad, width-rad,
                        height), start=270, extent=90, fill=color, outline=color)
      self.create_arc((0, height-rad, rad, height), start=180, extent=90, fill=color, outline=color)
      return self.create_polygon((0, height-border_radius, 0, border_radius, border_radius, 0, width-border_radius, 0, width,
                           border_radius, width, height-border_radius, width-border_radius, height, border_radius, height), fill=color, outline=color)

    id = shape()
    (x0, y0, x1, y1) = self.bbox("all")
    width = (x1-x0)
    height = (y1-y0)
    self.configure(width=width, height=height)
    self.create_text(width/2, height/2,text=text, fill='white', font= self.font)
    self.bind("<ButtonPress-1>", self._on_press)
    self.bind("<ButtonRelease-1>", self._on_release)

  def _on_press(self, event):
      self.configure(relief="sunken")

  def _on_release(self, event):
      self.configure(relief="raised")
      if self.command is not None:
          self.command()


class TxCanvas(tk.Canvas):
    def __init__(self,parent,*args, **kwargs):

        tk.Canvas.__init__(self,parent,borderwidth=0, highlightthickness=0,bg=parent["bg"])
        
        border_radius = 8
        padding = 5
        color = 'green'
        text='OOKK'
        font_size = 16

        self.font = font.Font(size=font_size, family='Helvetica', weight="bold")
        self.id = None
        height = font_size+(2*padding)
        width = self.font.measure(text)+(4*padding)
        width = width if width >= 80 else 80

        if border_radius > 0.5*width:
            print("Error: border_radius is greater than width.")
            return None

        if border_radius > 0.5*height:
            print("Error: border_radius is greater than height.")
            return None

        rad = 2*border_radius

        def shape():
            self.create_arc((0, rad, rad, 0),
                            start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-rad, 0, width,
                                rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width, height-rad, width-rad,
                                height), start=270, extent=90, fill=color, outline=color)
            self.create_arc((0, height-rad, rad, height), start=180, extent=90, fill=color, outline=color)
            return self.create_polygon((0, height-border_radius, 0, border_radius, border_radius, 0, width-border_radius, 0, width,
                                border_radius, width, height-border_radius, width-border_radius, height, border_radius, height), fill=color, outline=color)

        id = shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.create_text(width/2, height/2,text='OK', fill='green',font= self.font)