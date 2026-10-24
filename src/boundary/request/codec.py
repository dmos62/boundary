"""Versioned pre-change request input."""

import json
from pathlib import Path
from typing import TextIO

from boundary.pre_change.model import ChangeWriteSet, TaskWriteSet, WriteSetError

REQUEST_SCHEMA = "boundary.pre-change-request/v1"


def read_request(source: str, stdin: TextIO) -> tuple[ChangeWriteSet, tuple[str, ...]]:
    try:
        raw = stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise WriteSetError(f"invalid pre-change request: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != REQUEST_SCHEMA:
        raise WriteSetError(f"request schema must be {REQUEST_SCHEMA}")
    if set(value) != {"schema", "changeId", "tasks", "selectedTaskIds"}:
        raise WriteSetError("request fields must be schema, changeId, tasks, selectedTaskIds")
    tasks = value["tasks"]
    selected = value["selectedTaskIds"]
    if not isinstance(tasks, list) or not isinstance(selected, list):
        raise WriteSetError("tasks and selectedTaskIds must be arrays")
    projected = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict) or set(task) != {"id", "writes"} or not isinstance(task["writes"], list):
            raise WriteSetError(f"task {index} must contain id and writes")
        projected.append(TaskWriteSet(index, task["id"], None, tuple(task["writes"])))
    change = ChangeWriteSet(value["changeId"], tuple(projected))
    if any(not isinstance(item, str) for item in selected):
        raise WriteSetError("selectedTaskIds must contain strings")
    chosen = tuple(selected)
    change.select_tasks(chosen)
    return change, chosen
