# usage: rss-mem.sh <rootpid> <outfile> ; every 0.5 s: "<gpu_MiB> <host_rss_MiB> <mem_available_MiB>" for the process tree of rootpid
root=$1; out=$2; : > $out
while kill -0 $root 2>/dev/null; do
  pids=" $(pstree -p -T $root 2>/dev/null | grep -o '([0-9]*)' | tr -d '()' | tr '\n' ' ') "
  g=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits 2>/dev/null | awk -F', ' -v P="$pids" 'index(P," "$1" ")>0{s+=$2} END{print s+0}')
  r=$(for p in $pids; do awk '/VmRSS/{print $2}' /proc/$p/status 2>/dev/null; done | awk '{s+=$1} END{print int(s/1024)}')
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  echo "$g $r $a" >> $out
  sleep 0.5
done
