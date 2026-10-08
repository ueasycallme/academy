# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 26.08（不需要 Isaac Sim）
# 验证日期：2026-10-08
"""强度顺序 LIVRPS 的演示（2.3）。

同一个属性 /Robot.mass 在六处都有定义：本地（Local）、继承（Inherits）、变体（Variant）、
引用（Reference）、载荷（Payload）、特化（Specializes）。全部在内存里建 Layer，打印合成后谁赢；
然后依次删掉最强的那个意见，看下一个是谁。

    python livrps_demo.py
"""

from pxr import Sdf, Usd


def layer(text: str) -> Sdf.Layer:
    lyr = Sdf.Layer.CreateAnonymous(".usda")
    lyr.ImportFromString(text)
    return lyr


REF = layer('#usda 1.0\n(defaultPrim = "R")\ndef "R"\n{\n    double mass = 4.0\n}\n')  # 引用来的资产
PAY = layer('#usda 1.0\n(defaultPrim = "P")\ndef "P"\n{\n    double mass = 5.0\n}\n')  # 载荷
ROOT = f"""#usda 1.0
def "_class"
{{
    double mass = 2.0
}}
def "_special"
{{
    double mass = 6.0
}}
def "Robot" (
    inherits = </_class>
    specializes = </_special>
    references = @{REF.identifier}@
    payload = @{PAY.identifier}@
    variantSets = "v"
    variants = {{ string v = "a" }}
) {{
    variantSet "v" = {{
        "a" {{
            double mass = 3.0
        }}
    }}
    double mass = 1.0
}}
"""

NAMES = {1.0: "L 本地", 2.0: "I 继承", 3.0: "V 变体", 4.0: "R 引用", 5.0: "P 载荷", 6.0: "S 特化"}


def main() -> None:
    root = layer(ROOT)
    stage = Usd.Stage.Open(root)
    print(f"合成结果：mass = {stage.GetPrimAtPath('/Robot').GetAttribute('mass').Get()}（{NAMES[stage.GetPrimAtPath('/Robot').GetAttribute('mass').Get()]}）")
    steps = [
        ("删掉本地值", lambda: root.GetPrimAtPath("/Robot").RemoveProperty(root.GetPropertyAtPath("/Robot.mass"))),
        ("删掉 /_class 上的值", lambda: root.GetPrimAtPath("/_class").RemoveProperty(root.GetPropertyAtPath("/_class.mass"))),
        ("删掉变体里的值", lambda: root.GetPrimAtPath("/Robot{v=a}").RemoveProperty(root.GetPropertyAtPath("/Robot{v=a}.mass"))),
        ("删掉引用", lambda: root.GetPrimAtPath("/Robot").referenceList.ClearEdits()),
        ("删掉载荷", lambda: root.GetPrimAtPath("/Robot").payloadList.ClearEdits()),
    ]
    for desc, fn in steps:
        fn()
        v = stage.GetPrimAtPath("/Robot").GetAttribute("mass").Get()  # 编辑 Layer 后，Stage 自动重新合成
        print(f"{desc} → mass = {v}（{NAMES[v]}）")


if __name__ == "__main__":
    main()
