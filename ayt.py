#Auto Tuber:
#"I have no mouth but I must Survios."


PROGRAM_DESCRIPTION = 'Generates Youtube video titles.'
INDEX_FILE = "index.json"

KEY_index_templates = "templates"
KEY_index_games = "games"

KEY_game_name = "name"
KEY_game_concepts = "concepts"
KEY_concept_synsets = "synsets"

KEY_keyword_synonym = "synonym"
KEY_keyword_concepts = "concepts"
KEY_keyword_synnets = "synnets"
KEY_keyword_pos = "partofspeech"

# === Parse Arguments =========================================
import argparse
parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument('--verbose', action='store_const',
                    const=True, default=False,
					help='Print more.')
parser.add_argument('--quiet', action='store_const',
                    const=True, default=False,
					help='Print less.')
parser.add_argument('-i', dest='index_file', help='Custom index file to use')
parser.add_argument('game', help='The name of the game to load data on (from index).')
parser.add_argument('keywords', nargs='*', help='Words to use in construction of the video title.')

args = parser.parse_args()

keywords = args.keywords
game = args.game

# === Determine Logging Verbosity ============================
VERBOSE = 0
INFO = 1
WARNING = 2
ERROR = 3

PROGRAM_VERBOSITY = INFO
if args.verbose:
	PROGRAM_VERBOSITY = VERBOSE
if args.quiet:
	PROGRAM_VERBOSITY = WARNING

def Log(in_str,verbosity = INFO):
	if PROGRAM_VERBOSITY <= verbosity:
		print(("ERROR: " if verbosity == ERROR else "") + str(in_str))

# === Initialize NLTK ========================================
Log("=== Initializing Wordnet...", VERBOSE)
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet

# === Begin Program ==========================================
import sys
import json

Log("\n=== AutoYT - v0")
Log(PROGRAM_DESCRIPTION, VERBOSE)
Log("\tFor game: " + game)
Log("\tUsing keywords: " + ", ".join(keywords))


# --- Read Index Files ---
Log("\nReading Index File...", VERBOSE)

if args.index_file:
	INDEX_FILE = args.index_file
	
index_data = None
with open(INDEX_FILE) as json_file:
	try:
		index_data = json.load(json_file)
	except json.JSONDecodeError as err:
		# grab a reasonable section, say 40 characters.
		start, stop = int(max(0, err.pos - 20)), int(err.pos + 20)
		snippet = err.doc[start:stop]
		if err.pos < 20:
			snippet = '... ' + snippet
		if err.pos + 20 < len(err.doc):
			snippet += ' ...'
		print(err)
		print(snippet)
		sys.exit(1)

if not index_data:
	Log("Index file not found or invalid!", ERROR)
	sys.exit(1)


# --- Get Game from Index ---
if game not in index_data[KEY_index_games]:
	Log("Game '{0}' is not in the index file ({1})".format(game, INDEX_FILE), ERROR)
	sys.exit(1)
game_data = index_data[KEY_index_games][game]


# --- Clean Index Data ---
Log("\nCleaning Index Data...", VERBOSE)
for conkey, condata in game_data[KEY_game_concepts].items():
	# if only a single synset is specified, create a list with 1 element
	if KEY_concept_synsets not in condata:
		if "synset" in condata:
			game_data[KEY_game_concepts][conkey][KEY_concept_synsets] = [condata["synset"]]
	
	# convert concept synset list into actual synset objects
	if KEY_concept_synsets in condata:
		game_data[KEY_game_concepts][conkey][KEY_concept_synsets] = [wordnet.synset(s) for s in condata[KEY_concept_synsets]]


# --- Try to match keywords to concepts in the game defintion ---
Log("\nSynSets for keywords:", VERBOSE)

#keyword(synonym)
#keyword(n/v/a)

pos_keyword_template = r'(?P<keyword>w+)[(](?P<part>adj|adv|noun|verb)[)]'
syn_keyword_template = r'(?P<keyword>w+)[(](?P<synonym>w+)[)]'

#heuristic for keyword -> synset based on synonym, part of speech, and concept matches
def keyword_to_synnet_heuristic(keyword, synnet, pos, matching_concepts):
	return random.uniform(0, 1) 

# we want to end with a list that matches keywords to 
# possible concepts and includes information about
# user-specified parts of speech and synonyms.
# All this can be used later to best match keywords to tokens

keyword_data = []

for keyword_str in keywords:
	
	datum = {}
	
	keyword = None
	part_of_speech = None
	synonym = None
	
	# accept helper data in keyword
	keyword_parts = re.search(pos_keyword_template, keyword_str)
	if keyword_parts is None:
		keyword_parts = re.search(syn_keyword_template, keyword_str)
		
	if keyword_parts is None:
		keyword = keyword_str
	else:
		keyword = keyword_parts.group('keyword')
		
		try:
			synonym = instruction_parts.group('synonym')
		except: pass
		
		try:
			part_of_speech = instruction_parts.group('part')
		except: pass
	
	# search for synnets containing the keyword
	key_nets = wordnet.synsets(keyword)
	datum[KEY_keyword_synnets] = key_nets
	
	synonym_nets = [] if synonym is None else wordnet.synnets(synonym)
	if synonym_nets:
		datum[KEY_keyword_synonym] = synonym_nets
		
	if part_of_speech:
		datum[KEY_keyword_pos] = part_of_speech
	
	#TODO use synonym nets to augment keyword->synnet search
	#TODO use part of speech to augment keyword->synnet search

	matching_concepts = []
	
	if len(key_nets) == 0:	
		Log(" - {0}: No synsets!".format(keyword), VERBOSE)
		
		if keyword in game_data[KEY_game_concepts].keys():
			matching_concepts.append(keyword)
			Log("{0} strcomp matches a concept!".format(keyword), VERBOSE)
		
	else:
		# find concepts that have any of this keyword's synsets attached to it
		for conkey, condata in game_data[KEY_game_concepts].items():
			# this is a concept with no synset
			if KEY_concept_synsets not in condata:
				if conkey.lower() == keyword.lower():
					matching_concepts.append([conkey, None, part_of_speech, synonym])
				continue
		
			for con_net in condata[KEY_concept_synsets]:
				if con_net in key_nets:
					matching_concepts.append([conkey, con_net, part_of_speech, synonym])
					break
		
	
		if len(matching_concepts) == 0:
			default_net = key_nets[0]
			Log(" - {0}: NONE --> {1}".format(
				keyword, 
				default_net.name()), VERBOSE) 
			Log("{0} has no matching concepts!".format(keyword), VERBOSE)
			continue
	
	matching_set = matching_concepts[0][1]
	Log(" - {0}: {1} --> {2}".format(
		keyword, 
		matching_concepts[0][0], 
		(matching_set.name() if matching_set is not None else "PROPER")), VERBOSE)

	if len(matching_concepts) > 1:
		Log("{0} has multiple matching concepts!".format(keyword), VERBOSE)

# --- Grab a random template and parse it ---
import random
import string
import re

str_template = random.choice(index_data[KEY_index_templates])

template = string.Template(str_template)

tokens = re.findall(template.pattern, template.template)
token_names = [t[1] for t in tokens]

Log("\nUsing template: '{0}'".format(str_template), LOG)
Log("Tokens from template: '{0}'".format("', '".join(token_names)), VERBOSE)


# --- Compute subsitutions for template ---
import inflect
from pattern.en import conjugate, lemma

inf = inflect.engine()

# fix bug where first invocation throws a StopIteration error
try: lemma('test')
except: pass

substitutes = {}

#https://stackabuse.com/python-for-nlp-introduction-to-the-pattern-library/
#https://www.clips.uantwerpen.be/pages/pattern-en#wordnet
#https://wordnet.princeton.edu/documentation/wngloss7wn
#https://pythonprogramming.net/wordnet-nltk-tutorial/


# Sort tokens based on heuristic
# 	Uses variables such as specified token priority and grammatical category,
#	as well as token group number (group 1 precedes group 2, etc.) if that is
# 	a desired feature.

def token_heuristic(token):
	return random.uniform(0, 1)

token_sort_vals = [token_heuristic(x) for x in token_names]
sorted_zipped = sorted(zip(token_sort_vals,token_names))

Log("Tokens sorted by heuristic:", VERBOSE)
for value,token in sorted_zipped:
	Log("\t{0:.2f}: {1}".format(value, token), VERBOSE)

# One-by-one, attempt to match keywords to tokens based on a heuristic
# - Takes into account the grammatical category and the current 
# 	semantic content of other tokens (e.g. if the verb is filled, the 
# 	subject/object should be compatible with the verb)
# - Also accounts for compatibility of the keyword with the token;
# 	e.g. an adjective is hard to fit into a verb token. Usually this
# 	will be a simple Part of Speech comparison.

def keyword_token_match_heuristic(keyword, token, cur_subs):
	return random.uniform(0, 1)

for ,token in sorted_zipped:
	Log("Parsing token: %s".format(token), VERBOSE)

	if "Verb" in token:
		# '1sgp' -> 1st person, singular, past tense
		substitutes[token] = conjugate(lemma('test'), '1sgp')
		
	elif "Noun" in token:
		# select a noun
		noun = "test"
		
		# apply modifiers
		if token == "DecoratedNoun":
			# select adjectives
			decorators = ["testy"]
			substitutes[token] = " ".join(decorators + [noun])
			
		elif token == "PluralNoun":
			substitutes[token] = inf.plural(noun)
			
		else:
			substitutes[token] = noun
			
	elif "Game" in token:
		substitutes[token] = game_data[KEY_game_name]

	else:
		Log("Unknown token!: '{0}'".format(token), ERROR)


# Iterate over remaining tokens and search concepts to fit using 
# the same heuristic



# Calculate a total "fit" value based on viability of selected substitutions
# Sort proposed substitutions across templates by fitness value.




# --- Generate result based on template and substitutions ---
result = template.safe_substitute(substitutes)

Log("\nSubstitution results: '{0}'".format(result))


"""
+ hilarity lexicon for particular words that are just funny, like "wrecked"

+ add office memes as concepts esp. with visual aspect (emojis, etc)

+ fill shorter / less complicated titles with end junk tags
+ respect keyword capitalization if all csps
+ randomly all-caps other token subs

"""

#EOF