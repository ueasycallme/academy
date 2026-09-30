import sys
from isaacsim import SimulationApp
app = SimulationApp({"headless": True})
from isaacsim.core.api import World
from isaacsim.core.cloner import GridCloner
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path
CARTPOLE_USD = get_assets_root_path() + "/Isaac/IsaacLab/Robots/Classic/Cartpole/cartpole.usd"
print("USD", CARTPOLE_USD)
N = 8
world = World()
cloner = GridCloner(spacing=4.0)
cloner.define_base_env("/World/envs")
add_reference_to_stage(CARTPOLE_USD, "/World/envs/env_0/Cartpole")
paths = cloner.generate_paths("/World/envs/env", N)
cloner.clone(source_prim_path="/World/envs/env_0", prim_paths=paths)
cartpoles = Articulation(prim_paths_expr="/World/envs/env_.*/Cartpole")
world.reset()
q = cartpoles.get_joint_positions()
print("SIM q shape", tuple(q.shape), cartpoles.dof_names)
sys.stdout.flush()
app.close()
