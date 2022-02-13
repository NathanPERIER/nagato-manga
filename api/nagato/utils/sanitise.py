
def sanitiseNodeName(name: str) :
	if name == '..' :
		return '··'
	return name.replace('/', '\u2215')
