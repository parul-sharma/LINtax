#!/bin/python

'''Usage: find_taxid.py $acc_id $data_file'''


#!/bin/python

'''Usage: find_taxid.py $acc_id $data_file'''

import sys
import pandas as pd

acc_id = sys.argv[1]
data_file = sys.argv[2]

# Read the file
data = pd.read_csv(data_file, sep='\t')

# Function to convert string to list
def convert_LIN_string(LIN):
    return LIN.split(",")

def main():
    index_of_ID = data[data['Accession'] == acc_id].index.values  # index of accession id
    if len(index_of_ID) == 0:
        print("Accession ID not found")
        return
    
    index_of_ID = int(index_of_ID[0]) 
    taxid = data['taxid_LIN'][index_of_ID]
    taxid_list = convert_LIN_string(taxid)
    last_element = taxid_list[-1]
    print(last_element)

if __name__ == '__main__':
    main()