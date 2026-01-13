# -*- coding: utf-8 -*-
"""
应用程序主入口
"""

from app.core import MainWindow, setup_di_container
from app.core.util import load_components
from app.core.di.container import get_container
from app.core.util.logger import setup_logger

def main():
    setup_logger("app", level="INFO")
    setup_di_container()
    container = get_container()
    load_components(container)
    window = MainWindow()
    window.run()
    from app.core.util.mp_manager import MultiprocessManager
    MultiprocessManager().shutdown()

if __name__ == "__main__":
    main()
