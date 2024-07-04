#!/bin/bash

###usage ./change_header.sh $in_file $taxid

file=$1
taxid=$2

#grep -n '>' $file > list
#cut -d ':' -f1 list > line_number

newname="|kraken:taxid|${taxid} ";
###check if header has spaces then replace at the first space or end of line
if grep '>' $file | grep -q '[[:space:]]'; then
	echo "file header has spaces"
	sed -i -r "s/\s+/$newname/" $file
else
	echo "file header has NO spaces"
	sed  -i "/^>/ s/$/$newname/" $file
fi

#while read LINE;
#do
#  	line_number=$(cut -d ':' -f1 <<< "$LINE");
#        oldname=$(cut -d' ' -f1 <<< "$LINE" | cut -d '>' -f2);
#        #echo "$oldname"
#        newname="${oldname}|kraken:taxid|${taxid}";
#        #echo "$newname"
#        sed -i "${line_number}s/$oldname/$newname/" $file
#done < list

#rm list
#rm line_number
