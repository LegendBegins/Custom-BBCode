# Custom Python BBCode
An easily-extendable BBCode parser for Python

How to customize:

1. Add normal tags to the tagList list

2. Add tags that indicate following content should not be parsed to stopList

3. Modify behavior of onMisalignedTags(), processCloseTag(), and processTag()

4. Have fun!

Notes: 

The data variable in the tag processing functions contains variable data that might exist within tags such as [quote=@LegendBegins]This is a neat script![/quote]. Examples have been provided.

Tags are currently case sensitive, but this can be patched by converting all instances of the tag variable in parseBBCode() to lowercase

This is still being tested, so I don't make stability guarantees as of yet. Please try to break it and let me know how you did it! Stack overflows don't count.

Feel free to subscribe to me over at https://YouTube.com/LegendBegins!
