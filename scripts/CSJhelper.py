## Helper module for processing XML files from the Corpus of Spontaneous Japanese
## Oriana, June 2015

from xml.dom import minidom
import os
import re
import csv


class Token(minidom.Element):
	tokenList = []
	def __init__(self,tagName,node,TalkID):
		self.tagName = tagName
		self.node = node
		self.TalkID = TalkID
		minidom.Element.__init__(self,tagName)
		self._attrs.update(node._attrs)
		Token.tokenList.append(self)

	def getTokenInfo(self,phonemeList):
		assert self.node.ownerDocument.firstChild.tagName == 'Talk', 'This token should come from an XML Tree should have "Talk" as its first child, make sure the XML is compatible with this script.'
		valDict = {}
		pIndex = phonemeList.index(self.node)
		
		valDict['TalkID'] = self.TalkID
		
		nextPhoneme = phonemeList[pIndex+1] if pIndex+1<len(phonemeList) else 'FILE-END'
		valDict['nextPhoneme'] = nextPhoneme.getAttribute('PhonemeEntity')

		prevPhoneme = phonemeList[pIndex-1] if pIndex>0 else 'FILE-START'
		valDict['prevPhoneme'] = prevPhoneme.getAttribute('PhonemeEntity')

		childPhones = [n for n in self.node.getElementsByTagName('Phone') if n.getAttribute('PhoneClass') == 'vowel'] 
		try:
		    assert len(childPhones)<=1
		except:
		    print "More than 1 vowel phone!"
		if len(childPhones) == 0:
			print 'No child phones -- skipping'


		self.setAttribute('startTime',childPhones[0].getAttribute('PhoneStartTime'))
		self.setAttribute('endTime',childPhones[-1].getAttribute('PhoneEndTime'))
		assert float(self.getAttribute('endTime')) > float(self.getAttribute('startTime')), "Problem getting phoneme duration" 
		valDict['phonemeDuration'] = float(self.getAttribute('endTime')) - float(self.getAttribute('startTime'))

		# Pause
		pausePhone = [n for n in self.node.getElementsByTagName('Phone') if n.getAttribute('PhoneClass') == 'others']
		if len(pausePhone)==0:
			valDict['follPause'] = 'N'
			valDict['follPauseDuration'] = 'NA'
		else :
			valDict['follPause'] = 'Y'
			valDict['follPauseDuration'] = float(pausePhone[-1].getAttribute('PhoneEndTime')) - float(pausePhone[0].getAttribute('PhoneStartTime'))

		# Next word filled pause?

		# Breaks

		# Tones

		# Accent

		return valDict #something to be printed out







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
 '\xe8\xa8\x80\xe3\x81\x84\xe3\x82\x88\xe3\x81\xa9\xe3\x81\xbf':'Disfluencies'
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