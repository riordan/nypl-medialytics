import xlrd
import sys
import io
import os
import glob
import pickle
import dateutil.parser
import datetime

class Track:
	def __init__(self,handle, path, count, date):
		self.handle = handle
		self.path = path[:path.rfind('>')]
		#print "The folder is: %s" %self.path
		self.name = path[path.rfind('>')+2:]
		#print "The track is: %s" %self.name
		self.count = {}
		self.addDate(date,count)
		
		'''
		#Debug code:
		print "Handle = %i" % self.handle
		print "Path = %s" % self.path
		print "DayCount for %s: %i" %(str(self.count.keys()[0].date()), self.count[self.count.keys()[0]])
		print "TotalCount: %i" %self.downloads()
		'''
	
		
	def addDate(self,date,count):
		self.count[date] = count
		# print "TotalCount: %i" %self.downloads()
	
	def downloads(self):
		dls = 0
		for day in self.count.keys():
			dls += self.count[day]
		return dls
	
	
	def __str__(self):
		return self.name		
	


class TrackList:
	'''
	Tracklist: a collection of iTunes tracks
	Public Variables:
		allTracks: a dictionary of tracks indexed by handle
	
	Public Methods:
		hasDate(date) takes a python datetime (or string of a date) and returns true if it is represented in the set of tracks 
		countDate(date) takes a datetime and returns the total count of downloads for that date. returns 0 if none
		trackExists(handle) Takes a handle (numeric identifier) and returns true if that track exists
	'''
	def __init__(self):
		self.allTracks = {}
	
	def trackExists(self,handle):
		return handle in self.allTracks.keys()
	
	def hasDate(self, date):
		#Checks to see if date is not a datetime. If not, tries to convert from string. If datetime, then checks if it has one
		if not isinstance(date, datetime.datetime):
		  try:
		    date = dateutil.parser.parse(date)
		  except:
		    print "Invalid date format passed to TrackList.hasDate"
		    sys.exit()
		
		#Traverses tracks & dates to see if date is in system
		for tkey in self.allTracks.keys():
		  for dkey in range(len(self.allTracks[tkey].count.keys())):
		    if date == self.allTracks[tkey].count.keys()[dkey]: return True
		  
		return False



# Imports tracks. Takes filename of import file, returns list of rows in sheet
# Caveat: works only for workbook of 1 sheet with just tracks
def importReport(dirName, trackList):
	
	#Traverses directory looking for iTunes excel files
	
	dlist = os.listdir(dirName)
	for fileName in glob.glob( os.path.join(dirName, '*.xls') ) :	
		#opens excel workbook
		wb = xlrd.open_workbook(fileName)
		print "in workbook: %s" %fileName
	
		'''Opens all Track worksheets in a workbook'''
		trackSheets = []
		for sheet in wb.sheet_names():
			if "Tracks" in sheet:
				trackSheets.append(sheet)
		
		for shName in trackSheets:
		
			#opens Track Sheet
			sh = wb.sheet_by_name(shName)
			print "In Sheet: %s" %sh.name
			rows = []
			#Determines date of data based on name of sheet
			date = dateutil.parser.parse(sh.name[:sh.name.find(' ')]) 
			#print date
	
			#importer
			'''Sheet Parser: Tracks
			Track excel worksheets contain the date in their sheet name and a schema of
			|PATH|COUNT|HANDLE
			PATH is the path to the asset (including the actual track name, denoted by
			the final carrot ">".)
			COUNT is the number of downloads this week.
			HANDLE is the unique ID of each track.'''
			for rownum in range(1,sh.nrows):
				cRow = sh.row_values(rownum)
				path = sh.row_values(rownum)[0]
				count = sh.row_values(rownum)[1]
				handle = sh.row_values(rownum)[2]
		
				#Checks if it's an existing track
				if trackList.trackExists(handle):
					#Appends data to an existing track
					trackList.allTracks[handle].addDate(date,count)
				else: #creates a new Track
					trackList.allTracks[handle] = Track(handle, path, count, date)
			
	
	return




targetDirectory = 'sampleFiles/'
trackList = TrackList()
importReport(targetDirectory,trackList)

'''
testString = "2011-07-18"
testDate = dateutil.parser.parse(testString)
print testString
print testDate

print trackList.hasDate(testDate)

'''