#!/usr/bin/python


import argparse
import os
import subprocess
import sys

# Argument parsing
parser = argparse.ArgumentParser(description='Use LINtax-create script to create your custom taxonomy structure and save the essential files.')
parser.add_argument('input_file', metavar='input_file', type=str, help='Input LIN file')
parser.add_argument('output_dir', metavar='output_dir', type=str, help='Output directory')
parser.add_argument('-s', '--step', metavar='step', type=int, choices=[1, 2, 3, 4], help='Step to run (1-4): By default runs steps 1,3,4. Input genomes downloaded only when specified (step 2)')
parser.add_argument('-g', '--genomes', metavar='genomes_dir', type=str, required=True, help='Path to directory containing input genomes')

args = parser.parse_args()

# Assigning parsed arguments
# Resolving relative paths based on current working directory
input_file = os.path.abspath(args.input_file)
output_dir = os.path.abspath(args.output_dir)
genomes_dir = os.path.abspath(args.genomes)
step = args.step

# Current working directory
dir = os.getcwd()
# Get the directory of input_file
input_dir = os.path.dirname(input_file)

# Create a dictionary to store lines with unique LINs
unique_lines = {}
line_count = 0  # count of total lines

# Function to find the column index by header name
def find_column_index(header, column_name):
    for idx, col in enumerate(header):
        if col.strip() == column_name:
            return idx
    return None

# Read the input file and create a set and list of LINs
with open(input_file) as f:
    header = f.readline().strip().split('\t')  # read and split header line
    LIN_index = find_column_index(header, 'LIN')  # find column index for 'LIN'
    if LIN_index is None:
        print("Column 'LIN' not found in the input file header.")
        sys.exit(1)

    for line in f:
        LIN = line.strip().split('\t')[LIN_index]  # assuming LIN is at column 1
        unique_lines[LIN] = line # store the line with the LIN as key
        line_count += 1  # increment line count

# Check if all LINs are unique
new_file_created = False
if len(unique_lines) < line_count:
    # If not, create a new file with lines with unique LINs
    unique_input_file = os.path.join(input_dir, "unique_input_file.txt")
    with open(unique_input_file, "a") as f_out:
        f_out.write('\t'.join(header) + '\n')  # write header to new file
        for line in unique_lines.values():
            f_out.write(line + '\n')
    new_file_created = True
else:
    print("All LINs are unique. No new file created.")

# Use the new file if it was created, otherwise use the original input file
input_file_to_use = unique_input_file if new_file_created else input_file

try:
    # Making result directories
    os.makedirs(os.path.join(output_dir, 'genomes_with_taxids'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'taxonomy'), exist_ok=True)

    if step is None or step == 1:
        # Step 1: creating taxonomy files
        os.chdir(os.path.join(output_dir, 'taxonomy'))
        subprocess.run(['python', os.path.join(dir, 'creating-taxonomy-files.py'), input_file_to_use], check=True)
        os.chdir(dir)

    with open(input_file_to_use) as f:
        header = f.readline().strip().split('\t')  # read and split header line
        accession_index = find_column_index(header, 'Accession')  # find column index for 'Accession'
        if accession_index is None:
            print("Column 'Accession' not found in the input file header.")
            sys.exit(1)
        
        for line in f:
            line = line.strip().split('\t')
            acc_id = line[accession_index]  # assuming accession id is at column 5

            if step == 2:
                # Step 2: downloading genome (only if genomes_dir is specified)
                try:
                    os.makedirs(os.path.join(output_dir, 'genomes'), exist_ok=True)
                    subprocess.run([os.path.join(dir, 'genome_download.sh'), acc_id, os.path.join(genomes_dir)], check=True)
                    print("Genome downloaded")
                except subprocess.CalledProcessError as e:
                    print(f"Error running genome_download.sh for accession {acc_id}: {e}", file=sys.stderr)

            if step is None or step == 3:
                # Step 3: find taxid
                try:
                    result = subprocess.run(['python', 'find_taxid.py', acc_id, os.path.join(output_dir, 'taxonomy/data.txt')], capture_output=True, text=True, check=True)
                    taxid = result.stdout.strip()
                    print(f"taxid is {taxid}")
                except subprocess.CalledProcessError as e:
                    print(f"Error finding taxid for accession {acc_id}: {e}", file=sys.stderr)
                    continue

            if step is None or step == 4:
                # Step 4: change header of genome files
                genome_file = line[3]
                try:
                    if genome_file.endswith(".gz"):
                        subprocess.run(['gunzip', '-d', os.path.join(genomes_dir, genome_file + '.gz')], check=True)
                    subprocess.run(['cp', os.path.join(genomes_dir, genome_file), os.path.join(output_dir, 'genomes_with_taxids')], check=True)
                    subprocess.run([os.path.join(dir, 'change_header.sh'), os.path.join(output_dir, 'genomes_with_taxids', genome_file), taxid], check=True)
                    print("Header changed")
                except subprocess.CalledProcessError as e:
                    print(f"Error changing header for genome file {genome_file}: {e}", file=sys.stderr)
                    continue

except Exception as e:
    print(f"Error running pipeline: {e}", file=sys.stderr)
    sys.exit(1)
