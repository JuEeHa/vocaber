import random
import os
import stat
import sys

# Errors
def error(message):
	sys.stderr.write('Error: %s\n' % message)
	sys.exit(1)

# String processing
def trim(s):
	whitespace = [' ', '\t', '\n']
	while len(s) > 0 and s[0] in whitespace:
		s = s[1:]
	while len(s) > 0 and s[-1] in whitespace:
		s = s[:-1]
	return s

# Wordlist handling
def wordlist_line2entry(line):
	word, inflection, translation = line.split('\t')
	
	words = [trim(i) for i in word.split(';')]
	inflections = [trim(i) for i in inflection.split(';')]
	translations = [trim(i) for i in translation.split(';')]
	
	return (words, inflections, translations)

def load_wordlist(path):
	file = open(path, 'r')
	
	entries = []
	for line in file:
		# Comments
		if '#' in line:
			line = line[:line.index('#')]
		# Rogue whitespace
		line = trim(line)
		
		if line != '':
			entries.append(wordlist_line2entry(line))
	
	file.close()
	
	return entries

def getentries(entries, number):
	return random.sample(entries, number)

# Config handling
def config_line2entry(line):
	key, value = line.split(':')
	
	key = trim(key)
	value = trim(value)
	
	if value != '':
		# Only non-negative integers are supported
		isnumber = True
		for i in value:
			if i not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
				isnumber = False
				break
		
		if isnumber:
			value = int(value)
	
	return key, value

def load_config(path):
	file = open(path, 'r')
	
	vars = {}
	for line in file:
		# Comments
		if '#' in line:
			line = line[:line.index('#')]
		# Rogue whitespace
		line = trim(line)
		
		if line != '':
			key, value = config_line2entry(line)
			vars[key] = value
	
	file.close()
	
	return vars

def write_config(path, vars):
	file = open(path, 'w')
	
	for i in vars:
		file.write('%s: %s\n' % (i, vars[i]))
	
	file.close()

# File handling
def exists(path):
	return os.access(path, os.F_OK)

# Configurable
vocaber_dir = os.getenv('HOME') + '/.vocaber'
wordlist_dir = vocaber_dir
configfile_path = vocaber_dir + '/config'
statefile_path = vocaber_dir + '/state'

# Load config
if not exists(vocaber_dir):
	os.mkdir(vocaber_dir)

if not exists(configfile_path):
	open(configfile_path, 'w').close()

if not exists(statefile_path):
	open(statefile_path, 'w').close()

config = load_config(configfile_path)
state = load_config(statefile_path)

# Set up wordlist
# TODO: get wordlist name from command line
wordlist_name = None

if 'default-wordlist' in config:
	wordlist_name = config['default-wordlist']

if not wordlist_name:
	error('Wordlist not specified')

wordlist_path = wordlist_dir + '/' + wordlist_name + '.vocaber'

if not exists(wordlist_path):
	error('%s not found\n' % wordlist_path)

wordlist = load_wordlist(wordlist_path)

# Number of words
# TODO: get number of words from command line
number_words = None

if 'default-words' in config:
	number_words = config['default-words']

if not number_words:
	error('Number of words not specified')

# Scores
right_key = wordlist_name + '_right'
empty_key = wordlist_name + '_empty'
wrong_key = wordlist_name + '_wrong'

for i in [right_key, empty_key, wrong_key]:
	if i not in state:
		state[i] = 0

# Interactive part
# TODO: handle inflections
print 'Current score: +%i %i -%i' % (state[right_key], state[empty_key], state[wrong_key])
print '-'*16

for words, inflections, translations in getentries(wordlist, number_words):
	print ' / '.join(words)
	answer = raw_input('> ')
	
	right = False
	wrong = False
	for part in answer.split(','):
		part = trim(part)
		if part == '':
			continue
		if part in translations:
			right = True
		if part not in translations and part not in inflections:
			wrong = True
	
	if right:
		state[right_key] += 1
	elif wrong:
		state[wrong_key] += 1
	else:
		state[empty_key] += 1
	
	if not right:
		print ' / '.join(translations)
	
	print '-'*16
	

print 'Current score: +%i %i -%i' % (state[right_key], state[empty_key], state[wrong_key])
# Save state
write_config(statefile_path, state)
