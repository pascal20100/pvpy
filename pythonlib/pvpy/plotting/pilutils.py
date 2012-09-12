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
    
    image_matrix must be a ist of list or a 2d (or more) ndarray. Each of its elements can be either
    a PIL image, or an image filepath. These will be painted on a nrows x ncols grid of equal size boxes.
    Similarly, label_matrix can be provided as a list of list of strings or a 2d ndarrayof strings."""

    image_matrix = np.array(image_matrix)
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
                if type(imagette) is str or type(imagette) is np.string_:
                    imagette = Image.open(str(imagette))
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
        raise ValueError("row_lables notyet supported")

    if output_filename is not None:
        img.save(output_filename)

    return img
