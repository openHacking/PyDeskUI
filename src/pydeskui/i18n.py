"""Explicit translation contexts. Never changes the process locale."""

import gettext
from collections.abc import Callable
from importlib.resources import files


class TranslationContext:
    """Translate library-owned labels, with English fallback."""

    def __init__(self, locale: str = "en", translations=None):
        self._listeners: set[Callable[[], None]] = set()
        self._custom = translations
        self.locale = "en"
        self._catalog: gettext.NullTranslations = gettext.NullTranslations()
        self.configure(locale=locale)

    def configure(self, *, locale: str) -> None:
        self.locale = locale.replace("-", "_")
        self._catalog = self._custom or gettext.NullTranslations()
        if self._custom is None:
            for candidate in dict.fromkeys((self.locale, self.locale.split("_")[0], "en")):
                resource = files("pydeskui").joinpath(
                    "locales", candidate, "LC_MESSAGES", "pydeskui.mo"
                )
                if resource.is_file():
                    with resource.open("rb") as stream:
                        self._catalog = gettext.GNUTranslations(stream)
                    break
        for listener in tuple(self._listeners):
            listener()

    def gettext(self, message: str) -> str:
        return self._catalog.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        return self._catalog.ngettext(singular, plural, n)
