"""A no-Ray in-process Flower Grid for tiny demos/tests."""
from __future__ import annotations

from collections.abc import Iterable

from flwr.app import Context, Message, RecordDict
from flwr.serverapp.grid import Grid
from flwr.supercore.run import Run
from flwr.supercore.task_identity import TaskIdentity


class LocalGrid(Grid):
    """Synchronous Grid dispatching Messages to local ClientApp objects."""

    def __init__(self, apps: dict[int, object], contexts: dict[int, Context]) -> None:
        self.apps = apps
        self.contexts = contexts
        self._run = None
        self.killed: set[int] = set()

    def set_run(self, run: Run) -> None:
        self._run = run

    @property
    def run(self) -> Run:
        return self._run  # type: ignore[return-value]

    def create_message(self, content: RecordDict, message_type: str, dst_node_id: int, group_id: str, ttl: float | None = None) -> Message:
        TaskIdentity.run_id = 1
        TaskIdentity.node_id = 0
        TaskIdentity.task_id = 0
        return Message(content=content, dst_node_id=dst_node_id, message_type=message_type, group_id=group_id, ttl=ttl)

    def get_node_ids(self) -> Iterable[int]:
        return [node for node in sorted(self.apps) if node not in self.killed]

    def push_messages(self, messages: Iterable[Message]) -> Iterable[str]:
        self._pending = list(messages)
        return [str(i) for i, _ in enumerate(self._pending)]

    def pull_messages(self, message_ids: Iterable[str]) -> Iterable[Message]:
        return self.send_and_receive([self._pending[int(i)] for i in message_ids])

    def send_and_receive(self, messages: Iterable[Message], *, timeout: float | None = None) -> Iterable[Message]:  # noqa: ARG002
        replies = []
        for msg in messages:
            node_id = msg.metadata.dst_node_id
            if node_id in self.killed:
                continue
            app = self.apps[node_id]
            replies.append(app(msg, self.contexts[node_id]))
        return replies

    def kill_node(self, node_id: int) -> None:
        self.killed.add(node_id)
