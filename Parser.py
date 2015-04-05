#!/usr/bin/python3

import sys
import re
import os
from Lexer import Lexer

# Lazy resolved word list
unresolved_word = []

# Instruction image / Data image
iimage = []
dimage = []

# Base Stack pointer / Program counter
base_sp = 1024
base_pc = 0

custom_output = False

def print_usage():
	print("Usage:  mipsi <-o> <output path> <-s-d> <source file / data file> <Base PC / SP address>")
	print("-s: interpret source file")
	print("-d: interpret data file")
	print("-o: optional, custom output path, default is iimage.bin/dimage.bin at input file directory")

# Parse options
# illegal usage
if len(sys.argv) < 2:
	print_usage()
	exit(1)
# Ouput custom
elif sys.argv[1] == '-o':
	if len(sys.argv) >= 5:
		custom_output = True
		output_path = sys.argv[2]
		option = sys.argv[3]
		input_path = sys.argv[4]

		# Optional custom PC address
		if len(sys.argv) == 6:
			base_pc = int(sys.argv[5])

	else:
		print_usage()
		exit(1)
# Default output
elif sys.argv[1] == '-s' or sys.argv[1] == '-d':
	if len(sys.argv) >= 3:
		option = sys.argv[1]
		input_path = sys.argv[2]

		# Optional custom PC address
		if len(sys.argv) == 4:
			base_pc = int(sys.argv[3])

# getIndex in iimage
def getIndex(pc, base):
	return int((pc - base) / 4)

# Write a 32 bit word to binary file in big-endian
def writeWord(file, word):
	offsets = [24, 16, 8, 0]
	for offset in offsets:
		file.write(bytes([ (word >> offset) & 0xff ]))

# Output iimage
def output(path, image, header):
	with open(path, 'bw+') as file:
		for word in header + image:
			writeWord(file, word)
		print(path + " output")

# Interpret source file and return how many bytes be written
def interpret_src(filename):	
	pc_offset = base_pc
	with open(filename, 'r', encoding='UTF-8') as file:
	    for line in file:
	    	line = line.strip()
	    	op = line.split(' ', 1);

	    	# Parse labels
	    	if op[0].endswith(':'):
	    		Lexer.labels[op[0][:-1]] = pc_offset

	    		# label and expression in the same line
	    		if len(op) > 1:
	    			line = op[1]
	    			op = op[1].split(' ', 1)

	    	# Parse expression
	    	try:
	    		print(op[0])
	    		match = re.match(Lexer.opcode_map[op[0]]["regex"], line)

	    		# Syntax check
	    		if match:
	    			fields = match.groupdict()
	    			print(fields)

	    			# print("0x%08x"%opcode_map[op[0]]["code"])
	    			iimage.append(Lexer.opcode_map[op[0]]["code"])
	    			word = iimage[getIndex(pc_offset, base_pc)]
	    			iimage[getIndex(pc_offset, base_pc)] = Lexer.resolve(pc_offset, word, op[0], fields)

	    			# If lazy resolved
	    			if op[0] in Lexer.lazyresolved_op:
	    				unresolved_word.append({"pc":pc_offset, "op":op[0],"label": fields["addr"]})
	    		else:
	    			print("Syntax Error at %d: %s"%(pc_offset, op[0]))
	    			break

	    		# Read next instruction
	    		pc_offset = pc_offset + 4

	    	except KeyError as e:
	    		print("Unknown command: ", e)
	    		break
	
	# Lazy Resolve words
	for record in unresolved_word:
		pc = record['pc']
		op = record['op']
		label = record['label']
		word = iimage[getIndex(pc, base_pc)]

		iimage[getIndex(pc, base_pc)] = Lexer.lazyresolve(pc, word, op, label)    		

	return pc_offset

# Interpret data file
def interpret_data(filename):
	with open(filename, 'r', encoding='UTF-8') as file:
	    for line in file:
	    	form, value = line.split('\'', 1)[:2]
	    	if form.endswith("d"):
	    		value = int(value)
	    	elif form.endswith('h'):
	    		value = int(value, 16)
	    	dimage.append(value)

# Output path
if not custom_output:
	# Output file name
	if option == '-s': 
		output_filename = 'iimage.bin'
	else:
		output_filename = 'dimage.bin'

	output_path = os.getcwd() + '/' + output_filename

# Change stdout to log file
terminal_out = sys.stdout;
input_filename = input_path.rsplit('/')[-1]
sys.stdout = open(sys.path[0] + '/log/' + input_filename + '.log', 'w')

# Process input
if option == '-s':
	offset = interpret_src(input_path)
	image = iimage
	header = [base_pc, int((offset - base_pc) / 4)]
elif option == '-d':
	interpret_data(input_path)
	image = dimage
	header = [base_sp, len(dimage)]

# Ouput binary file
sys.stdout = terminal_out
output(output_path, image, header)