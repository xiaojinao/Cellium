# -*- coding: utf-8 -*-
"""
Miniblink 浏览器 - 主窗口
"""

import ctypes
import logging
import os
import pathlib
import sys
import time
import threading
from ctypes import wintypes, byref

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

user32.SetLayeredWindowAttributes.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_ubyte, ctypes.c_uint]
user32.SetLayeredWindowAttributes.restype = ctypes.c_bool

LWA_ALPHA = 0x00000002
LWA_COLORKEY = 0x00000001

from ..bridge.miniblink_bridge import MiniBlinkBridge
from ..bus.event_bus import event_bus
from ..bus.events import EventType
from ..bus.event_models import FadeOutEvent
from ..handler.message_handler import MessageHandler, MiniblinkButtonEvent
from ..di.container import get_container

WM_COMMAND = 0x0111
WM_CLOSE = 0x10
WM_SYSCOMMAND = 0x112
SC_MINIMIZE = 0xF020
SC_MAXIMIZE = 0xF030
SC_RESTORE = 0xF120
SC_CLOSE = 0xF060

BN_CLICKED = 0

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("showCmd", ctypes.c_uint),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT),
    ]

def _get_project_root():
    """获取项目根目录（相对于程序入口文件）"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return pathlib.Path(sys._MEIPASS)
    entry_point = sys.argv[0] if sys.argv[0] else __file__
    return pathlib.Path(entry_point).resolve().parent


class MainWindow:

    def __init__(self):
        self.project_root = _get_project_root()
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.dll_dir = str(self.project_root / "dll")
            self.font_dir = str(self.project_root / "font")
            self.dll_path = str(self.project_root / "dll" / "mb132_x64.dll")
            self.html_dir = str(self.project_root / "html")
            self.html_path = str(self.project_root / "html" / "index.html")
        else:
            self.dll_dir = str(self.project_root / "dll")
            self.dll_path = str(self.project_root / "dll" / "mb132_x64.dll")
            self.font_dir = str(self.project_root / "font")
            self.html_dir = str(self.project_root / "html")
            self.html_path = str(self.project_root / "html" / "index.html")
        self.lib = None
        self.webview = None
        self.hwnd = None
        self.running = True
        self.title = "Python MiniBlink"
        
        self._polling_active = False
        self._polling_thread = None
        self._last_clicked_id = None
        self._last_check_time = 0
        
        self._wnd_proc = None
        self._wnd_class = None
        
        self.bridge = None
        self.app_icon = None
        
        self.calculator = None
        self.message_handler = None
    
    def _get_component(self, component_type):
        """从 DI 容器获取组件
        
        Args:
            component_type: 组件类型
            
        Returns:
            组件实例，如果未注册返回 None
        """
        try:
            container = get_container()
            if container.has(component_type):
                return container.resolve(component_type)
        except Exception as e:
            logger.warning(f"获取组件失败 {component_type.__name__}: {e}")
        return None
    
    def load_window_icon(self):
        """加载并设置窗口图标"""
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(self.dll_dir, "app_icon.ico")
            else:
                icon_path = os.path.join(self.project_root, "app_icon.ico")
            
            if os.path.exists(icon_path):
                self.app_icon = user32.LoadImageW(None, icon_path, 1, 32, 32, 16)
                if self.app_icon:
                    user32.SendMessageW(self.hwnd, 0x80, 1, self.app_icon)
                    user32.SendMessageW(self.hwnd, 0x80, 0, self.app_icon)
                    logger.info(f"窗口图标已设置: {icon_path}")
                else:
                    logger.warning(f"加载图标失败，错误码: {kernel32.GetLastError()}")
            else:
                logger.warning(f"图标文件不存在: {icon_path}")
        except Exception as e:
            logger.error(f"设置窗口图标失败: {e}")
    
    def _window_procedure(self, hwnd, msg, wparam, lparam):
        """窗口过程 - 处理关闭消息"""
        if msg == WM_CLOSE:
            logger.info("收到 WM_CLOSE，停止应用程序...")
            self.fade_out(duration=300)
            self.running = False
            self.stop_polling()
            try:
                self.lib.mbDestroyWebWindow(self.webview)
            except:
                pass
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        
    def _init_dll_functions(self):
        functions = {
            'mbSetMbDllPath': ([wintypes.LPCWSTR], None),
            # 'mbSetMbMainDllPath': ([wintypes.LPCWSTR], None),
            'mbInit': ([ctypes.c_void_p], None),
            'mbCreateWebWindow': (
                [ctypes.c_int, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int],
                ctypes.c_void_p
            ),
            'mbDestroyWebWindow': ([ctypes.c_void_p], None),
            'mbShowWindow': ([ctypes.c_void_p, ctypes.c_bool], None),
            'mbMoveToCenter': ([ctypes.c_void_p], None),
            'mbGetHostHWND': ([ctypes.c_void_p], wintypes.HWND),
            'mbLoadHtmlWithBaseUrl': ([ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p], None),
            'mbOnAlertBox': ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], None),
            'mbOnNavigation': ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], None),
            'mbRunJS': ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, 
                        ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], None),
            'mbResponseQuery': ([ctypes.c_void_p, ctypes.c_int64, ctypes.c_int, ctypes.c_char_p], None),
            'mbOnJsQuery': ([ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p], None),
        }
        
        for name, (argtypes, restype) in functions.items():
            try:
                func = getattr(self.lib, name)
                func.argtypes = argtypes
                if restype:
                    func.restype = restype
            except AttributeError:
                pass
    
    def load_dll(self):
        if not os.path.exists(self.dll_path):
            logger.error(f"未找到 DLL: {self.dll_path}")
            return False
        
        try:
            self.lib = ctypes.WinDLL(self.dll_path)
            self._init_dll_functions()
            logger.info(f"DLL 已加载: {self.dll_path}")
            return True
        except Exception as e:
            logger.error(f"DLL 加载失败: {e}")
            return False
    
    def init_engine(self):
        try:
            mbInit = self.lib.mbInit
            mbInit.argtypes = [ctypes.c_void_p]
            mbInit(None)
            
            logger.info("引擎已初始化")
            return True
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_window(self):
        try:
            self.webview = self.lib.mbCreateWebWindow(
                0, None, 100, 100, 1024, 768
            )
            if not self.webview:
                logger.error("[ERROR] 创建窗口失败")
                return False
            
            self.hwnd = self.lib.mbGetHostHWND(self.webview)
            
            if self.hwnd:
                user32.SetWindowTextW(self.hwnd, "Python MiniBlink")
                
                GWL_EXSTYLE = -20
                GWL_HWNDPARENT = -8
                WS_EX_APPWINDOW = 0x00040000
                WS_EX_TOOLWINDOW = 0x00000080
                WS_EX_LAYERED = 0x00080000
                
                current_style = user32.GetWindowLongPtrW(self.hwnd, GWL_EXSTYLE)
                current_style &= ~WS_EX_TOOLWINDOW
                current_style |= WS_EX_APPWINDOW
                current_style |= WS_EX_LAYERED
                user32.SetWindowLongPtrW(self.hwnd, GWL_EXSTYLE, current_style)
                
                owner = user32.GetWindowLongPtrW(self.hwnd, GWL_HWNDPARENT)
                if owner:
                    user32.SetWindowLongPtrW(self.hwnd, GWL_HWNDPARENT, None)
                
                shell32 = ctypes.windll.shell32
                try:
                    shell32.SetCurrentProcessExplicitAppUserModelIDW("PythonMiniBlink.Browser")
                    logger.info("AppUserModelID 已设置")
                except Exception as e:
                    logger.warning(f"设置 AppUserModelID 失败: {e}")
                
                user32.ShowWindow(self.hwnd, 1)
                user32.SetForegroundWindow(self.hwnd)
            
            logger.info(f"窗口已创建: {self.hwnd}")
            return True
        except Exception as e:
            logger.error(f"创建窗口失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _handle_calc_result(self, result):
        """处理计算结果"""
        if self.calculator:
            self.calculator.handle_calc_result(result)
    
    def fade_out(self, duration=300):
        """淡出动画效果
        
        Args:
            duration: 动画持续时间（毫秒）
        """
        if not self.hwnd:
            return
        
        steps = 20
        step_duration = duration / steps
        
        for i in range(steps):
            alpha = 255 - int((255 / steps) * (i + 1))
            if alpha < 0:
                alpha = 0
            
            user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
            time.sleep(step_duration / 1000.0)
        
        logger.info("[INFO] 淡出动画完成")
    
    def _on_fade_out(self, event: FadeOutEvent):
        """处理淡出事件"""
        logger.info("[INFO] 收到淡出事件")
        self.fade_out(duration=300)
        self.running = False
        self.stop_polling()
        try:
            self.lib.mbDestroyWebWindow(self.webview)
        except:
            pass
        user32.PostQuitMessage(0)
    
    def register_button_callback(self, button_id, callback):
        """注册按钮点击回调
        
        Args:
            button_id: 按钮 ID（字符串，如 'btn-red'）
            callback: 回调函数，接收 MiniblinkButtonEvent 对象
        """
        if self.message_handler:
            self.message_handler.register_button_callback(button_id, callback)
        else:
            logger.error("MessageHandler 未初始化，无法注册按钮回调")
    
    def _check_clicked_element(self):
        """轮询检查点击的元素 - 使用 JavaScript"""
        try:
            script = b"""
                (function() {
                    if (window.lastClickedElement) {
                        var result = window.lastClickedElement;
                        window.lastClickedElement = null;
                        return result;
                    }
                    return null;
                })()
            """
            
            mbRunJS = self.lib.mbRunJS
            mbRunJS.argtypes = [
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p,
                ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
            ]
            
            result = []
            def callback(webview, param, es, code, str_result, str_len):
                try:
                    if str_result:
                        result.append(ctypes.cast(str_result, ctypes.c_char_p).value.decode('utf-8'))
                except:
                    pass
            
            MB_RUNJS_CALLBACK = ctypes.WINFUNCTYPE(
                None, ctypes.c_void_p, ctypes.c_void_p, 
                ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int
            )
            
            cb = MB_RUNJS_CALLBACK(callback)
            mbRunJS(self.webview, None, script, True, cb, None, None)
            
            if result and result[0] and result[0] != "null":
                element_id = result[0]
                if element_id != self._last_clicked_id:
                    self._last_clicked_id = element_id
                    event = MiniblinkButtonEvent(
                        button_id=element_id,
                        hwnd=self.hwnd,
                        event_type="click"
                    )
                    if self.message_handler:
                        self.message_handler._on_button_clicked(event)
                    
        except Exception as e:
            pass
    
    def _polling_worker(self):
        """轮询工作线程"""
        while self._polling_active and self.running:
            try:
                self._check_clicked_element()
            except:
                pass
            time.sleep(0.1)
    
    def start_polling(self):
        """开始轮询点击事件"""
        self._polling_active = True
        self._polling_thread = threading.Thread(target=self._polling_worker)
        self._polling_thread.daemon = True
        self._polling_thread.start()
        logger.info("开始点击轮询")
    
    def stop_polling(self):
        """停止轮询"""
        self._polling_active = False
        if self._polling_thread:
            self._polling_thread.join(timeout=1)
        logger.info("停止点击轮询")
    
    def load_html_with_buttons(self):
        """加载包含计算器和标题栏的 HTML 页面 - Google 风格"""
        try:
            with open(self.html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            logger.info("HTML 按钮已加载")
        except Exception as e:
            logger.error(f"加载 HTML 文件失败: {e}")
            return False
        
        try:
            self.lib.mbLoadHtmlWithBaseUrl(self.webview, html.encode('utf-8'), b"about:blank")
            return True
        except Exception as e:
            logger.error(f"加载 HTML 到 MiniBlink 失败: {e}")
            return False
    
    def run_message_loop(self):
        logger.info("启动消息循环...")
        try:
            msg = wintypes.MSG()
            while self.running:
                ret = user32.GetMessageW(byref(msg), None, 0, 0)
                if ret == 0:
                    break
                elif ret == -1:
                    logger.error("GetMessageW 错误")
                    break
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
                
                if self.hwnd:
                    if not user32.IsWindow(self.hwnd):
                        logger.info("窗口已关闭，退出...")
                        break
        except Exception as e:
            logger.error(f"消息循环错误: {e}")
        logger.info("消息循环已退出")
    
    def remove_titlebar(self):
        if not self.hwnd:
            return
        
        try:
            GWL_STYLE = -16
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            
            current_style = user32.GetWindowLongPtrW(self.hwnd, GWL_STYLE)
            new_style = current_style & ~WS_CAPTION & ~WS_THICKFRAME
            user32.SetWindowLongPtrW(self.hwnd, GWL_STYLE, new_style)
            
            SWP_FRAMECHANGED = 0x0020
            user32.SetWindowPos(self.hwnd, None, 0, 0, 0, 0,
                              SWP_FRAMECHANGED | 0x0010 | 0x0004 | 0x0001 | 0x0002)
            
            user32.ShowWindow(self.hwnd, 3)
            logger.info("标题栏已移除")
        except Exception as e:
            logger.error(f"移除标题栏失败: {e}")
    
    def run(self):
        
        if not self.load_dll():
            return
        
        if not self.init_engine():
            return
        
        if not self.create_window():
            return
        
        self.load_window_icon()
        
        # 初始化桥接模块
        self.bridge = MiniBlinkBridge(self)
        
        # 初始化计算器组件（从 DI 容器获取已配置的组件）
        from app.components import Calculator
        self.calculator = self._get_component(Calculator)
        if self.calculator:
            self.calculator.webview = self.webview
            self.calculator.lib = self.lib
            self.calculator.bridge = self.bridge
            logger.info(f"[INFO] 已从 DI 容器获取 Calculator 组件")
        else:
            logger.warning(f"[WARNING] Calculator 未在配置中注册，将创建新实例")
            self.calculator = Calculator(self.webview, self.lib)
        
        # 初始化消息处理器组件
        self.message_handler = MessageHandler(self.hwnd, self.calculator)
        
        # 订阅事件
        event_bus.subscribe(EventType.FADE_OUT, self._on_fade_out)
        
        # 设置所有回调
        self.bridge.setup_all_callbacks()
        
        self.load_html_with_buttons()
        self.remove_titlebar()
        
        try:
            self.lib.mbShowWindow(self.webview, True)
            self.lib.mbMoveToCenter(self.webview)
        except Exception as e:
            logger.error(f"显示窗口失败: {e}")
        
        logger.info("浏览器就绪! 点击按钮查看 Python 捕获的事件")
        
        self.start_polling()
        self.run_message_loop()
        self.stop_polling()
