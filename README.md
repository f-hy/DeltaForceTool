# DeltaForceTool

一个基于 Python 的游戏辅助工具库，采用现代化架构设计，支持扩展更多实用工具。

## 功能特性

### ⏰ 桌面时钟 (DeltaTimeClock)

显示北京时间的悬浮时钟，支持以下特性：

- **实时显示**：`时:分:秒` 格式（100ms 刷新率）
- **置顶显示**：窗口始终在其他窗口之上
- **透明背景**：使用抠像技术实现透明效果
- **可拖动**：按住鼠标左键可拖动窗口位置
- **右键菜单**：右键点击可弹出菜单（包含关闭选项）

**运行方式：**
```bash
uv run main.py
```

**打包可执行文件：**
```bash
# 开发环境
uv run main.py

# 分发使用
dist/DeltaTimeClock.exe
```

## 架构设计

本项目采用现代化 Python 库架构，运用以下设计模式：

- **Singleton（单例模式）**：TimeClock 全局唯一实例
- **Observer（观察者模式）**：时间事件订阅/通知机制
- **Registry（注册表模式）**：ToolRegistry 支持动态注册新工具

### 项目结构

```
DeltaForceTool/
├── src/deltaforcetool/
│   ├── __init__.py
│   ├── core/              # 核心框架
│   │   ├── base.py        # ITool 接口
│   │   └── registry.py    # ToolRegistry
│   └── utils/
│       └── time/          # 时间模块
│           ├── __init__.py
│           ├── singleton.py
│           ├── observer.py
│           ├── models.py
│           └── clock.py
├── tests/
│   └── time/
├── main.py
├── pyproject.toml
└── README.md
```

## 开发指南

### 安装依赖

```bash
uv sync
```
### 运行

```bash
uv run ./main.py
```

### 运行测试

```bash
uv run pytest tests/time/ -v
```

### 打包可执行文件

```bash
uv run pyinstaller --name "DeltaTimeClock" --onefile --windowed --add-data "src/deltaforcetool;src/deltaforcetool" main.py
```

> 注意：生成的 `DeltaTimeClock.spec` 是 PyInstaller 的临时配置文件，可以安全删除。

## 法律免责声明 (Disclaimer)

1. **用途限制**：本项目仅供学术研究、计算机自动化技术交流及个人学习使用。禁止用于任何商业用途、非法途径或网络游戏作弊行为。
2. **免责条款**：用户在使用本项目时，必须自行承担因违反相关游戏服务协议（ToS）而导致的账号被封禁、清卡等一切后果。作者不对任何因使用本项目导致的直接或间接损失负责。
3. **知识产权声明**：本项目为独立开发的自动化辅助工具，不包含、不传播、不破解任何目标游戏的受版权保护的资源（如美术资产、解密密钥、受保护代码）。本项目不修改游戏内存，不破坏游戏客户端完整性。
4. **侵权删除**：若游戏官方认为本项目侵犯了其合法权益，请通过 [邮件](mailto:friend0@qq.com?subject= 侵权) 联系作者，作者将在确认身份后第一时间下架或删除相关代码。

## 开源与商业双重授权 (Dual-Licensing)

本项目采用 **双重授权模式**（Dual-Licensing）：

1. **开源教学用途**：遵循 [AGPL-3.0 协议](./LICENSE)。如果你将本项目的代码用于开源、非盈利的学习和技术交流，你必须保持你的衍生项目同样开源，并保留原作者的署名。
2. **商业用途限制**：本项目**严禁任何形式的闭源商业化搬运、打包销售或黑产变现**。任何商业性质的使用、包装或服务化，必须遵循 [商业授权条款](./LICENSE-COMMERCIAL)，并提前联系作者获得书面商业授权。

3. **拒绝恶意白嫖**：一旦发现有人闭源二改并打包售卖，作者将依据 AGPL-3.0 协议在社区公开曝光并追究其开源违规责任。

## 引用与二次开发规范 (Attribution Rules)

如果你觉得本项目的架构或代码对你有启发，并决定**参考、抄录或基于本项目进行二次开发**，请务必遵守以下道义与法律底线：

*   **必须显式署名**：你必须在你的项目 `README.md` 的顶部或致谢（Credits）区域，以及软件的关于（About）页面中，高亮标注原作者的署名及本项目链接。
*   **示例格式**：
    > **致谢/参考**：本项目的 [某功能/核心架构] 运行逻辑参考/基于开源项目 [f-hy/DeltaForceTool](https://github.com/f-hy/DeltaForceTool) 开发，特此感谢原作者。
*   **严禁抹除版权**：所有从本项目复制、修改的代码文件，其头部的作者版权声明（Copyright）**绝对不允许删除或篡改**。

*对于不打招呼直接硬搬、甚至抹去原作者名字假装自己原创的行为，一经发现，不仅会在开源社区挂墙公开，还将依法追究其违反 AGPL-3.0 协议的侵权责任。*

## 许可证

- 开源版本：AGPL-3.0

---

**作者**: f-hy (friend0@qq.com)  
**GitHub**: https://github.com/f-hy
