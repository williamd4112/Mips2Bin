# Mips2bin v1.0
(NOTE: It is not include all mips instructions for now, because course progress)

## Usage:

```sh
$ python3 Parser.py <-o> <output path> <-s-d> <source file / data file> <Base PC / SP address>
```
#### Parse source code to binary file
```sh
$ python3 Parser.py -s <Source file name>  // Default PC address is 0
$ python3 Parser.py -s <Source file name> 288 // Custom PC address
```

#### Parse data file to binary file
```sh
$ python3 Parser.py -d <data file name>  // Default PC address is 1024
$ python3 Parser.py -d <data file name> 288 // Custom SP address
```
#### Custom output (Source / Data)
```sh
$ python3 Parser.py -o <Output path> -d <data file name>
```

## Data file format:
  - 'd : decimal number
  - 'h : hex number
  - 
all data will store from 0

