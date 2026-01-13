from app.core.interface.icell import ICell


class Greeter(ICell):
    """问候组件：接收文字，添加后缀后返回"""

    @property
    def cell_name(self) -> str:
        """组件唯一标识，用于前端调用"""
        return "greeter"

    def execute(self, command: str, *args, **kwargs):
        """自动映射命令到以 _cmd_ 开头的方法"""
        method_name = f"_cmd_{command}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(*args, **kwargs)
        return f"Cell '{self.cell_name}' has no command: {command}"

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
