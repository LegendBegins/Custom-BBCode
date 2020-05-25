import re

stopList = ['code']
#Noparse tags
tagList = ['b','i', 'quote']
#Regular tags with opening and closing versions

def onMisalignedTags():
	print('Some tags appear to be misaligned')

def processCloseTag(tag, data = None):
	return '</' + tag + '>'

def processTag(tag, data = None):
	return '<' + tag + '>'


tagList.extend(stopList)

tagRegex = '(?<=\[)(' + '|'.join(tagList) + ')(\\s*=.*?)?(?=\])'
endTagRegex = '(?<=\[/)(' + '|'.join(tagList) + ')(?=\])'
#Positive lookbehind and lookahead to grab the tag we care about


def getTagAndOptionalData(tagSearch):
	#Grab the two capturing groups (tag and the tag data) and return them. Return empty by default
	mainTag = ''
	innerData = ''
	if tagSearch:
		mainTag = tagSearch.groups()[0]
		#Grab main tag
		if tagSearch.groups()[1]:
			innerData = tagSearch.groups()[1][1:]
			#Also grab inner data if it exists but remove = sign
	return mainTag, innerData
	

def findClosingNoParse(tag, message):
	closeFinder = '(?<=\[/)(' + tag + ')(?=\])'
	endResult = re.search(closeFinder, message)
	if not endResult:
		#If the noparse tag isn't closed
		onMisalignedTags()
		return len(message), message
	else:
		return endResult.start() - 2, message[:endResult.start() - 2]
		#Return the content just before the closing tag starts (accounting for '[/')

def parseBBCode(message):
	contentEnd = 0
	#This value changes as we scan through the tag set
	rebuiltString = ''
	tagStack = []
	while True:
		#Loop until we have traversed every tag in this level
		result = re.search(tagRegex, message[contentEnd:])
		#We measure from contentEnd because we need to know where to search from when two tags are embedded on the same level
		endResult = re.search(endTagRegex, message[contentEnd:])
		#We grab both the next start and end tags and see which comes first
		if result and (not endResult or endResult.start() > result.start()):
			#If our next tag is an open tag
			tag, tagData = getTagAndOptionalData(result)
			tagStack.append(tag)
			#If there is no = in the tag, tagData will be null. If there is but it's unnecessary (e.g. [b=Random]), it will be ignored.
			rebuiltString += message[contentEnd: contentEnd + result.start() - 1]
			rebuiltString += processTag(tag, tagData)
			#Add everything up to and including the tag to the rebuilt string. We have to remember that results is always going to be offset by contentEnd
			contentEnd += result.end() + 1
			if tag in stopList:
				#If we encounter a noparse tag
				endIndex, embeddedContent = findClosingNoParse(tag, message[contentEnd:])
				contentEnd += endIndex
				rebuiltString += embeddedContent
				#We have to add the index of the result as well
		elif endResult:
			#If the next tag is a closing one
			rebuiltString += message[contentEnd:contentEnd + endResult.start() - 2]
			endTag = endResult.groups()[0]
			parserEnd = endResult.end() + 1
			if not tagStack:
				#If this is an unpaired closing tag, treat it as text and keep going
				rebuiltString += message[contentEnd:parserEnd]
				contentEnd += parserEnd
				continue
			elif endTag != tagStack[-1]:
				#If our tags don't match
				onMisalignedTags()
				endTag = tagStack[-1]
			rebuiltString += processCloseTag(endTag, None)
			contentEnd += parserEnd
			tagStack.pop()
		else:
			#If we're out of tags
			if tagStack:
				#If we don't have enough closing tags
				onMisalignedTags()
			rebuiltString += message[contentEnd:]
			break
	return rebuiltString


	
toEvaluate = '[i][b][quote=@LegendBegins]Hello![/quote][/b][b]Hello![/b][/i][b]Hello![/b] sdfs'
print(parseBBCode(toEvaluate))
toEvaluate = 'first[b]second[/b]third[i]fourth[/i]fifth'	
print(parseBBCode(toEvaluate))
