## Script to extract data from Corpus of Spontaneous Japanese XML annotation files
## Oriana, May 2015

## "argparse" !

from xml.dom import minidom
import os
import re
import csv
import datetime
from CSJhelper import * 

phonemeNames = ['i','u'] # These are the names of the phonemes to be extracted

def makeDict(tree,fileName,phonemeNames,csvWriter,colNames):
	for item in tree.getElementsByTagName('Phone'):
		item.setIdAttribute('PhoneStartTime')
	phonemeList = tree.getElementsByTagName("Phoneme")
	moraList = tree.getElementsByTagName("Mora")
	tokensToGet = [p for p in tree.getElementsByTagName("Phoneme") if p.attributes['PhonemeEntity'].value in phonemeNames]
	# Speaker-level speech rate.

	dictList = []



	for num, i in enumerate(tokensToGet):
		valDict = {}
		t = Token('Phoneme',i,tree.firstChild.getAttribute('TalkID'))
		
		t.getTokenInfo(valDict,phonemeList)
		t.getMoraInfo(valDict)
		t.getWordInfo(valDict)
		t.devoicingEnvt(valDict)
		t.getIPUInfo(valDict)	
		vPhone = [n for n in t.node.getElementsByTagName('Phone') if n.getAttribute('PhoneClass') == 'vowel']
		assert len(vPhone) == 1, "Can't get vowel phone."
		vPhone = vPhone[0]
		valDict['Devoiced'] = '1' if vPhone.hasAttribute('Devoiced')==True else '0'
		tokenDict = [t,valDict]
		dictList.append(tokenDict)

	## Check for consecutive devoicing. 
	for prev, item, nxt in previous_and_next(dictList): # Each item here is a list with the Phoneme XML object as its first object and the valDict as its second object. 
		if prev != None:
			if moraList.index(prev[0].mora)+1 == moraList.index(item[0].mora) and prev[1]['hvdEnvt']=='Y':
				dvL = True
			else: 
				dvL = False
		else: 
			dvL = False
		if nxt != None and moraList.index(nxt[0].mora) < len(moraList):
			if moraList.index(item[0].mora)+1 == moraList.index(nxt[0].mora):
				dvR = True if nxt[1]['hvdEnvt']=='Y' else False
			else: 
				dvR=False
		else:
			dvR = False
		if dvL == True and dvR == True:
			item[1]['adjacentDevoiceable'] = 'both'
		elif dvL == True and dvR == False:
			item[1]['adjacentDevoiceable'] = 'left'
		elif dvL == False and dvR == True:
			item[1]['adjacentDevoiceable'] = 'right'
		elif dvL == False and dvR == False:
			item[1]['adjacentDevoiceable'] = 'none'
		else:
			item[1]['adjacentDevoiceable'] = 'ERROR'
	for d in dictList:
		csvOut.writerow([d[1][v] if v in d[1].keys() else 'KeyError' for v in colNames])

	# print "pickling..."
	# f = open('test.pickle', 'wb')
	# pickle.dump(dictList, f)
	# f.close()


## Starting the actual extraction

setupInfo = scriptSetup()
dataDir = setupInfo[0]
fileName = setupInfo[1]
outputFile = setupInfo[2]


colNames = ['TalkID',
 'startTime',
 'Phoneme',
 'Accent',
 'Lemma',
 'nextPhoneme',
 'follPauseDuration',
 'ToneLabel',
 'prevPhonemeManner',
 'FinalInIPU',
 'POS',
 'onset',
 'nextPhonemeManner',
 'follPause',
 'adjacentDevoiceable',
 'MoraDuration',
 'MoraEntity',
 'MoraID',
 'phonemeDuration',
 'ToneClass',
 'phonemeLength',
 'prevPhoneme',
 'Orthography',
 'IPUSpeechRate',
 'hvdEnvt',
 'vclsOnset',
 'Devoiced',
 'wordBoundaryRight',
 'BreakIndex']

ts = datetime.datetime.now()
with open(outputFile, 'wb') as data:
    csvOut = csv.writer(data,delimiter="\t",quotechar='"')
    csvOut.writerow(colNames)
    for root, dirs, files in os.walk(dataDir):
        for fname in files:
            if re.search(fileName, fname):
                print 'Opening ' + fname + " at " +  str(datetime.datetime.now())
                try:
                    tree = minidom.parse(os.path.join(dataDir,fname))
                    makeDict(tree,fname,phonemeNames,csvOut,colNames)
                except ValueError as e:
                    print "problem opening %s" % fname
                    print e           			                
    print 'Writing out CSV file at ' + str(datetime.datetime.now())    
tf = datetime.datetime.now()
te = tf - ts
print 'This took %s seconds' % str(te)







