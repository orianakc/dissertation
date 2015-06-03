## Getting average mora duration

from xml.dom import minidom
import os
import re
import csv
import datetime

# tree = minidom.parse(fileName)
def makeDict(tree,fname,csvOut,colNames):
	moras = tree.getElementsByTagName("Mora")
	# return moras
	print 'Found %d moras' % len(moras)
	for mora in moras:
		valDict = {}
		moraPhones = mora.getElementsByTagName('Phone')

		if len(moraPhones) == 0:
			pass
		else:
			valDict['file'] = fname
			valDict['MoraStart'] = moraPhones[0].attributes['PhoneStartTime'].value
			valDict['MoraEnd'] = moraPhones[-1].attributes['PhoneEndTime'].value
			valDict['MoraDuration'] = float(valDict['MoraEnd']) - float(valDict['MoraStart'])
			valDict['MoraEntity'] = mora.getAttribute('MoraEntity').encode('utf-8')
			dictList.append(valDict)
			valDict['ID'] = mora
			dictList.append(valDict)
	

# moraNames = [d['MoraEntity'] for d in dictList]
# moraNamesUnique = list(set(moraNames))

# avgMoraDuration = {}
# for m in moraNamesUnique:
# 	durs = [d['MoraDuration'] for d in dictList if d['MoraEntity']==m]
# 	avgMoraDuration[m] = sum(durs)/float(len(durs))





outputFile = raw_input('Name of output file: ')
 #'mora-duration.tdf'
dataDir = raw_input('Path to XML files : ')
 #'/Users/oriana/dissertation/data/CSJ/XML/'
fileName = raw_input('What file(s) shall I process for you? : ')
# ".*.xml"
colNames = ['file','MoraStart','MoraEnd','MoraDuration','MoraEntity']

ts = datetime.datetime.now()
with open(outputFile, 'wb') as data:
    csvOut = csv.writer(data,delimiter="\t",quotechar='"')
    csvOut.writerow(colNames)
    dictList = []
    for root, dirs, files in os.walk(dataDir):
        for fname in files:
            if re.search(fileName, fname):
                print 'Opening ' + fname + " at " +  str(datetime.datetime.now())
                try:
                    tree = minidom.parse(os.path.join(dataDir,fname))
                    makeDict(tree,fname,csvOut,colNames)
                except ValueError as e:
                    print "problem opening %s" % fname
                    print e           			
                
    print 'Writing out CSV file at ' + str(datetime.datetime.now())
    print 'There will be %d rows' % len(dictList)
    for d in dictList:
		csvOut.writerow([d[v] for v in colNames])
tf = datetime.datetime.now()
te = tf - ts
print 'This took %s seconds' % str(te)




























