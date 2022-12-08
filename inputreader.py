#! /usr/bin/env python
"Parse Live Poker Tracking Notes Sheet and create XLS"

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
			print ("no game error")
			return
		self.games[game]['dough'] += dough
		print ("Added %d to get new dough %d" % (dough, self.games[game]['dough']))

	def add_hrs(self, game, hrs):
		if not game in self.games:
			print ("no game error")
			return
		self.games[game]['hrs'] += hrs
		print ("Added %d to get new hrs %d" % (hrs, self.games[game]['hrs']))

def get_args():
	"""Parse and return command-line arguments passed"""
	parser = argparse.ArgumentParser(description='Parse poker data, create XLS')
	parser.add_argument('-i', '--input', default='pokerdata',
	                    help='input pokerdata file (in format from iphone ' +
	                    'notes)')
	parser.add_argument('-o', '--output',
	                    default='pokersheet.xls', help='output xls file ' +
	                    'containing poker data')
	return parser.parse_args()

def fill_entry_row(stats, row, entry_cnt, date, place, dough_str, hours):

	# Check for cash given after win
	if re.match(".*[(]", dough_str):
	    # If winnings listed with following (X),
	    # that specifies amount of winnings given away
		result = re.search("(.*)\w?(\(.*\))\w?$", dough_str)
		print ("matched (")
	else:
	    # Just the winnings listed, so grab that value (in result)
		result = re.search("(.*)\w?$", dough_str)
		print ("nope, no (")
	given = re.search("\((.*)\)", dough_str)
	if result:
		print ("result=" + result.group(1))
		# Strip '+' if positive result
		result = re.search("\+?(.*)", result.group(1))
		dough = int(result.group(1))
	else:
	    dough = 0
	if given:
		print ("given=" + given.group(1))
		given_dough = int(given.group(1))
	else:
	    given_dough = 0

	# Identify game type and store stats for that game
	#pat_plo = re.search(".*{(PLO),(plo)}$", place)
	pat_plo = re.search(".*(PLO)$", place)
	pat_mitt = re.search(".*(MITT)$", place)
	if pat_plo:
		stats.add_hrs("PLO", hours)
		stats.add_dough("PLO", dough)
	elif pat_mitt:
		stats.add_hrs("MITT", hours)
		stats.add_dough("MITT", dough)
	else:
		stats.add_hrs("NLHE", hours)
		stats.add_dough("NLHE", dough)
	row += 1

	return row

def add_entry(stats, entry_cnt, line):
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
		print ("Invalid entry format.  Needs either 3 or 4 /-delimited values")

	# Write Date, Location, Game, Dough, Hours
	cur_row = fill_entry_row(stats, cur_row, entry_cnt, date, place,
	                         dough, int(hours))
	#print "dough=" + dough + ", hours=" + str(hours)


def process_file(in_file, out_file):
	flines = in_file.readlines()

	# Create pattern match entries
	#   One for a normal session entry
	#   One for a new year
	#   One for year-end totals
	
	# Example normal session
	# 
	# 6/5 - Kennell's - +205(60)
	pat_entry = re.compile(r"\d+\/\d+")
	
	# Example new year
	# 
	# 2009
	pat_year = re.compile(r"\d{4}")
	
	# Example year-end total
	#
	# 2009 total - +1002(672)
	pat_yearend = re.compile(r"\d{4}")
	entry_cnt = 0
	year_list = []	

	# Read each line from the poker data file
	for line in flines:
		if pat_entry.match(line):
			# Found a session entry
			
			# Empty year_list means sessions listed before an
			# initial year was provided.  Bad format.
			if not year_list:
				print ('Must have a year before adding entries! ' \
				      'Invalid data file format')
				return
			
			# Process the session entry
			add_entry(stats, entry_cnt, line)
			entry_cnt += 1
			#print ("Date " + pat_entry.match(line).group(0))
			
		elif pat_year.match(line):
			# Found a year
			#if entry_cnt != 0:
			#	add_totals(stats, entry_cnt)
			year = (int)(pat_year.match(line).group(0))
			if year not in year_list:
				print ("Year " + pat_year.match(line).group(0))
				stats = AnnualStats(year)
				year_list.append(year)
			entry_cnt = 0
			
		else:
			if line != '\n':
				print ("Found some other kind of line")
				print (line)
		#if re.search(line.split())

args = get_args()

input_file = open(args.input)
output_file = args.output
process_file(input_file, output_file)

