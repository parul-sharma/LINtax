#!/usr/bin/env python
'''Usage: ./creating-taxonomy-files.py --in_file $input_data_file_with_LINS --names-dmp-out names.dmp --nodes-dmp-out nodes.dmp'''



import sys
import pandas as pd
import argparse


# Function to convert list into string
def list_to_string(LIN):
    mystring = ','.join(map(str, LIN))
    return mystring  

# Function to convert string to List
def convert_LIN_string(LIN):
    LIN_string = LIN.split(",")
    return LIN_string

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
        nodes.write(str(taxid) + "\t|\t" + str(parent) + "\t|\t" + str(rank[start+i]) + "\t|\t-\t|\n")
        #nodes.write(node_update)
        names.write(str(taxid) + "\t|\t" + str(rank[start+i]) + "_" + str(LIN[i]) + "\t|\t-\t|\t" + str(LIN[i]) + "\t\n")
        #names.write(name_update)
        taxa_LIN.append(taxid)
        parent_LIN.append(parent)
        parent=taxid
        taxid=taxid+1
    return taxa_LIN, parent_LIN
        

# Function for Adding subsequent genomes in nodes and names.dmp files
# parent : parent taxid, passed to the function 
# start : integer number indicating the rank of the LIN position. Used as key against the Rank dictionary defined above
# taxa_LIN and parent_LIN are lists of taxids and parent_taxids passed in the function call. 
# These are retained from the most similar genome LIN.
def adding_to_nodes_and_names(nodes, names, parent, start, LIN, taxa_LIN, parent_LIN):
    for i in range(len(LIN)-start):
        global taxid
        nodes.write(str(taxid) + "\t|\t" + str(parent) + "\t|\t" + str(rank[start+i]) + "\t|\t-\t|\n")
        names.write(str(taxid) + "\t|\t" + str(rank[start+i+1]) + "_" + str(LIN[start+i]) + "\t|\t-\t|\t" + str(LIN[start+i]) + "\t\n")
        taxa_LIN.append(taxid)
        parent_LIN.append(parent)
        parent=taxid
        taxid=taxid+1
    return taxa_LIN, parent_LIN


# Initializing taxid and parent for assignment to first genome
# these are global and changed during the process of doing things.
taxid=1
parent=1

# dictionary of ranks
# this is global but not changed
rank={1:'LIN_A', 2:'LIN_B', 3:'LIN_C', 4:'LIN_D', 5:'LIN_E', 6:'LIN_F', 7:'LIN_G', 8:'LIN_H',
       9:'LIN_I', 10:'LIN_J', 11:'LIN_K', 12:'LIN_L', 13:'LIN_M', 14:'LIN_N', 15:'LIN_O', 
       16:'LIN_P', 17:'LIN_Q', 18:'LIN_R', 19:'LIN_S', 20:'LIN_T' }

# main body
def main():
    p = argparse.ArgumentParser()
    p.add_argument('in_file')
    p.add_argument('--names-dmp-out', default='names.dmp')
    p.add_argument('--nodes-dmp-out', default='nodes.dmp')
    p.add_argument('-o', '--intermediate-results', default='data.txt')
    args = p.parse_args()

    in_file=args.in_file

    # Reading the input file
    data = pd.read_csv(in_file,sep='\t')

    # creating output files
    nodes = open(args.nodes_dmp_out, 'w')
    names = open(args.names_dmp_out, 'w')

    # adding columns for storing taxids and parent_taxids
    data['taxid_LIN'] = ''
    data['parent_LIN'] = ''

    # add the complete taxonomy of first genome:
    first_genome_LIN=data['LIN'][0]
    first_genome_LIN=convert_LIN_string(first_genome_LIN)
    # call the function to add tax info to nodes.dmp and names.dmp
    tax_info=adding_first_genome(nodes, names, 1,1,first_genome_LIN)
    
    # update the data table with taxids and parent IDs
    data['taxid_LIN'][0]= tax_info[0]
    data['parent_LIN'][0]= tax_info[1]
    
    # adding second genome onwards:
    i = 1
    while i < len(data['LIN']):
        new_genome_LIN=convert_LIN_string(data['LIN'][i])
        most_similar_LIN=find_most_similar_LIN(new_genome_LIN, data['LIN'][0:i]) #find most similar genome
        
        index_of_similarLIN=data[data['LIN']==list_to_string(most_similar_LIN)].index.values #index of most similar genome
        index_of_similarLIN=int(index_of_similarLIN)
        #print(index_of_similarLIN)
        prefix=find_longest_common_LIN(new_genome_LIN, most_similar_LIN) #length of common LIN
        #print(prefix)
        parent_LIN=data['parent_LIN'][index_of_similarLIN] #store parent_taxids of the common LIN
        taxa_LIN=data['taxid_LIN'][index_of_similarLIN] #store taxids of the common LIN
        #taxa_LIN=list_to_string(taxa_LIN[index_of_similarLIN])
        
        parent=parent_LIN[prefix] #find parent_taxid to link to new taxid
        #print(parent)
        tax_info=adding_to_nodes_and_names(nodes, names, parent, prefix, new_genome_LIN, taxa_LIN[0:prefix], parent_LIN[0:prefix])
        data['taxid_LIN'][i]= tax_info[0]
        data['parent_LIN'][i]= tax_info[1]
        
        i=i+1

    print(data)
    data.to_csv(args.intermediate_results, sep='\t',  index=False)


if __name__== '__main__':
    main()
