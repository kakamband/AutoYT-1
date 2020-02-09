
def getset(w):
	from nltk.corpus import wordnet
	index = 0
	for s in wordnet.synsets(w): 
		print("{0}: {1} - {2}".format(index, s.name(), s.definition()))
		index += 1

def synonyms(t, n=0):
	from nltk.corpus import wordnet
	w = wordnet.synsets(t)[n]
	print(w.name())
	s = []
	for l in w.lemmas():
		s.append(l.name())
	print(", ".join(s))
	
getset("test")
synonyms("test")