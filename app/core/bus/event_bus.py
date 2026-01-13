# -*- coding: utf-8 -*-
"""
事件总线模块
提供发布-订阅模式的事件管理
支持同步和异步事件处理
"""

import asyncio
import inspect
import logging
from typing import Callable, Dict, List, Any, Optional, Type
from functools import wraps
from .events import EventType
from .event_models import BaseEvent

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_classes: Dict[str, Type[BaseEvent]] = {}
    
    def register_event_class(self, event_type: EventType, event_class: Type[BaseEvent]):
        """注册事件类
        
        Args:
            event_type: 事件类型
            event_class: 事件类
        """
        self._event_classes[str(event_type)] = event_class
        logger.info(f"已注册事件类: {event_type} -> {event_class.__name__}")
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 处理函数，接收 BaseEvent 对象
        """
        event_name = str(event_type)
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)
        logger.debug(f"[EVENT] 已订阅事件: {event_type} -> {handler.__name__}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """取消订阅事件
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        event_name = str(event_type)
        if event_name in self._subscribers:
            if handler in self._subscribers[event_name]:
                self._subscribers[event_name].remove(handler)
                logger.debug(f"已取消订阅事件: {event_type}")
    
    def publish(self, event_type: EventType, *args, **kwargs):
        """发布事件（同步）
        
        Args:
            event_type: 事件类型
            *args: 位置参数（兼容旧版）
            **kwargs: 关键字参数（兼容旧版）
            
        Returns:
            Any: 最后一个处理器的返回值
        """
        event_name = str(event_type)
        
        # 尝试创建事件对象
        event = None
        if event_name in self._event_classes:
            try:
                event_class = self._event_classes[event_name]
                if args and isinstance(args[0], BaseEvent):
                    event = args[0]
                else:
                    event = event_class(*args, **kwargs)
            except Exception as e:
                logger.warning(f"[WARNING] 创建事件对象失败: {e}")
        
        result = None
        if event_name in self._subscribers:
            for handler in self._subscribers[event_name]:
                try:
                    if inspect.iscoroutinefunction(handler):
                        # 异步处理器：在当前事件循环中调度
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.create_task(handler(event))
                            else:
                                loop.run_until_complete(handler(event))
                        except RuntimeError:
                            logger.warning(f"异步处理器需要事件循环: {handler.__name__}")
                    else:
                        # 同步处理器：直接调用
                        if event:
                            result = handler(event)
                        else:
                            result = handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[ERROR] 事件处理器错误 [{event_type}]: {e}")
        return result
    
    async def publish_async(self, event_type: EventType, *args, **kwargs):
        """发布事件（异步）
        
        Args:
            event_type: 事件类型
            *args: 位置参数（兼容旧版）
            **kwargs: 关键字参数（兼容旧版）
            
        Returns:
            Any: 最后一个处理器的返回值
        """
        event_name = str(event_type)
        
        # 尝试创建事件对象
        event = None
        if event_name in self._event_classes:
            try:
                event_class = self._event_classes[event_name]
                if args and isinstance(args[0], BaseEvent):
                    event = args[0]
                else:
                    event = event_class(*args, **kwargs)
            except Exception as e:
                logger.warning(f"[WARNING] 创建事件对象失败: {e}")
        
        result = None
        if event_name in self._subscribers:
            for handler in self._subscribers[event_name]:
                try:
                    if inspect.iscoroutinefunction(handler):
                        # 异步处理器：await
                        if event:
                            result = await handler(event)
                        else:
                            result = await handler(*args, **kwargs)
                    else:
                        # 同步处理器：直接调用
                        if event:
                            result = handler(event)
                        else:
                            result = handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[ERROR] 事件处理器错误 [{event_type}]: {e}")
        return result
    
    def has_subscribers(self, event_type: EventType) -> bool:
        """检查事件是否有订阅者
        
        Args:
            event_type: 事件类型
            
        Returns:
            bool: 是否有订阅者
        """
        event_name = str(event_type)
        return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    def clear(self):
        """清空所有订阅"""
        self._subscribers.clear()
        logger.info("已清空所有事件订阅")
    
    def get_subscribers_count(self, event_type: EventType) -> int:
        """获取事件的订阅者数量
        
        Args:
            event_type: 事件类型
            
        Returns:
            int: 订阅者数量
        """
        event_name = str(event_type)
        return len(self._subscribers.get(event_name, []))


def event_handler(event_type: EventType):
    """事件处理器装饰器
    
    使用示例:
        @event_handler(EventType.ALERT)
        def on_alert(event: AlertEvent):
            logger.info(f"收到 Alert: {event.message}")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, event: BaseEvent):
            return func(self, event)
        
        # 自动订阅事件
        event_bus.subscribe(event_type, wrapper)
        return wrapper
    return decorator


# 全局事件总线实例
event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线实例
    
    Returns:
        EventBus: 全局事件总线实例
    """
    return event_bus
