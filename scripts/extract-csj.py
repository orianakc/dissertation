## Script to extract data from Corpus of Spontaneous Japanese XML annotation files
## Oriana, May 2015

from xml.dom import minidom
import os
import re
import csv


''' Generates a list of Phoneme objects in 'tree' whose value is in 'myList'.
'''
def getPhonemes(tree,myList):
	phonemeList = [p for p in tree.getElementsByTagName("Phoneme") if p.attributes['PhonemeEntity'].value in myList]
	return phonemeList


''' For a Phoneme object, grab the child Phone objects which are vowels, making sure that there is exactly one of them
'''
def getVowelPhone(myPhoneme):
	phones = [ph for ph in myPhoneme.getElementsByTagName("Phone") if ph.attributes['PhoneClass'].value=="vowel"]
    ## there should be 0 or 1 vowel phone corresponding to this phoneme.  (not sure why there can be 0)
	try:
		assert len(phones)<=1
	except:
		print "More than 1 vowel phone!"
		# continue
    ## why does this happen?
	if len(phones)==0:
		print "High V phoneme without corresponding high V phone -- 	skipping"
		# continue
	phone = phones[0]
	return phone


'''Check whether a Phoneme object is flanked by (1) a voiceless consonant in the same Mora, and (2) the next Phoneme is a voiceless consonant. 
'''

def devoicingEnvt(myPhoneme):
	pass


## List of voiceless phonemes:
voiceless = {  u'c',
 u'cj',
 u'cy',
 u'h',
 u'hj',
 u'hy',
 u'k',
 u'kj',
 u'ky',
 u'p',
 u'py',
 u'pj',
 u's',
 u'sj',
 u'sy',
 u't',
 u'tj',
 u'ty'}


## Starting the actual extraction

fileName = 'A01F0055.xml'#raw_input('What file shall I process for you? : ')
tree = minidom.parse(fileName)
allPhonemes = tree.getElementsByTagName("Phoneme")

dictList = []

# Grab all high vowel phonemes
highVPhonemes = getPhonemes(tree,['i','u'])

for V in highVPhonemes:
	valDict = {} ## stuff you'll want to print out in each row
	valDict['object'] = V
	valDict['file'] = fileName
	## what phoneme is this?
	valDict['phoneme'] = V.attributes['PhonemeEntity'].value
	phone = getVowelPhone(V)
	phoneVars = ["Devoiced", "PhoneStartTime", "PhoneEndTime", "PhoneEntity"]

	for var in phoneVars:
		if var in phone.attributes.keys():
			valDict[var] = phone.attributes[var].value
		else:
			valDict[var] = '0'
	valDict['PhoneDuration'] = float(valDict['PhoneEndTime']) - float(valDict['PhoneStartTime'])
	
	## Information about the containing Mora
	mora = V.parentNode
	try:
		assert V.parentNode.tagName == 'Mora'
	except:
		print "This Phoneme has no parent Mora:" + V
		continue
	for k in ['MoraEntity','MoraID']:
		valDict[k] = mora.attributes[k].value
	
	## Mora duration
	moraPhones = mora.getElementsByTagName('Phone')
	valDict['MoraStart'] = moraPhones[0].attributes['PhoneStartTime'].value
	valDict['MoraEnd'] = moraPhones[-1].attributes['PhoneEndTime'].value
	valDict['MoraDuration'] = float(valDict['MoraEnd']) - float(valDict['MoraStart'])

	## Info about surrounding segments. 
	#### Check for the onset of the mora.
	moraPhonemes = mora.getElementsByTagName('Phoneme')
	if moraPhonemes[0].isSameNode(V):
		valDict['onset'] = 'NoOnset'
	else:
		valDict['onset'] = moraPhonemes[0].attributes['PhonemeEntity'].value
	## What is the next phoneme
	vIndex = allPhonemes.index(V)
	if vIndex == len(allPhonemes)-1:
		valDict['follPhoneme'] = 'END'
	else: 
		nextPhoneme = allPhonemes[vIndex+1]
		valDict['follPhoneme'] = nextPhoneme.attributes['PhonemeEntity'].value
	
	## Are both preceding and following segments voiceless?
	if valDict['onset'] in voiceless:
		valDict['onsetVcls'] = 'Y'
	else:
		valDict['onsetVcls'] = 'N'
	if valDict['follPhoneme'] in voiceless:
		valDict['follVcls'] = 'Y'
	else:
		valDict['follVcls'] = 'N'
	
	## Get the pause duration by calculating Start of nextPhoneme - end of current Phoneme
	if valDict['follPhoneme'] != 'END':
		valDict['Pause'] = float(nextPhoneme.getElementsByTagName('Phone')[0].attributes['PhoneStartTime'].value) - float(valDict['PhoneEndTime'])
	else:
		valDict['Pause'] = 'END'

	## Break information 
	breakList = V.getElementsByTagName('XJToBILabelBreak')
	if breakList != []:
		valDict['Break'] = breakList[0].firstChild.data
	else:
		valDict['Break'] = 'None'

	# Tone information
	toneTags = V.getElementsByTagName('XJToBILabelTone')
	valDict['Accent'] = 'N'
	valDict['ToneClass'] = 'NA'
	valDict['ToneLabel'] = 'NA'
	if toneTags !=[]:
		for t in toneTags:
			if t.attributes['ToneClass'].value == 'accent':
				valDict['Accent'] = 'Y'
			else:
				valDict['ToneClass'] = t.attributes['ToneClass'].value
				valDict['ToneLabel'] = t.firstChild.data


	## Add this entry to dictList to print out later. 
	dictList.append(valDict)


## Things to get:
## Source file
## ID no.
## Phone duration
## Mora duration
## Average mora duration?







