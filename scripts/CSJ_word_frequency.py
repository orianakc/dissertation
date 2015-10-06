import os
import re
from xml.dom import minidom
from collections import Counter

dataDir = '/Users/oriana/dissertation/data/CSJ/XML/'

word_frequency = Counter()
for root, dirs, files in os.walk(dataDir):
	for fname in files:
		# print 'Opening ' + fname + " at " +  str(datetime.datetime.now())
		if re.search('xml$',fname):
			try:
				tree = minidom.parse(os.path.join(dataDir,fname))
				SUWs = tree.getElementsByTagName('SUW')
				wordList = [w.getAttribute('OrthographicTranscription').encode('utf-8') for w in SUWs]
				word_frequency.update(wordList)
			except ValueError as e:
				print "problem opening %s" % fname
				print e 

with open('CSJ_word_frequency.txt','w+') as freqFile:
	freqFile.write('Orthography \t CSJFrequency')
	for k in word_frequency.keys():
		freqFile.write(k + '\t' + word_frequency[k])