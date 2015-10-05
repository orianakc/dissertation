## Helper module for processing XML files from the Corpus of Spontaneous Japanese
## Oriana, June 2015

from xml.dom import minidom
import os
import re
import csv
import argparse
import datetime

def scriptSetup():
	user = raw_input('User name : ')
	if user == 'oriana':
		dataDir = '/Users/oriana/dissertation/data/CSJ/XML/'
	elif user == 'mlml':
		dataDir = '/Users/mlml/Corpora/CorpusOfSpontaneousJapanese/Japanese/Vol2/XML/core/'
	else: 
		print 'Unknown user, please setup information:'
		dataDir = raw_input('Path to XML files : ')
	setting = raw_input('Settings (all/other): ')
	if setting == 'all':
		fileName = '.*xml'#raw_input('What file shall I process for you? : ')
		outputFile = ''.join(['csjHVDdata',datetime.datetime.now().isoformat(),'.txt'])
	else:
		fileName = raw_input('What file shall I process for you? (regular expressions accepted): ')
		outputFile = raw_input('Name of output file : ')

	return (dataDir,fileName,outputFile)


## Function found at http://stackoverflow.com/questions/1011938/python-previous-and-next-values-inside-a-loop
from itertools import tee, islice, chain, izip

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)

class Token(minidom.Element):
	tokenList = []
	def __init__(self,tagName,node,TalkID):
		self.tagName = tagName
		self.node = node
		self.TalkID = TalkID
		minidom.Element.__init__(self,tagName)
		self._attrs.update(node._attrs)
		Token.tokenList.append(self)

	def getTokenInfo(self,valDict,phonemeList):
		assert self.node.ownerDocument.firstChild.tagName == 'Talk', 'This token should come from an XML Tree should have "Talk" as its first child, make sure the XML is compatible with this script.'
		pIndex = phonemeList.index(self.node)
		
		valDict['TalkID'] = self.TalkID
		valDict['Phoneme'] = self.getAttribute('PhonemeEntity')
		
		nextPhoneme = phonemeList[pIndex+1] if pIndex+1<len(phonemeList) else None
		self.nextPhoneme = nextPhoneme
		valDict['nextPhoneme'] = nextPhoneme.getAttribute('PhonemeEntity') if nextPhoneme != None else 'FILE-END'
		valDict['phonemeLength'] = 'long' if valDict['nextPhoneme'] in ['Q','H'] else 'short'
		valDict['nextPhonemeManner'] = mannerDict[valDict['nextPhoneme']] if valDict['nextPhoneme'] in mannerDict.keys() else 'NA'

		prevPhoneme = phonemeList[pIndex-1] if pIndex>0 else None
		self.prevPhoneme = prevPhoneme
		valDict['prevPhoneme'] = prevPhoneme.getAttribute('PhonemeEntity') if prevPhoneme != None else 'FILE-START'
		valDict['prevPhonemeManner'] = mannerDict[valDict['prevPhoneme']] if valDict['prevPhoneme'] in mannerDict.keys() else 'NA'


		childPhones = [n for n in self.node.getElementsByTagName('Phone') if n.getAttribute('PhoneClass') in ['vowel','consonant','special']] 
		if len(childPhones) == 0:
			print 'No child phones -- skipping'


		self.setAttribute('startTime',childPhones[0].getAttribute('PhoneStartTime'))
		self.setAttribute('endTime',childPhones[-1].getAttribute('PhoneEndTime'))
		assert float(self.getAttribute('endTime')) > float(self.getAttribute('startTime')), "Problem getting phoneme duration" 
		valDict['phonemeDuration'] = float(self.getAttribute('endTime')) - float(self.getAttribute('startTime'))
		valDict['startTime'] = self.getAttribute('startTime')
		valDict['endTime'] = self.getAttribute('endTime')

		# Pause
		pausePhone = [n for n in self.node.getElementsByTagName('Phone') if n.getAttribute('PhoneEntity') == 'SpzS']
		if len(pausePhone)==0:
			valDict['follPause'] = 'N'
			valDict['follPauseDuration'] = 'NA'
		else :
			valDict['follPause'] = 'Y'
			valDict['follPauseDuration'] = float(pausePhone[-1].getAttribute('PhoneEndTime')) - float(pausePhone[0].getAttribute('PhoneStartTime'))

		# Next word filled pause?

		# Breaks
		breakList = self.node.getElementsByTagName('XJToBILabelBreak')
		valDict['BreakIndex'] = 'None' if len(breakList) == 0 else breakList[0].firstChild.data

		# Tones
		toneTags = self.node.getElementsByTagName('XJToBILabelTone')
		valDict['Accent'] = 'N'
		valDict['ToneClass'] = 'NA'
		valDict['ToneLabel'] = 'NA'
		if toneTags !=[]:
			for tone in toneTags:
				if tone.getAttribute('ToneClass') == 'accent':
					toneTags.pop(toneTags.index(tone))
					valDict['Accent'] = 'Y'
				## Need to fix this -- what if there is more than one non-accent tone tag?
				else:
					valDict['ToneClass'] = tone.getAttribute('ToneClass')
					valDict['ToneLabel'] = tone.firstChild.data
		return valDict #something to be printed out

	def getMoraInfo(self,valDict):
		mora = self.node.parentNode
		self.mora = mora
		try:
			assert self.node.parentNode.tagName == 'Mora'
		except:
			print "This Phoneme has no parent Mora:" + self.node
		for k in ['MoraEntity','MoraID']:
			valDict[k] = mora.getAttribute(k).encode('utf-8')
		
		## Mora duration
		moraPhones = [n for n in mora.getElementsByTagName('Phone') if n.getAttribute('PhonemeEntity') not in ['SpzS','S?S']]
		valDict['MoraDuration'] = float(moraPhones[-1].getAttribute('PhoneEndTime')) - float(moraPhones[0].getAttribute('PhoneStartTime'))
		moraPhonemes = mora.getElementsByTagName('Phoneme')
		if moraPhonemes[0].isSameNode(self.node):
			valDict['onset'] = 'NoOnset'
		else:
			valDict['onset'] = 'Onset:'+moraPhonemes[0].getAttribute('PhonemeEntity').encode('utf-8')
		return valDict

	def getWordInfo(self,valDict):
		word = self.node.parentNode.parentNode.parentNode
		self.word = word
		assert word.tagName == 'SUW', "Wrong kind of tag to extract word information from."
		valDict['Orthography'] = word.getAttribute('OrthographicTranscription').encode('utf-8')
		valDict['Lemma'] = word.getAttribute('SUWLemma').encode('utf-8')
		valDict['POS'] = posDict[word.getAttribute('SUWPOS').encode('utf-8')]
		valDict['wordBoundaryRight'] = 'Y' if self.node.isSameNode(word.getElementsByTagName('Phoneme')[-1]) else 'N'
	
	def devoicingEnvt(self,valDict):
		assert 'nextPhoneme' in valDict.keys() and 'prevPhoneme' in valDict.keys(), 'Need prevPhoneme and nextPhoneme, try using the getTokenInfo method.'
		valDict['vclsOnset'] = 'Y' if valDict['prevPhoneme'] in voiceless else 'N'
		valDict['hvdEnvt'] = 'Y' if valDict['prevPhoneme'] in voiceless and valDict['nextPhoneme'] in voiceless else 'N'
		if valDict['hvdEnvt'] == 'Y':
			self.setAttribute('hvdEnvt','True')
		else: 
			self.setAttribute('hvdEnvt','False')
		return valDict

	def getIPUInfo(self,valDict):
		self.IPU = self.node.parentNode.parentNode.parentNode.parentNode.parentNode 
		assert self.IPU.tagName == 'IPU', 'Error finding IPU parent node.'
		# IPU Edge? 
		valDict['FinalInIPU'] = 'Y' if self.node.isSameNode(self.IPU.getElementsByTagName('Phoneme')[-1]) else 'N'
		# speech rate
		IPUduration = float(self.IPU.getAttribute('IPUEndTime')) - float(self.IPU.getAttribute('IPUStartTime'))
		valDict['IPUSpeechRate'] = IPUduration/float(len(self.IPU.getElementsByTagName('Phoneme')))









## Part-of-speech Japanese-English dictionary
posDict = {
 '\xe6\x84\x9f\xe5\x8b\x95\xe8\xa9\x9e':'Interjection',
 '\xe5\x89\xaf\xe8\xa9\x9e':'Adverb',
 '\xe9\x80\xa3\xe4\xbd\x93\xe8\xa9\x9e':'Rentaishi',
 '\xe6\x8e\xa5\xe9\xa0\xad\xe8\xbe\x9e':'Prefix' ,
 '\xe5\x8a\xa9\xe8\xa9\x9e':'Particle' ,
 '\xe4\xbb\xa3\xe5\x90\x8d\xe8\xa9\x9e':'Pronoun' ,
 '\xe5\xbd\xa2\xe7\x8a\xb6\xe8\xa9\x9e':'Shape lyrics' ,
 '\xe6\x8e\xa5\xe7\xb6\x9a\xe8\xa9\x9e':'Conjunction' ,
 '\xe5\xbd\xa2\xe5\xae\xb9\xe8\xa9\x9e':'Adjective' ,
 '\xe5\x8a\xa9\xe5\x8b\x95\xe8\xa9\x9e':'Auxiliary verb' ,
 '\xe5\x8b\x95\xe8\xa9\x9e':'Verb' ,
 '\xe8\xa8\x98\xe5\x8f\xb7':'Symbol' ,
 '\xe5\x90\x8d\xe8\xa9\x9e':'Noun',
 '\xe6\x8e\xa5\xe5\xb0\xbe\xe8\xbe\x9e':'Suffix',
 '\xe8\xa8\x80\xe3\x81\x84\xe3\x82\x88\xe3\x81\xa9\xe3\x81\xbf':'Disfluencies',
 '':'ERROR'
}


poaDict = {
	'N':'uvl',
	'b':'lab',
	'p':'lab',
	'm':'lab',
	'F':'lab',
	'f':'lab',
	'c':'alv',
	'cy':'alv',
	'd':'alv',
	'n':'alv',
	't':'alv',
	'ty':'alv',
	's':'alv',
	'z':'alv',
	'k':'vel',
	'kj':'vel',
	'g':'vel',
	'gy':'vel',
	'gj':'vel',
	'y':'alv',
	'sj':'alv',
	'sy':'alv',
	'zj':'alv',
	'zy':'alv',
	'nj':'alv',
	'r':'palv',
	'h':'glot',
	'hj':'glot',
	'hy':'glot',
	'cj':'alv',
	'ky':'vel',
	'a':'low',
	'e':'mid',
	'o':'mid',
	'i':'high',
	'I':'high',
	'u':'high',
	'U':'high',
	'aH':'low',
	'eH':'mid',
	'oH':'mid',
	'iH':'high',
	'uH':'high',
	'w':'lab',
	'py':'lab'

}

mannerDict = {
	'N':'nasal',
	'b':'stop',
	'p':'stop',
	'm':'nasal',
	'F':'fric',
	'f':'fric',
	'c':'afr',
	'cy':'afr',
	'ky':'stop',
	'd':'stop',
	'n':'nasal',
	't':'stop',
	'ty':'stop',
	's':'fric',
	'z':'fric',
	'k':'stop',
	'kj':'stop',
	'g':'stop',
	'gy':'stop',
	'gj':'stop',
	'y':'approx',
	'sj':'fric',
	'sy':'fric',
	'zj':'fric',
	'zy':'fric',
	'nj':'nasal',
	'r':'approx',
	'h':'fric',
	'hj':'fric',
	'hy':'fric',
	'cj':'afr',
	'py':'stop',
	'a':'v',
	'e':'v',
	'o':'v',
	'i':'v',
	'I':'v',
	'u':'v',
	'U':'v',
	'aH':'v',
	'eH':'v',
	'oH':'v',
	'iH':'v',
	'uH':'v',
	'w':'approx',
	'Q':'gem',
	'H':'long'
}

## List of voiceless consonants
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