## Script for working with nxt swtichboard corpus annotations
## Oriana 17-05-2015


from xml.dom import minidom
import os
import re
import csv

def makeDict(tree,fileID,csvOut,colNames):
	## Get the files parsed.
	# phTree = minidom.parse(os.path.join(myPath,'phones/',fname))
	try: 
		syllTree = minidom.parse('/Users/oriana/Corpora/nxt_switchboard_ann/xml/syllables/'+fileID+'.syllables.xml')
	except ValueError as e:
		print "problem opening %s syllable file" % fileID
		print e

	try: 
		wordTree = minidom.parse('/Users/oriana/Corpora/nxt_switchboard_ann/xml/phonwords/'+fileID+'.phonwords.xml')
	except ValueError as e:
		print "problem opening %s phonword file" % fileID
		print e


	## Prepare lists of things to search through
	phs = tree.getElementsByTagName('ph')
	sylls = syllTree.getElementsByTagName('syllable')
	syllPhones = syllTree.getElementsByTagName('nite:child')
	syllHrefs = [s.getAttribute('href') for s in syllPhones]
	phonwords = wordTree.getElementsByTagName('phonword')


	## Pick up all the [t] (and [d]?)
	tphs = [p for p in phs if p.firstChild.data=='t']
	dictList = []
	wdIndex = 0
	for t in tphs:
		valDict = {}
		valDict['fileID'] = fileID
		for k in t.attributes.keys():
			valDict[k] = t.getAttribute(k)
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


		## Am I in a stressed syllable? p = primary, s=secondary, n=none. Some syllables have no stress attribute.

		## What phonword am I in? 
		myWord = None
		for w in phonwords[wdIndex:]:
			if float(w.getAttribute('nite:start'))<= float(t.getAttribute('nite:start')):
				if float(w.getAttribute('nite:end')) >= float(t.getAttribute('nite:end')):
					myWord = w
					wdIndex = phonwords.index(w)
				else: 
					pass


		valDict['wordOrth'] = myWord.getAttribute('orth')
		valDict['wordStress'] = myWord.getAttribute('stressProfile')
		valDict['wordID'] = myWord.getAttribute('nite:id')



		# mySyll.getAttribute('msstate') == t.getAttribute('msstate')
		dictList.append(valDict)

	for d in dictList:
		csvOut.writerow([d[v] for v in header])
	return dictList

header = ['fileID','msstate','nite:start','nite:end','nite:id','prevSeg','follSeg','wordOrth','wordStress','wordID']

def xmlExtract(fileName,dataName,colNames):
    with open(dataName, 'wb') as data:
        csvOut = csv.writer(data,delimiter="\t",quotechar='"')
        csvOut.writerow(colNames)
        for root, dirs, files in os.walk('/Users/oriana/Corpora/nxt_switchboard_ann/xml/phones'):
            for fname in files:
                if re.search(fileName, fname):
					fileID = re.search(".*(?=\.[a-z]*\.xml)",fname).group()
					try:
						tree = minidom.parse(os.path.join(root,fname))
						print fname
						makeDict(tree,fileID,csvOut,colNames)
					except ValueError as e:
						print "problem opening %s" % fname
						print e

                    



# myPath = '/Users/oriana/Corpora/nxt_switchboard_ann/xml/'
xmlExtract("sw4168.*xml","sw4168-flapping-switchboard.txt",header)
# xmlExtract(".*xml","flapping-switchboard.txt",header)







