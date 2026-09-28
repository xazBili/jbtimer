# 金避计时器

一款 Windows 桌面悬浮计时器。无边框、透明背景，只显示计时数字本身，安静悬浮在游戏、视频或任意窗口之上。

**官网：** https://jbtimer.netlify.app
**源码：** https://github.com/xazBili/jbtimer

## 特性

- **全局热键**：`W` 开始、`E` 暂停、`R` 清空，无需先点击窗口，全屏游戏中同样生效，键位可在设置里改
- **真·悬浮**：无边框透明窗口，不画背景，只保留计时区域
- **两种形态**：方块 `00h 03min 38s`，长条 `00:03:38`（右对齐，支持自定义背景图）
- **毫秒与缩放**：可追加毫秒显示，整体大小 50%–200% 自由缩放
- **两套外观**：黑色 / 半透明玻璃
- **缩到托盘**：关闭窗口不退出，缩进托盘继续计时，双击图标唤回
- **窗口置顶**：可浮在其他窗口之上

## 操作

| 操作 | 作用 |
| --- | --- |
| `W` | 开始计时 |
| `E` | 暂停计时 |
| `R` | 清空归零（计时中会二次确认） |
| 左键拖动 | 移动窗口，不会误触计时 |
| 右键菜单 | 设置、窗口置顶、隐藏到托盘、退出 |
| 双击托盘图标 | 显示 / 隐藏窗口 |

## 下载

前往 Releases 下载单文件 exe，双击即用，无需安装，也不需要 Python 环境。

## 从源码运行

需要带 **PyQt6** 的 Python（本项目开发时用的 Python 3.13）：

```bash
python main.py
```

## 打包成 exe

```bash
python -m PyInstaller --noconfirm --onefile --windowed --icon pmqdt-08edn-001.ico --name 金避计时器 main.py
```

注意两点：

1. `--icon` 必须传绝对路径，相对路径会被当成相对工作目录解析并报错
2. 旧 exe 若正在运行则无法覆盖，需先从托盘退出程序

打包后 `settings.json` 会生成在 exe 同级目录，用于保存键位、形状、外观等偏好设置。

## 项目结构

| 文件 | 职责 |
| --- | --- |
| `main.py` | 入口，含全局异常兜底（错误写入 error.log 并弹窗） |
| `app.py` | 主窗口：无边框窗口、右键菜单、托盘、布局切换 |
| `time_card.py` | 方块形态的单个计时块绘制 |
| `bar_display.py` | 长条形态绘制，含背景图拉伸铺满 |
| `timer_engine.py` | 计时核心逻辑，基于单调时钟 |
| `keyboard_hook.py` | 全局键盘钩子（Windows 低级钩子） |
| `settings.py` / `settings_dialog.py` | 配置持久化与设置界面 |
| `styles.py` / `config.py` / `font_util.py` | 外观样式、全局参数、字体选择 |

## 官网

静态站点位于仓库外的 `web/` 目录（`../web`，不在本 Git 仓库内），包含 `index.html`、`styles.css`、`app.js`、`netlify.toml`，可直接用 Netlify 部署：

```bash
netlify deploy --prod --dir=web
```

也可以把 `web` 文件夹直接拖到 Netlify 控制台完成部署。站点地址：https://jbtimer.netlify.app
