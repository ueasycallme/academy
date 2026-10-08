"""校验方探针（T-6.4.1）：① TcpPoseCommand 的 metrics 是否按 TCP；② 去掉 reset_to_default 的对照（坑一）。"""
import argparse, os, sys
from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser()
parser.add_argument("--no_reset_default", action="store_true")
parser.add_argument("--num_envs", type=int, default=16)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app
import gymnasium as gym, torch
import galbot_academy.tasks  # noqa
from isaaclab_tasks.utils import parse_env_cfg
from galbot_academy.tasks.manager_based.reach import mdp as gmdp
from galbot_academy.tasks.manager_based.reach.reach_env_cfg import EE, TCP
cfg = parse_env_cfg("Galbot-Reach-v0", num_envs=args.num_envs)
if args.no_reset_default:
    cfg.events.reset_to_default = None
env = gym.make("Galbot-Reach-v0", cfg=cfg).unwrapped
env.reset()
robot = env.scene["robot"]
EE.resolve(env.scene)
arm = [i for i, n in enumerate(robot.joint_names) if n.startswith("right_arm_joint")]
others = [i for i in range(robot.num_joints) if i not in arm]
act = torch.zeros(env.num_envs, 7, device=env.device)
for k in range(400):
    env.step(act)
    if k in (5, 200, 365):
        term = env.command_manager.get_term("ee_pose")
        m_pos = term.metrics["position_error"]; m_rot = term.metrics["orientation_error"]
        r_pos = gmdp.tcp_position_error(env, "ee_pose", EE, **TCP); r_rot = gmdp.tcp_orientation_error(env, "ee_pose", EE, **TCP)
        link7 = robot.data.body_pos_w[:, EE.body_ids[0]]
        tgt_w = term.pose_command_w[:, :3]
        d_link7 = (link7 - tgt_w).norm(dim=-1)
        dev = (robot.data.joint_pos[:, others] - robot.data.default_joint_pos[:, others]).abs()
        j = dev.max(dim=0).values.argmax().item()
        print(f"step {k}: metric pos {m_pos.mean():.4f} | tcp reward fn {r_pos.mean():.4f} | link7-origin dist {d_link7.mean():.4f} | "
              f"metric rot {m_rot.mean():.4f} vs fn {r_rot.mean():.4f} | max|diff| pos {(m_pos-r_pos).abs().max():.2e} rot {(m_rot-r_rot).abs().max():.2e}")
        print(f"   non-arm max dev from default {dev.max():.4f} rad ({robot.joint_names[others[j]]}); episode_length_buf[0]={env.episode_length_buf[0].item()}")
env.close(); sys.stdout.flush(); app.close()
