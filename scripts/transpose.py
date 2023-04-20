import csv
import sys
import os

"""
Transposes one or more CSV files like this:

one.csv
    1,  2,  3,  4
    5,  6,  7,  8
    9, 10, 11, 12

two.csv
    a, b, c
    d, e, f  

...into this:

    one, one, one, two, two
    one-01, one-02, one-03, two-01, two-02
    1,  5,  9, a, d
    2,  6, 10, b, e
    3,  7, 11, c, f
    4,  8, 12

Multiple input files are concatenated into a single output file.

Invocation: 
    $ python scripts/transpose.py one.csv two.csv > ~/transposed.csv

TODO:
    - add --mean and --median options (computes new vectors from each input file)
    - add --replace option (instead of APPENDING new computed vectors to output file, REPLACES the original input data)
"""

filenames = sys.argv[1:]
if len(filenames) == 0:
    print("Usage: list of filenames")
    sys.exit(1)

# load all files into a dict (keyed on filename)
data = {}
for filename in filenames:
    short = os.path.splitext(os.path.basename(filename))[0]
    data[short] = []
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            data[short].append(row)

# output header rows
header_one = [ "" ]
header_two = [ "" ]
max_cols = 0
for name in data:
    rows = len(data[name])
    cols = len(data[name][0])
    max_cols = max(max_cols, cols)
    for i in range(rows):
        header_one.append(name)
        header_two.append(f"{name}-{i:02d}")
print(", ".join(header_one))
print(", ".join(header_two))

# output transposed data
for col in range(max_cols):
    values = [ str(col) ]
    for name in data:
        rows = len(data[name])
        cols = len(data[name][0])
        for row in range(rows):
            value = ""
            if col < cols:
                value = data[name][row][col]
            values.append(str(value))
    print(", ".join(values))
