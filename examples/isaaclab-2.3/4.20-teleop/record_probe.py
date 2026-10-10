# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 record_demos.py 的同一套录制配置录一小段，看导出的 HDF5 里有什么（4.20）。

环境配置的改法逐条照搬 scripts/tools/record_demos.py 的 create_environment_config()：1 个环境、取出 success 项、
关掉超时、观测不拼接、挂 ActionStateRecorderManagerCfg。设备也一样：从环境配置的 teleop_devices 里按名字
"keyboard" 创建。不同之处只有两点：按键由脚本注入（同 keyboard_teleop_probe.py 的 provider 方式），
以及导出方式可选——record_demos.py 固定只导出成功的回合，这里默认导出全部，好让一段没完成任务的录制也落盘。

用法::

    python record_probe.py --headless                                  # 导出全部，打印 HDF5 结构
    python record_probe.py --headless --export succeeded_only          # 与 record_demos.py 相同：没成功就不落盘
"""

import argparse
import os
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="按 record_demos.py 的配置录一小段并查看 HDF5")
parser.add_argument("--task", default="Isaac-Stack-Cube-Franka-IK-Rel-v0")
parser.add_argument("--export", choices=["all", "succeeded_only"], default="all")
parser.add_argument("--dataset_file", default="./datasets/probe.hdf5")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import carb
import gymnasium as gym
import h5py
import torch

from isaacsim.core.utils.extensions import enable_extension

enable_extension("omni.appwindow")  # headless 下默认没有它，Se3Keyboard 会创建失败（见 keyboard_teleop_probe.py）
simulation_app.update()
import omni.appwindow  # noqa: E402

from isaaclab.devices.teleop_device_factory import create_teleop_device
from isaaclab.envs.mdp.recorders.recorders_cfg import ActionStateRecorderManagerCfg
from isaaclab.managers import DatasetExportMode

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

# 脚本"示教"：按住的键与步数
SCRIPT = [("Q", 15), ("W", 20), ("E", 15), ("K", 1), ("Q", 15)]


def main() -> None:
    out_dir, out_name = os.path.split(os.path.abspath(args.dataset_file))
    os.makedirs(out_dir, exist_ok=True)
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env_cfg.env_name = args.task
    success_term = env_cfg.terminations.success  # record_demos.py 把它取出来，在主循环里自己判断
    env_cfg.terminations.success = None
    env_cfg.terminations.time_out = None
    env_cfg.observations.policy.concatenate_terms = False
    env_cfg.recorders = ActionStateRecorderManagerCfg()
    env_cfg.recorders.dataset_export_dir_path = out_dir
    env_cfg.recorders.dataset_filename = os.path.splitext(out_name)[0]
    env_cfg.recorders.dataset_export_mode = (
        DatasetExportMode.EXPORT_ALL if args.export == "all" else DatasetExportMode.EXPORT_SUCCEEDED_ONLY
    )
    env = gym.make(args.task, cfg=env_cfg).unwrapped
    device = create_teleop_device("keyboard", env_cfg.teleop_devices.devices)
    print(f"[probe] 设备：{type(device).__name__}，pos_sensitivity {device.pos_sensitivity}；"
          f"recorder 项：{env.recorder_manager.active_terms}", flush=True)

    keyboard = omni.appwindow.get_default_app_window().get_keyboard()
    provider, iinput = carb.input.acquire_input_provider(), carb.input.acquire_input_interface()

    def key(name: str, pressed: bool):
        etype = carb.input.KeyboardEventType.KEY_PRESS if pressed else carb.input.KeyboardEventType.KEY_RELEASE
        provider.buffer_keyboard_key_event(keyboard, etype, getattr(carb.input.KeyboardInput, name), 0)
        iinput.distribute_buffered_events()

    env.sim.reset()
    env.reset()
    device.reset()
    steps = 0
    with torch.inference_mode():
        for name, hold in SCRIPT:
            key(name, True)
            for _ in range(hold):
                env.step(device.advance().repeat(env.num_envs, 1))
                steps += 1
            key(name, False)
        succeeded = bool(success_term.func(env, **success_term.params)[0])
        # 与 record_demos.py 的 process_success_condition() 相同的三步，只是不要求连续成功
        env.recorder_manager.record_pre_reset([0], force_export_or_skip=False)
        env.recorder_manager.set_success_to_episodes([0], torch.tensor([[succeeded]], dtype=torch.bool, device=env.device))
        env.recorder_manager.export_episodes([0])
    print(f"[probe] 录了 {steps} 步，任务成功：{succeeded}；已导出成功回合 {env.recorder_manager.exported_successful_episode_count}，"
          f"失败回合 {env.recorder_manager.exported_failed_episode_count}", flush=True)
    env.close()  # 关闭时 recorder 把文件写完

    path = os.path.join(out_dir, out_name)
    if not os.path.exists(path):
        print(f"[probe] {path} 不存在", flush=True)
        return
    with h5py.File(path, "r") as f:
        data = f["data"]
        print(f"[probe] {path}：data 下 {len(data)} 个回合，attrs total={data.attrs['total']}")
        print(f"        env_args={data.attrs['env_args']}")

        def show(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"        {name}  {obj.shape} {obj.dtype}")
            elif name.count("/") <= 1:
                print(f"        {name}/  attrs={dict(obj.attrs)}")

        data.visititems(show)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
