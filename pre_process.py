import shutil
from shutil import copyfile
from PIL import Image
import pandas as pd
import os
import sys
import csv
import time
from optparse import OptionParser, Option, OptionValueError
import math
import fitz

processor_count = int(sys.argv[1])
rootDir = str(sys.argv[2])

# processor_count = 1
# directory = "/Users/sz58/Desktop/Archival Sources Printed"

def split(pdf_filepath,jpg_dir):
	
	doc = fitz.open(pdf_filepath)
	#borrowed from https://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python?lq=1
	for i in range(len(doc)):
		for img in doc.getPageImageList(i):
			xref = img[0]
			pix = fitz.Pixmap(doc, xref)
			output_filename = "%s-%s.jpg" % (i, xref)
			output_filepath = os.path.join(jpg_dir,output_filename)
			print(output_filepath)
			
			pix = fitz.Pixmap(fitz.csRGB, pix)
			img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
			img.save(output_filepath,"JPEG")
			
			pix = None
  
  
starttime = time.time()  
 
#first get and split the pdfs
pdf_filepaths = [os.path.join(dp, f) for dp, dn, fn in os.walk(rootDir) for f in fn if f.endswith('.pdf')]


os.makedirs(os.path.join(rootDir,'../inputs'))


for pdf_filepath in pdf_filepaths:
	filename = str(os.path.basename(pdf_filepath))
	filepath = str(os.path.dirname(pdf_filepath))
	
	filepath = filepath.replace(rootDir,os.path.join(rootDir,'../inputs/'),1)
	jpg_dir= os.path.join(filepath,filename)
	os.makedirs(jpg_dir)
	try:
		split(pdf_filepath,jpg_dir)
	except:
		print("Failed on", pdf_filepath + ".pdf")
		print("Unexpected error:", sys.exc_info()[0])

#now that the pdf's have been sliced up, find any jpg's or png's lying around and shift them over into the input directory, too.
jpg_filepaths = [os.path.join(dp, f) for dp, dn, fn in os.walk(rootDir) for f in fn if f.endswith('.jpg') or f.endswith('.png')]
for jpg_filepath in jpg_filepaths:
	filename = str(os.path.basename(jpg_filepath))
	filepath = str(os.path.dirname(jpg_filepath))
	filepath = filepath.replace(rootDir,os.path.join(rootDir,'../inputs/'),1)
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	copyfile(jpg_filepath,os.path.join(filepath,filename))
		
#now get the final full list of jpg's and png's in the input file to divvy up amongst the processors
#and I've decided to pass it a relative path starting with "inputs" -- will make the handoff to the clusters easier
jpg_filepaths = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.relpath(os.path.join(rootDir,'../inputs/'))) for f in fn if f.endswith('.jpg') or f.endswith('.png')]		

#now create N+1 work assignment/checkpoint files, distributing the workload as evenly as possible
#It would be much cleaner if I knew how to open up an array of N+1 csv writers...
c=0
work_assignments = {c:[] for c in range(processor_count)}

##creates main checkpoint file, writes entries to it, lines up the workload in a large array
with open("checkpoint_main.csv","w") as maincsv:
	writer = csv.writer(maincsv)
	for jpg_filepath in jpg_filepaths:
	
		work_assignments[c].append(jpg_filepath)
	
		writer.writerow([jpg_filepath,"F"])
		c+=1
		c=c%processor_count
		
##creates child checkpoint files

for processor_id in work_assignments.keys():
	with open("checkpoint_%d.csv" %processor_id,'w') as childcsv:
		writer = csv.writer(childcsv)
		for filepath in work_assignments[processor_id]:
			writer.writerow([filepath,"F"])
	
			
endtime = time.time()
print("Process completed in %d seconds" %(int(endtime-starttime)))
