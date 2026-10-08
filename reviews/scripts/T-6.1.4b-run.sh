#!/bin/bash
S=/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/b3b5c5a0-a008-4fc3-a226-529016dee73c/scratchpad
P=$S/t612/6-galbot-project; O=$S/t614b; M=/home/wuql/wuql_ws/academy_ws/isaac_tutor/reviews/scripts/gpu-mem-per-process.sh
cd $P; source $S/clean14/env_isaaclab/bin/activate; export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1
run() { tag=$1; shift; t0=$(date +%s); timeout -s KILL 900 python "$@" > $O/$tag.log 2>&1 & pid=$!; bash $M $pid $O/$tag.mem & wait $pid; rc=$?; sleep 1
  echo "$tag rc=$rc t=$(( $(date +%s)-t0 ))s mem=$(sort -n $O/$tag.mem | tail -1)MiB | $(grep -a '8 s 后' $O/$tag.log)" >> $O/summary.txt; }
: > $O/summary.txt
B="scripts/probe_stuck_joint.py --headless"
for i in 1 2 3; do
  run base_$i $B
  run nosleep_$i $B --no_sleep
  run kick_$i $B --kick 0.05
  run vel100_$i $B --vel_limit_at5 100
  run eff10_$i $B --effort_scale_at5 10
  run vel_null_$i $B --vel_limit_at5 1.5
  run eff_null_$i $B --effort_scale_at5 1.0
done
for v in 1.6 2 3 10; do run vel_$v $B --vel_limit_at5 $v; done
for e in 1.2 2 5; do run eff_$e $B --effort_scale_at5 $e; done
run readback scripts/_probe_readback.py --headless --no_sleep
echo DONE >> $O/summary.txt
