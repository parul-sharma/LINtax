#!/bin/python

'''USAGE: ./report-lin.py lingroups.txt taxonomy/data.txt input.report'''

import sys
import pandas as pd
import argparse
import os

# Function to convert string to List
def convert_LIN_string(LIN):
    LIN_string = LIN.split(",")
    return LIN_string

def find_taxid_of_lingroup(lingroup, data):
    similarLIN = [i for i in data['LIN'] if i.startswith(lingroup)]
    top_LIN = similarLIN[0]
    index = data[data['LIN'] == top_LIN].index.values
    index = int(index[0])
    taxids = data['taxid_LIN'][index]
    taxids = convert_LIN_string(taxids)
    lingroup = convert_LIN_string(lingroup)
    LINgroup_taxids = taxids[0:len(lingroup)]
    return LINgroup_taxids

def cumulative_sum(taxids, in_file):
    reads = 0
    last_taxid = taxids[-1]
    index = in_file[in_file[4] == int(last_taxid)].index.values
    if index.size > 0:
        index = int(index[0])
        reads = in_file[1][index]
    return reads

def assigned_reads(taxids, in_file):
    reads = 0
    last_taxid = taxids[-1]
    index = in_file[in_file[4] == int(last_taxid)].index.values
    if index.size > 0:
        index = int(index[0])
        reads = in_file[2][index]
    return reads

def total_reads_count(taxids, in_file):
    reads = 0
    taxid = taxids[0]
    index = in_file[in_file[4] == int(taxid)].index.values
    if index.size > 0:
        index = int(index[0])
        reads = in_file[1][index]
    return reads

def total_reads_length(taxids, in_output):
    read_length = 0
    last_taxid = taxids[-1]
    index = in_output[in_output[2] == int(last_taxid)].index.values
    if index.size > 0:
        for i in range(len(index)):
            curr_index = int(index[i])
            if '|' in str(in_output[3][curr_index]):
                read_length = read_length + int(in_output[3][curr_index].split('|')[0])
            else:
                read_length = read_length + in_output[3][curr_index]
    return read_length

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lin_file', help='txt file containing lingroup names and prefixes')
    p.add_argument('--data_file', help='txt file containing the taxonomic details produced in the db construction step')
    p.add_argument('--in_file_report', help='report output generated from kraken2 (condensed output file)')
    p.add_argument('--in_file_output', help='default output generated from kraken2 (output file)')
    p.add_argument('--output')
    args = p.parse_args()

    lin_file = pd.read_csv(args.lin_file, sep='\t')
    data = pd.read_csv(args.data_file, sep='\t')
    data['taxid_LIN'] = data['taxid_LIN'].str.replace("[\]\[]", '')
    data['parent_LIN'] = data['parent_LIN'].str.replace("[\]\[]", '')

    in_file = pd.read_csv(args.in_file_report, sep='\t', header=None, index_col=False)
    in_output = pd.read_csv(args.in_file_output, sep='\t', header=None, index_col=False)

    out_file = lin_file.copy()
    out_file['Assigned_reads'] = ''
    out_file['Percentage_assigned_reads'] = ''
    out_file['Unique_Assigned_reads'] = ''
    out_file['Percentage_unique_assigned_reads'] = ''
    out_file['Total_reads_length'] = ''

    temp_taxid = find_taxid_of_lingroup(lin_file.loc[0, 'LINgroup_prefix'], data)
    total_reads = total_reads_count(temp_taxid, in_file)

    i = 0
    while (i < len(lin_file['LINgroup_Name'])) and (total_reads != 0):
        taxid = find_taxid_of_lingroup(lin_file.loc[i, 'LINgroup_prefix'], data)
        cumulative_reads = cumulative_sum(taxid, in_file)
        unique_reads = assigned_reads(taxid, in_file)
        reads_length = total_reads_length(taxid, in_output)

        out_file.loc[i, 'Assigned_reads'] = cumulative_reads
        out_file.loc[i, 'Percentage_assigned_reads'] = (cumulative_reads / total_reads) * 100
        out_file.loc[i, 'Unique_Assigned_reads'] = unique_reads
        out_file.loc[i, 'Percentage_unique_assigned_reads'] = (unique_reads / total_reads) * 100
        out_file.loc[i, 'Total_reads_length'] = reads_length
        i = i + 1

    df = pd.DataFrame({"LINgroup_Name": ['Total_reads'], "Assigned_reads": [total_reads]})
    out_file = pd.concat([out_file, df], ignore_index=True)
    #retain only lingroups with assignments
    out_file_filtered = out_file[out_file['Percentage_assigned_reads'] != 0]

    #output_dir = os.path.dirname(args.output)
    #if not os.path.exists(output_dir):
    #    os.makedirs(output_dir)

    out_file_filtered.to_csv(args.output, sep=',', index=False)

if __name__ == '__main__':
    main()