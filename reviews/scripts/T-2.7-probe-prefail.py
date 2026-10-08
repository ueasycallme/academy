"""校验方探针（T-2.7）：add_path 前先启用失败一次，再看 add_path 后立即启用 / 再试 / update 后的结果。"""
import sys
from isaacsim import SimulationApp
app = SimulationApp({"headless": True})
import omni.kit.app
m = omni.kit.app.get_app().get_extension_manager()
print("PROBE pre (before add_path):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
m.add_path(sys.argv[1])
print("PROBE try1 after add_path (no update):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
print("PROBE try2 immediately (no update):", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
app.update()
print("PROBE try3 after one update():", m.set_extension_enabled_immediate("academy.hello", True), flush=True)
sys.stdout.flush(); app.close()
