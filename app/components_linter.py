# -*- coding: utf-8 -*-
"""
组件代码审查工具
检查 app/components 目录下的组件是否符合 ICell 接口规范
"""

import ast
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))


class ComponentLinter:
    """组件代码审查器"""

    def __init__(self, components_dir: str = None):
        self.components_dir = components_dir or str(
            Path(__file__).parent / "components"
        )
        self.results: List[Dict] = []
        self.cell_names: Dict[str, str] = {}  # cell_name -> filename

    def check_all(self) -> Tuple[int, int]:
        """检查所有组件

        Returns:
            Tuple[通过数, 失败数]
        """
        passed = 0
        failed = 0

        for file_path in Path(self.components_dir).glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            result = self._check_file(file_path)
            self.results.append(result)

            if result["status"] == "pass":
                passed += 1
            else:
                failed += 1

        self._check_duplicate_cell_names()

        return passed, failed

    def _check_duplicate_cell_names(self):
        """检查跨文件的 cell_name 重复问题"""
        cell_names: Dict[str, List[str]] = {}

        for result in self.results:
            if 'cell_name_values' in result:
                for cell_name, class_name in result['cell_name_values']:
                    if cell_name not in cell_names:
                        cell_names[cell_name] = []
                    cell_names[cell_name].append(f"{result['file']}.{class_name}")

        for cell_name, locations in cell_names.items():
            if len(locations) > 1:
                for result in self.results:
                    if 'cell_name_values' in result:
                        for cn, class_name in result['cell_name_values']:
                            if cn == cell_name:
                                if '重复 cell_name' not in str(result['warnings']):
                                    result["warnings"].append(
                                        f"cell_name '{cell_name}' 在多个组件中重复: {locations}"
                                    )

    def _check_file(self, file_path: Path) -> Dict:
        """检查单个文件"""
        result = {
            "file": file_path.name,
            "status": "pass",
            "errors": [],
            "warnings": [],
            "info": [],
            "cell_name_values": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            has_icell_import = self._check_icell_import(tree)
            all_classes = self._find_all_classes(tree)
            icell_subclasses = self._find_icell_subclasses(tree)

            if not has_icell_import:
                result["warnings"].append("未检测到 ICell 导入，可能不是标准组件")

            if all_classes and not icell_subclasses:
                class_names = [c for c in all_classes.keys()]
                result["warnings"].append(f"文件包含类 {class_names}，但未继承 ICell")
                if not has_icell_import:
                    result["status"] = "fail"
            elif all_classes and icell_subclasses:
                all_class_names = set(all_classes.keys())
                icell_class_names = set(icell_subclasses.keys())
                non_icell_classes = all_class_names - icell_class_names
                if non_icell_classes:
                    result["warnings"].append(
                        f"类 {list(non_icell_classes)} 未继承 ICell，将不会被框架加载"
                    )

            if not icell_subclasses:
                if has_icell_import:
                    result["errors"].append("导入了 ICell 但未找到 ICell 子类")
                    result["status"] = "fail"
                return result

            for class_name, class_def in icell_subclasses.items():
                self._check_class(file_path, class_name, class_def, tree, result)

        except SyntaxError as e:
            result["errors"].append(f"语法错误: {e}")
            result["status"] = "fail"
        except Exception as e:
            result["errors"].append(f"检查失败: {e}")
            result["status"] = "fail"

        return result

    def _check_icell_import(self, tree: ast.AST) -> bool:
        """检查是否导入了 ICell"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "icell" in node.module.lower():
                    return True
        return False

    def _find_icell_subclasses(self, tree: ast.AST) -> Dict[str, ast.ClassDef]:
        """查找继承自 ICell 的类"""
        subclasses = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if hasattr(base, 'attr') and base.attr == 'ICell':
                            subclasses[node.name] = node
                    elif isinstance(base, ast.Name):
                        if base.id == 'ICell':
                            subclasses[node.name] = node
        return subclasses

    def _find_all_classes(self, tree: ast.AST) -> Dict[str, ast.ClassDef]:
        """查找所有类定义"""
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node
        return classes

    def _check_class(self, file_path: Path, class_name: str,
                     class_def: ast.ClassDef, tree: ast.AST, result: Dict):
        """检查单个类"""
        methods = {node.name: node for node in class_def.body
                   if isinstance(node, ast.FunctionDef)}

        if 'cell_name' not in methods:
            has_property = any(
                isinstance(node, ast.FunctionDef) and
                any(decorator.id == 'property'
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name))
                for node in class_def.body
                if isinstance(node, ast.FunctionDef) and node.name == 'cell_name'
            )
            if not has_property:
                result["warnings"].append(f"类 {class_name}: 未找到 'cell_name' 属性或 property")
        else:
            cell_name_value = self._get_cell_name_value(methods['cell_name'])
            if cell_name_value:
                result["cell_name_values"].append((cell_name_value, class_name))
                if not cell_name_value.islower():
                    result["warnings"].append(
                        f"类 {class_name}: cell_name '{cell_name_value}' 建议使用小写字母"
                    )

        if 'execute' not in methods:
            result["errors"].append(f"类 {class_name}: 缺少 'execute' 方法")
            result["status"] = "fail"
        else:
            self._check_execute_signature(class_name, methods['execute'], result)

        if 'get_commands' not in methods:
            result["warnings"].append(f"类 {class_name}: 未找到 'get_commands' 方法")
        else:
            self._check_get_commands_signature(class_name, methods['get_commands'], result)

        if 'cell_name' in methods:
            cell_name_method = methods['cell_name']
            if cell_name_method.returns:
                type_name = ast.unparse(cell_name_method.returns) if hasattr(ast, 'unparse') else ""
                if 'str' not in type_name.lower():
                    result["warnings"].append(f"类 {class_name}: 'cell_name' 应返回 str 类型")

        self._check_injected_properties(class_name, class_def, tree, result)
        self._check_decorators(class_name, class_def, result)

    def _get_cell_name_value(self, method: ast.FunctionDef) -> str:
        """尝试获取 cell_name 的返回值（静态分析）"""
        for node in ast.walk(method):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    return node.value.value
            elif isinstance(node, ast.Return) and isinstance(node.value, ast.Str):
                return node.value.s
        return ""

    def _check_execute_signature(self, class_name: str, method: ast.FunctionDef, result: Dict):
        """检查 execute 方法签名"""
        args = method.args
        if len(args.args) < 1:
            result["warnings"].append(
                f"类 {class_name}.execute: 缺少 command 参数"
            )

    def _check_get_commands_signature(self, class_name: str, method: ast.FunctionDef, result: Dict):
        """检查 get_commands 方法返回类型"""
        if method.returns:
            type_name = ast.unparse(method.returns) if hasattr(ast, 'unparse') else ""
            if 'dict' not in type_name.lower() and 'Dict' not in type_name:
                result["warnings"].append(
                    f"类 {class_name}.get_commands: 建议返回 Dict 类型"
                )

    def _check_injected_properties(self, class_name: str, class_def: ast.ClassDef, tree: ast.AST, result: Dict):
        """检查是否有 injected 声明的属性"""
        has_injected_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'container' in node.module.lower():
                    has_injected_import = True
                    break

        if has_injected_import:
            for node in class_def.body:
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    if hasattr(node.target, 'id'):
                        result["info"].append(
                            f"类 {class_name}: 检测到属性注入声明 ({node.target.id})"
                        )

    def _check_decorators(self, class_name: str, class_def: ast.ClassDef, result: Dict):
        """检查装饰器使用是否正确"""
        valid_decorators = {'event', 'event_once', 'event_pattern', 'emitter', 'event_wildcard', 'property'}

        for node in class_def.body:
            if not isinstance(node, ast.FunctionDef):
                continue

            method_name = node.name
            for decorator in node.decorator_list:
                decorator_info = self._get_decorator_info(decorator)
                if not decorator_info:
                    continue

                decorator_name = decorator_info['name']
                if decorator_name not in valid_decorators:
                    continue

                if decorator_name == 'event_wildcard':
                    if decorator_info['is_call'] and decorator_info['has_args']:
                        result["warnings"].append(
                            f"类 {class_name}.{method_name}: @event_wildcard 不应带参数"
                        )
                    continue

                if decorator_name == 'property':
                    continue

                if not decorator_info['is_call'] or not decorator_info['has_args']:
                    result["warnings"].append(
                        f"类 {class_name}.{method_name}: @{decorator_name}() 缺少事件名称参数"
                    )
                    continue

                arg = decorator_info['first_arg']
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    event_name = arg.value
                    if decorator_name == 'event_pattern' and '*' not in event_name:
                        result["warnings"].append(
                            f"类 {class_name}.{method_name}: @event_pattern 建议使用通配符，如 'data.*'"
                        )
                elif isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float, bool)):
                    result["errors"].append(
                        f"类 {class_name}.{method_name}: @{decorator_name}({arg.value}) 参数必须是字符串"
                    )
                elif isinstance(arg, ast.Str):
                    event_name = arg.s
                    if decorator_name == 'event_pattern' and '*' not in event_name:
                        result["warnings"].append(
                            f"类 {class_name}.{method_name}: @event_pattern 建议使用通配符，如 'data.*'"
                        )
                else:
                    result["warnings"].append(
                        f"类 {class_name}.{method_name}: @{decorator_name}() 参数格式可能不正确"
                    )

    def _get_decorator_info(self, decorator: ast.AST) -> Dict:
        """获取装饰器信息"""
        result = {
            'name': '',
            'is_call': False,
            'has_args': False,
            'first_arg': None
        }

        if isinstance(decorator, ast.Call):
            result['is_call'] = True
            result['has_args'] = len(decorator.args) > 0
            if decorator.args:
                result['first_arg'] = decorator.args[0]
            if isinstance(decorator.func, ast.Name):
                result['name'] = decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                result['name'] = decorator.func.attr
        elif isinstance(decorator, ast.Name):
            result['name'] = decorator.id

        return result

    def print_report(self):
        """打印审查报告"""
        print("=" * 60)
        print("组件代码审查报告")
        print("=" * 60)

        passed, failed = 0, 0

        for result in self.results:
            status_icon = "✅" if result["status"] == "pass" else "❌"
            print(f"\n{status_icon} {result['file']}")

            for error in result["errors"]:
                print(f"   [错误] {error}")

            for warning in result["warnings"]:
                print(f"   [警告] {warning}")

            for info in result["info"]:
                print(f"   [信息] {info}")

            if result["status"] == "pass":
                passed += 1
            else:
                failed += 1

        print("\n" + "=" * 60)
        print(f"总计: {passed + failed} 个组件 | ✅ 通过: {passed} | ❌ 失败: {failed}")
        print("=" * 60)

        return failed == 0


def main():
    """主函数"""
    linter = ComponentLinter()
    passed, failed = linter.check_all()
    success = linter.print_report()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
