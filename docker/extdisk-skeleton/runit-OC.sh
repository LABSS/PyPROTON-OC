#!/bin/bash
# argument is release version

# this is the simulation
cp /extdisk/exp-OC.xml .
/opt/netlogo/netlogo-headless.sh --model PROTON-OC.nlogo --setup-file exp-OC.xml --table table-output.csv > netlogo.log 2> netlogo.log

# now we save both result and experiment file
#https://unix.stackexchange.com/questions/340010/how-do-i-create-sequentially-numbered-file-names-in-bash

today="$( date +"%Y%m%d" )"
number=0
suffix='00'
while test -e "/extdisk/OC/$1/$today/$suffix"; do
    (( ++number ))
    suffix="$( printf -- '%02d' "$number" )"
done

dname="/extdisk/OC/$1/$today/$suffix"

printf 'Will use "%s" as dirname\n' "$dname"
mkdir -p $dname

cp table-output.csv exp-OC.xml netlogo.log $dname
