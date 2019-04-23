#!/bin/bash
# argument is release version

# this is the simulation
cd /Users/digitaldust/Documents/clients/LABSS-ISTC-CNR/PROTON-OC
/Applications/NetLogo\ 6.0.4/netlogo-headless.sh --model PROTON-OC.nlogo --setup-file outputs/exp-OC.xml --threads 4 --table outputs/table-output.csv > outputs/netlogo.log

# now we save both result and experiment file
#https://unix.stackexchange.com/questions/340010/how-do-i-create-sequentially-numbered-file-names-in-bash

today="$( date +"%Y%m%d" )"
number=0
suffix='00'
while test -e "/Users/digitaldust/Documents/$1/$today/$suffix"; do
    (( ++number ))
    suffix="$( printf -- '%02d' "$number" )"
done

dname="/Users/digitaldust/Documents/$1/$today/$suffix"

printf 'Will use "%s" as dirname\n' "$dname"
mkdir -p $dname

cp outputs/table-output.csv outputs/exp-OC.xml outputs/netlogo.log $dname
