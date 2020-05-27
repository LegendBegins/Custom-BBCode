let stopList = ['code']
//Noparse tags
let tagList = ['b','i', 'quote']
//Regular tags with opening and closing versions
let singleList = ['br']
//Tags that don't have a closing counterpart

function onMisalignedTags(){
	console.log('Some tags appear to be misaligned')
}
function processCloseTag(tag, data = false){
	return '</' + tag + '>'
}
function processTag(tag, data = false){
	return '<' + tag + '>'
}

tagList = tagList.concat(stopList)
tagList = tagList.concat(singleList)

let tagRegex = new RegExp('(?<=\\[)(' + tagList.join('|') + ')(\\s*=.*?)?(?=\\])', '')
let endTagRegex = new RegExp('(?<=\\[/)(' + tagList.join('|') + ')(?=\\])', '')
//Positive lookbehind and lookahead to grab the tag we care about


function getTagAndOptionalData(tagSearch){
	//Grab the two capturing groups (tag and the tag data) and return them. Return empty by functionault
	let mainTag = ''
	let innerData = ''
	if(tagSearch){
		mainTag = tagSearch[1]
		//Grab main tag
		if(tagSearch[2]){
			innerData = tagSearch[2].slice(1,)
			//Also grab inner data if(it exists but remove = sign
		}
	}
	return [mainTag, innerData]
}
	

function findClosingNoParse(tag, message){
	let closeFinder = new RegExp('(?<=\\[/)(' + tag + ')(?=\\])', '')
	let endResult = closeFinder.exec(message)
	if(!endResult){
		//if the noparse tag isn't closed
		onMisalignedTags()
		return [message.length, message]
	}
	else{
		return [endResult.index - 2, message.slice(0, endResult.index - 2)]
		//Return the content just before the closing tag starts (accounting for '[/')
	}
}

//TO DO{ Ignore case (could just set tag variable to lower?)
//TO DO{ Escape evil chars
//TO DO{ Add tags that don't include closing tags (e.g. [*])
//TO DO{ @mentions
//TO DO{ Enable tolerance for whitespace

function parseBBCode(message){
	let contentEnd = 0
	//This value changes as we scan through the tag set
	let rebuiltString = ''
	let tagStack = []
	while(true){
		//Loop until we have traversed every tag in this level
		let result = tagRegex.exec(message.slice(contentEnd,))
		//We measure from contentEnd because we need to know where to search from when two tags are embedded on the same level
		let endResult = endTagRegex.exec(message.slice(contentEnd,))
		//We grab both the next start and end tags and see which comes first
		if(result && (!endResult || endResult.index > result.index)){
			//if our next tag is an open tag
			let [tag, tagData] = getTagAndOptionalData(result)
			tagStack.push(tag)
			//if there is no = in the tag, tagData will be null. if there is but it's unnecessary (e.g. [b=Random]), it will be ignored.
			rebuiltString += message.slice(contentEnd, contentEnd + result.index - 1)
			rebuiltString += processTag(tag, tagData)
			//Add everything up to and including the tag to the rebuilt string. We have to remember that results is always going to be offset by contentEnd
			contentEnd += result.index + result[0].length + 1
			if(singleList.includes(tag)){
				tagStack.pop()
			}
			else if(stopList.includes(tag)){
				//if we encounter a noparse tag
				let [endIndex, embeddedContent] = findClosingNoParse(tag, message.slice(contentEnd,))
				contentEnd += endIndex
				rebuiltString += embeddedContent
				//We have to add the index of the result as well
			}
		}
		else if(endResult){
			//if the next tag is a closing one
			rebuiltString += message.slice(contentEnd, contentEnd + endResult.index - 2)
			let endTag = endResult[0]
			let parserEnd = endResult.index + endResult[0].length + 1
			if(!tagStack){
				//if this is an unpaired closing tag, treat it as text and keep going
				rebuiltString += message.slice(contentEnd, parserEnd)
				contentEnd += parserEnd
				continue
			}
			else if(endTag != tagStack[tagStack.length - 1]){
				//if our tags don't match
				onMisalignedTags()
				endTag = tagStack[tagStack.length - 1]
			}
			rebuiltString += processCloseTag(endTag, false)
			contentEnd += parserEnd
			tagStack.pop()
		}
		else{
			//if we're out of tags
			if(tagStack.length > 0){
				//if we don't have enough closing tags
				onMisalignedTags()
				while(tagStack.length > 0){
					rebuiltString += processCloseTag(tagStack.pop(), false)
					//Finish adding missing ending tags
				}
			}
			rebuiltString += message.slice(contentEnd,)
			break
		}
	}
	return rebuiltString
}


	
let toEvaluate = '[i][br][b][quote=@LegendBegins]Hello![/quote][/b][b]Hello![/b][/i][b]Hello![/b] sdfs'
console.log(parseBBCode(toEvaluate))
toEvaluate = 'first[b]second[/b]third[i]fourth[/i]fifth'	
console.log(parseBBCode(toEvaluate))
