from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
import operator


@dataclass
class AlarmRule:
    id: str
    name: str
    description: str
    predicate: Callable[[dict], bool]


class AlarmEngine:
    def __init__(self):
        self.rules: dict[str, AlarmRule] = {}

    def add_rule(self, rule: AlarmRule):
        self.rules[rule.id] = rule

    def evaluate(self, measurement: dict) -> list[dict[str, Any]]:
        events = []
        for rule in self.rules.values():
            try:
                if rule.predicate(measurement):
                    events.append({"rule_id": rule.id, "name": rule.name, "measurement": measurement})
            except Exception as exc:  # regra malformada não deve quebrar o engine
                events.append({"rule_id": rule.id, "name": rule.name, "error": str(exc)})
        return events


def eval_operator(op: str, a: float, b: float) -> bool:
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }
    if op not in ops:
        raise ValueError(f"operador inválido: {op}")
    return bool(ops[op](a, b))

