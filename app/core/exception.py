# -*- coding: utf-8 -*-
"""
组件异常定义
"""

class CommandNotFoundError(Exception):
    """命令未找到异常"""
    
    def __init__(self, command: str, cell_name: str = None):
        self.command = command
        self.cell_name = cell_name
        message = f"Command not found: '{command}'"
        if cell_name:
            message = f"Command not found: '{command}' in cell '{cell_name}'"
        super().__init__(message)


class ComponentError(Exception):
    """组件执行错误"""
    
    def __init__(self, message: str, cell_name: str = None):
        self.message = message
        self.cell_name = cell_name
        super().__init__(message)
