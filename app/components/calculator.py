# -*- coding: utf-8 -*-
"""
计算器组件
处理数学表达式计算

支持统一命令格式：pycmd('calculator:命令:参数')
例如：
    pycmd('calculator:calc:1+1')
    pycmd('calculator:eval:2*3+4')
"""

import logging
import re
from app.core.di.container import injected, AutoInjectMeta
from app.core.util.mp_manager import MultiprocessManager
from app.core.interface.icell import ICell

logger = logging.getLogger(__name__)


def _sanitize_expression(expression: str) -> str:
    """清理表达式，只允许安全的数学运算
    
    Args:
        expression: 原始表达式
        
    Returns:
        str: 清理后的表达式
    """
    allowed_chars = set('0123456789+-*/.() ')
    sanitized = ''.join(c if c in allowed_chars else '' for c in expression)
    return sanitized


def _calculate_impl(expression: str) -> str:
    """纯函数：计算表达式
    
    这是真正在子进程中执行的函数，只接受和返回可序列化数据。
    
    Args:
        expression: 数学表达式字符串
        
    Returns:
        str: 计算结果或错误信息
    """
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    logger = logging.getLogger("calculator")
    
    try:
        logger.info(f"计算表达式: {expression}")
        
        sanitized = _sanitize_expression(expression)
        result = eval(sanitized)
        
        logger.info(f"计算结果: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"计算错误: {e}")
        return f"Error: {str(e)}"


class Calculator(ICell, metaclass=AutoInjectMeta):
    mp_manager = injected(MultiprocessManager)
    
    def __init__(self, webview=None, lib=None):
        self._webview = webview
        self._lib = lib
    
    @property
    def cell_name(self) -> str:
        return "calculator"
    
    def execute(self, command: str, *args, **kwargs) -> str:
        """执行计算器命令
        
        Args:
            command: 命令名称（calc, eval）
            *args: 第一个参数为表达式字符串
            
        Returns:
            str: 计算结果
        """
        expression = args[0] if args else ''
        
        if command in ("calc", "eval"):
            return self.calculate(expression)
        else:
            return f"Error: Unknown command '{command}'"
    
    def get_commands(self) -> dict:
        return {
            "calc": "计算表达式，例如: calculator:calc:1+1",
            "eval": "计算表达式（与 calc 相同），例如: calculator:eval:2*3"
        }
    
    @property
    def webview(self):
        return self._webview
    
    @webview.setter
    def webview(self, value):
        self._webview = value
    
    @property
    def lib(self):
        return self._lib
    
    @lib.setter
    def lib(self, value):
        self._lib = value

    @property
    def bridge(self):
        return self._bridge

    @bridge.setter
    def bridge(self, value):
        self._bridge = value
    
    def calculate(self, expression: str) -> str:
        """计算表达式
        
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            str: 计算结果或错误信息
        """
        return self.mp_manager.submit(_calculate_impl, expression)
    
    def handle_calc_query(self, webview, query_id, custom_msg, expression):
        """处理计算查询
        
        Args:
            webview: Webview 对象
            query_id: 查询 ID
            custom_msg: 自定义消息
            expression: 计算表达式
            
        Returns:
            str: 计算结果
        """
        result = self.calculate(expression)
        logger.info(f"[INFO] 计算结果: {result}")
        return result
    
    def show_result(self, result: str):
        """显示计算结果到 HTML
        
        Args:
            result: 计算结果字符串
        """
        self.bridge.set_element_value('calc-display', result)
    
    def handle_calc_result(self, result: str):
        """处理计算结果
        
        Args:
            result: 计算结果字符串
        """
        self.show_result(result)
