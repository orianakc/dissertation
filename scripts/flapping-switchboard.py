## Script for working with nxt swtichboard corpus annotations
## Oriana 17-05-2015


from xml.dom import minidom
import os
import re
import csv

def makeDict(tree,fname,csvOut,colNames):
	## Get the files parsed.
	# phTree = minidom.parse(os.path.join(myPath,'phones/',fname))
	# syllTree = minidom.parse(os.path.join(,fname))
	## Pick up a list of all ph's
	phs = tree.getElementsByTagName('ph')
	## Pick up all the [t] (and [d]?)
	tphs = [p for p in phs if p.firstChild.data=='t']
	dictList = []
	for t in tphs:
		valDict = {}
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
				prevSeg = phs[phs.index(t)+count]
			if prevSeg != 'SIL':
				# print 'Stopping now!'
				break
			else:
				count -= 1
				# print 'Increasing count'
		valDict['prevSeg'] = prevSeg.firstChild.data
		## Following segment
		count = 1 
		while count > 0:
			try:
				follSeg = phs[phs.index(t)+count]
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
		valDict['follSeg'] = follSeg.firstChild.data

		## Am I in a stressed syllable? p = primary, s=secondary, n=none. Some syllables have no stress attribute.

		# mySyll.getAttribute('msstate') == t.getAttribute('msstate')
		dictList.append(valDict)

	for d in dictList:
		csvOut.writerow([d[v] for v in header])
	return dictList

header = ['msstate','nite:start','nite:end','nite:id','prevSeg','follSeg']

def xmlExtract(fileName,dataName,colNames):
    with open(dataName, 'wb') as data:
        csvOut = csv.writer(data,delimiter="\t",quotechar='"')
        csvOut.writerow(colNames)
        for root, dirs, files in os.walk('/Users/oriana/Corpora/nxt_switchboard_ann/xml/phones'):
            for fname in files:
                if re.search(fileName, fname):
                    try:
                        tree = minidom.parse(os.path.join(root,fname))
                        print fname
                        makeDict(tree,fname,csvOut,colNames)
                    except ValueError as e:
                        print "problem opening %s" % fname
                        print e
                    



# myPath = '/Users/oriana/Corpora/nxt_switchboard_ann/xml/'
xmlExtract("sw4168.*xml","sw4168-flapping-switchboard.txt",header)
xmlExtract(".*xml","flapping-switchboard.txt",header)







