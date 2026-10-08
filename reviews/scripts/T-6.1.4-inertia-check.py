# 校验方：对"组内只有一个连杆"的刚体，比较 USD 惯量主值/质心 与 URDF <inertial>（张量特征值）
import sys, math, xml.etree.ElementTree as ET
def eig3(A):
    # 对称 3x3 特征值（三角法）
    p1=A[0][1]**2+A[0][2]**2+A[1][2]**2; q=(A[0][0]+A[1][1]+A[2][2])/3
    if p1==0: return sorted([A[0][0],A[1][1],A[2][2]])
    p2=sum((A[i][i]-q)**2 for i in range(3))+2*p1; p=math.sqrt(p2/6)
    B=[[(A[i][j]-(q if i==j else 0))/p for j in range(3)] for i in range(3)]
    d=B[0][0]*(B[1][1]*B[2][2]-B[1][2]*B[2][1])-B[0][1]*(B[1][0]*B[2][2]-B[1][2]*B[2][0])+B[0][2]*(B[1][0]*B[2][1]-B[1][1]*B[2][0])
    r=max(-1,min(1,d/2)); phi=math.acos(r)/3
    e1=q+2*p*math.cos(phi); e3=q+2*p*math.cos(phi+2*math.pi/3); return sorted([e1,3*q-e1-e3,e3])
from pxr import Usd, UsdPhysics, UsdShade
usd, urdf = sys.argv[1], sys.argv[2]
r = ET.parse(urdf).getroot()
par = {j.find('child').get('link'): (j.find('parent').get('link'), j.get('type')) for j in r.findall('joint')}
grp = {}
for l in r.findall('link'):
    t = l.get('name')
    while t in par and par[t][1] == 'fixed': t = par[t][0]
    grp.setdefault(t, []).append(l)
st = Usd.Stage.Open(usd)
prims = list(st.Traverse(Usd.TraverseInstanceProxies()))
worst_i = worst_c = 0; n = 0
for p in prims:
    if not p.HasAPI(UsdPhysics.RigidBodyAPI): continue
    g = [l for l in grp.get(p.GetName(), []) if l.find('inertial') is not None and float(l.find('inertial/mass').get('value')) > 0]
    if len(g) != 1: print('skip(merged)', p.GetName(), len(g)); continue
    i = g[0].find('inertial'); a = {k: float(v) for k, v in i.find('inertia').attrib.items()}
    T = [[a['ixx'], a['ixy'], a['ixz']], [a['ixy'], a['iyy'], a['iyz']], [a['ixz'], a['iyz'], a['izz']]]
    ev = eig3(T); us = sorted(p.GetAttribute('physics:diagonalInertia').Get())
    xyz = [float(x) for x in i.find('origin').get('xyz').split()] if i.find('origin') is not None else [0,0,0]
    com = list(p.GetAttribute('physics:centerOfMass').Get())
    ri = max(abs(u-e)/max(e,1e-12) for u,e in zip(us,ev)); dc = math.dist(com, xyz)
    worst_i = max(worst_i, ri); worst_c = max(worst_c, dc); n += 1
    if ri > 1e-3 or dc > 1e-4: print('DIFF', p.GetName(), ev, us, xyz, com)
print(f'single-link bodies {n}: max rel inertia diff {worst_i:.2e}, max com diff {worst_c:.2e} m')
mb = [p.GetPath() for p in prims if p.HasAPI(UsdShade.MaterialBindingAPI) and UsdShade.MaterialBindingAPI(p).GetDirectBinding('physics').GetMaterial()]
print('physics material bindings:', len(mb), mb[:5])
fp = [(p.GetName(), [t.name for t in UsdPhysics.FilteredPairsAPI(p).GetFilteredPairsRel().GetTargets()]) for p in prims if p.HasAPI(UsdPhysics.FilteredPairsAPI)]
print('filtered pairs:', fp)
