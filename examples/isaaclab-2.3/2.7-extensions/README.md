# 2.7 扩展机制：最小扩展

对应页面：`docs/2-usd-kit/2.7-extensions.md`。

| 文件 | 说明 |
|---|---|
| `exts/academy.hello/` | 最小扩展：`config/extension.toml` + Python 包 `academy.hello`，启用 / 停用时各打印一行，并提供函数 `greet()` |
| `exts/academy.hello_noimport/` | 反例（页面坑三）：扩展类写在 `extension.py`，但 `__init__.py` 没有导入它 |
| `enable_hello.py` | headless 启动 Isaac Sim，把 `exts/` 加进扩展搜索路径，启用、调用、停用，并演示坑一、坑三、坑四 |

## 运行（在 Isaac Sim 或 Isaac Lab 环境中，本仓库根目录）

```bash
python examples/isaaclab-2.3/2.7-extensions/enable_hello.py
```

也可以不用脚本，直接用命令行启用（目录与扩展名照此替换）：`--ext-folder examples/isaaclab-2.3/2.7-extensions/exts --enable academy.hello`。

## 预期输出（节选）

```text
加入搜索路径前，启用 academy.hello：False
add_path 之后立即启用：False
[academy.hello] on_startup：academy.hello-0.1.0
update() 一帧之后再启用：True
启用后：is_extension_enabled = True，ext_id = academy.hello-0.1.0，目录 academy.hello
调用扩展提供的函数：hello from academy.hello
启用拼错的名字 academy.helo：False
academy.hello_noimport：is_extension_enabled = True
[academy.hello] on_shutdown
停用后：is_extension_enabled = False
```

日志里的 `Can't find extension with name` 错误对应前两次和拼错名字那次启用，属预期。第二次（add_path 之后立即启用）失败，是因为第一次对这个名字启用失败过（页面坑一）；没有先失败过时，add_path 之后立即启用就会成功。`academy.hello_noimport` 启用成功，但没有打印 `on_startup`。

验证版本：Isaac Sim 5.1.0（pip，Kit 107.3.3）+ Isaac Lab 2.3.2；验证日期 2026-10-08。
