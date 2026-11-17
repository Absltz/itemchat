# ItemChat

在 Minecraft 聊天栏分享物品和任务。将鼠标移到目标上，按下分享键，就能发送带悬停预览和可点击按钮的消息。

作者：Abslt_

## 下载

| 加载器 | Minecraft | Java | 当前版本 | 下载 |
| --- | --- | --- | --- | --- |
| Forge | 1.20.1 | 17 | 1.3.1 | [下载](https://github.com/Absltz/itemchat/releases/tag/forge-1.3.1) |
| NeoForge | 1.21.1 | 21 | 1.2.3 | [下载](https://github.com/Absltz/itemchat/releases/tag/neoforge-1.2.3) |

## 功能

- 分享背包、箱子等容器中的物品。
- 分享 JEI 物品列表、配方界面和书签中的物品。
- 分享 FTB 任务，点击消息中的 `[检查任务]` 可打开对应任务。
- 悬停物品名称查看提示，点击 `[检查]` 查看 JEI 配方。
- 支持自定义分享按键，内置简体中文和英文。

## 安装

下载对应游戏版本和加载器的 jar，放入客户端及服务端的 `mods` 目录。单人游戏只需放入客户端。

JEI 和 FTB Quests 为可选依赖。使用任务功能时，请安装 FTB Quests 及其依赖，服务端也需要安装。

更新时替换旧版 ItemChat jar，每个实例只保留一个对应版本。

## 使用

打开背包、容器或任务界面，将鼠标移到物品或任务上，按下分享键。默认按键为鼠标中键。

其他玩家可以悬停或点击聊天消息中的物品、任务和检查按钮。

## 按键设置

在「选项 → 控制 → 按键绑定 → ItemChat → 展示物品或任务」中修改分享按键。

支持鼠标键和键盘键；按住 Shift、Ctrl 或 Alt 再设置按键可绑定组合键，按 Esc 可解绑。设置会自动保存。

## 从源码构建

两个版本分别位于 [Forge 工程](itemchat-forge/README.md) 和 [NeoForge 工程](itemchat/README.md)，可独立构建。

设置 `JAVA_HOME` 指向对应的 JDK 后，进入工程目录执行：

```powershell
# Windows PowerShell
.\gradlew.bat build
```

```bash
# macOS / Linux
./gradlew build
```

产物位于各工程的 `build/libs/` 目录。

## 许可证

GPL-3.0，完整条款见 [Forge LICENSE](itemchat-forge/LICENSE) 和 [NeoForge LICENSE](itemchat/LICENSE)。
