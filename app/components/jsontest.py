# -*- coding: utf-8 -*-
"""
测试混合模式组件

演示：
1. 简单字符串参数处理
2. JSON 对象参数自动解析
3. JSON 数组参数自动解析
"""

import json
import logging
from app.core.interface.base_cell import BaseCell

logger = logging.getLogger(__name__)


class JsonTest(BaseCell):
    """JSON 混合模式测试组件"""
    
    def _cmd_echo(self, text: str) -> str:
        """简单字符串参数"""
        return f"Echo: {text}"
    
    def _cmd_greet(self, data: dict) -> str:
        """JSON 对象参数（自动解析）"""
        name = data.get("name", "Unknown")
        lang = data.get("language", "en")
        if lang == "zh":
            return f"你好，{name}！"
        elif lang == "de":
            return f"Hallo, {name}!"
        return f"Hello, {name}!"
    
    def _cmd_batch(self, items: list) -> str:
        """JSON 数组参数（自动解析）"""
        count = len(items)
        return f"收到 {count} 个项目: {', '.join(str(i) for i in items)}"
    
    def _cmd_complex(self, data: dict) -> str:
        """复杂 JSON 结构"""
        result = {
            "status": "success",
            "user": data.get("user", {}),
            "tags": data.get("tags", []),
            "metadata": data.get("metadata", {})
        }
        return json.dumps(result, ensure_ascii=False)
