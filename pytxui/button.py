from textwrap import fill
from tkinter import *
import tkinter as tk
import tkinter.font as font
from pytxui.common.const import *
from pytxui.common.util import hex_to_rgb,interpolate
from pytxui.common.svg_image import SVGImage

# reference https://stackoverflow.com/a/34466743
class TxButton(Frame):
    def __init__(self,*args, **kwargs):

        # reference:How to change border color in Tkinter widget? https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/
        Frame.__init__(self)

        type_style =  {
            'default':{
              'background':THEME_COLOR_BACKGROUND,
              'hoverBackground':THEME_COLOR_BACKGROUND,
              'foreground':THEME_COLOR_FONT,
              'hoverForeground':THEME_COLOR_PRIMARY_HOVER,
              'text':'Default Button',
              'borderColor':THEME_COLOR_PRIMARY_HOVER
            },
            'primary':{
              'background':THEME_COLOR_PRIMARY,
              'hoverBackground':THEME_COLOR_PRIMARY_HOVER,
              'foreground':THEME_COLOR_BACKGROUND,
              'hoverForeground':THEME_COLOR_BACKGROUND,
              'text':'Primary Button',
              'borderColor':THEME_COLOR_PRIMARY
            },
            'text':{
              'background':THEME_COLOR_BACKGROUND,
              'hoverBackground':THEME_COLOR_GRAY,
              'foreground':THEME_COLOR_FONT,
              'hoverForeground':THEME_COLOR_FONT,
              'text':'Text Button',
              'borderColor':THEME_COLOR_BACKGROUND
            },
            'link':{
              'background':THEME_COLOR_BACKGROUND,
              'hoverBackground':THEME_COLOR_BACKGROUND,
              'foreground':THEME_COLOR_PRIMARY,
              'hoverForeground':THEME_COLOR_PRIMARY_HOVER,
              'text':'Link Button',
              'borderColor':THEME_COLOR_BACKGROUND
            },
        }
        
        width = 0
        height = 0
        padx = {
          'small':4,
          'middle':6,
          'large':6,
        }
        pady = {
          'small':2,
          'middle':6,
          'large':8,
        }

        fontsize = {
          'small':10,
          'middle':10,
          'large':12,
        }
        self.type = kwargs.get('type','default')
        self.size = kwargs.get('size','middle')
        self.background = kwargs.get('background',type_style[self.type]['background'])
        self.hoverBackground = kwargs.get('hoverBackground',type_style[self.type]['hoverBackground'])
        self.foreground = kwargs.get('foreground',type_style[self.type]['foreground'])
        self.hoverForeground = kwargs.get('hoverForeground',type_style[self.type]['hoverForeground'])
        self.fontsize = kwargs.get('fontsize',fontsize[self.size]) 
        self.fontfamily = kwargs.get('fontfamily',"Microsoft YaHei") 
        self.text = kwargs.get('text',type_style[self.type]['text'])
        self.width = kwargs.get('width',width) # default width, fit content 
        self.height = kwargs.get('height',height) # default height, fit content 
        self.padx = kwargs.get('padx',padx[self.size]) 
        self.pady = kwargs.get('pady',pady[self.size]) 
        self.relief = kwargs.get('relief','solid') 
        self.borderwidth = kwargs.get('borderwidth',1) 
        self.anchor = kwargs.get('anchor','center') 
        self.justify = kwargs.get('justify','center')
        self.borderColor = kwargs.get('borderColor',type_style[self.type]['borderColor'])
        self.borderRadius = kwargs.get('borderRadius',4)
        
        icon_path = kwargs.get('icon')
        self.image = ''
        if icon_path != None:
          #  Creating a photoimage object to use image
          self.imgIns = SVGImage(path=icon_path)
          self.image = self.imgIns.get_image(fill=self.foreground,scale=0.1)

        # Label Widget inside the Frame
        label = Label(self)

        self.label = label
        
        # Place the widgets with border Frame
        label.grid(padx=self.borderwidth, pady=self.borderwidth)

        # set Frame style
        self.config(background=self.borderColor)

        label.bind("<Enter>", self.changeBGEnter)
        label.bind("<Leave>", self.changeBGLeave)
        label.bind("<Button-1>",kwargs.get('command',self.handleClickDefault) )

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
            borderwidth=0,
            cursor='hand2',
            image = self.image,  # must use image reference
            compound = LEFT
        )
        
    def changeBGEnter(self,event):

        self.transition_colors = {
          'background':(hex_to_rgb(self.background),hex_to_rgb(self.hoverBackground)),
          'foreground':(hex_to_rgb(self.foreground),hex_to_rgb(self.hoverForeground)),
          'image':(hex_to_rgb(self.foreground),hex_to_rgb(self.hoverForeground)),
        }
        self.transition()

    def changeBGLeave(self, event):
        self.transition_colors = {
          'background':(hex_to_rgb(self.hoverBackground),hex_to_rgb(self.background)),
          'foreground':(hex_to_rgb(self.hoverForeground),hex_to_rgb(self.foreground)),
          'image':(hex_to_rgb(self.hoverForeground),hex_to_rgb(self.foreground)),
        }
        self.transition()
    
    def handleClickDefault(self, event):
        print('click')

    def transition(self):
        # smooth fade in transition at a rate of 60 fps and a duration of 110ms
        self.duration_ms = 100
        self.frames_per_second = 60
        self.ms_sleep_duration = self.duration_ms // self.frames_per_second
        self.current_step = 0

        self.update_label()

    # https://stackoverflow.com/a/57338561
    def update_label(self):

        t = (1.0 / self.frames_per_second) * self.current_step
        self.current_step += 1

        dic = {}
        for attr in self.transition_colors:
            new_color = interpolate(self.transition_colors[attr][0], self.transition_colors[attr][1], t)
            new_color = "#%02x%02x%02x" % new_color
            if attr == 'image':
              if self.image != '':
                self.image = self.imgIns.get_image(fill=new_color,scale=0.1)
                dic[attr] = self.image
            else:
              dic[attr] = new_color

        self.label.configure(dic)

        if self.current_step <= self.frames_per_second:
            self.after(self.ms_sleep_duration, self.update_label)


# add border radius, https://github.com/ParthJadhav/Tkinter-Designer/issues/31#issuecomment-862535324
# The border is rounded. On the Windows platform, there will be jagged edges. Rounded corners are not recommended.
class TxRoundedButton(tk.Canvas):
  def __init__(self, parent, border_radius, padding, color, text='Rounded Button', command=None):
    tk.Canvas.__init__(self, parent, borderwidth=0,
                       relief="flat", highlightthickness=0, bg=parent["bg"])
    self.command = command
    font_size = 26
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

