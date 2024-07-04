#!/usr/bin/python

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser(description='LIN-kraken-db-pipeline script.')
parser.add_argument('input_file', metavar='input_file', type=str, help='Input LIN file')
parser.add_argument('output_dir', metavar='output_dir', type=str, help='Output directory')
parser.add_argument('-s', '--step', metavar='step', type=int, choices=[1, 2, 3, 4], help='Step to run (1-4): By default runs steps 1,3,4. Input genomes downloaded only when specified (step 2)')

args = parser.parse_args()

input_file = args.input_file
output_dir = args.output_dir
step = args.step

dir = os.getcwd()
# Get the directory of input_file
input_dir = os.path.dirname(input_file)

# Create a dictionary to store lines with unique LINs
unique_lines = {}
line_count = 0  # count of total lines
#all_LINs = []

# Read the input file and create a set and list of LINs
with open(input_file) as f:
    header = f.readline() # read header 
    #lines = f.readlines() # read the rest of the lines
    #next(f)  # skip header
    for line in f:
        LIN = line.strip().split('\t')[0]  # assuming LIN is at column 1
        #all_LINs.append(LIN)
        #unique_LINs.add(LIN)
        unique_lines[LIN] = line # store the line with the LIN as key
        line_count += 1  # increment line count
        #print(unique_lines.keys())

# Check if all LINs are unique
new_file_created = False
if len(unique_lines) < line_count:
    # If not, create a new file with lines with unique LINs
    unique_input_file = os.path.join(input_dir, "unique_input_file.txt")
    #unique_LINs_copy = unique_LINs.copy()  # create a copy of unique_LINs
    with open(unique_input_file, "a") as f_out:
        f_out.write(header)  # write header to new file
          # skip header for the rest of the comparisons
        for line in unique_lines.values():
            f_out.write(line)
    new_file_created = True
else:
    print("All LINs are unique. No new file created.")

# Use the new file if it was created, otherwise use the original input file
input_file_to_use = unique_input_file if new_file_created else input_file

# The rest of your code here, using input_file_to_use instead of input_file
try:
    # Making result directories
    os.makedirs(os.path.join(output_dir, 'genomes'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'new_genomes_taxids'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'taxonomy'), exist_ok=True)

    if step is None or step == 1:
        # Step 1: creating taxonomy files
        os.chdir(os.path.join(output_dir, 'taxonomy'))
        subprocess.run(['python', os.path.join(dir, 'creating-taxonomy-files.py'), input_file_to_use], check=True)
        os.chdir(dir)

    # Keep in mind to remove the header from the file
    with open(input_file_to_use) as f:
        next(f)  # skip header
        for line in f:
            line = line.strip().split('\t')
            acc_id = line[4] # assuming accession id is at column 5

            if step == 2:
                # Step 2: downloading genome
                try:
                    subprocess.run([os.path.join(dir, 'genome_download.sh'), acc_id, os.path.join(output_dir, 'genomes')], check=True)
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
                        subprocess.run(['gunzip', '-d', os.path.join(output_dir, 'genomes', genome_file + '.gz')], check=True)
                    subprocess.run(['cp', os.path.join(output_dir, 'genomes', genome_file), os.path.join(output_dir, 'new_genomes_taxids')], check=True)
                    subprocess.run([os.path.join(dir, 'change_header.sh'), os.path.join(output_dir, 'new_genomes_taxids', genome_file), taxid], check=True)
                    print("Header changed")
                except subprocess.CalledProcessError as e:
                    print(f"Error changing header for genome file {genome_file}: {e}", file=sys.stderr)
                    continue

except Exception as e:
    print(f"Error running pipeline: {e}", file=sys.stderr)
    sys.exit(1)

