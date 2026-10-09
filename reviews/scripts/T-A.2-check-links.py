import re,os,sys
from bs4 import BeautifulSoup
H=sys.argv[1]; base=os.path.join(H,'appendix')
s=BeautifulSoup(open(os.path.join(base,'A.2-error-index.html')),'html.parser')
cache={}
def sec(href):
    page,_,anc=href.partition('#')
    p=os.path.normpath(os.path.join(base,page))
    if p not in cache: cache[p]=BeautifulSoup(open(p),'html.parser')
    el=cache[p].find(id=anc)
    if el is None: return None,None
    sct=el if el.name=='section' else el.find_parent('section')
    h=sct.find(re.compile('h[1-6]'))
    return ' '.join(sct.get_text(' ').split()), h.get_text().strip('#¶ ') if h else ''
n=0
for ti,tb in enumerate(s.find_all('table')):
    for tr in tb.find_all('tr')[1:]:
        tds=tr.find_all('td'); first=tds[0]
        frags=[c.get_text() for c in first.find_all('code')] if ti==0 else []
        for a in tr.find_all('a',href=True):
            h=a['href']
            if '#' not in h: print('NOFRAG',h); continue
            t,head=sec(h); n+=1
            if t is None: print('MISSING',h); continue
            for f in frags:
                parts=[p.strip() for p in re.split(r' / |…|\.\.\.|（|）',f) if len(p.strip())>3]
                miss=[p for p in parts if p not in t]
                print(('FRAG? ' if miss else 'ok    ')+f[:50],'->',os.path.basename(h.split('#')[0]),'|',head[:40],'| miss:' if miss else '',miss if miss else '')
            if ti==1: print('sym   ',a.get_text(),'->',os.path.basename(h.split('#')[0]),'|',head[:50])
print('links',n)
