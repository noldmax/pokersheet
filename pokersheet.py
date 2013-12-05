#! /usr/bin/env python
"Parse Live Poker Tracking Notes Sheet and create XLS"

import xlwt
import re
import argparse


def get_args():
	"""Parse and return command-line arguments passed"""
	parser = argparse.ArgumentParser(description='Parse poker data, create XLS')
	parser.add_argument('-i', '--input', default='pokerdata', help='input pokerdata file (in format from iphone notes)')
	parser.add_argument('-o', '--output', action='store_true', default='pokersheet.xls', help='output xls file containing poker data')
	return parser.parse_args()

def add_entry(sheet, entry_cnt, line):
	#print line
	# If hours not specified, assume 4
	if len(line.split(" - ")) == 4:
		date, place, dough, hours = line.split(" - ")
	elif len(line.split(" - ")) == 3:
		date, place, dough = line.split(" - ")
		hours = '4'
	else:
		print "Invalid entry format.  Needs either 3 or 4 /-delimited values"

	# Write Date, Location
	sheet.write(entry_cnt,1,date)
	sheet.write(entry_cnt,2,place)
	#print "dough=" + dough + ", hours=" + str(hours)

	# Check for cash given after win
	given_match = re.match(".*[(]", dough)
	if given_match:
		result = re.search("(.*)\w?(\(.*\))\w?$", dough)
		#print "matched ("
	else:
		result = re.search("(.*)\w?$", dough)
		#print "nope, no ("
	given = re.search("\((.*)\)", dough)
	if result:
		#print "result=" + result.group(1)
		# Strip '+' if positive result
		result = re.search("\+?(.*)", result.group(1))
		sheet.write(entry_cnt,3,int(result.group(1)))
	if given:
		#print "given=" + given.group(1)
		sheet.write(entry_cnt,4,int(given.group(1)))

	# Write Hours
	sheet.write(entry_cnt,5,int(hours))

def add_totals(sheet, entry_cnt):
	sheet.write(entry_cnt+1,2,'Total')
	sheet.write(entry_cnt+1,3,xlwt.Formula('SUM(D1:D' + str(entry_cnt) + ')'))
	sheet.write(entry_cnt+1,4,xlwt.Formula('SUM(E1:E' + str(entry_cnt) + ')'))
	sheet.write(entry_cnt+1,5,xlwt.Formula('SUM(F1:F' + str(entry_cnt) + ')'))

def process_file(in_file, out_file):
	flines = in_file.readlines()

	# Create pattern match entries
	#   One for a normal session entry
	#   One for a new year
	#   One for year-end totals
	pat_entry = re.compile(r"\d+\/\d+")
	pat_year = re.compile(r"\d{4}")
	pat_yearend = re.compile(r"\d{4}")
	entry_cnt = 0
	year_list = []	

	wbk = xlwt.Workbook()

	# Create sheet, in case we don't find a leading year
	sheet = wbk.add_sheet('2009');

	for line in flines:
		if pat_entry.match(line):
			# Found a session entry
			add_entry(sheet, entry_cnt, line)
			entry_cnt += 1
			#print "Date " + pat_entry.match(line).group(0)
		elif pat_year.match(line):
			# Found a year
			print "Year " + pat_year.match(line).group(0)
			add_totals(sheet, entry_cnt)
			year = (int)(pat_year.match(line).group(0)) + 1
			if year not in year_list:
				sheet = wbk.add_sheet(str(year))
				year_list.append(year)
			entry_cnt = 0
		else:
			if line != '\n':
				print "Found some other kind of line"
				print line
		#if re.search(line.split())

	# Add final totals if file doesn't already end in total
	add_totals(sheet, entry_cnt)

	wbk.save(out_file)

args = get_args()

input_file = open(args.input)
output_file = args.output
process_file(input_file, output_file)

