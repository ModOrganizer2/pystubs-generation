from __future__ import annotations

__version__ = "2.5.0"

from typing import List, Tuple, Union, overload

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets

class TaskDialog:
    def __init__(
        self: TaskDialog,
        parent: PyQt6.QtWidgets.QWidget = None,
        title: str = "",
        main: str = "",
        content: str = "",
        details: str = "",
        icon: PyQt6.QtWidgets.QMessageBox.Icon = PyQt6.QtWidgets.QMessageBox.Icon.NoIcon,
        buttons: List[TaskDialogButton] = [],
        remember: Union[str, Tuple[str, str]] = "",
    ): ...
    def addButton(self: TaskDialog, button: TaskDialogButton) -> TaskDialog: ...
    def addContent(self: TaskDialog, widget: PyQt6.QtWidgets.QWidget): ...
    def exec(self: TaskDialog) -> PyQt6.QtWidgets.QMessageBox.StandardButton: ...
    def setContent(self: TaskDialog, content: str) -> TaskDialog: ...
    def setDetails(self: TaskDialog, details: str) -> TaskDialog: ...
    def setIcon(
        self: TaskDialog, icon: PyQt6.QtWidgets.QMessageBox.Icon
    ) -> TaskDialog: ...
    def setMain(self: TaskDialog, main: str) -> TaskDialog: ...
    def setRemember(self: TaskDialog, action: str, file: str = "") -> TaskDialog: ...
    def setTitle(self: TaskDialog, title: str) -> TaskDialog: ...
    def setWidth(self: TaskDialog, widget: int): ...

class TaskDialogButton:
    @overload
    def __init__(
        self: TaskDialogButton,
        text: str,
        description: str,
        button: PyQt6.QtWidgets.QMessageBox.StandardButton,
    ): ...
    @overload
    def __init__(
        self: TaskDialogButton,
        text: str,
        button: PyQt6.QtWidgets.QMessageBox.StandardButton,
    ): ...
