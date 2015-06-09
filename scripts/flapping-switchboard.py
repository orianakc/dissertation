## Script for working with nxt switchboard corpus annotations
## Oriana 17-05-2015


from xml.dom import minidom
import os
import re
import csv
import sys
sys.path.append("~/dissertation/scripts/")
from NXTparser import *

inputDir = '/Users/oriana/Corpora/nxt_switchboard_ann/xml/' # This should point to the file containing folders for each of the XML annotation types
outputDir = '~/dissertation/data/switchboard_nxt/' # Where the output file goes. 

def makeDict(speaker,csvOut,colNames):
	# ## Get the files parsed.
	# # phTree = minidom.parse(os.path.join(myPath,'phones/',fname))
	# try: 
	# 	syllTree = minidom.parse('/Users/oriana/Corpora/nxt_switchboard_ann/xml/syllables/'+fileID+'.syllables.xml')
	# except ValueError as e:
	# 	print "problem opening %s syllable file" % fileID
	# 	print e

	# try: 
	# 	wordTree = minidom.parse('/Users/oriana/Corpora/nxt_switchboard_ann/xml/phonwords/'+fileID+'.phonwords.xml')
	# except ValueError as e:
	# 	print "problem opening %s phonword file" % fileID
	# 	print e
	tags = ['phones','syllables','phonwords','phrases']
	for t in tags:
		speaker.makeTree(t)

	## Prepare lists of things to search through
	phs = speaker.phonesList
	sylls = speaker.syllablesList
	phonwords = speaker.phonwordsList

	## Pick up all the [t] (and [d]?)
	speaker.getTokens('t')
	tphs = speaker.tList
	dictList = []
	wdIndex = 0
	syllIndex = 0
	for t in tphs:
		valDict = {}
		valDict['fileID'] = speaker.ID
		for k in t.attributes.keys():
			valDict[k] = t.getAttribute(k)
		## Segment duration
		valDict['duration'] = float(valDict['nite:end'])-float(valDict['nite:start'])
		## Previous segments
		count = -1 
		while count < 0:
			if phs.index(t)+count < 0:
				prevSeg = "FILE-START"
				print "Too low!"
				break
			else:
				prevSeg = phs[phs.index(t)+count].firstChild.data
			if prevSeg != 'SIL':
				# print 'Stopping now!'
				break
			else:
				count -= 1
				# print 'Increasing count'
		valDict['prevSeg'] = prevSeg
		## Following segment
		count = 1 
		while count > 0:
			try:
				follSeg = phs[phs.index(t)+count].firstChild.data
				# print follSeg
			except IndexError:
				follSeg = "FILE-END"
				print 'out of range'
				break
			if follSeg != 'SIL':
				# print 'Stopping now!'
				break
			else:
				count += 1
				print 'Increasing count'
		valDict['follSeg'] = follSeg

		## Find the ID of the syllable I'm in 
		for s in sylls[syllIndex:]:
			childPhones = getChildren(s,speaker.phonesTree)
			if t.getAttribute('nite:id') in childPhones:
				valDict['syllableNode'] = s
				syllIndex = sylls.index(s)
				print "Found syllable node : " + valDict['syllableNode'].getAttribute('nite:id')
				break
			else:
				continue
		assert valDict['syllableNode'], "Couldn't find a syllable for "+ t 
		## Am I in a stressed syllable? p = primary, s=secondary, n=none. Some syllables have no stress attribute.
		if valDict['syllableNode'].hasAttribute('stress') == False:
			valDict['stressedSyll'] = 'NA'
		else:
			valDict['stressedSyll'] =valDict['syllableNode'].getAttribute('stress')

		## What phonword am I in? 
		for w in phonwords[wdIndex:]:
			childSylls = getChildren(w,speaker.syllablesTree)
			if valDict['syllableNode'].getAttribute('nite:id') in childSylls:
				myWord = w
				wdIndex = phonwords.index(w)
				valDict['wordOrth'] = myWord.getAttribute('orth')
				valDict['wordStress'] = myWord.getAttribute('stressProfile')
				valDict['wordID'] = myWord.getAttribute('nite:id')
				print 'Found it!: ' + valDict['wordOrth']
				break
		# assert type(valDict['wordOrth']) == str, "Couldn't find a word for " + valDict['syllableNode'].getAttribute('nite:id')



		## At word boundary? 		
		# print re.search('(.*)_.*',t.getAttribute('nite:id')).groups() 
		# print re.search('(.*)_.*',phs[phs.index(t)-1].getAttribute('nite:id')).groups()
		if re.search('(.*)_.*',t.getAttribute('nite:id')).groups() == re.search('(.*)_.*',phs[phs.index(t)-1].getAttribute('nite:id')).groups():
				valDict['wordBoundaryLeft'] = "N"
		else: 
			valDict['wordBoundaryLeft'] = "Y"

		if re.search('(.*)_.*',t.getAttribute('nite:id')).groups() == re.search('(.*)_.*',phs[phs.index(t)+1].getAttribute('nite:id')).groups():
				valDict['wordBoundaryRight'] = "N"
		else: 
			valDict['wordBoundaryRight'] = "Y"

		# mySyll.getAttribute('msstate') == t.getAttribute('msstate')
		dictList.append(valDict)

	for d in dictList:
		csvOut.writerow([d[v] for v in header])
	return dictList

header = ['fileID','msstate','nite:start','nite:end','duration','nite:id','prevSeg','follSeg','wordOrth','wordStress','wordID','wordBoundaryLeft','wordBoundaryRight']

def xmlExtract(fileName,dataName,colNames):
    with open(dataName, 'wb') as data:
        csvOut = csv.writer(data,delimiter="\t",quotechar='"')
        csvOut.writerow(colNames)
        for root, dirs, files in os.walk(inputDir+'phones'):
            for fname in files:
                if re.search(fileName, fname):
					fileID = re.search(".*(?=\.[a-z]*\.xml)",fname).group()
					try:
						speaker = Speaker(fileID,inputDir)
						print fname
						makeDict(speaker,csvOut,colNames)
					except ValueError as e:
						print "problem opening %s" % fname
						print e

                    



# myPath = '/Users/oriana/Corpora/nxt_switchboard_ann/xml/'
xmlExtract("sw4168.*xml","sw4168-flapping-switchboard.txt",header)
# xmlExtract(".*xml","flapping-switchboard.txt",header)


# Print summary stats. 


