from __future__ import annotations

__version__ = "2.5.0"

from typing import List, Tuple, Union, overload

import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWidgets

class TaskDialog:
    """
    Customizable choice dialog.
    """

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
    ):
        """
        Construct a new TaskDialog.

        Args:
            parent: Parent widget of the dialog.
            title: Title of the dialog.
            main: Header of the dialog (big text at the top).
            content: Main message of the dialog (text below main).
            details: Details for the dialog, initially collapsed (bottom of the dialog).
            icon: Icon for the dialog.
            buttons: List of buttons for the dialog.
            remember: Remember the choice for this dialog.
        """
        ...
    def addButton(self: TaskDialog, button: TaskDialogButton) -> TaskDialog:
        """
        Add a custom button to this TaskDialog.

        Args:
            button: Button to add to the dialog.
        """
        ...
    def addContent(self: TaskDialog, widget: PyQt6.QtWidgets.QWidget):
        """
        Add a custom widget content to this TaskDialog. Widget content are put between
        content and buttons (above buttons).

        Args:
            widget: Widget to add.
        """
        ...
    def exec(self: TaskDialog) -> PyQt6.QtWidgets.QMessageBox.StandardButton:
        """
        Display this dialog and wait for user-interaction to return. This is a blocking
        function.

        Returns:
            The button clicked by the user. Without custom buttons, this return Ok, otherwise it returns the button set in the TaskDialogButton.
        """
        ...
    def setContent(self: TaskDialog, content: str) -> TaskDialog:
        """
        Set the top-level message of this dialog.

        Args:
            content: Top-level message to set.
        """
        ...
    def setDetails(self: TaskDialog, details: str) -> TaskDialog:
        """
        Set the details for this TaskDialog.

        The details are hidden by default and the user can display them by clicking
        the "Details" button at the bottom of the TaskDialog.

        Args:
            details: Details content to display. Can be a multi-line string.
        """
        ...
    def setIcon(self: TaskDialog, icon: PyQt6.QtWidgets.QMessageBox.Icon) -> TaskDialog:
        """
        Set the icon of the dialog.

        Args:
            icon: Icon of the dialog.
        """
        ...
    def setMain(self: TaskDialog, main: str) -> TaskDialog:
        """
        Set the main message of the dialog. The main message is displayed at the top of
        the dialog in large font.

        Args:
            main: Main message of the dialog.
        """
        ...
    def setRemember(self: TaskDialog, action: str, file: str = "") -> TaskDialog:
        """
        Configure the dialog to remember user-choice.
        """
        ...
    def setTitle(self: TaskDialog, title: str) -> TaskDialog:
        """
        Set the title of the dialog.

        Args:
            title: Title of the dialog.
        """
        ...
    def setWidth(self: TaskDialog, width: int):
        """
        Set the width of the dialog.

        Args:
            width: Width of the dialog.
        """
        ...

class TaskDialogButton:
    """
    Special button to be used inside TaskDialog widgets.
    """

    @property
    def button(self) -> PyQt6.QtWidgets.QMessageBox.StandardButton: ...
    @button.setter
    def button(self, arg0: PyQt6.QtWidgets.QMessageBox.StandardButton): ...
    @property
    def description(self) -> str: ...
    @description.setter
    def description(self, arg0: str): ...
    @property
    def text(self) -> str: ...
    @text.setter
    def text(self, arg0: str): ...
    @overload
    def __init__(
        self: TaskDialogButton,
        text: str,
        description: str,
        button: PyQt6.QtWidgets.QMessageBox.StandardButton,
    ):
        """
        Create a TaskDialogButton.

        Args:
            text: Label of the button.
            description: Description of the button.
            button: Value returned by TaskDialog.exec() if this button is clicked.
        """
        ...
    @overload
    def __init__(
        self: TaskDialogButton,
        text: str,
        button: PyQt6.QtWidgets.QMessageBox.StandardButton,
    ):
        """
        Create a TaskDialogButton without description.

        Args:
            text: Label of the button.
            button: Value returned by TaskDialog.exec() if this button is clicked.
        """
        ...
