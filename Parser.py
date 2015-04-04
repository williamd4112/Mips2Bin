import sys
import re

lazyresolved_op = ["beq", "bne", "j", "jal"]
lazyresolved_field = ["addr"]
r_types = ["add", "sub", "and", "or", "xor", "nor", "nand", "slt", "sll", "srl", "sra", "jr"]
i_types = ["addi", "lw", "lh", "lhu", "lb", "lbu", "sw", "sh", "sb", "lui", "andi", "ori", "nori", "slti"]
field_offset = {"rs":21, "rt":16, "rd":11, "shamt": 6, "immediate":0, "addr":0}
field_mask = {"rs":31, "rt":31, "rd":31, "shamt":31, "immediate":0xffff, "addr":0x3FFFFFF}

opcode_map = {}
register_map = {}
labels = {}
unresolved_word = []
iimage = []

# build opcode_map by dictionary file
with open('./dependency/dictionary.txt', 'r', encoding='UTF-8') as file:
    for line in file:
    	op, hexcode, regx = line.split(" ")[:3]
    	opcode_map[op] = {"code":int(hexcode, 16), "regex":regx.rstrip()}

# build register_map by register file
with open('./dependency/register.txt', 'r', encoding='UTF-8') as file:
    for line in file:
    	key, value = line.split(" ")[:2]
    	register_map[key] = int(value)

# Parsing code
base_pc = 288
pc_offset = base_pc

# fields only literal symbols or digit
def resolve_symbols(fields):
	for key in fields:
		if key in lazyresolved_field:
			continue
		try:
			value = fields[key]
			if value in register_map:
				# print(value, register_map[value])
				# print("%s : 0x%08X"%(key, ((register_map[value]) << field_offset[key])))
				yield (((register_map[value]) & field_mask[key]) << field_offset[key])
			else:
				# print(value)
				# print("%s : 0x%08X"%(key, ((int(value)) << field_offset[key])))
				yield ((int(value) & field_mask[key]) << field_offset[key])
		except ValueError as e:
			raise KeyError

def resolve(command_pc, op, fields):
	try:
		for field in resolve_symbols(fields):
			word = iimage[int((command_pc - base_pc) / 4)] 
			iimage[int((command_pc - base_pc) / 4)]  = word | field
			# print("word = 0x%08X"%iimage[int((command_pc - base_pc) / 4)])
	except KeyError as e:
		print("Unresolved symbols")

def resolve_jal(command_pc, jump_label):
	# label_pc = pc_part | x << 2
	label_pc = labels[jump_label]
	c = (label_pc & 0x0FFFFFFF) >> 2; # mask pc part, and shift right 2
	iimage[int((command_pc - base_pc) / 4)] = iimage[int((command_pc - base_pc) / 4)] | c
	# print("0x%08X"%iimage[int((command_pc - base_pc) / 4)], command_pc)

def resolve_beq(command_pc, jump_label):
	# label_pc = command_pc + 4 + 4 * c
	label_pc = labels[jump_label]
	c = ((label_pc - command_pc - 4) >> 2) & 0x0000ffff
	iimage[int((command_pc - base_pc) / 4)] = iimage[int((command_pc - base_pc) / 4)] | c
	# print("0x%08X"%iimage[int((command_pc - base_pc) / 4)], command_pc)

def writeWord(word):
	offsets = [24, 16, 8, 0]
	for offset in offsets:
		file.write(bytes([ (word >> offset) & 0xff ]))

# Data segments
dimage = []
target_data = input("Enter data memory path: ")
base_sp = 0
with open('./data/' + target_data, 'r', encoding='UTF-8') as file:
    for line in file:
    	form, value = line.split('\'', 1)[:2]
    	if form.endswith("d"):
    		value = int(value)
    	elif form.endswith('h'):
    		value = int(value, 16)
    	if form.startswith('sp'):
    		base_sp = value
    	else:
    		dimage.append(value)

# Text segments
# Read source code and store unresolved jump label
target_src = input("Enter source code path: ")
terminal_out = sys.stdout;
sys.stdout = open('./log/' + target_src + '.log', 'w')
with open('./source/' + target_src, 'r', encoding='UTF-8') as file:
    for line in file:
    	line = line.strip()
    	op = line.split(' ', 1);

    	# Parse labels
    	if op[0].endswith(':'):
    		labels[op[0][:-1]] = pc_offset
    		# print(op[0][:-1], pc_offset)
    		# label and expression in the same line
    		if len(op) > 1:
    			line = op[1]
    			op = op[1].split(' ', 1)

    	# Parse expression
    	try:
    		#print(pc_offset)
    		print(op[0])
    		match = re.match(opcode_map[op[0]]["regex"], line)
    		# Syntax check
    		if match:
    			fields = match.groupdict()
    			print(fields)
    			# print("0x%08x"%opcode_map[op[0]]["code"])
    			iimage.append(opcode_map[op[0]]["code"])

    			resolve(pc_offset, op[0], fields)
    			# If lazy resolved
    			if op[0] in lazyresolved_op:
    				unresolved_word.append({"pc":pc_offset, "op":op[0],"label": fields["addr"]})

    		else:
    			print("Syntax Error at %d: %s"%(pc_offset, op[0]))

    		# Read next instruction
    		pc_offset = pc_offset + 4
    	except KeyError as e:
    		print("Unknown command: ", e)

# Resolve words
# print("Unresolved words:")
for record in unresolved_word:
	if record["op"] == "jal":
		resolve_jal(record["pc"], record["label"])
	elif record["op"] == "beq" or record["op"] == "bne":
		resolve_beq(record["pc"], record["label"])



# Ouput binary file
# print(base_pc, int((pc_offset - base_pc) / 4))
sys.stdout = terminal_out
with open("./output/" + target_src + "_iimage.bin", 'bw+') as file:
	writeWord(base_pc) # Write base_pc
	writeWord(int((pc_offset - base_pc) / 4)) # Write word count
	for word in iimage:
		writeWord(word)
	print("./output/" + target_src + "_iimage.bin" + " output")

with open("./output/" + target_data + "_dmage.bin", 'bw+') as file:
	writeWord(base_sp) # Write base_pc
	writeWord(len(dimage)) # Write word count
	for word in dimage:
		writeWord(word)
	print("./output/" + target_data + "_dmage.bin" + " output")
print('./log/' + target_src + '.log' + " output")