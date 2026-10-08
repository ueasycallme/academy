"""校验方探针（T-6.4.2）：真正实例化 DR-Play，读回物理参数与观测噪声，确认回放时确实关掉了。"""
import argparse, sys
from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser(); parser.add_argument("--task", default="Galbot-Reach-DR-Play-v0")
AppLauncher.add_app_launcher_args(parser); args = parser.parse_args(); app = AppLauncher(args).app
import gymnasium as gym, torch
import galbot_academy.tasks  # noqa
from isaaclab_tasks.utils import parse_env_cfg
from galbot_academy.tasks.manager_based.reach import mdp
from galbot_academy.tasks.manager_based.reach.reach_env_cfg import ARM
cfg = parse_env_cfg(args.task, num_envs=8); env = gym.make(args.task, cfg=cfg).unwrapped
r = env.scene["robot"]; arm = [i for i, n in enumerate(r.joint_names) if n.startswith("right_arm_joint")]
links = [i for i, n in enumerate(r.body_names) if n.startswith("right_arm_link")]
m = r.root_physx_view.get_masses()[:, links].to(env.device) / r.data.default_mass[:, links].to(env.device)
k = r.root_physx_view.get_dof_stiffnesses()[:, arm]; d = r.root_physx_view.get_dof_dampings()[:, arm]; a = r.root_physx_view.get_dof_armatures()[:, arm]
env.reset(); env.step(torch.zeros(env.num_envs, 7, device=env.device))
obs = env.observation_manager.compute()["policy"]; c = ARM.replace(); c.resolve(env.scene)
diff = obs[:, :7] - mdp.joint_pos_rel(env, c)
print(f"{args.task}: mass ratio {m.min():.4f}..{m.max():.4f}; stiffness {k.min():.2f}..{k.max():.2f}; damping {d.min():.2f}..{d.max():.2f}; armature {a.min():.5f}..{a.max():.5f}; obs noise |max| {diff.abs().max():.2e}")
env.close(); sys.stdout.flush(); app.close()
