import csv
import os
import re

processor_ids = [int(re.search("(?<=done_)[0-9]+",f).group(0)) for f in os.listdir('.') if re.match("done_[0-9]+\.csv",f)]

with open("checkpoint_main.csv","r") as maincheckpointcsv:
	main_checkpoint_dict = {i[0]:i[1] for i in csv.reader(maincheckpointcsv)}

#print(main_checkpoint_dict)


for process_id in processor_ids:
	
	done_csv_filename = "done_%d.csv" %process_id
	
	print(process_id)
	with open("checkpoint_%d.csv" %process_id,"r") as process_checkpoint_csv:
		'''for row in csv.reader(process_checkpoint_csv):
			print(row)'''
		process_checkpoint_dict = {i[0]:i[1] for i in csv.reader(process_checkpoint_csv)}
	
	with open(done_csv_filename,"r") as done_csv:
		reader = csv.reader(done_csv)
		for row in reader:
			done_filepath = row[0]
			main_checkpoint_dict[done_filepath] = "T"
			process_checkpoint_dict[done_filepath] = "T"
	
	with open("checkpoint_%d.csv" %process_id,"w") as process_checkpoint_csv:
		writer = csv.writer(process_checkpoint_csv)
		array = [[k,process_checkpoint_dict[k]] for k in process_checkpoint_dict.keys()]
		for item in array:
			writer.writerow(item)
	
	os.remove(done_csv_filename)

with open("checkpoint_main.csv","w") as maincheckpointcsv:
	writer = csv.writer(maincheckpointcsv)
	array = [[k,main_checkpoint_dict[k]] for k in main_checkpoint_dict.keys()]
	for item in array:
		writer.writerow(item)	

