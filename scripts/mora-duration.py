## Getting average mora duration

from xml.dom import minidom
import os
import re
import csv

fileName = 'A01F0055.xml'#raw_input('What file shall I process for you? : ')
tree = minidom.parse(fileName)

moras = tree.getElementsByTagName("Mora")

dictList = []

for mora in moras:
	valDict = {}
	moraPhones = mora.getElementsByTagName('Phone')

	if len(moraPhones) == 0:
		pass
	else:
		valDict['file'] = fileName
		valDict['MoraStart'] = moraPhones[0].attributes['PhoneStartTime'].value
		valDict['MoraEnd'] = moraPhones[-1].attributes['PhoneEndTime'].value
		valDict['MoraDuration'] = float(valDict['MoraEnd']) - float(valDict['MoraStart'])
		valDict['MoraEntity'] = mora.getAttribute('MoraEntity').encode('utf-8')
		dictList.append(valDict)


colNames = ['file','MoraStart','MoraEnd','MoraDuration','MoraEntity']

with open('mora-duration.tdf','wb') as data:
	csvOut = csv.writer(data,delimiter='\t',quotechar='"')
	csvOut.writerow(colNames)
	for d in dictList:
		csvOut.writerow([d[v] for v in colNames])







