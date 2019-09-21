#!/bin/bash
if [ $# -lt 1 ]
then
        echo "Usage : $0 string to expand in experiments-xml"
        exit
fi


echo $netlogo

for arg in `ls experiments-xml/$1`; do
    case `hostname` in
    tiny )
        /home/paolucci/NetLogo\ 6.0.4/netlogo-headless.sh --model PROTON-OC.nlogo --setup-file $arg --table $arg.`hostname`.`git rev-parse --short HEAD`.csv > $arg.`hostname`.`git rev-parse --short HEAD`.out
        ;;
    drake1 )
        netlogo="/Applications/NetLogo\ 6.0.4/netlogo-headless.sh" ;;
    labss-simul )
        netlogo="/home/paolucci/NetLogo\ 6.0.4/netlogo-headless-2.sh" ;;
    barcelona )
        netlogo="/home/paolucci/NetLogo\ 6.0.4/netlogo-headless-2G.sh" ;; 
    pc54-77.nizza.rm.cnr.it )
        netlogo="/Applications/NetLogo\ 6.0.4/netlogo-headless.sh" ;;
    esac    
done
