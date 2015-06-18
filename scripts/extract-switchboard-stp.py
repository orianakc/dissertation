## Extracting information from the Switchboard Transcription Project files. 
## Data is available at http://www1.icsi.berkeley.edu/Speech/stp/
## Oriana Kilbourn-Ceron, June 2015
## https://github.com/orianakc

from xml.dom import minidom
import os
import re
import csv
import sys
sys.path.append("~/dissertation/scripts/")
# NXTparser.py can be downloaded from https://github.com/orianakc/dissertation
from NXTparser import *

inputDir = '/Users/oriana/Corpora/Switchboard_phonetic/ws96to97-release1/' # This should point to the file containing folders for each of the XML annotation types
outputDir = '~/dissertation/data/switchboard_nxt/' # Where the output file goes. 

missingFiles = []

def makeDict(speaker,csvOut,colNames):
	getInfo(speaker,'phn')
	try:
		getInfo(speaker,'syl')
	except:
		missingFiles.append(speaker.ID+'.syl')
		print 'No syl file for ' + speaker.ID 
	try:
		getInfo(speaker,'wrd')
	except:
		missingFiles.append(speaker.ID+'.wrd')
		print 'No wrd file for ' + speaker.ID  
	dictList = []

	for i in speaker.phn:
		if i['value'] in ['t','q','dx']:
			valDict = {}
			valDict['speakerID'] = speaker.ID
			valDict['phone'] = i['value']
			valDict['phoneTime'] = i['time']
			valDict['prevSeg'] = speaker.phn[speaker.phn.index(i)-1]['value']
			try:
				valDict['follSeg'] = speaker.phn[speaker.phn.index(i)+1]['value']
			except IndexError:
				valDict['follSeg'] = 'FILE-END'
			#Find syllable\
			valDict['syl'] = 'NA'
			valDict['sylTime'] = 'NA'	
			for s in speaker.syl:
				if s['time']>=i['time'] and speaker.syl[speaker.syl.index(s)-1]<i['time']:
						valDict['syl'] = s['value']
						valDict['sylTime'] = s['time']
						break
				else:
						continue
				


			#Find word
			valDict['wrd'] = 'NA'
			valDict['wrdTime'] = 'NA'
			
			for s in speaker.wrd:
				if s['time']>=i['time'] and speaker.wrd[speaker.wrd.index(s)-1]['time']<i['time']:
					valDict['wrd'] = s['value']
					valDict['wrdTime'] = s['time']
			
			if re.search('[aeiour]',valDict['prevSeg']) and re.search('[lraeiou]',valDict['follSeg']):
				valDict['intervocalic'] = 'Y'
			else:
				valDict['intervocalic'] = 'N'

			if valDict['wrdTime'] == valDict['phoneTime']:
				valDict['wrdBoundaryRight'] = 'Y'
			else: 
				valDict['wrdBoundaryRight'] = 'N'

			valDict['context'] = '_'.join([p['value'] for p in speaker.phn])

			dictList.append(valDict)

	for d in dictList:
		csvOut.writerow([d[v] for v in colNames])
	return dictList

def getInfo(speaker,ext):
	infoFile = '%s%s/%s.%s' %(speaker.xmlDir,ext,speaker.ID,ext)
	with open(infoFile,'r') as f:
		info  = [l for l in f.read().splitlines()]
	for l in info:
		if l == '#':
			info=info[info.index(l)+1:]
			break
		elif info.index(l)<len(info):
			continue
		else: 
			print "Header problem with " + "\n".join(info[:4])
	items = []
	for l in info:
		lineInfo = l.split()
		time = lineInfo.pop(0)
		lineInfo.pop(0)
		itemInfo = {
		'time':time,
		'value':' '.join(lineInfo)
		}
		items.append(itemInfo)
	setattr(speaker,ext,items)

def xmlExtract(fileName,dataName,colNames):
    with open(dataName, 'wb') as data:
        csvOut = csv.writer(data,delimiter="\t",quotechar='"')
        csvOut.writerow(colNames)
        for root, dirs, files in os.walk(inputDir):
            for fname in files:
                if re.search(fileName+'.phn', fname):
					fileID = ''.join(re.search("(.*).phn",fname).groups())
					try:
						speaker = Speaker(fileID,root[:-3])
						print fname
						makeDict(speaker,csvOut,colNames)
					except ValueError as e:
						print "problem opening %s" % fname
						print e


# This line should contain all the keys in valDict that will be written to the output file.
header = ['speakerID','phone','phoneTime','prevSeg','follSeg','syl','sylTime','wrd','wrdTime','intervocalic','wrdBoundaryRight']

xmlExtract('.*','icsitest.txt',header)

print 'Missing these files:' + '\n' + '\n'.join(missingFiles)
















