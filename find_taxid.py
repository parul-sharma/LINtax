#!/bin/python

'''Usage: find_taxid.py $acc_id $data_file'''

import sys
import pandas as pd

acc_id=sys.argv[1]
data_file=sys.argv[2]

#read the file
data = pd.read_csv(data_file,sep='\t')

#function to convert list into string
def list_to_string(LIN):
    mystring=','.join(map(str,LIN))
    return mystring

#Function to convert string to List
def convert_LIN_string(LIN):
    LIN_string=LIN.split(",")
    return LIN_string

def main():
    index_of_ID=data[data['Accession']==acc_id].index.values #index of accession id
    index_of_ID=int(index_of_ID) 
    taxid=data['taxid_LIN'][index_of_ID]
    taxid=taxid[1:len(taxid)-1]
    taxid=convert_LIN_string(taxid)
    print(taxid[19])

if __name__== '__main__':
    main()



