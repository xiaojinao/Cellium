[English](README.en.md)

<div align="center">

![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue?logo=python&style=flat-square)
![License](https://img.shields.io/badge/license-Apache%202.0-blue?logo=apache&style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?logo=windows&style=flat-square)
![MiniBlink](https://img.shields.io/badge/MiniBlink-v132-yellow?logo=webkit&style=flat-square)

![GitHub Stars](https://img.shields.io/github/stars/Cellium-Project/Cellium?logo=github&style=flat-square)
![GitHub Forks](https://img.shields.io/github/forks/Cellium-Project/Cellium?logo=github&style=flat-square)
![GitHub Issues](https://img.shields.io/github/issues/Cellium-Project/Cellium?logo=github&style=flat-square)
![GitHub Last Commit](https://img.shields.io/github/last-commit/Cellium-Project/Cellium?logo=github&style=flat-square)

</div>

**文档网站：** [https://cellium-project.github.io/Cellium/](https://cellium-project.github.io/Cellium/) （推荐 | 更好的阅读体验）

**文档导航：**
- [Component Tutorial](/docs/component-tutorial.en.md) | [组件开发教程](/docs/component-tutorial.md)
- [Multiprocessing Tutorial](/docs/multiprocessing-tutorial.en.md) | [多进程教程](/docs/multiprocessing-tutorial.md)
- [Event Mode Tutorial](/docs/event-mode-tutorial.en.md) | [事件模式教程](/docs/event-mode-tutorial.md)
- [Logging Tutorial](/docs/logging-tutorial.en.md) | [日志使用](/docs/logging-tutorial.md)

<p align="center">
  <img src="logo.png" alt="Cellium Logo" width="400">
</p>

# Cellium

**Python + HTML/JS 的桌面应用框架。**

基于"核心驱动-模块解耦"理念的 Python 桌面应用框架。

通过一个精密的微内核（Core）作为调度中枢，实现了前端交互与后端逻辑的彻底分离。开发者只需将功能封装为独立的"细胞单元"，其余的跨模块通信、并发调度与资源管理均由 Cellium 核心透明完成，让复杂的系统构建变得像拼图一样简单。


| 特点 | 说明 |
|------|------|
| **核心驱动** | 微内核统一调度，开发者只需关注业务逻辑 |
| **模块解耦** | 前后端独立开发，通过协议通信 |
| **简单** | 只需写 Python 函数定义功能，前端调用即可 |
| **灵活** | 完整 Web 前端生态，任意 UI 框架 |
| **轻量** | 基于 MiniBlink，体积小、启动快 |

**对比传统方案：**

| 方案 | 学习成本 | 开发效率 | UI 灵活性 |
|------|---------|---------|----------|
| PyQt/Tkinter | 高 | 中 | 低 |
| Electron | 中 | 高 | 高 |
| **Cellium** | **低** | **高** | **高** |

**快速示例：**
```python
# app/components/greeter.py
from app.core.interface.base_cell import BaseCell


class Greeter(BaseCell):
    """问候组件：接收文字，添加后缀后返回"""

    @property
    def cell_name(self) -> str:
        """组件唯一标识，用于前端调用"""
        return "greeter"

    def get_commands(self) -> dict:
        """返回可用命令列表"""
        return {
            "greet": "添加问候后缀，例如: greeter:greet:你好"
        }

    def _cmd_greet(self, text: str = "") -> str:
        """添加 Hallo Cellium 后缀"""
        if not text:
            return "Hallo Cellium"
        return f"{text} Hallo Cellium"
```

```html
<!-- html/index.html -->
<button onclick="window.mbQuery(0, 'greeter:greet:你好', function(){})">问候</button>
```

### 直接调用方法

Cellium 组件支持**直接调用**模式，即前端通过 `window.mbQuery()` 直接调用后端组件方法，无需配置路由。

#### 1. 后端组件定义

组件只需继承 `BaseCell` 基类，实现三个核心方法：

| 方法 | 说明 |
|------|------|
| `cell_name` | 组件唯一标识，用于前端调用 |
| `get_commands()` | 返回可用命令字典 |
| `_cmd_<命令名>` | 具体命令实现，BaseCell 自动映射 |

**BaseCell 自动处理命令映射**，无需编写 `execute` 方法。

#### 2. 前端调用格式

```javascript
// 格式：window.mbQuery(id, 'cell_name:command[:args]', callback)
// id: 消息ID，通常传 0
// cell_name: 组件的 cell_name 属性值
// command: get_commands() 中定义的命令名
// args: 可选参数，支持字符串或 JSON
// callback: 回调函数，接收返回结果
```

#### 3. 调用示例

**简单参数：**
```javascript
window.mbQuery(0, 'greeter:greet:你好', function(response) {
    console.log(response);  // "你好 Hallo Cellium"
});
```

**复杂数据：**
```javascript
const data = JSON.stringify({name: "Alice", age: 25});
window.mbQuery(0, `user:create:${data}`, function(response) {
    console.log(response);
});
```

**无参数：**
```javascript
window.mbQuery(0, 'greeter:greet:', function(response) {
    console.log(response);  // "Hallo Cellium"
});
```

#### 4. 命令格式规范

- **格式**：`cell_name:command[:args]`
- **cell_name**：组件的 `cell_name` 属性值（小写字母）
- **command**：组件 `get_commands()` 中定义的命令名
- **args**：可选参数，支持简单字符串或 JSON 格式

选择 Cellium：**用你熟悉的 Python 和 Web 技术，快速构建桌面应用。**

## MiniBlink 依赖

Cellium 依赖 [MiniBlink](https://github.com/weolar/miniblink49) 作为 WebView 引擎。

**下载地址：**

- **官方 GitHub Releases**: https://github.com/weolar/miniblink49/releases
- **每日构建版本**: https://gitcode.com/Resource-Bundle-Collection/68b02

**放置方法：**

1. 从上述地址下载 MiniBlink SDK（或直接下载 `mb132_x64.dll`）
2. 将 `mb132_x64.dll` 复制到项目根目录的 `dll/` 文件夹中：

```
python-miniblink/
├── dll/
│   └── mb132_x64.dll    # <-- 将下载的 DLL 放在这里
└── main.py
```

> **感谢**：感谢 [MiniBlink](https://github.com/weolar/miniblink49) 团队开源如此轻量级、高性能的浏览器引擎，让开发者能够轻松构建桌面应用。

## 目录

- [文档](docs/component-tutorial.md)
- [MiniBlink 依赖](#miniblink-依赖)
- [核心理念](#核心理念)
- [架构设计](#架构设计)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
  - [微内核 Core](#微内核-core)
  - [事件总线 EventBus](#事件总线-eventbus)
  - [组件接口 ICell](#组件接口-icell)
  - [基础组件 BaseCell](#基础组件-basecell-推荐)
  - [消息处理器 MessageHandler](#消息处理器-messagehandler)
  - [桥接层 MiniBlinkBridge](#桥接层-miniblinkbridge)
  - [前端日志](#前端日志)
  - [依赖注入 DI](#依赖注入-di)
- [API 参考](#api-参考)
- [组件开发指南](#组件开发指南)
  - [创建新组件](#创建新组件)
  - [ICell vs BaseCell](#icell-vs-basecell)
  - [BaseCell 功能](#basecell-功能)
  - [组件接口规范](#组件接口规范)
  - [命令调用格式](#命令调用格式)
- [配置指南](#配置指南)
- [快速开始](#快速开始)

## 核心理念

Cellium 的设计遵循"核心驱动-模块解耦"的核心哲学，将复杂系统简化为可组合的细胞单元。

### 核心驱动

微内核作为系统的唯一核心，负责：

- **命令路由** - 解析并分发前端命令到对应组件
- **事件调度** - 管理组件间的事件通信
- **生命周期** - 协调组件的加载、初始化和销毁
- **资源管理** - 统一管理多进程、线程等系统资源

### 模块解耦

每个组件单元（Cell）具有以下特性：

- **独立封装** - 组件包含完整的业务逻辑和状态
- **接口契约** - 所有组件实现统一的 ICell 接口
- **透明通信** - 通过事件总线进行跨组件通信
- **即插即用** - 配置即加载，无须修改核心代码

### 前端后端分离

```mermaid
flowchart TB
    subgraph Frontend["前端层"]
        H["HTML/CSS"]
        J["JavaScript"]
        MB["window.mbQuery() 调用"]
    end

    Core["Cellium 微内核"]

    subgraph Backend["后端层"]
        Calc["Calculator"]
        Grt["Greeter"]
        Json["JsonTest"]
    end

    Frontend -->|"window.mbQuery()"| Core
    Core --> Backend
```

## 架构设计

```mermaid
flowchart TB
    subgraph Presentation["前端交互层"]
        MW["MainWindow"]
        MW -->|"窗口管理"| MW
        MW -->|"事件订阅"| MW
        MW -->|"UI 渲染"| MW
    end

    subgraph Kernel["微内核层"]
        EB["EventBus"]
        BR["Bridge"]
        HD["Handler"]
        DI["DIContainer"]
    end

    subgraph Component["组件层"]
        Calc["Calculator"]
        Grt["Greeter"]
        Json["JsonTest"]
    end

    Presentation -->|"前端交互"| Kernel
    Kernel -->|"事件通信"| Component
    HD <-->|"消息处理"| DI
    BR <-->|"桥接通信"| EB
```

### 设计原则

1. **微内核架构** - 核心只负责调度和协调，不包含业务逻辑
2. **组件单元** - 所有功能以独立组件形式存在
3. **统一接口** - 所有组件实现 ICell 接口，遵循相同契约
4. **事件驱动** - 组件间通过事件总线通信，互不直接依赖
5. **依赖注入** - 组件无需手动导入核心服务，自动注入解耦

### 数据流向

```mermaid
flowchart TD
    A["用户操作"] --> B["JavaScript HTML/CSS"]
    B -->|"window.mbQuery()"| C["MiniBlinkBridge 接收回调"]
    C --> D["MessageHandler 命令解析与路由"]

    D --> E{处理方式}
    E -->|"事件模式"| F["EventBus 事件"]
    E -->|"直接调用"| G["直接方法调用"]

    F --> H["组件处理"]
    G --> I["返回结果"]
    H --> J["返回结果"]

    J -->|"->"| K["JavaScript 更新 UI"]
    I -->|"->"| K
```

## 目录结构

```
python-miniblink/
├── app/
│   ├── core/                    # 微内核模块
│   │   ├── __init__.py          # 模块导出
│   │   ├── bus/                 # 事件总线
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py     # 事件总线实现
│   │   │   ├── events.py        # 事件类型定义
│   │   │   └── event_models.py  # 事件模型定义
│   │   ├── window/              # 窗口管理
│   │   │   ├── __init__.py
│   │   │   └── main_window.py   # 主窗口
│   │   ├── bridge/              # 桥接层
│   │   │   ├── __init__.py
│   │   │   └── miniblink_bridge.py  # MiniBlink 通信桥接
│   │   ├── handler/             # 消息处理
│   │   │   ├── __init__.py
│   │   │   ├── message_handler.py   # 消息处理器（命令路由）
│   │   │   └── title_bar_handler.py # 标题栏处理器
│   │   ├── util/                # 工具模块
│   │   │   ├── __init__.py
│   │   │   ├── logger.py        # 日志管理
│   │   │   ├── mp_manager.py    # 多进程管理器
│   │   │   └── components_loader.py  # 组件加载器
│   │   ├── di/                  # 依赖注入
│   │   │   ├── __init__.py
│   │   │   └── container.py     # DI 容器
│   │   ├── interface/           # 接口定义
│   │   │   ├── __init__.py
│   │   │   ├── icell.py         # ICell 组件接口
│   │   │   └── base_cell.py     # BaseCell 基础组件（推荐）
│   │   └── __init__.py          # 模块导出
│   ├── components/              # 组件单元
│   │   ├── __init__.py
│   │   ├── calculator.py        # 计算器组件
│   │   └── greeter.py           # 问候组件
│   └── __init__.py              # 模块导出
├── docs/                        # 文档教程
│   ├── index.md                 # 文档首页
│   ├── index.en.md              # 文档首页（英文）
│   ├── component-tutorial.md    # 组件开发教程
│   ├── component-tutorial.en.md # 组件开发教程（英文）
│   ├── event-mode-tutorial.md   # 事件模式教程
│   ├── event-mode-tutorial.en.md # 事件模式教程（英文）
│   ├── multiprocessing-tutorial.md   # 多进程教程
│   └── multiprocessing-tutorial.en.md # 多进程教程（英文）
├── html/                        # HTML 资源
│   └── index.html               # 主页面
├── font/                        # 字体文件
├── dll/                         # DLL 文件
│   └── mb132_x64.dll            # MiniBlink 引擎
├── config/                      # 配置文件
│   └── settings.yaml            # 组件配置
├── dist/                        # 构建输出目录
├── main.py                      # 入口文件
├── build.bat                    # 构建脚本
├── requirements.txt             # 依赖配置
└── README.md                    # 文档
```

## 核心模块

### 微内核 Core

微内核是 Cellium 的核心调度器，负责协调各组件工作。

```mermaid
flowchart TB
    subgraph Kernel["Cellium 微内核"]
        EB["EventBus"]
        MH["MessageHandler"]
        DI["DIContainer"]
        MP["MultiprocessManager"]
        WM["WindowManager"]
        Components["组件单元"]
    end

    MH -.->|"调度协调"| EB
    EB -.->|"事件通信"| MH

    DI -->|"依赖注入"| MH
    MP -->|"进程管理"| MH
    WM -->|"窗口管理"| MH

    MH & DI & MP & WM -->|"组件协调"| Components
```

### 事件总线 EventBus

事件总线实现组件间的解耦通信，采用发布-订阅模式。

```python
from app.core import event_bus
from app.core.events import EventType

# 订阅事件
event_bus.subscribe(EventType.CALC_RESULT, on_calc_result)

# 发布事件
event_bus.publish(EventType.CALC_RESULT, result="2")
```

#### 装饰器方式订阅事件（推荐）

单元组件开发推荐使用装饰器方式，无需修改核心代码即可注册事件处理器。

```python
from app.core.bus import event, event_once, event_pattern, event_wildcard, register_component_handlers

class MyComponent:
    @event("user.login")
    def on_user_login(self, event_name, **kwargs):
        """处理用户登录事件"""
        print(f"用户登录: {kwargs.get('username')}")
    
    @event_once("order.completed")
    def on_order_once(self, event_name, **kwargs):
        """一次性事件，只触发一次"""
        print("订单完成")
    
    @event_pattern("user.*")
    def on_user_pattern(self, event_name, **kwargs):
        """模式匹配，匹配 user.login, user.logout 等"""
        print(f"用户事件: {event_name}")
    
    @event_wildcard()
    def on_all_events(self, event_name, **kwargs):
        """通配符匹配，匹配所有事件"""
        print(f"收到事件: {event_name}")

# 自动注册组件内的所有事件处理器
component = MyComponent()
register_component_handlers(component)
```

#### 事件发布装饰器

使用 `@emitter` 装饰器让方法自动发布事件。

```python
from app.core.bus import emitter

class OrderService:
    @emitter("order.created")
    def create_order(self, order_id):
        """创建订单后自动发布事件"""
        return f"订单 {order_id} 已创建"
```

#### 事件优先级

支持按优先级控制处理器执行顺序，优先级高的处理器先执行。

```python
from app.core.bus import event, EventPriority

class PriorityComponent:
    @event("data.ready", priority=EventPriority.HIGHEST)
    def handler_highest(self, event_name, **kwargs):
        """最高优先级，最先执行"""
        print("HIGHEST")
    
    @event("data.ready", priority=EventPriority.HIGH)
    def handler_high(self, event_name, **kwargs):
        """高优先级"""
        print("HIGH")
    
    @event("data.ready", priority=EventPriority.NORMAL)
    def handler_normal(self, event_name, **kwargs):
        """普通优先级"""
        print("NORMAL")
    
    @event("data.ready", priority=EventPriority.LOW)
    def handler_low(self, event_name, **kwargs):
        """低优先级"""
        print("LOW")
```

#### 命名空间

使用命名空间避免事件名冲突，适合多模块协作。

```python
from app.core.bus import set_namespace, event

# 设置命名空间前缀
set_namespace("myapp")

# 事件名自动添加前缀: myapp.user.login
class UserModule:
    @event("user.login")
    def on_login(self, event_name, **kwargs):
        print(f"收到: {event_name}")  # 实际收到: myapp.user.login
```

#### 动态订阅

运行时动态订阅事件，适合不确定事件类型的场景。

```python
from app.core.bus import subscribe_dynamic, subscribe_pattern_dynamic, subscribe_once_dynamic

def on_dynamic_event(event_name, **kwargs):
    print(f"动态订阅: {event_name}")

# 动态订阅
subscribe_dynamic("custom.event", on_dynamic_event)

# 动态模式订阅
subscribe_pattern_dynamic("data.*", on_dynamic_event)

# 一次性动态订阅
subscribe_once_dynamic("once.event", on_dynamic_event)
```

### 组件接口 ICell

所有组件必须实现的统一接口规范。

```python
from app.core.interface.icell import ICell

class MyCell(ICell):
    @property
    def cell_name(self) -> str:
        """组件名称，用于前端调用标识"""
        return "mycell"
    
    def execute(self, command: str, *args, **kwargs) -> any:
        """执行命令"""
        if command == "greet":
            return f"Hello, {args[0] if args else 'World'}!"
        return f"Unknown command: {command}"
    
    def get_commands(self) -> dict:
        """获取可用命令列表"""
        return {
            "greet": "打招呼，例如: mycell:greet:Alice"
        }
```

#### 基础组件 BaseCell（推荐）

`BaseCell` 是基于 `ICell` 的封装，提供自动命令映射和事件注册功能。

```python
from app.core.interface.base_cell import BaseCell


class MyCell(BaseCell):
    """我的组件"""

    def _cmd_greet(self, name: str = "") -> str:
        """打招呼"""
        return f"Hello, {name}!"
```

**自动功能：**
- 命令映射：`greet` → `_cmd_greet()`
- 命令列表：自动扫描 docstring
- 事件注册：自动调用 `register_component_handlers()`
- 默认 cell_name：使用类名小写

### 消息处理器 MessageHandler

消息处理器是前端与后端组件的桥梁，负责解析和路由命令。

```python
class MessageHandler:
    def handle_message(self, message: str) -> str:
        """处理前端消息
        
        支持两种格式：
        1. ICell 命令: 'cell_name:command:args'
        2. 事件消息: JSON 格式的事件数据
        """
        if ':' in message:
            # ICell 命令格式
            return self._handle_cell_command(message)
        else:
            # 事件消息格式
            return self._handle_event_message(message)
```

#### 自动 JSON 解析

MessageHandler 自动识别 Args 是否为 JSON 格式：

- Args 以 `{` 开头 → 解析为 `dict`
- Args 以 `[` 开头 → 解析为 `list`
- 其他情况 → 作为原始 `str` 传递

```javascript
// 简单参数
window.mbQuery(0, 'greeter:greet:你好', callback)

// 复杂数据（自动解析为 dict）
let userData = JSON.stringify({name: "Alice", age: 25});
window.mbQuery(0, `user:create:${userData}`, callback)
```

```python
# 组件直接接收 dict，无需 json.loads
def _cmd_create(self, user_data: dict):
    name = user_data.get('name')  # user_data 已是 dict
    return f"用户 {name} 创建成功"
```

#### 异步执行支持

耗时操作可使用异步执行避免阻塞 UI：

```python
# 前端调用时指定 async_exec=True
window.mbQuery(0, 'file:read:C:/large.txt:async', callback)

# 后端自动提交到线程池，立即返回 "Task submitted to thread pool"
```

### 桥接层 MiniBlinkBridge

桥接层封装 Python 与 MiniBlink 浏览器引擎之间的通信，组件可通过 bridge 与前端页面交互。详见 [API 参考](#api-参考)。

### 依赖注入 DI

依赖注入容器提供自动化的服务注入。

```python
from app.core.di.container import injected, AutoInjectMeta

class Calculator(metaclass=AutoInjectMeta):
    mp_manager = injected(MultiprocessManager)
    event_bus = injected(EventBus)
    
    def calculate(self, expression: str) -> str:
        return self.mp_manager.submit(_calculate_impl, expression)
```

## 组件开发指南

### 创建新组件

Cellium 推荐使用 `BaseCell` 作为组件基类，它提供了自动命令映射、依赖注入和事件支持。

在 `app/components/` 目录下创建新的 Python 文件：

```python
# app/components/filemanager.py
from app.core.interface.base_cell import BaseCell


class FileManager(BaseCell):
    """文件管理组件"""

    def _cmd_read(self, path: str = "") -> str:
        """读取文件内容"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _cmd_write(self, path: str = "", content: str = "") -> str:
        """写入文件内容"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "Write successful"
```

**BaseCell 自动处理：**
- `cell_name`：默认使用类名小写（如 `FileManager` → `filemanager`）
- `execute`：自动映射命令到 `_cmd_` 方法
- `get_commands`：自动扫描 `_cmd_` 方法的 docstring

#### 高级用法

如果需要自定义，可以重写方法：

```python
class FileManager(BaseCell):
    @property
    def cell_name(self) -> str:
        return "filemanager"  # 自定义名称

    def get_commands(self) -> dict:
        return {"read": "读取文件"}  # 自定义命令列表
```

### ICell vs BaseCell

| 特性 | ICell | BaseCell |
|------|-------|----------|
| 灵活性 | 高（完全自定义） | 中（约定优先） |
| 代码量 | 较多（需写 execute） | 较少（自动映射） |
| 学习曲线 | 需要理解分发逻辑 | 简单（遵循约定） |
| 事件注册 | 需手动调用 | 自动 |
| 适合场景 | 特殊需求 | 大多数组件 |

**推荐：** 新手使用 `BaseCell`，熟手根据需求选择。

### BaseCell 功能

#### 自动命令映射

组件方法以 `_cmd_` 前缀开头，自动被映射为命令：

```python
class Greeter(BaseCell):
    def _cmd_greet(self, name: str = "") -> str:
        """打招呼"""
        return f"Hello, {name}!"

# 前端调用：greeter:greet:World
```

#### 自动命令列表

`get_commands()` 自动扫描 `_cmd_` 方法的 docstring：

```python
class Greeter(BaseCell):
    def _cmd_greet(self, name: str = "") -> str:
        """打招呼，例如: greeter:greet:Alice"""
        return f"Hello, {name}!"

# get_commands() 返回：
# {"greet": "打招呼，例如: greeter:greet:Alice"}
```

#### 依赖注入

使用 `injected()` 声明依赖：

```python
from app.core.di.container import injected

class MyCell(BaseCell):
    event_bus = injected(EventBus)  # 自动注入

    def _cmd_do_something(self):
        self.event_bus.publish("event.name")  # 使用注入的服务
```

#### 事件处理

使用 `@event` 装饰器声明事件处理器：

```python
from app.core.bus import event

class MyCell(BaseCell):
    @event("user.login")
    def on_user_login(self, event_name, **kwargs):
        """处理用户登录事件"""
        print(f"用户登录: {kwargs.get('username')}")
```

### 组件接口规范

所有组件必须实现以下方法（或继承 BaseCell）：

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `cell_name` | `str` | 组件唯一标识，小写字母 |
| `execute(command, *args, **kwargs)` | `Any` | 执行命令，返回可序列化结果 |
| `get_commands()` | `Dict[str, str]` | 返回 {命令名: 命令描述} |

## API 参考

本节列出 Cellium 框架的所有公共 API。

### 标题栏处理器 TitleBarHandler

标题栏处理器封装窗口控制操作，提供统一的 API 供前端调用。

#### 前端调用格式

所有命令使用 `titlebar:<command>[:参数]` 格式调用：

| 前端命令 | 说明 | 示例 |
|---------|------|------|
| `titlebar:minimize` | 最小化窗口 | `titlebar:minimize` |
| `titlebar:toggle` | 切换最大化/还原 | `titlebar:toggle` |
| `titlebar:restore` | 还原窗口 | `titlebar:restore` |
| `titlebar:close` | 关闭窗口 | `titlebar:close` |
| `titlebar:show` | 显示窗口 | `titlebar:show` |
| `titlebar:hide` | 隐藏窗口 | `titlebar:hide` |
| `titlebar:setTitle:<标题>` | 设置窗口标题 | `titlebar:setTitle:我的应用` |
| `titlebar:getTitle` | 获取窗口标题 | `titlebar:getTitle` |
| `titlebar:startDrag` | 开始拖动窗口 | `titlebar:startDrag` |
| `titlebar:flash[:true]` | 闪烁任务栏按钮 | `titlebar:flash` 或 `titlebar:flash:true` |
| `titlebar:setAlwaysOnTop:<true\|false>` | 设置置顶状态 | `titlebar:setAlwaysOnTop:true` |
| `titlebar:getState` | 获取窗口状态 | `titlebar:getState` |
| `titlebar:resize:<宽>:<高>` | 调整窗口大小 | `titlebar:resize:1024:768` |
| `titlebar:move:<x>:<y>` | 移动窗口位置 | `titlebar:move:100:100` |
| `titlebar:center` | 窗口居中显示 | `titlebar:center` |

#### 前端调用示例

```javascript
// 最小化窗口
window.mbQuery(0, 'titlebar:minimize', function() {});

// 最大化/还原窗口
window.mbQuery(0, 'titlebar:toggle', function() {});

// 关闭窗口
window.mbQuery(0, 'titlebar:close', function() {});

// 设置窗口标题
window.mbQuery(0, 'titlebar:setTitle:我的应用', function(response) {
    console.log(response);
});

// 获取窗口标题
window.mbQuery(0, 'titlebar:getTitle', function(response) {
    console.log(response);
});

// 开始拖动（在前端 mousedown 时调用）
window.mbQuery(0, 'titlebar:startDrag', function() {});

// 闪烁窗口任务栏按钮
window.mbQuery(0, 'titlebar:flash', function() {});

// 设置窗口置顶
window.mbQuery(0, 'titlebar:setAlwaysOnTop:true', function() {});

// 获取窗口状态
window.mbQuery(0, 'titlebar:getState', function(customMsg, response) {
    console.log(response);
    // 输出: {"state": "maximized", "isMaximized": true, "isMinimized": false, "isAlwaysOnTop": false, "title": "我的应用"}
});

// 调整窗口大小
window.mbQuery(0, 'titlebar:resize:1024:768', function() {});

// 移动窗口位置
window.mbQuery(0, 'titlebar:move:100:100', function() {});

// 窗口居中显示
window.mbQuery(0, 'titlebar:center', function() {});
```

#### getState 返回值

```json
{
    "state": "maximized",
    "isMaximized": true,
    "isMinimized": false,
    "isAlwaysOnTop": false,
    "title": "我的应用"
}
```

state 取值：`"normal"` | `"minimized"` | `"maximized"` | `"restored"`

### 依赖注入 DI

依赖注入容器管理组件及其依赖关系。

```python
from app.core.di.container import injected, DIContainer

class MyComponent:
    mp_manager = injected(MultiprocessManager)
    event_bus = injected(EventBus)
```

#### 核心方法

| 方法 | 说明 |
|------|------|
| `register(service_type, instance, singleton=True)` | 注册服务实例 |
| `register_factory(service_type, factory)` | 注册工厂函数 |
| `resolve(service_type)` | 获取服务实例 |
| `has(service_type)` | 检查服务是否已注册 |
| `clear()` | 清空所有注册 |

#### 装饰器

| 装饰器 | 说明 |
|--------|------|
| `@injected(service_type)` | 属性装饰器，自动注入服务 |
| `@inject(service_type)` | 函数参数装饰器 |

### 多进程管理 MultiprocessManager

多进程管理器提供安全的代码隔离执行，将耗时任务放到子进程中运行，避免阻塞主进程。

```python
from app.core import MultiprocessManager

mp_manager = MultiprocessManager()
result = mp_manager.submit(heavy_function, "input_data")
```

#### 为什么需要多进程

Python 的 GIL（全局解释器锁）限制了多线程的并行执行能力。对于 CPU 密集型任务，多进程可以充分利用多核 CPU，提高执行效率。同时，多进程提供进程隔离，一个进程崩溃不会影响其他进程。

#### 核心方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `submit(func, *args, **kwargs)` | 同步提交任务，阻塞等待结果 | 任务返回值 |
| `submit_async(func, *args, **kwargs)` | 异步提交任务，立即返回 Future | Future 对象 |
| `map(func, args_list)` | 同步批量执行多个任务 | 结果列表 |
| `map_async(func, args_list)` | 异步批量执行多个任务 | Future 列表 |
| `shutdown(wait=True)` | 关闭进程池 | 无 |
| `is_enabled()` | 检查是否启用多进程 | bool |
| `set_enabled(enabled)` | 设置启用状态 | 无 |

#### 使用示例

**同步执行：**

```python
from app.core import MultiprocessManager

mp_manager = MultiprocessManager()

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# 同步执行，阻塞等待结果
result = mp_manager.submit(calculate_fibonacci, 30)
print(result)  # 832040
```

**异步执行：**

```python
import asyncio
from app.core import get_multiprocess_manager

async def async_calculation():
    mp_manager = get_multiprocess_manager()
    future = mp_manager.submit_async(calculate_fibonacci, 30)
    result = await asyncio.wrap_future(future)
    return result

result = asyncio.run(async_calculation())
```

**批量执行：**

```python
from app.core import get_multiprocess_manager

mp_manager = get_multiprocess_manager()

# 同步批量执行
results = mp_manager.map(
    calculate_fibonacci,
    [20, 25, 30, 35, 40]
)
print(results)  # [6765, 75025, 832040, 9227465, 102334155]
```

#### 辅助函数

| 函数 | 说明 |
|------|------|
| `run_in_process(func)` | 装饰器，函数在子进程执行 |
| `run_in_process_async(func)` | 装饰器，函数在子进程异步执行 |
| `get_multiprocess_manager()` | 获取全局 MultiprocessManager 实例 |

**装饰器用法：**

```python
from app.core.util.mp_manager import run_in_process, run_in_process_async

# 同步执行装饰器
@run_in_process
def heavy_computation(data):
    # 耗时计算
    result = sum(i*i for i in range(10000000))
    return result

# 直接调用，会在子进程执行
result = heavy_computation("data")
```

#### 在组件中使用

组件可以通过依赖注入获取 MultiprocessManager：

```python
from app.core.interface.icell import ICell
from app.core.di.container import injected

class DataProcessor(ICell):
    mp_manager = injected("MultiprocessManager")
    
    @property
    def cell_name(self) -> str:
        return "dataprocessor"
    
    def execute(self, command: str, *args, **kwargs):
        if command == "process":
            data = args[0] if args else ""
            # 在子进程执行耗时操作
            result = self.mp_manager.submit(self._heavy_process, data)
            return result
        return f"Unknown command: {command}"
    
    def _heavy_process(self, data: str) -> str:
        """耗时处理逻辑"""
        import time
        time.sleep(2)  # 模拟耗时操作
        return f"Processed: {data.upper()}"
```

#### 配置与限制

```python
from app.core import get_multiprocess_manager

mp_manager = get_multiprocess_manager()

# 禁用多进程（回退到单进程执行）
mp_manager.set_enabled(False)

# 检查是否启用
if mp_manager.is_enabled():
    print("多进程已启用")
```

#### 注意事项

1. **进程间通信**：进程间数据传递需要序列化（pickle），避免传递不可序列化对象
2. **资源限制**：进程池大小默认为 CPU 核心数，可根据任务类型调整
3. **生命周期**：进程池在程序退出时自动关闭，也可手动调用 `shutdown()`
4. **异常处理**：子进程中的异常会传递到主进程，使用 `try/except` 捕获

### 消息处理器 MessageHandler

消息处理器负责解析前端命令并路由到对应组件。

```python
from app.core import MessageHandler

handler = MessageHandler(hwnd)
handler.register_cell(calculator)
result = handler.handle_message("calculator:calc:1+1")
```

#### 核心方法

| 方法 | 说明 |
|------|------|
| `register_cell(cell)` | 注册 ICell 组件 |
| `get_cell(name)` | 根据名称获取组件 |

### 桥接层 MiniBlinkBridge

桥接层封装 Python 与 MiniBlink 浏览器引擎的通信。

```python
from app.core import MiniBlinkBridge

# 组件中通过 MainWindow 获取 bridge
class MyComponent:
    def __init__(self, bridge):
        self.bridge = bridge
    
    def update_ui(self, value):
        self.bridge.set_element_value('output', value)
```

#### 核心方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `send_to_js(script)` | 发送 JS 代码执行 | `bridge.send_to_js("alert('hi')")` |
| `set_element_value(element_id, value)` | 设置元素值 | `bridge.set_element_value('output', '2')` |
| `get_element_value(element_id, callback)` | 获取元素值（异步） | `bridge.get_element_value('input', callback)` |
| `setup_all_callbacks()` | 设置所有 MiniBlink 回调 | 初始化时调用 |

#### 前端日志

MiniBlink 支持将前端 JavaScript 的 `console` 日志转发到 Python 日志系统，方便调试。

**前端 JavaScript**
```javascript
console.log("调试信息");
console.warn("警告信息");
console.error("错误信息");
console.info("普通信息");
console.debug("调试信息");
```

**Python 日志输出**
```bash
[DEBUG] [Console][LOG] 调试信息 (file:index.html:100)
[DEBUG] [Console][WARNING] 警告信息 (file:index.html:101)
[DEBUG] [Console][ERROR] 错误信息 (file:index.html:102)
```

**日志级别映射**

| 前端 console | Python 日志级别 |
|-------------|----------------|
| console.log | DEBUG |
| console.warn | WARNING |
| console.error | ERROR |
| console.info | INFO |
| console.debug | DEBUG |

> **注意**：此功能需要 MiniBlink DLL 支持 `mbOnConsole` 接口（v132 及以上版本）。

### 主窗口 MainWindow

主窗口类管理应用窗口生命周期。

```python
from app.core import MainWindow

window = MainWindow()
window.run()
```

#### 核心方法

| 方法 | 说明 |
|------|------|
| `run()` | 启动窗口主循环 |
| `load_window_icon()` | 加载窗口图标 |
| `create_window()` | 创建窗口 |
| `init_engine()` | 初始化浏览器引擎 |
| `load_dll()` | 加载 MiniBlink DLL |
| `fade_out(duration)` | 窗口淡出效果 |
| `remove_titlebar()` | 移除标题栏 |

### 组件加载器 ComponentsLoader

组件加载器负责从配置文件加载组件。

```python
from app.core.util.components_loader import load_components, load_component_config

# 加载配置
config = load_component_config(config_path)

# 加载组件
components = load_components(container, debug=True)
```

#### 核心函数

| 函数 | 说明 |
|------|------|
| `load_component_config(config_path)` | 加载 YAML 配置文件 |
| `load_components(container, debug)` | 根据配置加载组件 |
| `dynamic_import(module_path)` | 动态导入模块 |

### 命令调用格式

前端通过 `window.mbQuery()` 函数调用组件：

```javascript
// 计算表达式
window.mbQuery(0, 'calculator:calc:1+1', function(customMsg, response) {
    console.log(response);
})

// 读取文件
window.mbQuery(0, 'filemanager:read:C:/test.txt', function(customMsg, response) {
    console.log(response);
})

// 写入文件
window.mbQuery(0, 'filemanager:write:C:/test.txt:Hello World', function(customMsg, response) {
    console.log(response);
})

// 调用自定义组件
window.mbQuery(0, 'mycell:greet:Cellium', function(customMsg, response) {
    console.log(response);
})
```

## 配置指南

组件通过 `config/settings.yaml` 配置文件管理：

```yaml
# config/settings.yaml
enabled_components:
  - app.components.calculator.Calculator
  - app.components.filemanager.FileManager
  # - app.components.debug.DebugTool  <-- 注释则不加载
```

### 自动发现

Cellium 支持两种组件加载方式：

**1. 配置加载（当前默认）**

在配置文件中显式声明要加载的组件：

```yaml
enabled_components:
  - app.components.calculator.Calculator
```

**2. 自动扫描（可选）**

配置自动扫描 `app/components/` 目录，发现并加载所有 ICell 实现：

```yaml
auto_discover: true
scan_paths:
  - app.components
```

## 快速开始

### 1. 运行应用

```python
from app.core import MainWindow

def main():
    window = MainWindow()
    window.run()

if __name__ == "__main__":
    main()
```

### 2. 前端调用组件

```javascript
// 在 HTML/JavaScript 中
<button onclick="window.mbQuery(0, 'calculator:calc:1+1', function(customMsg, response){ document.getElementById('result').innerText = response; })">计算 1+1</button>
<button onclick="window.mbQuery(0, 'calculator:calc:2*3', function(customMsg, response){ document.getElementById('result').innerText = response; })">计算 2*3</button>
```

### 3. 查看组件列表

所有已加载的组件及其命令会在启动日志中显示：

```
[INFO] 已加载组件: Calculator (cell_name: calculator)
[INFO] 已加载组件: FileManager (cell_name: filemanager)
```

## 扩展指南

### 添加异步组件

组件支持异步执行：

```python
import asyncio
from app.core.interface.icell import ICell

class AsyncCell(ICell):
    @property
    def cell_name(self) -> str:
        return "async"
    
    async def execute(self, command: str, *args, **kwargs) -> str:
        if command == "fetch":
            return await self._async_fetch(args[0] if args else "")
        return f"Unknown command: {command}"
    
    async def _async_fetch(self, url: str) -> str:
        # 异步操作
        await asyncio.sleep(1)
        return f"Fetched: {url}"
    
    def get_commands(self) -> dict:
        return {
            "fetch": "异步获取数据，例如: async:fetch:https://example.com"
        }
```

### 组件间通信

通过事件总线进行组件间通信：

```python
from app.core import event_bus
from app.core.events import EventType

class CellA(ICell):
    def execute(self, command: str, *args, **kwargs) -> str:
        if command == "notify":
            event_bus.publish(EventType.CUSTOM_NOTIFY, message=args[0])
            return "Notification sent"
        return "Unknown command"
    
    def get_commands(self) -> dict:
        return {"notify": "发送通知"}


class CellB(ICell):
    def __init__(self):
        event_bus.subscribe(EventType.CUSTOM_NOTIFY, self._on_notify)
    
    def _on_notify(self, event):
        print(f"收到通知: {event.data}")
    
    # ... 其他 ICell 方法
```

### 资源路径管理

```python
from app.core.util import get_project_root

# 获取项目根目录
root = get_project_root()

# 资源路径
dll_path = root / "dll" / "mb132_x64.dll"
html_path = root / "html" / "index.html"
```

## 最佳实践

1. **保持组件独立** - 每个组件应专注于单一功能
2. **遵循 ICell 规范** - 正确实现 cell_name、execute、get_commands
3. **使用依赖注入** - 通过 injected 获取服务，避免硬编码依赖
4. **处理异常** - 在 execute 中捕获异常并返回错误信息
5. **返回可序列化结果** - 确保返回结果可以被 JSON 序列化


