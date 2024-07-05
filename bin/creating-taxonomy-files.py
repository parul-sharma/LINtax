#!/usr/bin/env python
'''Usage: ./creating-taxonomy-files.py --in_file $input_data_file_with_LINS --names-dmp-out names.dmp --nodes-dmp-out nodes.dmp'''

import sys
import pandas as pd
import argparse

# Function to convert list into string
def list_to_string(LIN):
    return ','.join(map(str, LIN))

# Function to convert string to List
def convert_LIN_string(LIN):
    return LIN.split(",")

# Function to find the length of the common LIN between new genome and most similar genome
def find_longest_common_LIN(LIN, most_common_LIN):
    i = 0
    while i < len(LIN) and LIN[i] == most_common_LIN[i]:
        i += 1
    prefix = LIN[0:i]
    return len(prefix)

# Function to find the most similar genome by comparing new genome LIN against LINs already in db with assigned taxids 
def find_most_similar_LIN(LIN, genome_LIN_db):
    most_similar_LIN = ''
    max_common = 0
    for i in range(len(genome_LIN_db)):
        genome_LIN = convert_LIN_string(genome_LIN_db[i])
        common = find_longest_common_LIN(LIN, genome_LIN)
        if common > max_common:
            max_common = common
            most_similar_LIN = genome_LIN
    return most_similar_LIN

# Function for Adding first genome in nodes and names.dmp files
# parent : parent taxid, passed to the function 
# start : integer number indicating the rank of the LIN position. Used as key against the Rank dictionary defined above
def adding_first_genome(nodes, names, parent, start, LIN):
    taxa_LIN=[]
    parent_LIN=[]
    for i in range(len(LIN)):
        global taxid
        nodes.write(f"{taxid}\t|\t{parent}\t|\t{rank[start+i]}\t|\t-\t|\n")
        names.write(f"{taxid}\t|\t{rank[start+i]}_{LIN[i]}\t|\t-\t|\t{LIN[i]}\t\n")
        taxa_LIN.append(taxid)
        parent_LIN.append(parent)
        parent = taxid
        taxid += 1
    return taxa_LIN, parent_LIN

# Function for Adding subsequent genomes in nodes and names.dmp files
# parent : parent taxid, passed to the function 
# start : integer number indicating the rank of the LIN position. Used as key against the Rank dictionary defined above
# taxa_LIN and parent_LIN are lists of taxids and parent_taxids passed in the function call. 
# These are retained from the most similar genome LIN.
def adding_to_nodes_and_names(nodes, names, parent, start, LIN, taxa_LIN, parent_LIN):
    for i in range(len(LIN) - start):
        global taxid
        nodes.write(f"{taxid}\t|\t{parent}\t|\t{rank[start + i]}\t|\t-\t|\n")
        names.write(f"{taxid}\t|\t{rank[start + i + 1]}_{LIN[start + i]}\t|\t-\t|\t{LIN[start + i]}\t\n")
        taxa_LIN.append(taxid)
        parent_LIN.append(parent)
        parent = taxid
        taxid += 1
    return taxa_LIN, parent_LIN

# Initializing taxid and parent for assignment to first genome
# these are global and changed during the process of doing things.
taxid = 1
parent = 1

# dictionary of ranks
# this is global but not changed
rank = {
    1: 'LIN_A', 2: 'LIN_B', 3: 'LIN_C', 4: 'LIN_D', 5: 'LIN_E', 6: 'LIN_F', 7: 'LIN_G', 8: 'LIN_H',
    9: 'LIN_I', 10: 'LIN_J', 11: 'LIN_K', 12: 'LIN_L', 13: 'LIN_M', 14: 'LIN_N', 15: 'LIN_O',
    16: 'LIN_P', 17: 'LIN_Q', 18: 'LIN_R', 19: 'LIN_S', 20: 'LIN_T'
}

# main body
def main():
    p = argparse.ArgumentParser()
    p.add_argument('in_file')
    p.add_argument('--names-dmp-out', default='names.dmp')
    p.add_argument('--nodes-dmp-out', default='nodes.dmp')
    p.add_argument('-o', '--intermediate-results', default='data.txt')
    args = p.parse_args()

    in_file = args.in_file

    # Reading the input file
    data = pd.read_csv(in_file, sep='\t')

    # creating output files
    nodes = open(args.nodes_dmp_out, 'w')
    names = open(args.names_dmp_out, 'w')

    # adding columns for storing taxids and parent_taxids
    data['taxid_LIN'] = ''
    data['parent_LIN'] = ''

    # add the complete taxonomy of first genome:
    first_genome_LIN = data.loc[0, 'LIN']
    first_genome_LIN = convert_LIN_string(first_genome_LIN)
    # call the function to add tax info to nodes.dmp and names.dmp
    tax_info = adding_first_genome(nodes, names, 1, 1, first_genome_LIN)
    
    # update the data table with taxids and parent IDs
    data.at[0, 'taxid_LIN'] = list_to_string(tax_info[0])
    data.at[0, 'parent_LIN'] = list_to_string(tax_info[1])
    
    # adding second genome onwards:
    i = 1
    while i < len(data['LIN']):
        new_genome_LIN = convert_LIN_string(data.loc[i, 'LIN'])
        most_similar_LIN = find_most_similar_LIN(new_genome_LIN, data['LIN'][0:i])  # find most similar genome
        
        index_of_similarLIN = data[data['LIN'] == list_to_string(most_similar_LIN)].index.values  # index of most similar genome
        index_of_similarLIN = index_of_similarLIN[0]  # extract single element
        
        prefix = find_longest_common_LIN(new_genome_LIN, most_similar_LIN)  # length of common LIN
        
        parent_LIN = convert_LIN_string(data.loc[index_of_similarLIN, 'parent_LIN'])  # store parent_taxids of the common LIN
        taxa_LIN = convert_LIN_string(data.loc[index_of_similarLIN, 'taxid_LIN'])  # store taxids of the common LIN
        
        parent = parent_LIN[prefix]  # find parent_taxid to link to new taxid
        
        tax_info = adding_to_nodes_and_names(nodes, names, parent, prefix, new_genome_LIN, taxa_LIN[0:prefix], parent_LIN[0:prefix])
        data.at[i, 'taxid_LIN'] = list_to_string(tax_info[0])
        data.at[i, 'parent_LIN'] = list_to_string(tax_info[1])
        
        i += 1

    print(data)
    data.to_csv(args.intermediate_results, sep='\t', index=False)

if __name__ == '__main__':
    main()
