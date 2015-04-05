import sys
import re

lazyresolved_op = ["beq", "bne", "j", "jal"]
lazyresolved_field = ["addr"]
jump_op = ["j", "jal"]
branch_op = ["beq", "bne"]
r_types = ["add", "sub", "and", "or", "xor", "nor", "nand", "slt", "sll", "srl", "sra", "jr"]
i_types = ["addi", "lw", "lh", "lhu", "lb", "lbu", "sw", "sh", "sb", "lui", "andi", "ori", "nori", "slti"]
field_offset = {"rs":21, "rt":16, "rd":11, "shamt": 6, "immediate":0, "addr":0}
field_mask = {"rs":31, "rt":31, "rd":31, "shamt":31, "immediate":0xffff, "addr":0x3FFFFFF}

opcode_map = {}
register_map = {}
labels = {}

# build opcode_map by dictionary file
with open(sys.path[0] + '/dependency/dictionary.txt', 'r', encoding='UTF-8') as file:
    for line in file:
    	op, hexcode, regx = line.split(" ")[:3]
    	opcode_map[op] = {"code":int(hexcode, 16), "regex":regx.rstrip()}

# build register_map by register file
with open(sys.path[0] + '/dependency/register.txt', 'r', encoding='UTF-8') as file:
    for line in file:
    	key, value = line.split(" ")[:2]
    	register_map[key] = int(value)


# fields only literal symbols or digit
def resovle_digit_form(digit_str):
	if re.match("[+-]?0x[0-9A-Fa-f]+", digit_str):
		return 16
	else:
		return 10

def resolve_symbols(fields):
	for key in fields:
		if key in lazyresolved_field:
			continue
		try:
			value = fields[key]

			if value in register_map:
				yield (((register_map[value]) & field_mask[key]) << field_offset[key])
			else:
				yield ((int(value, resovle_digit_form(value)) & field_mask[key]) << field_offset[key])
		except ValueError as e:
			print(e)
			raise KeyError

def resolve(command_pc, command_word, op, fields):
	try:
		for field in resolve_symbols(fields):
			command_word  = command_word | field
		return command_word
	except KeyError as e:
		print("Unresolved symbols " ,op, fields)
	return None


def resolve_jump(command_pc, command_word, jump_label):
	# label_pc = pc_part | x << 2
	return command_word | ((labels[jump_label] & 0x0FFFFFFF) >> 2)


def resolve_branch(command_pc, command_word, jump_label):
	# label_pc = command_pc + 4 + 4 * c
	return word | (((labels[jump_label] - command_pc - 4) >> 2) & 0x0000ffff)

# Lazy Resolve words
def lazyresolve(pc, word, op, label):
	if op in jump_op:
		return resolve_jump(pc, word, label)
	elif op in branch_op:
		return resolve_branch(pc, word, label)
	else:
		print("Unknown lazy resolved word: ", op)