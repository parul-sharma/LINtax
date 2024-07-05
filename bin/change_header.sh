#!/bin/bash

### Usage: ./change_header.sh $in_file $taxid

file=$1
taxid=$2

newname="|kraken:taxid|${taxid}"

### Check if header has spaces then replace at the first space or end of line
if grep -q '^>.*[[:space:]]' "$file"; then
    echo "File header has spaces"
    # Insert newname after the first space
    awk -v newname="$newname" '/^>/ {sub(/ /, ""newname " "); print; next} {print}' "$file" > "${file}.tmp"
else
    echo "File header has NO spaces"
    # Append newname at the end of the header line
    sed -e "s/^\(>.*\)/\1 $newname/" "$file" > "${file}.tmp"
fi

### Replace original file with the modified file
mv "${file}.tmp" "$file"



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
