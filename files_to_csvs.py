import os
import csv
import sys
import re

processor_count = int(sys.argv[1])
rootDir = str(sys.argv[2])

jpg_filepaths = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.relpath(os.path.join(rootDir,'../inputs/'))) for f in fn if f.endswith('.jpg') or f.endswith('.png')]		

#now create N+1 work assignment/checkpoint files, distributing the workload as evenly as possible
#It would be much cleaner if I knew how to open up an array of N+1 csv writers...
c=0
work_assignments = {c:[] for c in range(processor_count)}

##creates main checkpoint file, writes entries to it, lines up the workload in a large array
with open("checkpoint_main.csv","w") as maincsv:
	writer = csv.writer(maincsv)
	for jpg_filepath in jpg_filepaths:
		jpg_filepath_truncated = jpg_filepath.replace("../../../mnt/rdf/uh/","")
		work_assignments[c].append(jpg_filepath_truncated)
		writer.writerow([jpg_filepath_truncated,"F"])
		c+=1
		c=c%processor_count

for processor_id in work_assignments.keys():
	with open("checkpoint_%d.csv" %processor_id,'w') as childcsv:
		writer = csv.writer(childcsv)
		for filepath in work_assignments[processor_id]:
			filepath_truncated = filepath.replace("../../../mnt/rdf/uh/","")
			writer.writerow([filepath_truncated,"F"])