## pilutils.py
##
## Copyright (C) 2012 Pascal Vincent
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##
##  2. Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in the
##     documentation and/or other materials provided with the distribution.
##
##  3. The name of the authors may not be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR
## IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
## NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
## TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
##
## Author: Pascal Vincent


# PIL import
import Image, ImageDraw, ImageFont
import numpy
import math
import os

def pil_center_draw( draw, position, text, font):
    """Will draw a text string on a PIL ImageDraw context, centered on position (x,y) (both horizontally and vertically)"""
    x,y = position
    w,h = draw.textsize(text, font=font)
    draw.text( (x-w/2, y-h/2), text, font=font)

def locate_file(filenames, dirnames):
    """Takes a single filename or a list of filenames, and a list of dirnames.
    Will look for and return the first existing dirname/filename file.
    ~ can be used to denote the home directory."""
    
    if isinstance(filenames,str):
        filenames = [filenames]
    home = os.environ['HOME']
    for filename in filenames:
        for dirname in dirnames:
            fullpath = os.path.join(dirname, filename)
            if fullpath[0]=='~':
                fullpath = home+fullpath[1:]
            if os.path.exists(fullpath):
                return fullpath
    return None

def rescale_to_uint8_maxrange(x):
    """If dtype is already uint8, return as is without any processing.
    If not, x will first be converted to float64, rescaled to max range (min->0.0, max->255.0)
    and the result converted to uint8 and returned."""
    
    if x.dtype==numpy.uint8:
        return x
    else:
        x = x.astype(numpy.float64)
        xmin = numpy.min(x)
        xmax = numpy.max(x)
        x -= xmin
        if xmax>xmin: # to avoid division by 0
            x *= 255.0/(xmax-xmin)
    return x.astype(numpy.uint8)

def toImage(x):
    """
    Converts x into a PIL Image
    
    Recognized types and associated behavior:
    Image: return as is
    str or numpy.string_: considered as a filepath from which to load the Image
    1d numpy.ndarray : first reshaped into 2d by taking square root, the considered grayscale imagette
    2d numpy.ndarray : grayscale image 
    3d numpy.ndarray : RGB image
    If not already of dtype uint8, the ndarrays will be converted to uint8 after rescaling to maximal range, i.e. min->0 max->255
    """

    if isinstance(x, Image.Image):
        return x    

    elif isinstance(x, str): # interpret as image file path
        x = Image.open(str(x))

    elif isinstance(x, numpy.ndarray):
        x = rescale_to_uint8_maxrange(x) # transform into uint8 if not already, rescaling to maximal range, i.e. min->0 max->255.
        d = len(x.shape)
        if d==1: # 1d: interpret as flattened square grayscale
            height = int(math.sqrt(x.shape[0]))
            x = x.reshape((height,height))
        if d==2: # 2d: Grayscale
            x = Image.fromarray(x, mode='L')
        elif d==3: # RGB
            if x.shape[2]!=3:
                if x.shape[0]==3: # Make first dimension the 3rd
                    x = x.swapaxes(0,2).swapaxes(0,1)
                else:
                    raise ValueError("3d RGB array must have either its 3rd dimension or its first equal 3 for the R,G,B channels")
            x = Image.fromarray(x, mode='RGB')
        else:
            raise ValueError("ndarray must be of dimension 1, 2, or 3")

    return x



    
def draw_image_matrix(image_matrix, label_matrix=None,
                      boxwidth=200, boxheight=200, boxmargin=5,
                      figtitle="", col_labels=None, row_labels=None,
                      topmargin = 100, leftmargin = 100, rightmargin = 100, bottommargin = 100,                      
                      keep_aspect_ratio=True,
                      label_font_size = 24,
                      title_font_size = 36,
                      output_filename=None):
    """
    Builds ans returns a PIL Image composed from a matrix of imagettes and optional underlying imagette labels.
    
    image_matrix must be a ist of list or a 2d (or more) ndarray. Each image_matrix[i][j] can be either
    a PIL Image, or a string representing an image filepath, or a 2d ndarray (considered grayscale image)
    or a 3d ndarray whose 3rd (or 1st) dimension is 3 represneting RGB image data,
    or a 1D ndarray that will be considered a flattened 2D grayscale image.
    These will be painted on a nrows x ncols grid of equal size boxes.
    Similarly, label_matrix can be provided as a list of list of strings or a 2d ndarray of strings."""

    image_matrix = numpy.array(image_matrix)
    nrows = len(image_matrix)
    ncols = len(image_matrix[0])
    img_height = topmargin + nrows*boxwidth + bottommargin
    img_width  = leftmargin + ncols*boxheight + rightmargin

    boxh = boxheight-2*boxmargin
    boxw = boxwidth-2*boxmargin

    img = Image.new('RGB',(img_width,img_height))    
    draw = ImageDraw.Draw(img)
    font_file = locate_file(["Times New Roman.ttf","DejaVuSerif.ttf","Arial.ttf"],
                            ["/Library/Fonts","/usr/share/fonts","/usr/share/fonts/dejavu","C:\\Windows\\fonts","~/fonts"])
    labelfont = ImageFont.truetype(font_file, label_font_size)
    titlefont = ImageFont.truetype(font_file, title_font_size)
    # titlefont = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf",25)
    # labelfont = ImageFont.load_default()
    # titlefont = ImageFont.load_default()
    # titlefont = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf",25)
    
    for i in xrange(nrows):
        for j in xrange(ncols):
            imagette = image_matrix[i][j]
            if imagette is not None:
                imagette = toImage(imagette)                
                # print "type and size of imagette", type(imagette), imagette.size
                if not keep_aspect_ratio:
                    imagette = imagette.resize( (boxw, boxh) )
                else:
                    w,h = imagette.size
                    if w*boxh/h>boxw:
                        imagette = imagette.resize( (boxw, h*boxw/w) )
                    else:
                        imagette = imagette.resize( (w*boxh/h, boxw) )
                    w,h = imagette.size
                x = leftmargin+j*boxwidth+boxmargin+(boxw-w)/2
                y = topmargin+i*boxheight+boxmargin+(boxh-h)/2
                img.paste(imagette, (x,y) )

            if label_matrix is not None:
                label = label_matrix[i][j]
                if label is not None:
                    x = leftmargin+j*boxwidth+boxwidth/2
                    y = topmargin+(i+1)*boxheight
                    pil_center_draw( draw, (x,y), str(label), labelfont)

    if figtitle is not None:
            pil_center_draw( draw, (img_width/2, topmargin/4), figtitle, titlefont)
            
    if col_labels is not None:
        for j in xrange(ncols):
            x = leftmargin+j*boxwidth+boxwidth/2
            y = 3*topmargin/4
            pil_center_draw( draw, (x,y), col_labels[j], labelfont)
    
    if row_labels is not None:
        raise ValueError("row_labels not yet supported")

    if output_filename is not None:
        img.save(output_filename)

    return img
