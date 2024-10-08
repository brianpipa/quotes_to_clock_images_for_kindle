# -*- coding: utf-8 -*-
from sys import argv, exit
from os import path
import csv
import datetime
try:
    from PIL import Image, ImageFont, ImageDraw
except ModuleNotFoundError:
    print("Please install Pillow!\nrun 'pip3 install pillow'")
    exit(1)

# options (these are constants)
csvpath = 'quotes.csv'      # csv file to read quotes from
imgdir = 'images/'                          # save location for images
imgformat = 'png'                           # format. jpeg is faster but lossy
imgsize = (600,800)                         # width/height of image
color_bg = 255                              # white. color for the background
color_norm = 125                            # grey. color for normal text
color_high = 0                              # black. color for highlighted text
fntname_norm = 'bookerly.ttf'               # font for normal text
fntname_high = 'bookerlybold.ttf'           # font for highlighted text
fntname_mdata = 'baskervilleboldbt.ttf'     # font for the author
fntsize_mdata = 25                          # fontsize for the author
use_regular_time = True                     # whether to use non-military time

# don't touch
imgnumber = 0
previoustime = ''


def TurnQuoteIntoImage(index:int, quote:str, author:str):

    incomingtime = convert_to_minutes(index) 

    time = incomingtime        

    if use_regular_time:
        time = timeConvert(time)

    timestring = "["+time+"] "
    quote = timestring + quote

    global imgnumber, previoustime
    savepath = imgdir
    quoteheight = 720
    quotelength = 570
    quotestart_y = 0
    quotestart_x = 20
    mdatalength = 450
    mdatastart_y = 785
    mdatastart_x = 585

    # create the object. mode 'L' restricts to 8bit greyscale
    paintedworld = Image.new(mode='L', size=(imgsize), color=color_bg)
    ariandel = ImageDraw.Draw(paintedworld)

    # draw the author name

    font_mdata = create_fnt(fntname_mdata, fntsize_mdata)

    if not author:
        author = "unknown"

    metadata = f'—{author.strip()}'
    # wrap lines into a reasonable length and lower the maximum height the
    # quote can occupy according to the number of lines the credits use
    if font_mdata.getlength(metadata) > mdatalength:
        metadata = wrap_lines(metadata, font_mdata, mdatalength - 30)
    for line in metadata.splitlines():
        mdatastart_y -= font_mdata.getbbox("A")[3] + 4
    quoteheight = mdatastart_y - 35
    mdata_y = mdatastart_y
    for line in metadata.splitlines():
        ariandel.text((mdatastart_x, mdata_y), line, color_high, font_mdata, anchor='rm')
        mdata_y += font_mdata.getbbox("A")[3] + 4

    # draw the quote (pretty)
    quote, fntsize = calc_fntsize(quotelength, quoteheight, quote, fntname_high)
    font_norm = create_fnt(fntname_norm, fntsize)
    font_high = create_fnt(fntname_high, fntsize)
    try:
        draw_quote(ariandel, (quotestart_x,quotestart_y), quote, timestring, font_norm, font_high)
    # warn and discard image if timestring is just not there
    except LookupError:
        print(f"WARNING: missing timestring at csv line {index+2}, skipping")
        return

    # increment a number if time is identical to the last one, so
    # images can't be overwritten
    # this assumes lines are actually chronological so inshallah
    if incomingtime == previoustime:
        imgnumber += 1
    else:
        imgnumber = 0
        previoustime = incomingtime
    incomingtime = incomingtime.replace(':','')
    savepath += f'quote_{incomingtime}_{imgnumber}.{imgformat}'
    savepath = path.normpath(savepath)
    paintedworld.save(savepath)


def draw_quote(drawobj, anchors:tuple, text:str, substr:str,
        font_norm:ImageFont.truetype, font_high:ImageFont.truetype):
    # draws text with substr highlighted. doesn't check if it will fit the
    # image or anything else
    start_x = anchors[0]
    start_y = anchors[1]

    # search for the substring as if text were a single line, and
    # mark its starting and ending position for the upcoming write loop
    flattened = text.replace('\n',' ')
    substr_starts = 0
    try:
        substr_starts = flattened.lower().index(substr.lower())
    except ValueError:
        raise LookupError
    substr_ends = substr_starts + len(substr)
    bookmark = '|'
    lines = text[:substr_starts]
    lines += f'{bookmark}{text[substr_starts:substr_ends]}{bookmark}'
    lines += text[substr_ends:]

    fntstyle_norm = (color_norm, font_norm)
    fntstyle_high = (color_high, font_high)
    current_style = fntstyle_norm
    marks_found = 0
    write = drawobj.text
    textlength = drawobj.textlength
    x = start_x
    y = start_y
    # this would be a LOT simpler if we didn't have to check the edges attached
    # to the substring. it might be easier to implement a char by char loop
    # in the future, using the kerning calculation method in this example:
    # https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.getlength
    for line in lines.splitlines():
        for word in line.split():
            word += ' '
            # if the entire substr is one contiguous word, split the
            # non-substr bits stuck to it and print the whole thing in 3 parts
            if word.count(bookmark) == 2:
                wordnow = word.split(bookmark)[0]
                write((x,y), wordnow, *fntstyle_norm)
                x += textlength(wordnow, font_norm)
                wordnow = word.split(bookmark)[1]
                write((x,y), wordnow, *fntstyle_high)
                x += textlength(wordnow, font_high)
                wordnow = word.split(bookmark)[2]
                write((x,y), wordnow, *fntstyle_norm)
                x += textlength(wordnow, font_norm)
                word = ''
            # otherwise change the default font, and wait for the next mark
            elif word.count(bookmark) == 1:
                marks_found += 1
                wordnow = word.split(bookmark)[0]
                word = word.split(bookmark)[1]
                write((x,y), wordnow, *current_style)
                x += textlength(wordnow, current_style[1])
                if marks_found == 1:
                    current_style = fntstyle_high
                else: # if marks == 2:
                    current_style = fntstyle_norm
            # this is the bit that actually does most of the writing
            write((x,y), word, *current_style)
            x += textlength(word, current_style[1])
        # the offset calculated by multiline_text (what we're trying to mimic)
        # is based on uppercase letter A plus 4 pixels for whatever fucking
        # reason. see https://github.com/python-pillow/Pillow/discussions/6620
        y += font_norm.getbbox("A")[3] + 4
        x = start_x


def wrap_lines(text:str, font:ImageFont.truetype, line_length:int):
    # wraps lines to maximize the number of words within line_length. note
    # that lines *can* exceed line_length, this is intentional, as text looks
    # better if the font is rescaled afterwards. adapted from Chris Collett
    # https://stackoverflow.com/a/67203353/8225672
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)

def timeConvert(timetext:str):
    newds = datetime.datetime.strptime(timetext,'%H:%M').strftime('%I:%M %p')
    return newds

def convert_to_minutes(i):
    import datetime
    hr = i // 60
    m = i - hr * 60
    res_ = str(hr) + ":" + str(m) + ":" + "00"
    res = datetime.datetime.strptime(res_, '%H:%M:%S').time()
    res = res.strftime('%H:%M')
    return res


def calc_fntsize(length:int, height:int, text:str, fntname:str, basesize=50,
                                                              maxsize=800):
    # this will dynamically wrap and scale text with the optimal font size to
    # fill a given textbox, both length and height wise.
    # manually setting basesize to just below the mean of a sample will
    # massively reduce processing time with large batches of text, at the risk
    # of potentially wasting it with strings much larger than the mean

    # these are just for calculating the textbox size, they're discarded
    louvre = Image.new(mode='1', size=(0,0))
    monalisa = ImageDraw.Draw(louvre)

    lines = ''
    fntsize = basesize
    fnt = create_fnt(fntname, fntsize)
    boxheight = 0
    while not boxheight > height and not fntsize > maxsize:
        fntsize += 1
        fnt = fnt.font_variant(size=fntsize)
        lines = wrap_lines(text, fnt, length)
        boxheight = monalisa.multiline_textbbox((0,0), lines, fnt)[3]

    fntsize -= 1
    fnt = fnt.font_variant(size=fntsize)
    lines = wrap_lines(text, fnt, length)
    boxlength = monalisa.multiline_textbbox((0,0), lines, fnt)[2]
    while boxlength > length:
        # note: this is a sanity check. we intentionally don't reformat lines
        # here, as wrap_lines only checks if its output is *longer* than length,
        # which can produce a recursive loop where lines always get wrapped
        # into something longer, leading to overly small and unreadable fonts
        fntsize -= 1
        fnt = fnt.font_variant(size=fntsize)
        boxlength = monalisa.multiline_textbbox((0,0), lines, fnt)[2]
    # recursive call in case original basesize was too low
    boxheight = monalisa.multiline_textbbox((0,0), lines, fnt)[3]
    if boxheight > height:
        return calc_fntsize(length, height, text, fntname, basesize-5)
    return lines, fntsize


def create_fnt(name:str, size:int, layout_engine=ImageFont.Layout.BASIC):
    # Layout.BASIC is orders of magnitude faster than RAQM but will struggle
    # with RTL languages
    # see https://github.com/python-pillow/Pillow/issues/6631
    return ImageFont.truetype(name, size, layout_engine=layout_engine)


def main():
    hardworker = ' /ᐠ - ˕ -マ Ⳋ'
    with open(csvpath, newline='\n', encoding="utf8") as csvfile:
        jobs = len(csvfile.readlines()) - 1
        csvfile.seek(0)
        if len(argv) > 1:
            if argv[1].isdigit() and int(argv[1]) < jobs:
                jobs = int(argv[1])
        quotereader = csv.DictReader(csvfile, delimiter='|')
        for i, row in enumerate(quotereader):
            if i >= jobs:
                break
            else:
                TurnQuoteIntoImage(i, row['quote'], row['author'])
            progressbar = f'{hardworker} working.... {i+1}/{jobs}'
            print(progressbar, end='\r', flush=True)
    print("")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nI hate work")
        exit(0)
