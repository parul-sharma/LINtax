#!/bin/bash
#set -x
set -e

###usage: ./LIN-kraken-db-pipeline.sh $input-LIN-file $output_directory

in_file=$1
o_dir=$2

dir=$(pwd)
##making result directories
mkdir -p $o_dir/genomes
mkdir -p $o_dir/genomes_taxids
mkdir -p $o_dir/taxonomy


###step1: creating taxonomy files
cd $o_dir/taxonomy
python $dir/creating-taxonomy-files.py --in_file ${in_file} --names-dmp-out $o_dir/taxonomy/names.dmp --nodes-dmp-out $o_dir/taxonomy/nodes.dmp

cd $dir
##keep in mind to removing the header from the file
sed 1d ${in_file} > content

while read LINE;
do
	echo $LINE
	acc_id=$(cut -f5 <<< "$LINE")
	echo $acc_id
	######step2: downloading genome
	#./genome_download.sh $acc_id $o_dir/genomes 
	echo "Genome downloaded"
	######step3: find taxid
	taxid=$(python find_taxid.py $acc_id $o_dir/taxonomy/data.txt)
	echo "taxid is $taxid"
	#####step4: change header of genome files
	genome_file=$(cut -f4 <<< "$LINE")
	#gunzip -d $o_dir/genomes/${genome_file}.gz
	cp $o_dir/genomes/${genome_file} $o_dir/genomes_taxids/
	./change_header.sh $o_dir/genomes_taxids/${genome_file} $taxid 
	echo "Header changed"
done  < content

#rm content
