#!/usr/bin/python

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser(description='LIN-kraken-db-pipeline script.')
parser.add_argument('input_file', metavar='input_file', type=str, help='Input LIN file')
parser.add_argument('output_dir', metavar='output_dir', type=str, help='Output directory')
parser.add_argument('-s', '--step', metavar='step', type=int, choices=[1, 2, 3, 4], help='Step to run (1-4)')

args = parser.parse_args()

input_file = args.input_file
output_dir = args.output_dir
step = args.step

dir = os.getcwd()

try:
    # Making result directories
    os.makedirs(os.path.join(output_dir, 'genomes'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'new_genomes_taxids'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'taxonomy'), exist_ok=True)

    if step is None or step == 1:
        # Step 1: creating taxonomy files
        os.chdir(os.path.join(output_dir, 'taxonomy'))
        subprocess.run(['python', os.path.join(dir, 'creating-taxonomy-files.py'), input_file], check=True)
        os.chdir(dir)

    # Keep in mind to remove the header from the file
    with open(input_file) as f:
        next(f)  # skip header
        for line in f:
            line = line.strip().split('\t')
            acc_id = line[4]

            if step is None or step == 2:
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
                    subprocess.run(['gunzip', '-d', os.path.join(output_dir, 'genomes', genome_file + '.gz')], check=True)
                    subprocess.run(['cp', os.path.join(output_dir, 'genomes', genome_file), os.path.join(output_dir, 'new_genomes_taxids')], check=True)
                    subprocess.run([os.path.join(dir, 'new_change_header.sh'), os.path.join(output_dir, 'new_genomes_taxids', genome_file), taxid], check=True)
                    print("Header changed")
                except subprocess.CalledProcessError as e:
                    print(f"Error changing header for genome file {genome_file}: {e}", file=sys.stderr)
                    continue

except Exception as e:
    print(f"Error running pipeline: {e}", file=sys.stderr)
    sys.exit(1)

