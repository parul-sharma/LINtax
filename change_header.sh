#!/bin/bash

###usage ./change_header.sh $in_file $taxid

file=$1
taxid=$2

grep '>' $file > list

while read LINE;
do
	oldname=$(cut -f1 -d' ' <<< "$LINE");
	#echo "$oldname"
	newname="${oldname}|kraken:taxid|${taxid}";
	#echo "$newname"
	sed -i "s/$oldname/$newname/" $file
done < list

rm list
