"""Internal ownership helpers."""

from typing import Any, cast

from ..theme import resolve_theme


class Owned:
    def _own(self, master, theme):
        self.theme = resolve_theme(master, theme)
        self.theme._widgets.add(self)
        self.theme._register_toplevel(self)
        self._owned_binding = cast(Any, self).bind("<Destroy>", self._released, add="+")
        self.theme._apply_focus_visibility()

    def _released(self, event):
        if event.widget is self:
            self.theme._widgets.discard(self)
            self._cleanup()

    def _cleanup(self):
        pass

    def _refresh_theme(self):
        pass

    def _t(self, message):
        return self.theme.translator.gettext(message)
