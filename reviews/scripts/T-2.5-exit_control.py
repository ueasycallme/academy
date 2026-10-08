# 对照：不启动 SimulationApp，纯 python 下 sys.exit(3) 与未捕获异常的退出码
import sys
if sys.argv[1] == "exit3":
    sys.exit(3)
raise RuntimeError("control")
