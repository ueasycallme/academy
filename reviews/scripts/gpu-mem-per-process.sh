# usage: mem.sh <rootpid> <outfile> ; sums used_memory of processes in the tree of rootpid
root=$1; out=$2; : > $out
while kill -0 $root 2>/dev/null; do
  pids=" $(pstree -p $root 2>/dev/null | grep -o '([0-9]*)' | tr -d '()' | tr '\n' ' ') "
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits 2>/dev/null | awk -F', ' -v P="$pids" 'index(P," "$1" ")>0{s+=$2} END{print s+0}' >> $out
  sleep 0.5
done
