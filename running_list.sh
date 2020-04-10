export NLOGO=/home/mario/NetLogo\ 6.1.1/netlogo-headless.sh
#export NLOGO=/home/paolucci/NetLogo\ 6.1.1/netlogo-headless.sh
while read p; do
  echo "$p"
  EXP=$p
  time "$NLOGO" --model PROTON-OC.nlogo --setup-file experiments-xml/$EXP --table $EXP.`hostname`.`git rev-parse --short HEAD`.csv > $EXP.`hostname`.`git rev-parse --short HEAD`.out 2>&1
  #sleep 1s
done < $1