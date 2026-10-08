# 校验方探针：close() 之后的 sys.exit(3) 是否执行
import sys
from isaacsim import SimulationApp
app = SimulationApp({"headless": True})
print("before close", flush=True)
app.close()
print("AFTER CLOSE (should not print if close ends process)", flush=True)
sys.exit(3)
