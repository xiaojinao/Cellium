# -*- coding: utf-8 -*-
"""
计算器组件
"""

import logging
from app.core.interface.base_cell import BaseCell
from app.core.bus import event

logger = logging.getLogger(__name__)


def _sanitize_expression(expression: str) -> str:
    allowed_chars = set('0123456789+-*/.() ')
    return ''.join(c for c in expression if c in allowed_chars)


def _calculate_impl(expression: str) -> str:
    return str(eval(_sanitize_expression(expression)))


class Calculator(BaseCell):
    """计算器组件"""
    
    @event("calc.requested")
    def on_calc_requested(self, event_name, **kwargs):
        """计算请求事件处理器"""
        logger.info(f"[事件] 收到计算请求: {kwargs.get('expression', '')}")
    
    @event("calc.completed")
    def on_calc_completed(self, event_name, **kwargs):
        """计算完成事件处理器"""
        logger.info(f"[事件] 计算完成: {kwargs.get('expression', '')} = {kwargs.get('result', '')}")
    
    @event("calc.error")
    def on_calc_error(self, event_name, **kwargs):
        """计算错误事件处理器"""
        logger.error(f"[事件] 计算错误: {kwargs.get('expression', '')} - {kwargs.get('error', '')}")
    
    @property
    def cell_name(self) -> str:
        return "calculator"
    
    def _cmd_calc(self, expression: str = '') -> str:
        """计算表达式"""
        return self._calculate(expression)
    
    def _cmd_eval(self, expression: str = '') -> str:
        """计算表达式（与 calc 相同）"""
        return self._calculate(expression)
    
    def _calculate(self, expression: str) -> str:
        self.event_bus.publish("calc.requested", expression=expression)
        try:
            result = _calculate_impl(expression)
            self.event_bus.publish("calc.completed", expression=expression, result=result)
            return result
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.event_bus.publish("calc.error", expression=expression, error=error_msg)
            return error_msg
