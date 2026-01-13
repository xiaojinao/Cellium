# -*- coding: utf-8 -*-
"""
核心模块
按职责分组的子模块：
- bus: 事件总线（EventBus、事件类型、事件模型）
- window: 窗口管理（MainWindow）
- bridge: MiniBlink 通信桥接
- handler: 消息处理器
- util: 工具类（多进程管理）
"""

from .window.main_window import MainWindow
from .bridge.miniblink_bridge import MiniBlinkBridge
from .handler.message_handler import MessageHandler, MiniblinkButtonEvent
from .bus.event_bus import event_bus, EventBus
from .bus.events import EventType
from .bus.event_models import BaseEvent
from .util.mp_manager import (
    MultiprocessManager,
    get_multiprocess_manager,
    run_in_process,
    run_in_process_async
)
from .di.container import (
    DIContainer,
    get_container,
    inject,
    injected,
    AutoInjectMeta,
    setup_di_container
)

__all__ = [
    'MainWindow',
    'MiniBlinkBridge',
    'MessageHandler',
    'MiniblinkButtonEvent',
    'event_bus',
    'EventBus',
    'EventType',
    'BaseEvent',
    'MultiprocessManager',
    'get_multiprocess_manager',
    'run_in_process',
    'run_in_process_async',
    'DIContainer',
    'get_container',
    'inject',
    'injected',
    'AutoInjectMeta',
    'setup_di_container'
]
