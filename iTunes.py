import xlrd
import sys
import io
import os
import glob
import pickle
import dateutil.parser
import datetime

class Track:
	def __init__(self,handle, path):
		self.handle = handle
		self.path = path[:path.rfind('>')]
		#print "The folder is: %s" %self.path
		self.name = path[path.rfind('>')+2:]
		#print "The track is: %s" %self.name
		self.dlCount = {}
		self.pvCount = {}
		
		'''
		#Debug code:
		print "Handle = %i" % self.handle
		print "Path = %s" % self.path
		print "DaydlCount for %s: %i" %(str(self.dlCount.keys()[0].date()), self.dlCount[self.dlCount.keys()[0]])
		print "TotaldlCount: %i" %self.downloads()
		'''
		
	
	#Adds a new count to Downloads
	def addDlDate(self,date,dlCount):
		self.dlCount[date] = dlCount
		# print "TotaldlCount: %i" %self.downloads()
	
	#Adds a new count to Previews
	def addPvDate(self,date,pvCount):
		self.pvCount[date] = pvCount
	
	#Returns cumulative number of downloads for a track
	def downloads(self):
		dls = 0
		for day in self.dlCount.keys():
			dls += self.dlCount[day]
		return dls
	
	#Returns cumulative number of previews for a track
	def previews(self):
		pvs = 0
		for day in self.pvCount.keys():
			pvs += self.pvCount[day]
	
	
	def __str__(self):
		return self.name



class TrackList:
	'''
	Tracklist: a collection of iTunes tracks
	Public Variables:
		allTracks: a dictionary of tracks indexed by handle
	
	Public Methods:
		hasDate(date) takes a python datetime (or string of a date) and returns true if it is represented in the set of tracks
		dlCountDate(date) takes a datetime and returns the total dlCount of downloads for that date. returns 0 if none
		trackExists(handle) Takes a handle (numeric identifier) and returns true if that track exists
	'''
	def __init__(self):
		self.allTracks = {}
		self.allDates = []
	
	def newTrack(self,handle,path):
		self.allTracks[handle] = Track(handle, path)
	
	def addDlCount(self, handle, date, dlCount):
		self.allTracks[handle].addDlDate(date,dlCount)
		if not date in self.allDates:
			self.allDates.append(date)
	
	
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
		  for dkey in range(len(self.allTracks[tkey].dlCount.keys())):
		    if date == self.allTracks[tkey].dlCount.keys()[dkey]: return True
		
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
			|PATH|dlCount|HANDLE
			PATH is the path to the asset (including the actual track name, denoted by
			the final carrot ">".)
			dlCount is the number of downloads this week.
			HANDLE is the unique ID of each track.'''
			for rownum in range(1,sh.nrows):
				cRow = sh.row_values(rownum)
				path = sh.row_values(rownum)[0]
				dlCount = sh.row_values(rownum)[1]
				handle = sh.row_values(rownum)[2]
				
				#If this track doesn't exist yet, it creates a new instance
				if not trackList.trackExists(handle):
					#print "Creating New Track"
					trackList.newTrack(handle, path)
				# Updates the count of downloads for that date
				#print "Adding Download Record"
				trackList.addDlCount(handle, date, dlCount)
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