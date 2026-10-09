import re,subprocess,os
R='/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/b3b5c5a0-a008-4fc3-a226-529016dee73c/scratchpad/clean14/IsaacLab'
src=open('docs/appendix/A.1-api-cheatsheet.md').read()
cache={}
def line(path,n):
    if path not in cache: cache[path]=subprocess.run(['git','-C',R,'show','v2.3.2:'+path],capture_output=True,text=True).stdout.splitlines()
    L=cache[path]; return L[n-1] if 0<n<=len(L) else '<EOF>'
rows=0
for l in src.splitlines():
    m=re.match(r'\| `([^`]+)` \|',l)
    if not m: continue
    rows+=1; name=m.group(1)
    u=re.search(r'blob/v2\.3\.2/([^#]+)#L(\d+)',l); page=re.search(r'\]\(\.\./([^)#]+)',l).group(1)
    d=line(u.group(1),int(u.group(2))).strip()
    names=[re.sub(r'^.*\.','',x.strip()) for x in name.split('/')]
    ok_def=any(re.search(rf'(class|def) {re.escape(n)}\b',d) for n in names)
    txt=open('docs/'+page).read()
    inpage=[n for n in names if n in txt]
    flag='' if ok_def and len(inpage)==len(names) else '  <<<'
    print(f'{name[:45]:45} | {d[:60]:60} | page {os.path.basename(page)[:22]} has {inpage}{flag}')
print('rows',rows)
