# -*- coding: utf-8 -*-
"""
日志模块
提供统一的日志管理和格式化输出
"""

import logging
import sys
from typing import Optional

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

_loggers: dict = {}


def setup_logger(
    name: str = "app",
    level: str = "INFO",
    log_format: Optional[str] = None
) -> logging.Logger:
    """设置并获取日志器
    
    Args:
        name: 日志器名称
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_format: 日志格式
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    if name in _loggers:
        return _loggers[name]
    
    numeric_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    if log_format is None:
        log_format = "[%(levelname)s] %(name)s: %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    logger.propagate = False
    _loggers[name] = logger
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取已配置的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    if name not in _loggers:
        return setup_logger(name)
    return _loggers[name]


def log_exception(logger: logging.Logger, message: str, exc_info: bool = True):
    """记录异常信息
    
    Args:
        logger: 日志器
        message: 错误消息
        exc_info: 是否包含异常信息
    """
    if exc_info:
        logger.exception(message)
    else:
        logger.error(message)


def log_function_entry(logger: logging.Logger, func_name: str, args: tuple = None, kwargs: dict = None):
    """记录函数入口
    
    Args:
        logger: 日志器
        func_name: 函数名
        args: 位置参数
        kwargs: 关键字参数
    """
    extra_info = ""
    if args or kwargs:
        extra_info = f" with args={args}, kwargs={kwargs}"
    logger.debug(f"Entering function: {func_name}{extra_info}")


def log_function_exit(logger: logging.Logger, func_name: str, result=None):
    """记录函数出口
    
    Args:
        logger: 日志器
        func_name: 函数名
        result: 返回值
    """
    logger.debug(f"Exiting function: {func_name} -> {result}")


class LogMixin:
    """日志混入类
    
    为类提供日志功能
    
    Example:
        class MyClass(LogMixin):
            def do_something(self):
                self.logger.info("Doing something")
    """
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def timed_operation(logger: logging.Logger, operation_name: str):
    """计时操作装饰器
    
    Args:
        logger: 日志器
        operation_name: 操作名称
        
    Example:
        @timed_operation(logger, "database_query")
        def query_database():
            ...
    """
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting operation: {operation_name}")
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"Completed operation: {operation_name} in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Operation failed: {operation_name} after {elapsed:.2f}s - {e}")
                raise
        return wrapper
    return decorator
