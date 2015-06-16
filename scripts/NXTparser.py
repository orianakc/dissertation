## Script for putting together all of a file's information.
## Oriana June 2015

from xml.dom import minidom
import os
import re
import csv

mainTags = {
	'phones':'ph',
	'syllables':'syllable',
	'phonwords':'phonword',
	'phrases':'phrase'
}

class Token(minidom.Element):
	tokenList = []
	def __init__(self,tagName,node,speaker):
		self.tagName = tagName
		self.node = node
		self.speaker = speaker
		minidom.Element.__init__(self,tagName)
		self._attrs.update(node._attrs)
		Token.tokenList.append(self)




class Speaker:
	'One speaker in a dialogue with a unique ID number.'

	def __init__(self, ID, xmlDir):
		self.ID = ID
		self.xmlDir = xmlDir

	def makeTree(self, tag):
		try:
			xmlFile = '%s%s/%s.%s.xml'%(self.xmlDir, tag, self.ID, tag)
			tree = minidom.parse(xmlFile)
			for c in tree.firstChild.childNodes:
				if c.nodeType == 1:
					c.setIdAttribute('nite:id')
			setattr(self,tag+'Tree',tree)
			nameOfTag = mainTags[tag]
			setattr(self,tag+'List',tree.getElementsByTagName(nameOfTag))
		except Exception, e:
			print "Can't build %s Tree for %s" % (tag, self.ID)
			raise e

	def getTokens(self,phone):
		assert hasattr(self,'phonesList'), "Need to create a phonesList first. Try using the makeTree(phones) method."
		tokenList = [t for t in self.phonesList if t.firstChild.data==phone]
		return tokenList

# Gets the nodes corresponding to those defined by nite:child
def getChildren(node,childTree):
	nitechild = node.getElementsByTagName('nite:child')[0]
	hrefs = re.search('.*#(.*)',nitechild.getAttribute('href')).groups()[0]
	idStartEnd = hrefs.split('..')
	# print idStartEnd
	childIDs = []
	if idStartEnd[0]==idStartEnd[-1]:
		childIDs = re.search('id\((\w*)\)',idStartEnd[0]).groups()[0]
		# print "Only 1 child : " + " ".join(childIDs)
	else:
		assert len(idStartEnd)==2, "Can't find first/last child IDs for %s" % str(node)
		start = re.search('id\((\w*)\)',idStartEnd[0]).groups()[0]
		end = re.search('id\((\w*)\)',idStartEnd[1]).groups()[0]
		startNo = re.search('.*\_..(\d+)',start).groups()[0]
		endNo = re.search('.*\_..(\d+)',end).groups()[0]
		prefix = re.search('(.*\_..)\d+',start).groups()[0]
		for n in range(int(startNo),int(endNo)+1):
			childIDs.append(prefix+str(n))
		# print childIDs
	return childIDs



















