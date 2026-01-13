# -*- coding: utf-8 -*-
"""
事件类型定义
使用枚举避免字符串硬编码
"""

from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    
    # 导航事件
    NAVIGATION = "navigation"
    
    # Alert 事件
    ALERT = "alert"
    
    # JsQuery 事件
    JSQUERY = "jsquery"
    
    # 窗口事件
    FADE_OUT = "fade_out"
    WINDOW_RESIZE = "window_resize"
    WINDOW_MOVE = "window_move"
    
    # 按钮事件
    BUTTON_CLICK = "button_click"
    
    # 计算器事件
    CALC_RESULT = "calc_result"
    
    # 系统事件
    SYSTEM_COMMAND = "system_command"
    
    def __str__(self):
        return self.value
