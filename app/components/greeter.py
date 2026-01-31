from app.core.interface.base_cell import BaseCell


class Greeter(BaseCell):
    """问候组件：接收文字，添加后缀后返回"""

    def _cmd_greet(self, text: str = "") -> str:
        """添加问候后缀，例如: greeter:greet:你好"""
        if not text:
            return "Hallo Cellium"
        return f"{text} Hallo Cellium"

    def _cmd_reverse(self, text: str = "") -> str:
        """反转字符串，例如: greeter:reverse:你好"""
        return text[::-1]
