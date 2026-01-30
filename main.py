# -*- coding: utf-8 -*-
"""
应用程序主入口
"""
import sys
import io

from app.core import MainWindow, setup_di_container
from app.core.util import load_components
from app.core.di.container import get_container
from app.core.util.logger import setup_logger

def _ensure_utf8_encoding():
    for stream in (sys.stdout, sys.stderr):
        if stream.encoding.lower() != 'utf-8':
            setattr(sys, stream.name, io.TextIOWrapper(stream.buffer, encoding='utf-8'))

def main():
    _ensure_utf8_encoding()
    # 日志级别: DEBUG, INFO, WARNING, ERROR
    setup_logger("app", level="DEBUG")
    setup_di_container()
    container = get_container()
    load_components(container)
    window = MainWindow()
    window.run()
    from app.core.util.mp_manager import MultiprocessManager
    MultiprocessManager().shutdown()

if __name__ == "__main__":
    main()
