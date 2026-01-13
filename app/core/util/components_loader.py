import importlib
import logging
import os
import pathlib
import sys
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None

from app.core.di.container import DIContainer
from app.core.interface.icell import ICell

logger = logging.getLogger(__name__)

_cell_registry: Dict[str, ICell] = {}


def get_all_cells() -> Dict[str, ICell]:
    """获取所有已注册的组件"""
    return _cell_registry


def register_cell(cell: ICell):
    """注册组件到全局注册表"""
    _cell_registry[cell.cell_name] = cell
    logger.info(f"组件已注册: {cell.cell_name}")


def get_cell(name: str) -> Optional[ICell]:
    """根据名称获取组件"""
    return _cell_registry.get(name)


def clear_registry():
    """清空注册表"""
    _cell_registry.clear()


def get_config_path() -> pathlib.Path:
    """获取配置文件路径"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = pathlib.Path(sys._MEIPASS)
    else:
        entry_point = sys.argv[0] if sys.argv[0] else __file__
        base_path = pathlib.Path(entry_point).resolve().parent
    
    config_path = base_path / "config" / "settings.yaml"
    return config_path


def load_component_config(config_path: pathlib.Path) -> Dict[str, Any]:
    """加载组件配置文件"""
    if not config_path.exists():
        logger.warning(f"配置文件不存在: {config_path}")
        return {"enabled_components": []}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if not yaml:
                logger.error("PyYAML 未安装，无法解析配置文件")
                return {"enabled_components": []}
            
            config = yaml.safe_load(content)
            return config or {"enabled_components": []}
            
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {"enabled_components": []}


def dynamic_import(module_path: str) -> Any:
    """动态导入模块"""
    parts = module_path.rsplit('.', 1)
    if len(parts) != 2:
        raise ValueError(f"无效的模块路径: {module_path}")
    
    module_name, class_name = parts
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def load_components(container: DIContainer, debug: bool = False) -> Dict[str, Any]:
    """根据配置文件加载组件
    
    支持 ICell 接口的组件会自动注册到全局组件注册表
    
    Args:
        container: DI 容器实例
        debug: 是否启用调试模式
        
    Returns:
        已加载组件的字典 {类名: 实例}
        同时填充全局组件注册表
    """
    if yaml is None:
        logger.warning("PyYAML 未安装，将不加载任何组件")
        return {}
    
    config_path = get_config_path()
    config = load_component_config(config_path)
    
    component_list = config.get("enabled_components", [])
    loaded_components = {}
    
    logger.info(f"开始加载组件，共 {len(component_list)} 个配置项")
    
    for component_path in component_list:
        try:
            component_class = dynamic_import(component_path)
            instance = component_class()
            component_name = component_class.__name__
            
            container.register(component_class, instance)
            loaded_components[component_name] = instance
            
            if isinstance(instance, ICell):
                register_cell(instance)
                logger.info(f"已加载组件: {component_name} (cell_name: {instance.cell_name})")
            else:
                logger.info(f"已加载组件: {component_name}")
                
        except ImportError as e:
            logger.error(f"组件导入失败 {component_path}: {e}")
        except AttributeError as e:
            logger.error(f"组件类不存在 {component_path}: {e}")
        except Exception as e:
            logger.error(f"组件加载异常 {component_path}: {e}")
    
    logger.info(f"组件加载完成，共加载 {len(loaded_components)} 个组件")
    return loaded_components
