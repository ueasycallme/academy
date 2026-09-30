import sys
from isaaclab.app import AppLauncher
app = AppLauncher(headless=True).app
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG
N = 8
@configclass
class CartpoleSceneCfg(InteractiveSceneCfg):
    robot: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
sim = sim_utils.SimulationContext(sim_utils.SimulationCfg())
scene = InteractiveScene(CartpoleSceneCfg(num_envs=N, env_spacing=4.0))
sim.reset()
q = scene["robot"].data.joint_pos
print("LAB q shape", tuple(q.shape), scene["robot"].joint_names)
sim.clear_all_callbacks(); sim.clear_instance()
sys.stdout.flush()
app.close()
