# -*- coding: utf-8 -*-
"""
MiniBlink 通信桥接模块
封装 Python 与 MiniBlink 之间的通信功能
"""

import ctypes
import logging
from ctypes import wintypes, byref
from ..bus.event_bus import event_bus
from ..bus.events import EventType
from ..bus.event_models import NavigationEvent, AlertEvent, JsQueryEvent

user32 = ctypes.windll.user32
logger = logging.getLogger(__name__)


class MbConsoleLevel:
    """MiniBlink 控制台日志级别"""
    MB_LEVEL_LOG = 1
    MB_LEVEL_WARNING = 2
    MB_LEVEL_ERROR = 3
    MB_LEVEL_DEBUG = 4
    MB_LEVEL_INFO = 5
    MB_LEVEL_REVOKED_ERROR = 6


class MiniBlinkBridge:
    def __init__(self, browser):
        self.browser = browser
        self.lib = browser.lib
        self.webview = browser.webview
        self.hwnd = browser.hwnd
        
        self._nav_callback = None
        self._alert_callback = None
        self._jsquery_callback = None
        self._console_callback = None
    
    def send_to_js(self, script):
        """发送 JavaScript 代码到页面执行
        
        Args:
            script: JavaScript 代码字符串
        """
        try:
            logger.debug(f"[BRIDGE] 发送JS: {script[:100]}")
            self.lib.mbRunJs(
                self.webview, None,
                script.encode('utf-8'),
                True, None, None, None
            )
        except Exception as e:
            logger.error(f"[ERROR] 发送 JS 失败: {e}")
            import traceback
            logger.error(f"[ERROR] 堆栈: {traceback.format_exc()}")
    
    def eval_js(self, expression):
        """在全局作用域执行 JS 表达式
        
        Args:
            expression: JS 表达式
        """
        try:
            script = f"try {{ {expression} }} catch(e) {{ console.error('JS Error:', e.message); }}"
            logger.debug(f"[BRIDGE] evalJS: {expression[:100]}")
            self.lib.mbRunJs(
                self.webview, None,
                script.encode('utf-8'),
                True, None, None, None
            )
        except Exception as e:
            logger.error(f"[ERROR] 执行 JS 失败: {e}")
    
    def set_element_value(self, element_id, value):
        """设置 HTML 元素的值
        
        Args:
            element_id: 元素 ID
            value: 要设置的值
        """
        script = f"document.getElementById('{element_id}').value = '{value}';"
        self.send_to_js(script)
    
    def get_element_value(self, element_id, callback):
        """获取 HTML 元素的值（异步）
        
        Args:
            element_id: 元素 ID
            callback: 回调函数，接收获取到的值
        """
        script = f"""
            (function() {{
                var elem = document.getElementById('{element_id}');
                return elem ? elem.value : null;
            }})()
        """
        
        def js_callback(webview, param, es, code, str_result, str_len):
            try:
                if str_result:
                    value = ctypes.cast(str_result, ctypes.c_char_p).value.decode('utf-8')
                    callback(value)
            except Exception as e:
                logger.error(f"[ERROR] 获取元素值失败: {e}")
        
        MB_RUNJS_CALLBACK = ctypes.WINFUNCTYPE(
            None, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int
        )
        
        cb = MB_RUNJS_CALLBACK(js_callback)
        self.lib.mbRunJS(self.webview, None, script.encode('utf-8'), True, cb, None, None)
    
    def _on_navigation_callback(self, webview, param, navigation_type, url):
        """导航回调"""
        try:
            url_str = ctypes.cast(url, ctypes.c_char_p).value.decode('utf-8') if url else ""
            logger.debug(f"[DEBUG] 导航: type={navigation_type}, url={url_str}")
            event = NavigationEvent(navigation_type, url_str)
            event_bus.publish(EventType.NAVIGATION, event)
        except Exception as e:
            logger.error(f"[ERROR] 导航回调错误: {e}")
        return True
    
    def _setup_navigation_callback(self):
        """设置导航回调"""
        try:
            MB_NAVIGATION_CALLBACK = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_char_p
            )
            
            self._nav_callback = MB_NAVIGATION_CALLBACK(self._on_navigation_callback)
            self.lib.mbOnNavigation(self.webview, self._nav_callback, None)
            logger.info("[INFO] 导航回调已设置")
            return True
        except Exception as e:
            logger.error(f"[ERROR] 设置导航回调失败: {e}")
            return False
    
    def _on_alert_callback(self, webview, msg):
        """Alert 回调"""
        try:
            msg_str = ctypes.cast(msg, ctypes.c_char_p).value.decode('utf-8') if msg else ""
            logger.debug(f"[DEBUG] 收到 Alert: {msg_str}")
            event = AlertEvent(msg_str)
            event_bus.publish(EventType.ALERT, event)
        except Exception as e:
            logger.error(f"[ERROR] Alert 回调错误: {e}")
    
    def _setup_alert_callback(self):
        """设置 Alert 回调"""
        try:
            MB_ALERT_CALLBACK = ctypes.WINFUNCTYPE(
                None,
                ctypes.c_void_p,
                ctypes.c_char_p
            )
            
            self._alert_callback = MB_ALERT_CALLBACK(self._on_alert_callback)
            self.lib.mbOnAlertBox(self.webview, self._alert_callback, None)
            logger.info("[INFO] Alert 回调已设置")
            return True
        except Exception as e:
            logger.error(f"[ERROR] 设置 Alert 回调失败: {e}")
            return False
    
    def _on_js_query(self, webview, param, es, query_id, custom_msg, msg):
        """JsQuery 回调"""
        try:
            msg_str = ctypes.cast(msg, ctypes.c_char_p).value.decode('utf-8') if msg else ""
            logger.debug(f"[DEBUG] 收到 JsQuery: {msg_str}")
            
            event = JsQueryEvent(webview, query_id, custom_msg, msg_str)
            result = event_bus.publish(EventType.JSQUERY, event)
            
            if result is not None:
                self.lib.mbResponseQuery(
                    self.webview,
                    query_id,
                    custom_msg,
                    result.encode('utf-8')
                )
            return 0
        except Exception as e:
            logger.error(f"[ERROR] JsQuery 回调错误: {e}")
        return 0
    
    def _setup_js_query_callback(self):
        """设置 JsQuery 回调"""
        try:
            MB_JSQUERY_CALLBACK = ctypes.WINFUNCTYPE(
                ctypes.c_int,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int64,
                ctypes.c_int,
                ctypes.c_char_p
            )
            
            self._jsquery_callback = MB_JSQUERY_CALLBACK(self._on_js_query)
            self.lib.mbOnJsQuery(self.webview, self._jsquery_callback, None)
            logger.info("[INFO] JsQuery 回调已设置")
            return True
        except Exception as e:
            logger.error(f"[ERROR] 设置 JsQuery 回调失败: {e}")
            return False
    
    def _on_console_callback(self, webview, param, level, message, source_name, source_line, stack_trace):
        """控制台回调"""
        try:
            level_names = {
                MbConsoleLevel.MB_LEVEL_LOG: "LOG",
                MbConsoleLevel.MB_LEVEL_WARNING: "WARNING",
                MbConsoleLevel.MB_LEVEL_ERROR: "ERROR",
                MbConsoleLevel.MB_LEVEL_DEBUG: "DEBUG",
                MbConsoleLevel.MB_LEVEL_INFO: "INFO",
                MbConsoleLevel.MB_LEVEL_REVOKED_ERROR: "REVOKED_ERROR"
            }
            
            msg_str = ctypes.cast(message, ctypes.c_char_p).value.decode('utf-8') if message else ""
            src_name = ctypes.cast(source_name, ctypes.c_char_p).value.decode('utf-8') if source_name else ""
            
            level_name = level_names.get(level, f"LEVEL_{level}")
            logger.debug(f"[CONSOLE][{level_name}] {msg_str} (file:{src_name}:{source_line})")
        except Exception as e:
            logger.error(f"[ERROR] 控制台回调错误: {e}")
    
    def _setup_console_callback(self):
        """设置控制台回调"""
        try:
            MB_CONSOLE_CALLBACK = ctypes.WINFUNCTYPE(
                None,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_uint,
                ctypes.c_char_p
            )
            
            self._console_callback = MB_CONSOLE_CALLBACK(self._on_console_callback)
            
            if hasattr(self.lib, 'mbOnConsole'):
                self.lib.mbOnConsole(self.webview, self._console_callback, None)
                logger.info("[INFO] 控制台回调已设置")
                return True
            else:
                logger.warn("[WARN] mbOnConsole 不可用，跳过")
                return False
        except Exception as e:
            logger.error(f"[ERROR] 设置控制台回调失败: {e}")
            return False
    
    def setup_all_callbacks(self):
        """设置所有回调"""
        self._setup_navigation_callback()
        self._setup_alert_callback()
        self._setup_js_query_callback()
        self._setup_console_callback()
