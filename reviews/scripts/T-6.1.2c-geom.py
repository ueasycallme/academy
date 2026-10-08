# 校验方：零位时每个碰撞球在世界系中的最低 z；滚子关节的阻尼值
import sys
from pxr import Usd, UsdGeom, UsdPhysics
for path in sys.argv[1:]:
    st = Usd.Stage.Open(path); xc = UsdGeom.XformCache()
    lows = []
    for p in st.Traverse(Usd.TraverseInstanceProxies()):
        if p.IsA(UsdGeom.Sphere) and p.HasAPI(UsdPhysics.CollisionAPI):
            m = xc.GetLocalToWorldTransform(p); r = UsdGeom.Sphere(p).GetRadiusAttr().Get()
            c = m.ExtractTranslation(); s = m.GetRow3(2).GetLength()
            lows.append((c[2] - r * s, r * s, str(p.GetPath())))
    lows.sort()
    print(path.split('/')[-2], 'spheres', len(lows), 'min z %.4f' % lows[0][0], 'r %.4f' % lows[0][1], 'below0', sum(1 for l in lows if l[0] < 0))
    d = [(p.GetName(), p.GetAttribute('drive:angular:physics:damping').Get(), p.GetAttribute('drive:angular:physics:stiffness').Get()) for p in st.Traverse(Usd.TraverseInstanceProxies()) if '_passive_' in p.GetName() and p.IsA(UsdPhysics.Joint)]
    if d: print('  roller joints', len(d), 'damping set', set(x[1] for x in d), 'stiffness set', set(x[2] for x in d))
