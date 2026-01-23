# -*- coding: utf-8 -*-
"""
Cellium 组件模板生成器
直接运行脚本，按提示操作
支持交互式和命令行两种模式：
- 交互式: 直接运行脚本，按提示操作
- 命令行: python scripts/generate_component.py <name> [options]
"""

import os
import sys

COMPONENTS_DIR = "app/components"
SETTINGS_FILE = "config/settings.yaml"


def find_available_name(name: str) -> str:
    """查找可用的组件文件名（处理重复名称）"""
    base_name = name.lower()
    component_name = base_name
    suffix = 1

    while True:
        path = os.path.join(COMPONENTS_DIR, f"{component_name}.py")
        if not os.path.exists(path):
            return component_name
        component_name = f"{base_name}_{suffix}"
        suffix += 1


def generate_component(name: str) -> str:
    """生成组件模板，返回生成的组件名"""
    component_name = find_available_name(name)
    class_name = component_name.title().replace('_', '')

    template = f'''# -*- coding: utf-8 -*-
"""
{class_name} 组件

由组件模板生成器自动生成
"""

import logging
from typing import Any, Dict, List, Optional
from app.core.interface.icell import ICell
from app.core.bus import event, event_bus, register_component_handlers
from app.core.bus.events import EventType

logger = logging.getLogger(__name__)


class {class_name}(ICell):
    """
    {class_name} 组件

    Cellium 组件开发说明：

    1. 必须实现 ICell 接口
       - cell_name: 组件唯一标识（小写字母）
       - execute(): 处理前端命令
       - get_commands(): 返回可用命令列表

    2. 可选特性
       - @event 装饰器: 订阅事件
       - @emitter 装饰器: 发布事件
       - AutoInjectMeta: 自动依赖注入
       - mp_manager.submit(): 异步执行
    """

    def __init__(self):
        register_component_handlers(self)
        self._internal_state = None

    @property
    def cell_name(self) -> str:
        return "{component_name}"

    def execute(self, command: str, *args, **kwargs) -> Any:
        """执行命令"""
        method_name = f"_cmd_{{command}}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(*args, **kwargs)
        return {{"error": f"Unknown command: {{command}}"}}

    def get_commands(self) -> Dict[str, str]:
        """返回可用命令列表"""
        return {{
            "example": "示例，例如: {component_name}:example:参数",
            "greet": "打招呼，例如: {component_name}:greet:姓名",
            "get_data": "获取数据，例如: {component_name}:get_data",
            "set_data": "设置数据，例如: {component_name}:set_data:值",
            "process": "处理数据，例如: {component_name}:process:数据"
        }}

    def _cmd_example(self, *args, **kwargs) -> str:
        """示例命令"""
        param = args[0] if args else "World"
        return f"Hello {{param}} from {component_name}!"

    def _cmd_greet(self, *args, **kwargs) -> Dict[str, Any]:
        """打招呼命令"""
        name = args[0] if args else "Guest"
        return {{
            "message": f"Welcome, {{name}}!",
            "component": self.cell_name,
            "timestamp": self._get_timestamp()
        }}

    def _cmd_get_data(self, *args, **kwargs) -> Dict[str, Any]:
        """获取数据"""
        return {{
            "state": self._internal_state,
            "component": self.cell_name
        }}

    def _cmd_set_data(self, *args, **kwargs) -> Dict[str, Any]:
        """设置数据"""
        value = args[0] if args else None
        self._internal_state = value
        return {{
            "success": True,
            "message": f"Data set to: {{value}}"
        }}

    def _cmd_process(self, *args, **kwargs) -> Dict[str, Any]:
        """处理数据"""
        data = args[0] if args else ""
        result = {{"processed": data, "length": len(data)}}
        return result

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    # ========================================================================
    # 事件处理示例
    # ========================================================================
    # 使用 @event 装饰器订阅事件

    # @event("app.startup")
    # def on_startup(self, event_name: str, **kwargs) -> None:
    #     """应用启动时触发"""
    #     logger.info(f"{{self.cell_name}} 收到事件: {{event_name}}")

    # @event("app.shutdown")
    # def on_shutdown(self, event_name: str, **kwargs) -> None:
    #     """应用关闭时触发"""
    #     logger.info(f"{{self.cell_name}} 收到事件: {{event_name}}")

    # @event("data.updated")
    # def on_data_updated(self, event_name: str, **kwargs) -> None:
    #     """数据更新时触发"""
    #     data = kwargs.get("data")
    #     logger.info(f"数据更新: {{data}}")

    # @event_pattern("user.*")
    # def on_user_event(self, event_name: str, **kwargs) -> None:
    #     """用户相关事件（模式匹配）"""
    #     logger.info(f"用户事件: {{event_name}}")

    # ========================================================================
    # 事件发布示例
    # ========================================================================
    # 使用 event_bus.publish(事件名, **kwargs) 发布事件

    # def notify_complete(self, result: Any) -> None:
    #     """通知任务完成"""
    #     event_bus.publish(
    #         "{component_name}.completed",
    #         result=result
    #     )

    # ========================================================================
    # 异步执行示例
    # ========================================================================
    # 耗时操作应使用 mp_manager.submit() 异步执行

    # def _cmd_heavy_task(self, *args, **kwargs) -> str:
    #     """异步执行耗时任务"""
    #     from app.core.util.mp_manager import mp_manager
    #     data = args[0] if args else ""
    #     return mp_manager.submit(self._heavy_impl, data)
    #
    # def _heavy_impl(self, data: str) -> Dict[str, Any]:
    #     """耗时任务实现（在新进程中执行）"""
    #     import time
    #     time.sleep(2)
    #     return {{"processed": data, "status": "completed"}}

    # ========================================================================
    # 依赖注入示例
    # ========================================================================
    # 使用 AutoInjectMeta 元类自动注入依赖

    # class {class_name}(ICell, metaclass=AutoInjectMeta):
    #     mp_manager = injected(MultiprocessManager)
    #     event_bus = injected(EventBus)
    #
    #     def some_method(self):
    #         self.event_bus.publish("{component_name}.test", value=123)

'''

    os.makedirs(COMPONENTS_DIR, exist_ok=True)

    component_path = os.path.join(COMPONENTS_DIR, f"{component_name}.py")
    with open(component_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"✓ 组件已生成: {component_path}")
    return component_name


def register_component(name: str) -> bool:
    """注册组件到 settings.yaml"""
    if not os.path.exists(SETTINGS_FILE):
        print(f"⚠ 配置文件不存在，跳过注册: {SETTINGS_FILE}")
        return False

    class_name = name.lower().title().replace('_', '')
    component_line = f"  - app.components.{name}.{class_name}"

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if component_line in content:
        print(f"⚠ 组件已注册，跳过: {name}")
        return True

    lines = content.split("\n")
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        stripped = line.strip()
        if not inserted and stripped == "enabled_components:":
            new_lines.append(component_line)
            inserted = True

    if not inserted:
        new_lines.append(component_line)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✓ 组件已注册: {name}")
    return True


def unregister_component(name: str) -> bool:
    """从 settings.yaml 注销组件"""
    if not os.path.exists(SETTINGS_FILE):
        print(f"⚠ 配置文件不存在: {SETTINGS_FILE}")
        return False

    class_name = name.lower().title().replace('_', '')
    component_line = f"  - app.components.{name}.{class_name}"
    component_stripped = component_line.strip()

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    original_count = len(lines)
    new_lines = [
        line for line in lines
        if line.strip() != component_stripped and line != component_line
    ]

    if len(new_lines) == original_count:
        print(f"⚠ 未找到组件注册项: {name}")
        return False

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✓ 组件已注销: {name}")
    return True


def delete_component(name: str) -> bool:
    """删除组件文件"""
    component_path = os.path.join(COMPONENTS_DIR, f"{name}.py")
    if os.path.exists(component_path):
        os.remove(component_path)
        print(f"✓ 已删除: {component_path}")
        return True
    return False


def list_components() -> list:
    """列出所有已注册的组件"""
    if not os.path.exists(SETTINGS_FILE):
        return []

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    components = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("  - app.components."):
            components.append(line.replace("  - app.components.", "").strip())

    return components


def list_local_components() -> list:
    """列出本地所有组件文件"""
    if not os.path.exists(COMPONENTS_DIR):
        return []

    components = []
    for f in os.listdir(COMPONENTS_DIR):
        if f.endswith(".py") and f not in ["__init__.py", "__pycache__"]:
            components.append(f.replace(".py", ""))

    return components


def print_header():
    """打印标题"""
    print("Cellium 组件模板生成器")
    print("生成组件 -> 自动命名 -> 自动注册")
    print()


def print_menu():
    """打印菜单"""
    print("选项:")
    print()
    print("  1. 创建新组件")
    print("  2. 注销组件")
    print()
    print("  help / ?  显示帮助")
    print("  q / quit  退出")
    print()


def interactive_mode():
    """交互式模式"""
    print_header()
    print_menu()

    while True:
        try:
            choice = input("\n请选择 [1-2]: ").strip().lower()

            if choice in ["q", "quit", "exit", "退出"]:
                break

            elif choice in ["help", "?", "帮助"]:
                print_menu()

            elif choice == "1":
                create_component_interactive()
                print_menu()

            elif choice == "2":
                unregister_component_interactive()
                print_menu()

            else:
                print("无效选项，请输入 1-2 或 help 查看帮助")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")


def create_component_interactive():
    """交互式创建组件"""
    print("创建新组件")
    print("-" * 30)

    name = input("请输入组件名称: ").strip().lower()

    if not name:
        name = "mycomponent"
        print(f"使用默认名称: {name}")

    if not name.replace("_", "").isalnum():
        print("错误: 组件名称只能包含字母、数字和下划线")
        return

    do_register = input("是否自动注册到 settings.yaml? [y/N]: ").strip().lower()
    do_register = do_register in ["y", "yes", "是"]

    component_name = generate_component(name)

    if do_register:
        register_component(component_name)

    print()
    print("=" * 40)
    print(f"组件 {component_name} 创建成功！")
    print()
    print(f"文件: app/components/{component_name}.py")
    print(f"注册: {'是' if do_register else '否'}")
    print()
    print("前端调用示例:")
    print(f"  window.mbQuery(0, '{component_name}:example:参数', callback);")
    print(f"  window.mbQuery(0, '{component_name}:greet:张三', callback);")
    print("=" * 40)


def unregister_component_interactive():
    """交互式注销组件"""
    print("注销组件")
    print("-" * 30)

    components = list_local_components()

    if not components:
        print("没有本地组件文件")
        return

    print("本地组件列表:")
    for i, comp in enumerate(components, 1):
        print(f"  {i}. {comp}")

    print()
    print("可输入组件名称或序号进行注销")
    choice = input("请选择: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(components):
        name = components[int(choice) - 1]
    else:
        name = choice

    delete = input(f"是否同时删除组件文件? [y/N]: ").strip().lower()
    delete_file = delete in ["y", "yes", "是"]

    if delete_file:
        delete_component(name)
    unregister_component(name)

    print(f"\n组件 {name} 已注销")


def print_usage():
    """打印命令行使用说明"""
    print("Cellium 组件模板生成器")
    print()
    print("用法:")
    print("  python scripts/generate_component.py <component_name> [options]")
    print()
    print("参数:")
    print("  <component_name>    组件名称（使用下划线分隔单词）")
    print()
    print("选项:")
    print("  --register, -r      自动注册组件到 settings.yaml")
    print("  --unregister, -u    删除组件文件并注销")
    print("  --regen, -g         重新生成（先删除再创建）")
    print("  --list, -l          列出所有已注册的组件")
    print()
    print("示例:")
    print("  python scripts/generate_component.py filemanager")
    print("  python scripts/generate_component.py filemanager --register")
    print("  python scripts/generate_component.py filemanager -u")
    print("  python scripts/generate_component.py --list")
    print()
    print("不带参数运行将进入交互式模式:")
    print("  python scripts/generate_component.py")


def main():
    if len(sys.argv) < 2:
        interactive_mode()
        return

    command = sys.argv[1].lower()

    if command in ["--help", "-h", "help", "?"]:
        print_usage()
        return

    if command in ["--list", "-l"]:
        components = list_components()
        print("\n已注册的组件:")
        for comp in components:
            print(f"  - {comp}")
        return

    name = sys.argv[1].lower()
    auto_register = "--register" in sys.argv or "-r" in sys.argv
    auto_unregister = "--unregister" in sys.argv or "-u" in sys.argv
    regen = "--regen" in sys.argv or "-g" in sys.argv

    if not name.replace("_", "").isalnum():
        print("错误: 组件名称只能包含字母、数字和下划线")
        return

    if regen:
        delete_component(name)
        unregister_component(name)

    if auto_unregister:
        delete_component(name)
        unregister_component(name)
        print(f"\n组件 {name} 已注销")
        return

    component_name = generate_component(name)

    if auto_register:
        register_component(component_name)

    print()
    print("=" * 40)
    print(f"组件 {component_name} 创建成功！")
    print()
    print(f"文件: app/components/{component_name}.py")
    print()
    print("前端调用示例:")
    print(f"  window.mbQuery(0, '{component_name}:example:参数', callback);")
    print(f"  window.mbQuery(0, '{component_name}:greet:张三', callback);")
    print("=" * 40)


if __name__ == "__main__":
    main()
