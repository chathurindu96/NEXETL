"""Small allow-listed expression and predicate evaluator; never calls eval()."""

from __future__ import annotations

import ast
import operator
from datetime import date, datetime, timedelta
from typing import Any


class ExpressionError(ValueError): pass


FUNCTIONS={
    "concat":lambda *values:"".join("" if value is None else str(value) for value in values),
    "upper":lambda value:None if value is None else str(value).upper(),
    "lower":lambda value:None if value is None else str(value).lower(),
    "trim":lambda value:None if value is None else str(value).strip(),
    "coalesce":lambda *values:next((value for value in values if value is not None),None),
    "substring":lambda value,start,length=None:str(value)[int(start):int(start)+int(length)] if length is not None else str(value)[int(start):],
    "date_add_days":lambda value,days:(_date(value)+timedelta(days=int(days))).isoformat(),
}
BIN={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod}


def _date(value): return value if isinstance(value,(date,datetime)) else date.fromisoformat(str(value))


def evaluate(expression: str,row: dict[str,Any])->Any:
    try: tree=ast.parse(expression,mode="eval")
    except SyntaxError as error: raise ExpressionError("The expression syntax is invalid.") from error
    def visit(node):
        if isinstance(node,ast.Expression): return visit(node.body)
        if isinstance(node,ast.Constant): return node.value
        if isinstance(node,ast.Name): return row.get(node.id)
        if isinstance(node,ast.BinOp) and type(node.op) in BIN: return BIN[type(node.op)](visit(node.left),visit(node.right))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)): return -visit(node.operand) if isinstance(node.op,ast.USub) else +visit(node.operand)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FUNCTIONS and not node.keywords: return FUNCTIONS[node.func.id](*(visit(arg) for arg in node.args))
        raise ExpressionError("The expression contains an unsupported operation.")
    return visit(tree)


def predicate(value: dict[str,Any],row: dict[str,Any])->bool:
    if "conditions" in value:
        operation=str(value.get("logic","AND")).upper(); results=[predicate(item,row) for item in value.get("conditions",[]) if isinstance(item,dict)]; return all(results) if operation=="AND" else any(results)
    column=value.get("column"); operation=str(value.get("operator","=")).lower(); expected=value.get("value"); actual=row.get(str(column))
    if operation=="is null": return actual is None
    if operation=="is not null": return actual is not None
    if operation=="in": return actual in (expected if isinstance(expected,list) else [expected])
    if operation=="contains": return str(expected) in str(actual)
    if operation=="starts with": return str(actual).startswith(str(expected))
    if operation=="ends with": return str(actual).endswith(str(expected))
    operations={"=":operator.eq,"!=":operator.ne,">":operator.gt,">=":operator.ge,"<":operator.lt,"<=":operator.le}
    if operation not in operations: raise ExpressionError("The predicate operator is unsupported.")
    return operations[operation](actual,expected)
