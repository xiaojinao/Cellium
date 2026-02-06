# -*- coding: utf-8 -*-
"""
消息处理器
处理来自 JavaScript 的消息和命令

支持统一命令格式：window.mbQuery(0, '组件名:命令:参数', callback)
例如：
    mbQuery(0, 'greeter:greet:你好', callback)
    mbQuery(0, 'calculator:calc:1+1', callback)

"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional
from ..bus.event_bus import event_bus
from ..bus.events import EventType
from ..bus.event_models import AlertEvent, JsQueryEvent
from ..handler.title_bar_handler import TitleBarHandler
from ..interface.icell import ICell
from ..util.components_loader import get_cell as get_cell_from_registry, register_cell as register_cell_to_global

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="cell-")


class MessageHandler:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._titlebar_handler = TitleBarHandler(hwnd)
        
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
            tuple: (组件名, 命令, 参数字符串)
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
    
    def _parse_args(self, args: str) -> Any:
        """参数解析
        
        自动识别 JSON 字符串：
        - 以 '{' 开头 -> 尝试解析为 dict
        - 以 '[' 开头 -> 尝试解析为 list
        - 其他情况 -> 返回原始字符串
        
        Args:
            args: 参数字符串
            
        Returns:
            解析后的参数（dict/list/str）
        """
        if not args:
            return args
        
        if args.startswith(('{', '[')):
            try:
                return json.loads(args)
            except json.JSONDecodeError:
                logger.debug(f"JSON 解析失败，保持原字符串: {args}")
                return args
        
        return args
    
    def _handle_cell_command(self, command: str, async_exec: bool = False) -> Any:
        """处理统一格式的组件命令
        
        格式：组件名:命令:参数
        
        特性：
        1. 自动解析 JSON 参数
        2. 支持异步执行（耗时操作）
        
        Args:
            command: 命令字符串
            async_exec: 是否异步执行（耗时操作设为 True）
            
        Returns:
            命令执行结果
        """
        cell_name, cmd, args_str = self._parse_cell_command(command)
        
        if not cell_name:
            logger.warning(f"无法解析命令: {command}")
            return "Error: Invalid command format"
        
        cell = self.get_cell(cell_name)
        if not cell:
            if cell_name == "titlebar":
                return self._handle_titlebar_command(cmd, args_str)
            logger.warning(f"组件不存在: {cell_name}")
            return f"Error: Cell '{cell_name}' not found"
        
        args = self._parse_args(args_str)
        
        logger.info(f"执行命令: {cell_name}:{cmd}:{args_str}")
        
        if async_exec:
            return self._execute_async(cell, cmd, args)
        
        try:
            return cell.execute(cmd, args)
        except Exception as e:
            logger.error(f"命令执行失败: {cell_name}:{cmd}, 错误: {e}")
            return f"Error: {str(e)}"
    
    def _execute_async(self, cell: ICell, cmd: str, args: Any) -> str:
        """异步执行组件命令（提交到线程池）"""
        def run():
            try:
                return cell.execute(cmd, args)
            except Exception as e:
                logger.error(f"异步命令执行失败: {cell.cell_name}:{cmd}, 错误: {e}")
                return f"Error: {str(e)}"
        
        future = _executor.submit(run)
        return "Task submitted to thread pool"
    
    def _handle_titlebar_command(self, cmd: str, args: str) -> str:
        """处理标题栏命令"""
        try:
            result = self._titlebar_handler.execute(cmd, args)
            if result and isinstance(result, str) and result.startswith("Error"):
                logger.warning(f"标题栏命令执行失败: {cmd}, {result}")
            return result if result else "OK"
        except Exception as e:
            logger.error(f"执行标题栏命令失败: {cmd}, 错误: {e}")
            return f"Error: {str(e)}"
    
    def _on_alert_message(self, event: AlertEvent):
        """处理 Alert 消息
        
        统一命令格式：组件名:命令:参数
        """
        msg_str = event.message
        if not msg_str:
            return
        
        if ':' not in msg_str:
            logger.warning(f"[WARN] 无法解析消息: {msg_str}")
            return
        
        result = self._handle_cell_command(msg_str)
        logger.info(f"[INFO] 执行结果: {result}")
    
    def _on_jsquery_message(self, event: JsQueryEvent):
        """处理 JsQuery 消息
        
        统一命令分发：只要包含冒号，就尝试按组件协议分发
        """
        msg_str = event.message
        
        if not msg_str or ':' not in msg_str:
            return None
        
        return self._handle_cell_command(msg_str)
    
    def _on_python_command(self, command):
        """处理来自 JavaScript 的命令
        
        统一命令格式：组件名:命令:参数
        """
        logger.info(f"[INFO] 收到命令: {command}")
        
        if ':' not in command:
            logger.warning(f"[WARN] 无法解析命令: {command}")
            return
        
        cell_name, cmd, args = self._parse_cell_command(command)
        if cell_name:
            cell = self.get_cell(cell_name)
            if cell:
                result = self._handle_cell_command(command)
                logger.info(f"[INFO] 执行结果: {result}")
            else:
                logger.warning(f"[WARN] 组件不存在: {cell_name}")
        else:
            logger.warning(f"[WARN] 无法解析命令格式: {command}")

