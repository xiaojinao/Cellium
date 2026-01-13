# -*- coding: utf-8 -*-
"""
消息处理器
处理来自 JavaScript 的消息和命令

支持统一命令格式：pycmd('组件名:命令:参数')
例如：
    pycmd('calculator:calc:1+1')
    pycmd('filemanager:read:C:/test.txt')
"""

import ctypes
import logging
from ctypes import wintypes, byref
from typing import Any, Optional
from ..bus.event_bus import event_bus, event_handler
from ..bus.events import EventType
from ..bus.event_models import AlertEvent, JsQueryEvent, FadeOutEvent
from ..interface.icell import ICell
from ..util.components_loader import get_cell as get_cell_from_registry, register_cell as register_cell_to_global

user32 = ctypes.windll.user32
logger = logging.getLogger(__name__)


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("showCmd", ctypes.c_uint),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT),
    ]


class MessageHandler:
    def __init__(self, hwnd, calculator=None):
        self.hwnd = hwnd
        self.calculator = calculator
        self._button_callbacks = {}
        
        if self.calculator and isinstance(self.calculator, ICell):
            register_cell_to_global(self.calculator)
        
        event_bus.subscribe(EventType.ALERT, self._on_alert_message)
        event_bus.subscribe(EventType.JSQUERY, self._on_jsquery_message)
    
    def get_cell(self, name: str) -> Optional[ICell]:
        """根据名称获取组件（从全局注册表）"""
        return get_cell_from_registry(name)
    
    def _parse_cell_command(self, command: str) -> tuple:
        """解析组件命令格式
        
        格式：组件名:命令:参数
        
        Args:
            command: 原始命令字符串
            
        Returns:
            tuple: (组件名, 命令, 参数列表)
            解析失败返回 (None, None, None)
        """
        try:
            parts = command.split(':', 2)
            if len(parts) < 2:
                return (None, None, None)
            
            cell_name = parts[0]
            cmd = parts[1]
            args = parts[2] if len(parts) > 2 else ''
            
            return (cell_name, cmd, args)
        except Exception as e:
            logger.error(f"解析命令失败: {command}, 错误: {e}")
            return (None, None, None)
    
    def _handle_cell_command(self, command: str) -> Any:
        """处理统一格式的组件命令
        
        格式：组件名:命令:参数
        
        Args:
            command: 命令字符串
            
        Returns:
            命令执行结果
        """
        cell_name, cmd, args = self._parse_cell_command(command)
        
        if not cell_name:
            logger.warning(f"无法解析命令: {command}")
            return "Error: Invalid command format"
        
        cell = self.get_cell(cell_name)
        if not cell:
            logger.warning(f"组件不存在: {cell_name}")
            return f"Error: Cell '{cell_name}' not found"
        
        try:
            logger.info(f"执行命令: {cell_name}:{cmd}:{args}")
            return cell.execute(cmd, args)
        except Exception as e:
            logger.error(f"命令执行失败: {cell_name}:{cmd}, 错误: {e}")
            return f"Error: {str(e)}"
    
    def _on_alert_message(self, event: AlertEvent):
        """处理 Alert 消息"""
        msg_str = event.message
        if msg_str.startswith("__CALC_RESULT__:"):
            result = msg_str[len("__CALC_RESULT__"):]
            self._handle_calc_result(result)
        elif msg_str and ':' in msg_str:
            result = self._handle_cell_command(msg_str)
            logger.info(f"[INFO] 命令执行结果: {result}")
        elif msg_str:
            self._on_python_command(msg_str)
    
    def _on_jsquery_message(self, event: JsQueryEvent):
        """处理 JsQuery 消息"""
        msg_str = event.message
        if msg_str.startswith("syscmd:"):
            cmd = msg_str[7:]
            return self._handle_system_command(event.webview, event.query_id, event.custom_msg, cmd)
        elif msg_str.startswith("calc:"):
            expression = msg_str[5:]
            return self._handle_calc_query(event.webview, event.query_id, event.custom_msg, expression)
        elif ':' in msg_str:
            return self._handle_cell_command(msg_str)
        return None
    
    def _on_python_command(self, command):
        """处理来自 JavaScript 的命令
        
        优先使用统一命令格式：组件名:命令:参数
        """
        logger.info(f"[INFO] 收到 Python 命令: {command}")
        
        if ':' in command:
            cell_name, cmd, args = self._parse_cell_command(command)
            if cell_name and self.get_cell(cell_name):
                result = self._handle_cell_command(command)
                logger.info(f"[INFO] 命令执行结果: {result}")
                return
        
        if command.startswith("calc:"):
            expression = command[5:]
            if self.calculator:
                result = self.calculator.calculate(expression)
                self.calculator.show_result(result)
        
        elif command.startswith("click:"):
            button_id = command[6:]
            event = MiniblinkButtonEvent(
                button_id=button_id,
                hwnd=self.hwnd,
                event_type="click"
            )
            self._on_button_clicked(event)
    
    def _handle_calc_result(self, result):
        """处理计算结果"""
        if self.calculator:
            self.calculator.handle_calc_result(result)
    
    def _handle_system_command(self, webview, query_id, custom_msg, cmd):
        """处理系统命令"""
        if cmd == "minimize":
            user32.ShowWindow(self.hwnd, 2)
        elif cmd == "maximize":
            placement = WINDOWPLACEMENT()
            placement.length = ctypes.sizeof(WINDOWPLACEMENT)
            user32.GetWindowPlacement(self.hwnd, byref(placement))
            
            if placement.showCmd == 3:
                user32.ShowWindow(self.hwnd, 9)
            else:
                user32.ShowWindow(self.hwnd, 3)
        elif cmd == "close":
            logger.info("[INFO] 开始关闭窗口...")
            event = FadeOutEvent()
            event_bus.publish(EventType.FADE_OUT, event)
        return "OK"
    
    def _handle_calc_query(self, webview, query_id, custom_msg, expression):
        """处理计算查询"""
        if self.calculator:
            return self.calculator.handle_calc_query(webview, query_id, custom_msg, expression)
        return "Error: Calculator not initialized"
    
    def _on_button_clicked(self, event):
        """按钮点击事件处理"""
        logger.info(f"[INFO] 按钮点击: {event}")
        
        if event.button_id in self._button_callbacks:
            callback = self._button_callbacks[event.button_id]
            try:
                callback(event)
            except Exception as e:
                logger.error(f"[ERROR] 按钮回调失败: {e}")
    
    def register_button_callback(self, button_id, callback):
        """注册按钮点击回调
        
        Args:
            button_id: 按钮 ID（字符串，如 'btn-red'）
            callback: 回调函数，接收 MiniblinkButtonEvent 对象
        """
        self._button_callbacks[button_id] = callback
        logger.info(f"[INFO] 已注册按钮回调: {button_id}")


class MiniblinkButtonEvent:
    def __init__(self, button_id, hwnd, event_type, data=None):
        self.button_id = button_id
        self.hwnd = hwnd
        self.event_type = event_type
        self.data = data
    
    def __repr__(self):
        return f"<ButtonEvent type={self.event_type} id={self.button_id}>"
