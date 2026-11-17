# ItemChat — 项目总览

一个 Minecraft 模组：**对着物品按【鼠标中键】，就能在聊天栏向所有玩家展示它**，并附一个可点击的
`[检查]` 按钮，点一下直接跳到 JEI 里该物品的配方界面。对着 FTB 任务按中键则会展示该任务，
并附 `[检查任务]` 按钮回跳任务书。

> 许可：**GPL-3.0**（见各子项目根目录的 `LICENSE`）
> 作者：**Abslt_**

默认使用鼠标中键分享。可在「选项 → 控制 → 按键绑定 → ItemChat → 展示物品或任务」中修改按键，支持鼠标、键盘、组合键和按 Esc 解绑。

**使用 AE 中键合成时，请先把 ItemChat 分享改到其它键或解绑。** 改键后，原来的中键会交还给 AE；默认仍保留普通中键。

成品下载：[Forge 1.20.1 / ItemChat 1.3.1](https://github.com/Absltz/itemchat/releases/tag/forge-1.3.1) · [NeoForge 1.21.1 / ItemChat 1.2.3](https://github.com/Absltz/itemchat/releases/tag/neoforge-1.2.3)

---

## 仓库结构

本目录下是**两条互相独立的产品线**，各自是一个可直接构建的 Gradle 工程：

```
.
├── README.md              ← 本文件（总览）
├── itemchat/              ← ① NeoForge 1.21.1 线，版本 1.2.3
│   ├── LICENSE
│   ├── README.md          ← 该线的详细说明与踩坑记录
│   ├── build.gradle
│   ├── gradle.properties
│   └── src/main/{java,resources}
├── itemchat-forge/        ← ② Forge 1.20.1 线，版本 1.3.1
│   ├── LICENSE
│   ├── README.md
│   ├── build.gradle
│   ├── gradle.properties
│   └── src/main/{java,resources}
└── tests/                 ← 两版客户端输入回归检查
```

两个工程**不共享任何可编译单元**：各自持有自己那份源码、语言文件、README。
这是刻意的设计——两条线要能分别独立更新，改一条不能牵动另一条。

## 两条线速查

| 项 | `itemchat` | `itemchat-forge` |
| --- | --- | --- |
| 加载器 | **NeoForge 21.1.259** | **Forge 47.4.10** |
| Minecraft | **1.21.1** | **1.20.1** |
| Java | **21** | **17** |
| 当前版本 | **1.2.3** | **1.3.1** |
| 构建插件 | ModDevGradle 2.0.148 | ForgeGradle 6 |
| 元数据文件 | `META-INF/neoforge.mods.toml` | `META-INF/mods.toml` |
| 产物名 | `itemchat-<ver>-neoforge.jar` | `itemchat-<ver>-forge.jar` |
| JEI | 19.25.1.332 | 15.49.0.188 |
| FTB Quests | 2101.1.33 | 2001.4.22 |
| 网络层 | `CustomPacketPayload` + `PayloadRegistrar` | `SimpleChannel` |

> **两条线的版本号故意不同，且互不跟随。** 版本号只表示各自线上的演进顺序，
> 不代表功能多少；两个 Gradle 工程可以分别构建和更新。

## 功能

| 操作 | 结果 |
| --- | --- |
| 在背包 / 箱子 / 任意容器界面里，鼠标悬停在物品上按**中键** | 聊天栏广播 `[物品] 玩家 展示了 钻石剑 ×64 [检查]` |
| 在 **JEI 物品列表 / 配方界面 / 书签栏** 里对物品按**中键** | 同上，分享 JEI 里悬停的那个物品 |
| 在 **FTB 任务书**里对着一条任务按**中键** | 广播 `[任务] 玩家 展示了 某任务 [检查任务]` |
| 点击 `[检查]` | 打开 JEI 中该物品的配方（等价于在 JEI 里按 R） |
| 点击 `[检查任务]` | 打开 FTB 任务书并定位到那条任务 |
| 悬停在物品名上 | 显示完整 tooltip |

- JEI 与 FTB Quests 都是**软依赖**：没装时其它功能照常，只有对应按钮会提示未检测到。
- 没装本模组的客户端也能正常进服，并且**能看懂广播内容**（不会看到裸翻译键）。
- 聊天消息模板走翻译键，跟随**每个玩家自己的游戏语言**（内置 `en_us` / `zh_cn`）；任务标题的语言限制见下方已知问题。

## 本次更新

Forge **1.3.1** 与 NeoForge **1.2.3**：

- 新增原生按键设置，默认保留普通中键；改键或解绑后不再抢占 AE 的中键合成。
- 鼠标与键盘绑定均可分享背包、JEI 中的物品和 FTB 任务。
- JEI 搜索框或已聚焦的原版输入框正在输入时，不触发键盘分享；长按分享键只广播一次。
- 网络包结构不变，Forge 协议保持 `"1"`，NeoForge 协议保持 `"2"`。

## 构建

需要自备 JDK（本仓库刻意不写死任何本机路径）：

```bash
# NeoForge 线：需要 JDK 21
cd itemchat
JAVA_HOME=/path/to/jdk-21 ./gradlew build

# Forge 线：需要 JDK 17
cd itemchat-forge
JAVA_HOME=/path/to/jdk-17 ./gradlew build
```

Windows PowerShell 中进入对应工程，设置 `$env:JAVA_HOME='C:\path\to\jdk'` 后执行 `.\gradlew.bat build`。

产物在各自的 `build/libs/` 下。首次构建会下载 NeoForge / Forge / Minecraft / JEI / FTB 依赖。

> 也可以不设 `JAVA_HOME`，改用用户级 `~/.gradle/gradle.properties` 里的
> `org.gradle.java.home=/path/to/jdk`（该文件不会进仓库）。

## 开发运行

```bash
./gradlew runClient     # 带模组的客户端
./gradlew runServer     # 专用服务端
```

NeoForge 线额外支持 `-PwithFtb=false`：不加载 FTB，用于验证「没装 FTB 也不崩」的软依赖降级。

在仓库根目录可运行输入回归检查，需要 Python 3 与 JDK 17 或更高版本：

```bash
python -m unittest discover -s tests -v
```

如果 `javac` 不在 PATH 中，可将环境变量 `ITEMCHAT_TEST_JDK` 指向 JDK 目录。检查会编译实际客户端输入类，在独立的无图形测试环境中验证两版合计 40 个输入场景。

## 已知问题

| 线 | 问题 | 说明 |
| --- | --- | --- |
| **Forge 1.3.1** | 分享**任务链接**会报「找不到这条任务」 | FTB 的 `QuestLink` 有独立 id，当前只判 `instanceof Quest`。NeoForge 线已修；本次按键更新不涉及这项历史问题 |
| **Forge 1.3.1** | 任务名由服务端生成 | 专用服务端上可能触发客户端专有类的 `NoClassDefFoundError`。NeoForge 线已改成客户端渲染后随包传递 |
| NeoForge | 任务名跟随**分享者**的语言 | 任务标题由分享者客户端渲染；聊天模板仍按各玩家语言显示 |
| 两条线 | 模组列表里的**描述**不跟随语言 | 元数据 `description` 是静态字符串，无翻译机制 |
| 两条线 | 附魔书 / 药水点开的是基础物品配方 | 包里只传物品 ID，不传组件 |

## 文档索引

| 文档 | 内容 |
| --- | --- |
| [itemchat/README.md](itemchat/README.md) | NeoForge 线详细说明（含 8 条踩坑解析） |
| [itemchat-forge/README.md](itemchat-forge/README.md) | Forge 线详细说明（含反编译重建背景、mixin refmap 问题） |

## 许可证

GNU General Public License v3.0，完整条款见 [NeoForge LICENSE](itemchat/LICENSE) 与 [Forge LICENSE](itemchat-forge/LICENSE)。
