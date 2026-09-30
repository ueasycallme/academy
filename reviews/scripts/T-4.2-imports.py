import sys, importlib
from isaaclab.app import AppLauncher
app = AppLauncher(headless=True).app
names = {"isaaclab.app":["AppLauncher"],"isaaclab.sim":["SimulationContext","SimulationCfg","UsdFileCfg"],
"isaaclab.scene":["InteractiveScene","InteractiveSceneCfg"],"isaaclab.assets":["Articulation","RigidObject","ArticulationCfg"],
"isaaclab.actuators":["ImplicitActuatorCfg","IdealPDActuatorCfg","DCMotorCfg"],"isaaclab.sensors":["Camera","ContactSensor","RayCaster"],
"isaaclab.managers":["ObservationTermCfg","RewardTermCfg","SceneEntityCfg"],"isaaclab.envs":["ManagerBasedRLEnv","DirectRLEnv","ManagerBasedRLEnvCfg","DirectRLEnvCfg"],
"isaaclab.envs.mdp":["joint_pos_rel","is_alive","reset_joints_by_offset"],"isaaclab.terrains":["TerrainImporterCfg","TerrainGeneratorCfg"],
"isaaclab.controllers":["DifferentialIKController","OperationalSpaceController"],"isaaclab.devices":["Se3Keyboard","Se3Gamepad"],
"isaaclab.markers":["VisualizationMarkers"],"isaaclab.utils":["configclass","math"]}
bad=[]
for m,ns in names.items():
    mod=importlib.import_module(m)
    for n in ns:
        if not hasattr(mod,n): bad.append(f"{m}.{n}")
print("IMPORT-CHECK missing:", bad or "none", "checked", sum(map(len,names.values())))
sys.stdout.flush(); app.close()
