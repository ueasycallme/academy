---
title: ① 资产
---

# ① 资产

第 6 部分的主线机器人是 Galbot One Golf：一台轮式底盘、可升降躯干、双 7 自由度臂的移动操作机器人。它的描述仓库提供 xacro、URDF、MJCF 与 USD 几种格式。这一节把它导入 Isaac Sim、调好碰撞与驱动，最后做成 Isaac Lab 可以直接训练的资产；先从 [6.1.1 认识 Galbot One Golf 描述仓库](6.1.1-galbot-repo.md) 读起。

```{figure} ../../_static/img/6.1.1-galbot-one-golf-urdf.png
:alt: Galbot One Golf 的 URDF 渲染图：轮式底盘、升降躯干、双臂与头部
:align: center
:width: 380px
:figclass: figure-card

Galbot One Golf · URDF 渲染\
来源：[galbot_one_golf_description](https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description/blob/2d496b053f0d4e9e2688f59fac66022f447226be/docs/.images/galbot_one_golf_urdf.png)（[Apache-2.0](../../_static/licenses/galbot_one_golf_description-LICENSE.txt)）
```

```{toctree}


6.1.1-galbot-repo
6.1.2-import-urdf
6.1.3-vendor-vs-imported-usd
6.1.4-collision-mass-inertia
6.1.5-joint-drive-tuning
6.1.6-articulation-cfg
6.1.7-asset-versioning
```
