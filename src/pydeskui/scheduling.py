"""Tk-thread scheduling whose callbacks cannot outlive their owner."""

import tkinter as tk
from collections.abc import Callable


class CancelHandle:
    """An idempotent cancellation handle; use only on the owning Tk thread."""

    def __init__(self, cancel: Callable[[], None]):
        self._cancel = cancel

    def cancel(self) -> None:
        callback, self._cancel = self._cancel, lambda: None
        callback()


class Scheduler:
    """Schedule callbacks on an explicit widget and cancel them on destruction."""

    def __init__(self, owner: tk.Misc):
        self.owner = owner
        self._pending: set[str] = set()
        self._closed = False
        self._binding: str | None = owner.bind("<Destroy>", self._destroyed, add="+")

    def _destroyed(self, event: tk.Event) -> None:
        if event.widget is self.owner:
            self.close()

    def call_later(self, delay_ms: int, callback: Callable[[], None]) -> CancelHandle:
        if self._closed:
            raise RuntimeError("Scheduler is closed")
        if not isinstance(delay_ms, int) or delay_ms < 0:
            raise ValueError("delay_ms must be a nonnegative integer")

        def run() -> None:
            self._pending.discard(identifier)
            if not self._closed:
                callback()

        identifier = self.owner.after(delay_ms, run)
        self._pending.add(identifier)

        def cancel() -> None:
            if identifier in self._pending:
                self._pending.remove(identifier)
                self.owner.after_cancel(identifier)

        return CancelHandle(cancel)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for identifier in tuple(self._pending):
            self.owner.after_cancel(identifier)
        self._pending.clear()
        if self._binding:
            self.owner.unbind("<Destroy>", self._binding)
            self._binding = None
