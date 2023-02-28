#!/bin/bash

####USage: ./genome_download.sh $accession_number $outpu_dir
acc_id=$1
out_dir=$2

ncbi-genome-download -F 'fasta' -A $acc_id -o $out_dir --flat-output bacteria 
