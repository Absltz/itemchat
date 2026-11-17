# ItemChat NeoForge 1.21.1

将物品和任务分享到聊天栏，附带悬停预览与可点击的检查按钮。

当前版本：1.2.3。作者：Abslt_。

[下载成品](https://github.com/Absltz/itemchat/releases/tag/neoforge-1.2.3) · [项目总览](../README.md) · [Forge 1.20.1 版](../itemchat-forge/README.md)

## 环境要求

| 项目 | 版本 |
| --- | --- |
| Minecraft | 1.21.1 |
| NeoForge | 21.1.259（编译版本） |
| Java | 21 |
| JEI | 19.x（可选） |
| FTB Quests | 2101.x（可选） |

## 功能

- 分享背包、箱子及其它容器中的物品。
- 分享 JEI 物品列表、配方界面和书签中的物品。
- 分享 FTB 任务，点击 `[检查任务]` 打开对应任务。
- 悬停消息中的物品名称查看提示，点击 `[检查]` 查看配方。
- 内置简体中文和英文，支持自定义分享按键。

## 安装

将 `itemchat-1.2.3-neoforge.jar` 放入客户端和服务端的 `mods` 目录。单人游戏只需放入客户端。更新时替换旧 jar，保留一个 ItemChat 版本即可。

JEI 和 FTB Quests 为可选依赖。需要任务功能时，请在客户端和服务端安装 FTB Quests 及其依赖。

## 使用与按键

打开背包、容器或任务界面，鼠标悬停在目标上，按下分享键。默认使用鼠标中键。

在「选项 → 控制 → 按键绑定 → ItemChat → 展示物品或任务」中改键。支持鼠标键、键盘键及 Shift、Ctrl、Alt 组合键；按 Esc 可解绑。设置会自动保存。

## 构建

使用 JDK 21，设置 `JAVA_HOME` 后在本目录执行：

```powershell
# Windows PowerShell
.\gradlew.bat build
```

```bash
# macOS / Linux
./gradlew build
```

产物：`build/libs/itemchat-1.2.3-neoforge.jar`。

## 许可证

GPL-3.0，完整条款见 [LICENSE](LICENSE)。
