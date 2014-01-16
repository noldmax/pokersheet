#! /usr/bin/env python
"Parse Live Poker Tracking Notes Sheet and create XLS"

import xlwt
import re
import argparse

class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

class AnnualStats:
	year = ""
	games = {}

	def __init__(self, yr):
		self.year = yr

	def add_game(self, game):
		if not game in self.games:
			self.games[game] = {'hrs': 0, 'dough': 0}

	def add_dough(self, game, dough):
		if not game in self.games:
			print "no game error"
			return
		self.games[game]['dough'] += dough
		print ("Added %d to get new dough %d" % (dough, self.games[game]['dough']))

	def add_hrs(self, game, hrs):
		if not game in self.games:
			print "no game error"
			return
		self.games[game]['hrs'] += dough
		print ("Added %d to get new hrs %d" % (hrs, self.games[game]['hrs']))

def get_args():
	"""Parse and return command-line arguments passed"""
	parser = argparse.ArgumentParser(description='Parse poker data, create XLS')
	parser.add_argument('-i', '--input', default='pokerdata', help='input pokerdata file (in format from iphone notes)')
	parser.add_argument('-o', '--output', action='store_true', default='pokersheet.xls', help='output xls file containing poker data')
	return parser.parse_args()

def fill_date_location(stats, sheet, row, entry_cnt, date, place):
	sheet.write(entry_cnt,row,date)
	sheet.write(entry_cnt,row+1,place)
	
	#pat_plo = re.search(".*{(PLO),(plo)}$", place)
	pat_plo = re.search(".*(PLO)$", place)
	pat_mitt = re.search(".*(MITT)$", place)
	if pat_plo:
		sheet.write(entry_cnt,row+2,"PLO")
		stats.add_hrs("PLO", hrs)
		stats.add_dough("PLO", dough)
	elif pat_mitt:
		sheet.write(entry_cnt,row+2,"MITT")
		stats.add_hrs("MITT", hrs)
		stats.add_dough("MITT", dough)
	else:
		sheet.write(entry_cnt,row+2,"NLHE")
		stats.add_hrs("NLHE", hrs)
		stats.add_dough("NLHE", dough)

	return row+3

def fill_cash_result(stats, sheet, row, entry_cnt, dough_str):
	# Check for cash given after win
	if re.match(".*[(]", dough_str):
		result = re.search("(.*)\w?(\(.*\))\w?$", dough_str)
		print "matched ("
	else:
		result = re.search("(.*)\w?$", dough_str)
		print "nope, no ("
	given = re.search("\((.*)\)", dough_str)
	if result:
		print "result=" + result.group(1)
		# Strip '+' if positive result
		result = re.search("\+?(.*)", result.group(1))
		sheet.write(entry_cnt,row,int(result.group(1)))
	if given:
		print "given=" + given.group(1)
		sheet.write(entry_cnt,row+1,int(given.group(1)))
	return row+2

def add_entry(stats, sheet, entry_cnt, line):
	#print line
	cur_row = 1;

	# Extract entry components
	if len(line.split(" - ")) == 4:
		date, place, dough, hours = line.split(" - ")
	elif len(line.split(" - ")) == 3:
		# If hours not specified, assume 4
		date, place, dough = line.split(" - ")
		hours = '4'
	else:
		print "Invalid entry format.  Needs either 3 or 4 /-delimited values"

	# Write Date, Location, Game
	cur_row = fill_date_location(stats, sheet, cur_row, entry_cnt, date, place)
	#print "dough=" + dough + ", hours=" + str(hours)

	# Write winnings/losings and money given (if any)
	cur_row = fill_cash_result(stats, sheet, cur_row, entry_cnt, dough)

	# Write Hours
	sheet.write(entry_cnt,cur_row,int(hours))

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
	#sheet = wbk.add_sheet('2009');

	for line in flines:
		if pat_entry.match(line):
			# Found a session entry
			if not year_list:
				print "Must have a year before adding entries!  Invalid data file format"
				return
			add_entry(stats, sheet, entry_cnt, line)
			entry_cnt += 1
			#print "Date " + pat_entry.match(line).group(0)
		elif pat_year.match(line):
			# Found a year
			if entry_cnt != 0:
				add_totals(stats, sheet, entry_cnt)
			year = (int)(pat_year.match(line).group(0))
			if year not in year_list:
				print "Year " + pat_year.match(line).group(0)
				stats = AnnualStats(year)
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

