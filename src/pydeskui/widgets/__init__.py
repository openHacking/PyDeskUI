"""Supported reusable widgets."""

from .controls import Button, Entry, SearchEntry
from .form import FieldSpec, Form
from .views import DetailView, Dialog, Item, ItemList, ProgressView

__all__ = [
    "Button",
    "Entry",
    "SearchEntry",
    "FieldSpec",
    "Form",
    "DetailView",
    "Dialog",
    "Item",
    "ItemList",
    "ProgressView",
]

from .inputs import Checkbox, Combobox, RadioGroup, Select, Slider, Spinbox, Switch, Textarea
from .overlays import (
    Alert,
    ContextMenu,
    DropdownMenu,
    EmptyState,
    Popover,
    Sheet,
    Skeleton,
    Toast,
    Tooltip,
)
from .structure import (
    Badge,
    Card,
    Frame,
    Icon,
    Label,
    ScrollArea,
    Separator,
    Sidebar,
    SplitPane,
    Table,
    Tabs,
    Toolbar,
    Tree,
)

__all__ += [
    "Checkbox",
    "Combobox",
    "RadioGroup",
    "Select",
    "Slider",
    "Spinbox",
    "Switch",
    "Textarea",
    "Badge",
    "Card",
    "Frame",
    "Icon",
    "Label",
    "ScrollArea",
    "Separator",
    "Sidebar",
    "SplitPane",
    "Table",
    "Tabs",
    "Toolbar",
    "Tree",
    "Alert",
    "ContextMenu",
    "DropdownMenu",
    "EmptyState",
    "Popover",
    "Sheet",
    "Skeleton",
    "Toast",
    "Tooltip",
]
