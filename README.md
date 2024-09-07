## Converting Quotes to Images

This contains a Python script to convert a CSV list of quotes into png images that are suitable for use with the Kindle clock at https://github.com/avalonv/literaryclock/tree/main . 

The format is quite simple if you want to add new quotes or edit existing ones

`quote |Author`

if no author is specified, the author will be "unknown"

The script goes through the CSV sequentially, so the first quote in the file will be midnight (00:00), the second will be 12:01 (00:01), etc. I thought about making it random, but it is easy to randomize the quotes using the commandline:  
  
`cat quotes.csv | sort --random-sort >random.csv`

just make sure you put the header row back at the top.

if you want it to use military time, in quote_to_image.py, change  
`use_regular_time = True`
to False

## Using the script
This requires Python 3.6 or higher, and the [Pillow](https://pillow.readthedocs.io/en/latest/installation.html#basic-installation) imaging library (`pip3 install pillow`)[^1].

Run the script with `python3 quote_to_image.py`, from the same folder as the csv file and fonts.

If you only want to generate x images (say, for testing how a font or a quote looks), you can pass a number as an argument to the script — `python3 quote_to_image.py 5` will only process the first 5 lines in the csv file (excluding the header).

## Credits

Thanks to [tjaap](https://www.instructables.com/Literary-Clock-Made-From-E-reader/) for creating the original version of this script in PHP.

Thanks to [avalonv](https://github.com/avalonv/literaryclock/tree/main) for the modifications.

Thanks to [JakubPetriska](https://gist.github.com/JakubPetriska/060958fd744ca34f099e947cd080b540) for the quotes.csv.




