from PIL import Image
import os
import sys
import csv
import time
from PIL import ImageEnhance
import pytesseract
from optparse import OptionParser, Option, OptionValueError

directory = str(sys.argv[2])
proc_id = int(sys.argv[1])

def list_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def binarizing(img, threshold):
    img = img.convert("L")

    enh_con = ImageEnhance.Contrast(img)
    contrast = 3
    img = enh_con.enhance(contrast)

    pixdata = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    return img

def ocr(file_path, proc_id):
	
	with open("done_%d.csv" %proc_id, "w") as c:
		writer = csv.writer(c)
		with open("checkpoint_%d.csv" %proc_id, "r") as c:
			reader = csv.reader(c)
			paths = [row for row in reader]
			for path in paths:
				imgpath=path[0]
				filename = str(os.path.basename(imgpath))
				filedir = str(os.path.dirname(imgpath))
				fileext = os.path.splitext(imgpath)[1]
				start = time.time()
				img = Image.open(imgpath)
				img = binarizing(img, 160)
				img.save(imgpath)
				text = pytesseract.image_to_string(Image.open(imgpath), lang='spa')
				outdir = filedir.replace("input", "output",1)
				if not os.path.exists(outdir):
					os.makedirs(outdir)
				outfile = os.path.join(outdir,filename.replace(fileext, ".txt"))
				out = open(outfile, "w")
				out.write(text)
				out.close()
				with open("done_%d.csv" %proc_id, "a") as c2:
					writer = csv.writer(c2)
					writer.writerow(path)
				end = time.time()
				print("Time for OCR:", end - start, ",", end)

print(proc_id)
print(directory)


ocr(directory, proc_id)
