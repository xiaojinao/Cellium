# -*- coding: utf-8 -*-
"""
应用程序主入口
"""

from app.core import MainWindow, setup_di_container
from app.core.util import load_components
from app.core.di.container import get_container
from app.core.util.logger import setup_logger
import sys
import io

def main():
    # 日志级别: DEBUG, INFO, WARNING, ERROR
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
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
