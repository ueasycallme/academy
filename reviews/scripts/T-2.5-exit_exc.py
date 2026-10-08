# 校验方探针：SimulationApp 启动后未捕获异常，进程退出码是多少
from isaacsim import SimulationApp
app = SimulationApp({"headless": True})
from pxr import Usd
print("HAS_GetCompositionErrors", hasattr(Usd.Stage, "GetCompositionErrors"), "USD", Usd.GetVersion(), flush=True)
raise RuntimeError("probe: uncaught exception")
