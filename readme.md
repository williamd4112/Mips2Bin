# Mips2bin v1.0

## Usage:
1. put mips assembly code into "source" directory
2. put data memory file into "data" directory
3. use python3 to open the "Parser.py"
4. enter data memory file's relative directory
5. enter soruce code file's relative directory
6. finally, <source file name>_iimage.bin and <data file name>_dimage.bin will be in the output directory

## Data file format:
prefix sp means the sp value
spd'1024, sph'ff are all legal expression

after sp, all the datas will be stored at index 0, 4, 8, 12...and so on

'd : decimal number
'h : hex number

