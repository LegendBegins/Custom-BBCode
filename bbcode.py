import re

stopList = ['code']
#Noparse tags
tagList = ['b','i', 'quote']
#Regular tags with opening and closing versions

RESERVED_TAG = 'bbcode'
#Feel free to change if you want it


def onMisalignedTags():
	print('Some tags appear to be misalligned')

def processCloseTag(tag, data = None):
	return '</' + tag + '>'

def processTag(tag, data = None):
	return '<' + tag + '>'


tagList.extend(stopList)
tagList.append(RESERVED_TAG)

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
		return 0, message
	else:
		return endResult.start() - 2, message[:endResult.start() - 2]
		#Return the content just before the closing tag starts (accounting for '[/')

def parseBBCode(message):
	contentEnd = 0
	#This value only changes if we find a deeper tag set. It is returned 
	tag = ''
	endTag = ''
	rebuiltString = ''
	while True:
		#Loop until we have traversed every tag in this level
		result = re.search(tagRegex, message[contentEnd:])
		#We measure from contentEnd because we need to know where to search from when two tags are embedded on the same level
		endResult = re.search(endTagRegex, message[contentEnd:])
		#We grab both the next start and end tags and see which comes first
		if result:
			hasInnerTags = False
			if not endResult or endResult.start() > result.start():
				#If we find another opening tag before a closing one, we need to go a step deeper
				hasInnerTags = True
				tag, tagData = getTagAndOptionalData(result)
				#If there is no = in the tag, tagData will be null. If there is but it's unnecessary (e.g. [b=Random]), it will be ignored.
				rebuiltString += message[contentEnd: contentEnd + result.start() - 1] + processTag(tag, tagData)
				#Add everything up to and including the tag to the rebuilt string. We have to remember that results is always going to be offset by contentEnd
				contentEnd += result.end() + 1
				if tag not in stopList:
					endIndex, embeddedContent = parseBBCode(message[contentEnd:])
					contentEnd += endIndex
					rebuiltString += embeddedContent
				else:
					#If we encounter a noparse tag
					endIndex, embeddedContent = findClosingNoParse(tag, message[contentEnd:])
					contentEnd += endIndex
					rebuiltString += embeddedContent
					#We have to add the index of the result as well
				endResult = re.search(endTagRegex, message[contentEnd:])
				#Search for ending tag after our enclosed data ends. Update endResult with the new tag after embedded content

			if endResult:
				if hasInnerTags:
					rebuiltString += message[contentEnd:contentEnd + endResult.start() - 2]
					#Embed everything up to our closing tag in the resulting content
					contentEnd += endResult.end() + 1
					#We have to add 1 to account for close bracket and shift our index forward
					endTag = endResult.groups()[0]
					#We only care about updating the end tag if we need to check that it matches for inner tags.
					rebuiltString += processCloseTag(endTag, None)
				else:
					#If another opening tag exists later but 
					return contentEnd, rebuiltString
				
			if endTag != tag:
				#If tag is an empty string, endTag is necessarily also an empty string because result is necessarily null
				#Otherwise, it means there's a deeper set of tags and the end tag doesn't match the start tag
				onMisalignedTags()
				return contentEnd, rebuiltString
		else:
			#If we didn't find any more opening tags, we've reached the end of the tags on this level (and by definition, lower levels)
			return contentEnd, rebuiltString
			#Return the index of where this tag's scope ends

def evaluateBBCode(codeString):
	return parseBBCode('[' + RESERVED_TAG + ']' + codeString + '[/' + RESERVED_TAG + ']')[1]

	
toEvaluate = '[i][i][quote=@LegendBegins]Hello![/quote][/i][b]Hello![/b][/i][b]Hello![/b] sdfs'
print(evaluateBBCode(toEvaluate))
toEvaluate = 'first[b]second[/b]third[i]fourth[/i]fifth'	
print(evaluateBBCode(toEvaluate))
