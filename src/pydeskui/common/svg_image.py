import io
import os
import tksvg
from lxml import etree
# reference: https://shayallenhill.com/svg-with-css-in-python/
# https://github.com/israel-dryer/tkfontawesome

class SVGImage():
    """Transform a svg file to Image instance.

    Attributes:
        source: SVG content string.
    """
    def __init__(self,path):
        """
        Args:
            path: File path or svg content.
        """
        self.source = self.path_to_string(path)
         # parse xml data
        self.root = etree.fromstring(self.source)
        self.tree = etree.ElementTree(self.root)

    def get_image(self,fill=None, scale_to_width=None, scale_to_height=None, scale=1):
        """
        Args:
            fill: SVG color
            scale_to_with: target width
            scale_to_height: target height
            scale: Required scale factor
        """
        # set path fill color if provided
        if fill is not None:
            self.root.attrib["fill"] = fill

        imgdata = io.BytesIO()
        self.tree.write(imgdata)
        kw = {"data": imgdata.getvalue()}
        if scale_to_width:
            kw["scaletowidth"] = scale_to_width
        if scale_to_height:
            kw["scaletoheight"] = scale_to_height
        if scale != 1:
            kw["scale"] = scale

        return tksvg.SvgImage(**kw)

    def path_to_string(self,path):
        if os.path.isfile(path):
            f = open(path,'r')
            return f.read()
        else:
            return path
        
