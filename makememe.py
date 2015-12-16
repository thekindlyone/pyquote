from __future__ import division
from PIL import ImageFont, Image, ImageDraw, ImageOps
from image_utils import ImageText
import os
def make_meme(infile,text,url):
    # text=unidecode(text)
    maxwidth,maxheight = 640.0,480.0
    try:
        page = Image.open(infile)
    except Exception as e:
        print e,url
        os.remove(infile)
        return False
    page=page.convert('RGB')
    ratio = min(maxwidth/page.size[0], maxheight/page.size[1])
    page.thumbnail((int(page.size[0]*ratio),int(page.size[1]*ratio)), Image.ANTIALIAS)
    w,h=page.size
#     print w,h
    rs = []
    gs = []
    bs = []
    for y in range(10):
        for x in range(page.size[0]):
#             print page.getpixel((x, page.size[1]-1-y))
            r, g, b = page.getpixel((x, page.size[1]-1-y))
            rs.append(r)
            bs.append(g)
            gs.append(g)
    bkcolor = tuple(map(lambda l:sum(l)/len(l),[rs,gs,bs]))
    r,g,b=bkcolor

    magic_no = ((r*299)+(g*587)+(b*114))/1000
    fgcolor= (0,0,0) if magic_no >=128 else (255,255,255)
    bkcolor = tuple(map(int, bkcolor))

    # if sum(bkcolor) >30:
    #     magic_number=max(bkcolor)+min(bkcolor)
    #     fgcolor = tuple(map(lambda x:magic_number-x,bkcolor))   
    # else:
    #     fgcolor=255,255,255


    temp=ImageText((w, 1000), background=bkcolor)

    width,height=temp.write_text_box((5,0), text, box_width=w-3, font_filename='Times_New_Roman.ttf',font_size=25, color=fgcolor)
    textbox=temp.image.crop( (0,0,width,height+50) )
    output=Image.new("RGB", (width,h+height+50),bkcolor)
    output.paste(page,(0,0))
    output.paste(textbox,(0,h))
    output.save(infile)
    page.close()
    output.close()
    return True