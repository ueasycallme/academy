"""校验方探针（T-2.7）：add_path 之后，是"必须 update() 一帧"，还是"再试一次 / 等一会儿"也行？"""
import sys, time
from pathlib import Path
from isaacsim import SimulationApp
app = SimulationApp({"headless": True})
import omni.kit.app
m = omni.kit.app.get_app().get_extension_manager()
ext_dir = sys.argv[1]; mode = sys.argv[2]
m.add_path(ext_dir)
print("PROBE try1 (no update):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
if mode == "retry":
    print("PROBE try2 immediately (no update):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
elif mode == "sleep":
    time.sleep(2.0)
    print("PROBE try2 after sleep 2 s (no update):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
elif mode == "update":
    app.update()
    print("PROBE try2 after one update():", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
sys.stdout.flush(); app.close()
