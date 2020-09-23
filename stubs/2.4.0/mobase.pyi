__version__ = "2.4.0.alpha1"

import abc
from enum import Enum
from typing import (
    Dict,
    Iterator,
    List,
    Tuple,
    Union,
    Any,
    Optional,
    Callable,
    overload,
    TypeVar,
    Type,
)
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

MoVariant = Union[None, bool, int, str, List[Any], Dict[str, Any]]
GameFeatureType = TypeVar("GameFeatureType")

class InterfaceNotImplemented: ...

def getFileVersion(filepath: str) -> str:
    """
    Retrieve the file version of the given executable.

    Args:
        filepath: Absolute path to the executable.

    Returns:
        The file version, or an empty string if the file version could not be retrieved.
    """
    ...

def getIconForExecutable(executable: str) -> PyQt5.QtGui.QIcon:
    """
    Retrieve the icon of an executable. Currently this always extracts the biggest icon.

    Args:
        executable: Absolute path to the executable.

    Returns:
        The icon for this executable, if any.
    """
    ...

def getProductVersion(executable: str) -> str:
    """
    Retrieve the product version of the given executable.

    Args:
        executable: Absolute path to the executable.

    Returns:
        The product version, or an empty string if the product version could not be retrieved.
    """
    ...

class EndorsedState(Enum):
    ENDORSED_FALSE = ...
    ENDORSED_TRUE = ...
    ENDORSED_UNKNOWN = ...
    ENDORSED_NEVER = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class GuessQuality(Enum):
    """
    Describes how good the code considers a guess (i.e. for a mod name) this is used to
    determine if a name from another source should overwrite or not.
    """

    INVALID = ...
    FALLBACK = ...
    GOOD = ...
    META = ...
    PRESET = ...
    USER = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class InstallResult(Enum):
    SUCCESS = ...
    FAILED = ...
    CANCELED = ...
    MANUAL_REQUESTED = ...
    NOT_ATTEMPTED = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class LoadOrderMechanism(Enum):
    FILE_TIME = ...
    PLUGINS_TXT = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class ModState(Enum):
    EXISTS = ...
    ACTIVE = ...
    ESSENTIAL = ...
    EMPTY = ...
    ENDORSED = ...
    VALID = ...
    ALTERNATE = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class PluginState(Enum):
    MISSING = ...
    INACTIVE = ...
    ACTIVE = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class ProfileSetting(Enum):
    MODS = ...
    CONFIGURATION = ...
    SAVEGAMES = ...
    PREFER_DEFAULTS = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class ReleaseType(Enum):
    PRE_ALPHA = ...
    ALPHA = ...
    BETA = ...
    CANDIDATE = ...
    FINAL = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class SortMechanism(Enum):
    NONE = ...
    MLOX = ...
    BOSS = ...
    LOOT = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class TrackedState(Enum):
    TRACKED_FALSE = ...
    TRACKED_TRUE = ...
    TRACKED_UNKNOWN = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class VersionScheme(Enum):
    DISCOVER = ...
    REGULAR = ...
    DECIMAL_MARK = ...
    NUMBERS_AND_LETTERS = ...
    DATE = ...
    LITERAL = ...
    def __and__(self, other: int) -> bool: ...
    def __or__(self, other: int) -> bool: ...
    def __rand__(self, other: int) -> bool: ...
    def __ro__(self, other: int) -> bool: ...

class BSAInvalidation(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def activate(self, profile: "IProfile"): ...
    @abc.abstractmethod
    def deactivate(self, profile: "IProfile"): ...
    @abc.abstractmethod
    def isInvalidationBSA(self, name: str) -> bool: ...

class DataArchives(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def addArchive(self, profile: "IProfile", index: int, name: str):
        """
        Add an archive to the archive list.

        Args:
            profile: Profile to add the archive to.
            index: Index to insert before. Use 0 for the beginning of the list or INT_MAX for
                the end of the list).
            name: Name of the archive to add.
        """
        ...
    @abc.abstractmethod
    def archives(self, profile: "IProfile") -> List[str]:
        """
        Retrieve the list of archives in the given profile.

        Args:
            profile: Profile to retrieve archives from.

        Returns:
            The list of archives in the given profile.
        """
        ...
    @abc.abstractmethod
    def removeArchive(self, profile: "IProfile", name: str):
        """
        Remove the given archive from the given profile.

        Args:
            profile: Profile to remove the archive from.
            name: Name of the archive to remove.
        """
        ...
    @abc.abstractmethod
    def vanillaArchives(self) -> List[str]:
        """
        Retrieve the list of vanilla archives.

        Vanilla archives are archive files that are shipped with the original
        game.

        Returns:
            The list of vanilla archives.
        """
        ...

class ExecutableForcedLoadSetting:
    def __init__(self, process: str, library: str): ...
    def enabled(self) -> bool: ...
    def forced(self) -> bool: ...
    def library(self) -> str: ...
    def process(self) -> str: ...
    def withEnabled(self, enabled: bool) -> "ExecutableForcedLoadSetting": ...
    def withForced(self, forced: bool) -> "ExecutableForcedLoadSetting": ...

class ExecutableInfo:
    def __init__(self, title: str, binary: PyQt5.QtCore.QFileInfo): ...
    def arguments(self) -> List[str]: ...
    def asCustom(self) -> "ExecutableInfo": ...
    def binary(self) -> PyQt5.QtCore.QFileInfo: ...
    def isCustom(self) -> bool: ...
    def isValid(self) -> bool: ...
    def steamAppID(self) -> str: ...
    def title(self) -> str: ...
    def withArgument(self, argument: str) -> "ExecutableInfo": ...
    def withSteamAppId(self, app_id: str) -> "ExecutableInfo": ...
    def withWorkingDirectory(
        self, directory: PyQt5.QtCore.QDir
    ) -> "ExecutableInfo": ...
    def workingDirectory(self) -> PyQt5.QtCore.QDir: ...

class FileInfo:
    """
    Information about a virtualised file
    """

    @property
    def archive(self) -> str: ...
    @archive.setter
    def archive(self, arg0: str): ...
    @property
    def filePath(self) -> str: ...
    @filePath.setter
    def filePath(self, arg0: str): ...
    @property
    def origins(self) -> List[str]: ...
    @origins.setter
    def origins(self, arg0: List[str]): ...
    def __init__(self):
        """
        Creates an uninitialized FileInfo.
        """
        ...

class FileTreeEntry:
    """
    Represent an entry in a file tree, either a file or a directory. This class
    inherited by IFileTree so that operations on entry are the same for a file or
    a directory.

    This class provides convenience methods to query information on the file, like its
    name or the its last modification time. It also provides a convenience astree() method
    that can be used to retrieve the tree corresponding to its entry in case the entry
    represent a directory.
    """

    class FileTypes(Enum):
        """
        Enumeration of the different file type or combinations.
        """

        DIRECTORY = ...
        FILE = ...
        FILE_OR_DIRECTORY = ...
        def __and__(self, other: int) -> bool: ...
        def __or__(self, other: int) -> bool: ...
        def __rand__(self, other: int) -> bool: ...
        def __ro__(self, other: int) -> bool: ...
    DIRECTORY: "FileTreeEntry.FileTypes" = ...
    FILE: "FileTreeEntry.FileTypes" = ...
    FILE_OR_DIRECTORY: "FileTreeEntry.FileTypes" = ...
    @overload
    def __eq__(self, arg2: str) -> bool: ...
    @overload
    def __eq__(self, arg2: "FileTreeEntry") -> bool: ...
    @overload
    def __eq__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def detach(self) -> bool:
        """
        Detach this entry from its parent tree.

        Returns:
            True if the entry was removed correctly, False otherwize.
        """
        ...
    def fileType(self) -> "FileTreeEntry.FileTypes":
        """
        Returns:
            The filetype of this entry.
        """
        ...
    @overload
    def hasSuffix(self, suffixes: List[str]) -> bool:
        """
        Check if this entry has one of the given suffixes.

        Args:
            suffixes: Suffixes to check.

        Returns:
            True if this entry is a file and has one of the given suffix.
        """
        ...
    @overload
    def hasSuffix(self, suffix: str) -> bool:
        """
        Check if this entry has the given suffix.

        Args:
            suffix: Suffix to check.

        Returns:
            True if this entry is a file and has the given suffix.
        """
        ...
    def isDir(self) -> bool:
        """
        Returns:
            True if this entry is a directory, False otherwise.
        """
        ...
    def isFile(self) -> bool:
        """
        Returns:
            True if this entry is a file, False otherwise.
        """
        ...
    def moveTo(self, tree: "IFileTree") -> bool:
        """
        Move this entry to the given tree.

        Args:
            tree: The tree to move this entry to.

        Returns:
            True if the entry was moved correctly, False otherwize.
        """
        ...
    def name(self) -> str:
        """
        Returns:
            The name of this entry.
        """
        ...
    def parent(self) -> Optional["IFileTree"]:
        """
        Returns:
            The parent tree containing this entry, or a `None` if this entry is the root
        or the parent tree is unreachable.
        """
        ...
    def path(self, sep: str = "\\") -> str:
        """
        Retrieve the path from this entry up to the root of the tree.

        This method propagate up the tree so is not constant complexity as
        the full path is never stored.

        Args:
            sep: The type of separator to use to create the path.

        Returns:
            The path from this entry to the root, including the name of this entry.
        """
        ...
    def pathFrom(self, tree: "IFileTree", sep: str = "\\") -> str:
        """
        Retrieve the path from the given tree to this entry.

        Args:
            tree: The tree to reach, must be a parent of this entry.
            sep: The type of separator to use to create the path.

        Returns:
            The path from the given tree to this entry, including the name of this entry, or
        an empty string if the given tree is not a parent of this entry.
        """
        ...
    def suffix(self) -> str:
        """
        Retrieve the "last" extension of this entry.

        The "last" extension is everything after the last dot in the file name.

        Returns:
            The last extension of this entry, or an empty string if the file has no extension
        or is directory.
        """
        ...

class GamePlugins(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def getLoadOrder(self) -> List[str]: ...
    @abc.abstractmethod
    def lightPluginsAreSupported(self) -> bool:
        """
        Returns:
            True if light plugins are supported, False otherwise.
        """
        ...
    @abc.abstractmethod
    def readPluginLists(self, plugin_list: "IPluginList"): ...
    @abc.abstractmethod
    def writePluginLists(self, plugin_list: "IPluginList"): ...

class GuessedString:
    """
    Represents a string that may be set from different places. Each time the value is
    changed a "quality" is specified to say how probable it is the value is the best choice.
    Only the best choice should be used in the end but alternatives can be queried. This
    class also allows a filter to be set. If a "guess" doesn't pass the filter, it is ignored.
    """

    @overload
    def __init__(self):
        """
        Creates a GuessedString with no associated value.
        """
        ...
    @overload
    def __init__(self, value: str, quality: "GuessQuality"):
        """
        Creates a GuessedString with the given value and quality.

        Args:
            value: Initial value of the GuessedString.
            quality: Quality of the initial value.
        """
        ...
    def __str__(self) -> str: ...
    @overload
    def reset(self) -> "GuessedString":
        """
        Reset this GuessedString to an invalid state.

        Returns:
            This GuessedString object.
        """
        ...
    @overload
    def reset(self, value: str, quality: "GuessQuality") -> "GuessedString":
        """
        Reset this GuessedString object with the given value and quality, only
        if the given quality is better than the current one.

        Args:
            value: New value for this GuessedString.
            quality: Quality of the new value.

        Returns:
            This GuessedString object.
        """
        ...
    @overload
    def reset(self, other: "GuessedString") -> "GuessedString":
        """
        Reset this GuessedString object by copying the given one, only
        if the given one has better quality.

        Args:
            other: The GuessedString to copy.

        Returns:
            This GuessedString object.
        """
        ...
    def setFilter(self, filter: Callable[[str], Union[str, bool]]):
        """
        Set the filter for this GuessedString.

        The filter is applied on every `update()` and can reject the new value
        altogether or modify it (by returning a new value).

        Args:
            filter: The new filter.
        """
        ...
    @overload
    def update(self, value: str) -> "GuessedString":
        """
        Update this GuessedString by adding the given value to the list of variants
        and setting the actual value without changing the current quality of this
        GuessedString.

        The GuessedString is only updated if the given value passes the filter.

        Args:
            value: The new value for this string.

        Returns:
            This GuessedString object.
        """
        ...
    @overload
    def update(self, value: str, quality: "GuessQuality") -> "GuessedString":
        """
        Update this GuessedString by adding a new variants with the given quality.

        If the specified quality is better than the current one, the actual value of
        the GuessedString is also updated.

        The GuessedString is only updated if the given value passes the filter.

        Args:
            value: The new variant to add.
            quality: The quality of the variant.

        Returns:
            This GuessedString object.
        """
        ...
    def variants(self) -> List[str]:
        """
        Returns:
            The list of variants for this GuessedString.
        """
        ...

class IDownloadManager(PyQt5.QtCore.QObject):
    downloadComplete: PyQt5.QtCore.pyqtSignal = ...
    downloadPaused: PyQt5.QtCore.pyqtSignal = ...
    downloadFailed: PyQt5.QtCore.pyqtSignal = ...
    downloadRemoved: PyQt5.QtCore.pyqtSignal = ...
    def _object(self) -> PyQt5.QtCore.QObject:
        """
        Returns:
            The underlying `QObject` for the manager.
        """
        ...
    def downloadPath(self, id: int) -> str:
        """
        Retrieve the (absolute) path of the specified download.

        Args:
            id: ID of the download.

        Returns:
            The absolute path to the file corresponding to the given download. This file
        may not exist yet if the download is incomplete.
        """
        ...
    def startDownloadNexusFile(self, mod_id: int, file_id: int) -> int:
        """
        Download a file from www.nexusmods.com/<game>. <game> is always the game
        currently being managed.

        Args:
            mod_id: ID of the mod to download the file from.
            file_id: ID of the file to download.

        Returns:
            An ID identifying the download.
        """
        ...
    def startDownloadURLs(self, urls: List[str]) -> int:
        """
        Download a file by url.

        The list can contain alternative URLs to allow the download manager to switch
        in case of download problems

        Args:
            urls: List of urls to download from.

        Returns:
            An ID identifying the download.
        """
        ...

class IFileTree(FileTreeEntry):
    """
    Interface to classes that provides way to visualize and alter file trees. The tree
    may not correspond to an actual file tree on the disk (e.g., inside an archive,
    from a QTree Widget, ...).

    Read-only operations on the tree are thread-safe, even when the tree has not been populated
    yet.

    In order to prevent wrong usage of the tree, implementing classes may throw
    UnsupportedOperationException if an operation is not supported. By default, all operations
    are supported, but some may not make sense in many situations.

    The goal of this is not reflect the change made to a IFileTree to the disk, but child
    classes may override relevant methods to do so.

    The tree is built upon FileTreeEntry. A given tree holds shared pointers to its entries
    while each entry holds a weak pointer to its parent, this means that the descending link
    are strong (shared pointers) but the uplink are weaks.

    Accessing the parent is always done by locking the weak pointer so that returned pointer
    or either null or valid. This structure implies that as long as the initial root lives,
    entry should not be destroyed, unless the entry are detached from the root and no shared
    pointers are kept.

    However, it is not guarantee that one can go up the tree from a single node entry. If the
    root node is destroyed, it will not be possible to go up the tree, even if we still have
    a valid shared pointer.
    """

    class InsertPolicy(Enum):
        FAIL_IF_EXISTS = ...
        REPLACE = ...
        MERGE = ...
        def __and__(self, other: int) -> bool: ...
        def __or__(self, other: int) -> bool: ...
        def __rand__(self, other: int) -> bool: ...
        def __ro__(self, other: int) -> bool: ...
    class WalkReturn(Enum):
        """
        Enumeration that can be returned by the callback for the `walk()` method to stop the
        walking operation early.
        """

        CONTINUE = ...
        STOP = ...
        SKIP = ...
        def __and__(self, other: int) -> bool: ...
        def __or__(self, other: int) -> bool: ...
        def __rand__(self, other: int) -> bool: ...
        def __ro__(self, other: int) -> bool: ...
    CONTINUE: "IFileTree.WalkReturn" = ...
    FAIL_IF_EXISTS: "IFileTree.InsertPolicy" = ...
    MERGE: "IFileTree.InsertPolicy" = ...
    REPLACE: "IFileTree.InsertPolicy" = ...
    SKIP: "IFileTree.WalkReturn" = ...
    STOP: "IFileTree.WalkReturn" = ...
    def __bool__(self) -> bool:
        """
        Returns:
            True if this tree is not empty, False otherwise.
        """
        ...
    def __getitem__(self, index: int) -> "FileTreeEntry":
        """
        Retrieve the entry at the given index in this tree.

        Args:
            index: Index of the entry to retrieve, must be less than the size.

        Returns:
            The entry at the given index.

        Raises:
            IndexError: If the given index is not in range for this tree.
        """
        ...
    def __iter__(self) -> Iterator[FileTreeEntry]:
        """
        Retrieves an iterator for entries directly under this tree.

        This method does not recurse into subtrees, see `walk()` for this.

        Returns:
            An iterator object that can be used to iterate over entries in this tree.
        """
        ...
    def __len__(self) -> int:
        """
        Returns:
            The number of entries directly under this tree.
        """
        ...
    def addDirectory(self, path: str) -> "IFileTree":
        """
        Create a new directory tree under this tree.

        This method will create missing folders in the given path and will
        not fail if the directory already exists but will fail if the given
        path contains "." or "..".
        This method invalidates iterators to this tree and all the subtrees
        present in the given path.

        Args:
            path: Path to the directory to create.

        Returns:
            An IFileTree corresponding to the created directory.

        Raises:
            RuntimeError: If the directory could not be created.
        """
        ...
    def addFile(self, path: str, replace_if_exists: bool = False) -> "FileTreeEntry":
        """
        Create a new file directly under this tree.

        This method will fail if the file already exists and `replace_if_exists` is `False`.
        This method invalidates iterators to this tree and all the subtrees present in the
        given path.

        Args:
            path: Path to the file to create.
            replace_if_exists: If True and an entry already exists at the given location, it will be replaced by
                a new entry. This will replace both files and directories.

        Returns:
            A FileTreeEntry corresponding to the created file.

        Raises:
            RuntimeError: If the file could not be created.
        """
        ...
    def clear(self) -> bool:
        """
        Delete (detach) all the entries from this tree.

        This method will go through the entries in this tree and stop at the first
        entry that cannot be deleted, this means that the tree can be partially cleared.

        Returns:
            True if all entries have been detached, False otherwise.
        """
        ...
    def copy(
        self,
        entry: "FileTreeEntry",
        path: str = "",
        policy: "IFileTree.InsertPolicy" = InsertPolicy.FAIL_IF_EXISTS,
    ) -> "FileTreeEntry":
        """
        Move the given entry to the given path under this tree.

        The entry must not be a parent tree of this tree. This method can also be used
        to rename entries.

        If the insert policy if FAIL_IF_EXISTS, the call will fail if an entry
        at the same location already exists. If the policy is REPLACE, an existing
        entry will be replaced. If MERGE, the entry will be merged with the existing
        one (if the entry is a file, and a file exists, the file will be replaced).

        This method invalidates iterator to this tree, to the parent tree of the given
        entry, and to subtrees of this tree if the insert policy is MERGE.

        Args:
            entry: Entry to copy.
            path: The path to copy the entry to. If the path ends with / or \\, the entry will
                be copied in the corresponding directory instead of replacing it. If the
                given path is empty (`""`), the entry is copied directly under this tree.
            policy: Policy to use to resolve conflicts.

        Returns:
            The new entry (copy of the specified entry).

        Raises:
            RuntimeError: If the entry could not be copied.
        """
        ...
    def createOrphanTree(self, name: str = "") -> "IFileTree":
        """
        Create a new orphan empty tree.

        Args:
            name: Name of the tree.

        Returns:
            A new tree without any parent.
        """
        ...
    def exists(
        self,
        path: str,
        type: "FileTreeEntry.FileTypes" = FileTreeEntry.FileTypes.FILE_OR_DIRECTORY,
    ) -> bool:
        """
        Check if the given entry exists.

        Args:
            path: Path to the entry, separated by / or \\.
            type: The type of the entry to check.

        Returns:
            True if the entry was found, False otherwise.
        """
        ...
    def find(
        self,
        path: str,
        type: "FileTreeEntry.FileTypes" = FileTreeEntry.FileTypes.FILE_OR_DIRECTORY,
    ) -> Optional[Union["IFileTree", "FileTreeEntry"]]:
        """
        Retrieve the given entry.

        If no entry exists at the given path, or if the entry is not of the right
        type, `None` is returned.

        Args:
            path: Path to the entry, separated by / or \\.
            type: The type of the entry to check.

        Returns:
            The entry at the given location, or `None` if the entry was not found or
        was not of the correct type.
        """
        ...
    def insert(
        self,
        entry: "FileTreeEntry",
        policy: "IFileTree.InsertPolicy" = InsertPolicy.FAIL_IF_EXISTS,
    ) -> bool:
        """
        Insert the given entry in this tree, removing it from its
        previouis parent.

        The entry must not be this tree or a parent entry of this tree.

          - If the insert policy if `FAIL_IF_EXISTS`, the call will fail if an entry
            with the same name already exists.
          - If the policy is `REPLACE`, an existing entry will be replaced by the given entry.
          - If the policy is `MERGE`:

            - If there is no entry with the same name, the new entry is inserted.
            - If there is an entry with the same name:

              - If both entries are files, the old file is replaced by the given entry.
              - If both entries are directories, a merge is performed as if using merge().
              - Otherwize the insertion fails (two entries with different types).

        This method invalidates iterator to this tree, to the parent tree of the given
        entry, and to subtrees of this tree if the insert policy is MERGE.

        Args:
            entry: Entry to insert.
            policy: Policy to use to resolve conflicts.

        Returns:
            True if the entry was insert, False otherwise.
        """
        ...
    def merge(
        self, other: "IFileTree", overwrites: bool = False
    ) -> Union[Dict["FileTreeEntry", "FileTreeEntry"], int]:
        """
        Merge the given tree with this tree, i.e., insert all entries
        of the given tree into this tree.

        The tree must not be this tree or a parent entry of this tree. Files present in both tree
        will be replaced by files in the given tree. After a merge, the source tree will be
        empty but still attached to its parent.

        If `overwrites` is `True`, a map from overriden files to new files will be returned.

        Note that the merge process makes no distinction between files and directories
        when merging: if a directory is present in this tree and a file from source
        is in conflict with it, the tree will be removed and the file inserted; if a file
        is in this tree and a directory from source is in conflict with it, the file will
        be replaced with the directory.

        This method invalidates iterators to this tree, all the subtrees under this tree
        present in the given path, and all the subtrees of the given source.

        Args:
            other: Tree to merge.
            overwrites: If True, a mapping from overriden files to new files will be returned.

        Returns:
            If `overwrites` is True, a mapping from overriden files to new files, otherwise
        the number of overwritten entries.

        Raises:
            RuntimeError: If the merge failed.
        """
        ...
    def move(
        self,
        entry: "FileTreeEntry",
        path: str,
        policy: "IFileTree.InsertPolicy" = InsertPolicy.FAIL_IF_EXISTS,
    ) -> bool:
        """
        Move the given entry to the given path under this tree.

        The entry must not be a parent tree of this tree. This method can also be used
        to rename entries.

        If the insert policy if FAIL_IF_EXISTS, the call will fail if an entry
        at the same location already exists. If the policy is REPLACE, an existing
        entry will be replaced. If MERGE, the entry will be merged with the existing
        one (if the entry is a file, and a file exists, the file will be replaced).

        This method invalidates iterator to this tree, to the parent tree of the given
        entry, and to subtrees of this tree if the insert policy is MERGE.

        Args:
            entry: Entry to move.
            path: The path to move the entry to. If the path ends with / or \\, the entry will
                be inserted in the corresponding directory instead of replacing it. If the
                given path is empty (`""`), this is equivalent to `insert()`.
            policy: Policy to use to resolve conflicts.

        Returns:
            True if the entry was moved correctly, False otherwise.
        """
        ...
    def pathTo(self, entry: "FileTreeEntry", sep: str = "\\") -> str:
        """
        Retrieve the path from this tree to the given entry.

        Args:
            entry: The entry to reach, must be in this tree.
            sep: The type of separator to use to create the path.

        Returns:
            The path from this tree to the given entry, including the name of the entry, or
        an empty string if the given entry was not found under this tree.
        """
        ...
    @overload
    def remove(self, name: str) -> bool:
        """
        Delete the entry with the given name.

        This method does not recurse into subtrees, so the entry should be
        accessible directly from this tree.

        Args:
            name: Name of the entry to delete.

        Returns:
            True if the entry was deleted, False otherwise.
        """
        ...
    @overload
    def remove(self, entry: "FileTreeEntry") -> bool:
        """
        Delete the given entry.

        Args:
            entry: Entry to delete. The entry must belongs to this tree (and not to a subtree).

        Returns:
            True if the entry was deleted, False otherwise.
        """
        ...
    def removeAll(self, names: List[str]) -> int:
        """
        Delete the entries with the given names from the tree.

        This method does not recurse into subtrees, so only entries accessible
        directly from this tree will be removed. This method invalidates iterators.

        Args:
            names: Names of the entries to delete.

        Returns:
            The number of deleted entry.
        """
        ...
    def removeIf(self, filter: Callable[["FileTreeEntry"], bool]) -> int:
        """
        Delete entries matching the given predicate from the tree.

        This method does not recurse into subtrees, so only entries accessible
        directly from this tree will be removed. This method invalidates iterators.

        Args:
            filter: Predicate that should return true for entries to delete.

        Returns:
            The number of deleted entry.
        """
        ...
    def walk(
        self,
        callback: Callable[[str, "FileTreeEntry"], "IFileTree.WalkReturn"],
        sep: str = "\\",
    ):
        """
        Walk this tree, calling the given function for each entry in it.

        The given callback will be called with two parameters: the path from this tree to the given entry
        (with a trailing separator, not including the entry name), and the actual entry. The method returns
        a `WalkReturn` object to indicates what to do.

        Args:
            callback: Method to call for each entry in the tree.
            sep: Type of separator to use to construct the path.
        """
        ...

class IInstallationManager:
    def createFile(self, entry: "FileTreeEntry") -> str:
        """
        Create a new file on the disk corresponding to the given entry.

        This method can be used by installer that needs to create files that are not in the original
        archive. At the end of the installation, if there are entries in the final tree that were used
        to create files, the corresponding files will be moved to the mod folder.

        Temporary files corresponding to created files are automatically cleaned up at the end of
        the installation.

        Args:
            entry: The entry for which a temporary file should be created.

        Returns:
            The path to the created file, or an empty string if the file could not be created.
        """
        ...
    def extractFile(self, entry: "FileTreeEntry", silent: bool = False) -> str:
        """
        Extract the specified file from the currently opened archive to a temporary
        location.

        This method cannot be used to extract directory.

        The call will fail with an exception if no archive is open (plugins deriving from
        IPluginInstallerSimple can rely on that, custom installers should not). The temporary
        file is automatically cleaned up after the installation. This call can be very slow
        if the archive is large and "solid".

        Args:
            entry: Entry corresponding to the file to extract.
            silent: If true, the dialog showing extraction progress will not be shown.

        Returns:
            The absolute path to the temporary file, or an empty string if the file was not extracted.
        """
        ...
    def extractFiles(
        self, entries: List["FileTreeEntry"], silent: bool = False
    ) -> List[str]:
        """
        Extract the specified files from the currently opened archive to a temporary
        location.

        This method cannot be used to extract directories.

        The call will fail with an exception if no archive is open (plugins deriving from
        IPluginInstallerSimple can rely on that, custom installers should not). The temporary
        files are automatically cleaned up after the installation. This call can be very slow
        if the archive is large and "solid".

        Args:
            entries: Entries corresponding to the files to extract.
            silent: If true, the dialog showing extraction progress will not be shown.

        Returns:
            A list containing absolute paths to the temporary files.
        """
        ...
    def getSupportedExtensions(self) -> List[str]:
        """
        Returns:
            The extensions of archives supported by this installation manager.
        """
        ...
    def installArchive(
        self, mod_name: "GuessedString", archive: str, mod_id: int
    ) -> "InstallResult":
        """
        Install the given archive.

        Args:
            mod_name: Suggested name of the mod.
            archive: Path to the archive to install.
            mod_id: ID of the mod, if available.

        Returns:
            The result of the installation.
        """
        ...
    def setURL(self, url: str):
        """
        Set the url associated with the mod being installed.

        Args:
            url: Url to set.
        """
        ...

class IModInterface:
    def absolutePath(self) -> str:
        """
        Returns:
            Absolute path to the mod to be used in file system operations.
        """
        ...
    def addCategory(self, name: str):
        """
        Assign a category to the mod. If the named category does not exist it is created.

        Args:
            name: Name of the new category to assign.
        """
        ...
    def addNexusCategory(self, category_id: int):
        """
        Set the category id from a nexus category id. Conversion to MO ID happens internally.

        If a mapping is not possible, the category is set to the default value.

        Args:
            category_id: The Nexus category ID.
        """
        ...
    def categories(self) -> List[str]:
        """
        Returns:
            The list of categories this mod belongs to.
        """
        ...
    def clearPluginSettings(self, plugin_name: str) -> Dict[str, MoVariant]:
        """
        Remove all the settings of the specified plugin this mod.

        Args:
            plugin_name: Name of the plugin for which settings should be removed. This should always be `IPlugin.name()`
                unless you have a really good reason to access settings of another plugin.

        Returns:
            The old settings from the given plugin, as returned by `pluginSettings()`.
        """
        ...
    def color(self) -> PyQt5.QtGui.QColor:
        """
        Returns:
            The color of the 'Notes' column chosen by the user.
        """
        ...
    def comments(self) -> str:
        """
        Returns:
            The comments for this mod, if any.
        """
        ...
    def converted(self) -> bool:
        """
        Check if the mod was marked as converted by the user.

        When a mod is for a different game, a flag is shown to users to warn them, but
        they can mark mods as converted to remove this flag.

        Returns:
            True if this mod was marked as converted by the user.
        """
        ...
    def endorsedState(self) -> "EndorsedState":
        """
        Returns:
            The endorsement state of this mod.
        """
        ...
    def gameName(self) -> str:
        """
        Retrieve the short name of the game associated with this mod. This may differ
        from the current game plugin (e.g. you can install a Skyrim LE game in a SSE
        installation).

        Returns:
            The name of the game associated with this mod.
        """
        ...
    def ignoredVersion(self) -> "VersionInfo":
        """
        Returns:
            The ignored version of this mod (for update), or an invalid version if the user
        did not ignore version for this mod.
        """
        ...
    def installationFile(self) -> str:
        """
        Returns:
            The absolute path to the file that was used to install this mod.
        """
        ...
    def name(self) -> str:
        """
        Returns:
            The name of this mod.
        """
        ...
    def newestVersion(self) -> "VersionInfo":
        """
        Returns:
            The newest version of thid mod (as known by MO2). If this matches version(),
        then the mod is up-to-date.
        """
        ...
    def nexusId(self) -> int:
        """
        Returns:
            The Nexus ID of this mod.
        """
        ...
    def notes(self) -> str:
        """
        Returns:
            The notes for this mod, if any.
        """
        ...
    def pluginSetting(
        self, plugin_name: str, key: str, default: MoVariant = None
    ) -> MoVariant:
        """
        Retrieve the specified setting in this mod for a plugin.

        Args:
            plugin_name: Name of the plugin for which to retrieve a setting. This should always be `IPlugin.name()`
                unless you have a really good reason to access settings of another plugin.
            key: Identifier of the setting.
            default: The default value to return if the setting does not exist.

        Returns:
            The setting, if found, or the default value.
        """
        ...
    def pluginSettings(self, plugin_name: str) -> Dict[str, MoVariant]:
        """
        Retrieve the settings in this mod for a plugin.

        Args:
            plugin_name: Name of the plugin for which to retrieve settings. This should always be `IPlugin.name()`
                unless you have a really good reason to access settings of another plugin.

        Returns:
            A map from setting key to value. The map is empty if there are not settings for this mod.
        """
        ...
    def primaryCategory(self) -> int:
        """
        Returns:
            The ID of the primary category of this mod.
        """
        ...
    def remove(self) -> bool:
        """
        Delete the mod from the disc.

        This does not update the global ModInfo structure or indices.

        Returns:
            True if the mod was deleted, False otherwise.
        """
        ...
    def removeCategory(self, name: str) -> bool:
        """
        Unassign a category from this mod.

        Args:
            name: Name of the category to remove.

        Returns:
            True if the category was removed, False otherwise (e.g. if no such category
        was assigned).
        """
        ...
    def repository(self) -> str:
        """
        Returns:
            The name of the repository from which this mod was installed.
        """
        ...
    def setGameName(self, name: str):
        """
        Set the source game of this mod.

        Args:
            name: The new source game short name of this mod.
        """
        ...
    def setIsEndorsed(self, endorsed: bool):
        """
        Set endorsement state of the mod.

        Args:
            endorsed: New endorsement state of this mod.
        """
        ...
    def setName(self, name: str) -> bool:
        """
        Set the name of this mod.

        This will also update the name of the directory that contains this mod

        Args:
            name: New name for this mod.

        Returns:
            True if the name was changed, False if an error occured (e.g. if the name is not a valid
        directory name).
        """
        ...
    def setNewestVersion(self, version: "VersionInfo"):
        """
        Set the latest known version of this mod.

        Args:
            version: The latest known version of this mod.
        """
        ...
    def setNexusID(self, nexus_id: int):
        """
        Set the Nexus ID of this mod.

        Args:
            nexus_id: Thew new Nexus ID of this mod.
        """
        ...
    def setPluginSetting(self, plugin_name: str, key: str, value: MoVariant) -> bool:
        """
        Set the specified setting in this mod for a plugin.

        Args:
            plugin_name: Name of the plugin for which to retrieve a setting. This should always be `IPlugin.name()`
                unless you have a really good reason to access settings of another plugin.
            key: Identifier of the setting.
            value: New value for the setting to set.

        Returns:
            True if the setting was set correctly, False otherwise.
        """
        ...
    def setVersion(self, version: "VersionInfo"):
        """
        Set the version of this mod.

        Args:
            version: The new version of this mod.
        """
        ...
    def trackedState(self) -> "TrackedState":
        """
        Returns:
            The tracked state of this mod.
        """
        ...
    def url(self) -> str:
        """
        Returns:
            The URL of this mod, or an empty QString() if no URL is associated
        with this mod.
        """
        ...
    def validated(self) -> bool:
        """
        Check if the mod was marked as validated by the user.

        MO2 uses ModDataChecker to check the content of mods, but sometimes these fail, in
        which case mods are incorrectly marked as 'not containing valid games data'. Users can
        choose to mark these mods as valid to hide the warning / flag.

        Returns:
            True if th is mod was marked as containing valid game data.
        """
        ...
    def version(self) -> "VersionInfo":
        """
        Returns:
            The current version of this mod.
        """
        ...

class IModList:
    """
    Interface to the mod-list.

    All api functions in this interface work need the internal name of a mod to find a
    mod. For regular mods (mods the user installed) the display name (as shown to the user)
    and internal name are identical. For other mods (non-MO mods) there is currently no way
    to translate from display name to internal name because the display name might not me un-ambiguous.
    """

    def allMods(self) -> List[str]:
        """
        Returns:
            A list containing the internal names of all installed mods.
        """
        ...
    def displayName(self, name: str) -> str:
        """
        Retrieve the display name of a mod from its internal name.

        If you received an internal name from the API (e.g. `IPluginList.origin`) then you should use
        that name to identify the mod in all other api calls but use this function to retrieve the name
        to show to the user.

        Args:
            name: Internal name of the mod.

        Returns:
            The display name of the given mod.
        """
        ...
    def onModMoved(self, callback: Callable[[str, int, int], None]) -> bool:
        """
        Install a handler to be called when a mod is moved.

        Args:
            callback: The function to call when a mod is moved. The first argument is the internal name of the
                mod, the second argument the old priority and the third argument the new priority.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onModStateChanged(self, callback: Callable[[Dict[str, int]], None]) -> bool:
        """
        Install a handler to be called when mod states change (enabled/disabled, endorsed, ...).

        Args:
            callback: The function to call when the states of mod change. The argument is a map containing the
                mods whose states have changed. Keys are internal mod names and values are mod states.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def priority(self, name: str) -> int:
        """
        Retrieve the priority of a mod.

        Args:
            name: Internal name of the mod.

        Returns:
            The priority of the given mod.
        """
        ...
    @overload
    def setActive(self, names: List[str], active: bool) -> int:
        """
        Enable or disable a list of mods.

        Calling this will cause MO to re-evaluate its virtual file system so this is
        a fairly expensive call.

        Args:
            names: Internal names of the mod to enable or disable.
            active: True to enable the mods, False to disable them.

        Returns:
            True on success, False otherwise.
        """
        ...
    @overload
    def setActive(self, name: str, active: bool) -> bool:
        """
        Enable or disable a mod.

        Calling this will cause MO to re-evaluate its virtual file system so this is
        a fairly expensive call.

        Args:
            name: Internal name of the mod to enable or disable.
            active: True to enable the mod, False to disable it.

        Returns:
            True on success, False otherwise.
        """
        ...
    def setPriority(self, name: str, priority: int) -> bool:
        """
        Change the priority of a mod.

        `priority` is the new priority after the move. Keep in mind that the mod disappears from its
        old location and all mods with higher priority than the moved mod decrease in priority by one.

        Args:
            name: Internal name of the mod.
            priority: The new priority of the mod.

        Returns:
            True if the priority was changed, False otherwise (if the name or priority were invalid).
        """
        ...
    def state(self, name: str) -> int:
        """
        Retrieve the state of a mod.

        Args:
            name: Internal name of the mod.

        Returns:
            The state of the given mod.
        """
        ...

class IModRepositoryBridge(PyQt5.QtCore.QObject):
    descriptionAvailable: PyQt5.QtCore.pyqtSignal = ...
    filesAvailable: PyQt5.QtCore.pyqtSignal = ...
    fileInfoAvailable: PyQt5.QtCore.pyqtSignal = ...
    downloadURLsAvailable: PyQt5.QtCore.pyqtSignal = ...
    endorsementsAvailable: PyQt5.QtCore.pyqtSignal = ...
    endorsementToggled: PyQt5.QtCore.pyqtSignal = ...
    trackedModsAvailable: PyQt5.QtCore.pyqtSignal = ...
    trackingToggled: PyQt5.QtCore.pyqtSignal = ...
    requestFailed: PyQt5.QtCore.pyqtSignal = ...
    def _object(self) -> PyQt5.QtCore.QObject:
        """
        Returns:
            The underlying `QObject` for the bridge.
        """
        ...
    def requestDescription(self, game_name: str, mod_id: int, user_data: MoVariant):
        """
        Request description of a mod.

        Args:
            game_name: Name of the game containing the mod.
            mod_id: Nexus ID of the mod.
            user_data: User data to be returned with the result.
        """
        ...
    def requestDownloadURL(
        self, game_name: str, mod_id: int, file_id: int, user_data: MoVariant
    ):
        """
        Request download URL for mod file.0

        Args:
            game_name: Name of the game containing the mod.
            mod_id: Nexus ID of the mod.
            file_id: ID of the file for which a URL should be returned.
            user_data: User data to be returned with the result.
        """
        ...
    def requestFileInfo(
        self, game_name: str, mod_id: int, file_id: int, user_data: MoVariant
    ):
        """
        Args:
            game_name: Name of the game containing the mod.
            mod_id: Nexus ID of the mod.
            file_id: ID of the file for which information is requested.
            user_data: User data to be returned with the result.
        """
        ...
    def requestFiles(self, game_name: str, mod_id: int, user_data: MoVariant):
        """
        Request the list of files belonging to a mod.

        Args:
            game_name: Name of the game containing the mod.
            mod_id: Nexus ID of the mod.
            user_data: User data to be returned with the result.
        """
        ...
    def requestToggleEndorsement(
        self,
        game_name: str,
        mod_id: int,
        mod_version: str,
        endorse: bool,
        user_data: MoVariant,
    ):
        """
        Args:
            game_name: Name of the game containing the mod.
            mod_id: Nexus ID of the mod.
            mod_version: Version of the mod.
            endorse:
            user_data: User data to be returned with the result.
        """
        ...

class IOrganizer:
    """
    Interface to class that provides information about the running session
    of Mod Organizer to be used by plugins.
    """

    def appVersion(self) -> "VersionInfo":
        """
        Returns:
            The running version of Mod Organizer.
        """
        ...
    def basePath(self) -> str:
        """
        Returns:
            The absolute path to the base directory of Mod Organizer.
        """
        ...
    def createMod(self, name: "GuessedString") -> "IModInterface":
        """
        Create a new mod with the specified name.

        If a mod with the same name already exists, the user will be queried. If the user chooses
        to merge or replace, the call will succeed, otheriwse the call will fail.

        Args:
            name: Name of the mod to create.

        Returns:
            An interface to the newly created mod that can be used to modify it, or `None` if the mod
        could not be created.
        """
        ...
    def createNexusBridge(self) -> "IModRepositoryBridge":
        """
        Create a new Nexus interface.

        Returns:
            The newly created Nexus interface.
        """
        ...
    def downloadManager(self) -> "IDownloadManager":
        """
        Returns:
            The interface to the download manager.
        """
        ...
    def downloadsPath(self) -> str:
        """
        Returns:
            The absolute path to the download directory.
        """
        ...
    def findFileInfos(
        self, path: str, filter: Callable[["FileInfo"], bool]
    ) -> List["FileInfo"]:
        """
        Find files in the virtual directory matching the specified filter.

        Args:
            path: The path to search in (relative to the 'data' folder).
            filter: The function to use to filter files. Should return True for the files to keep.

        Returns:
            The list of `QFileInfo` corresponding to the matching files.
        """
        ...
    @overload
    def findFiles(self, path: str, filter: Callable[[str], bool]) -> List[str]:
        """
        Find files in the given folder that matches the given filter.

        Args:
            path: The path to search in (relative to the 'data' folder).
            filter: The function to use to filter files. Should return True for the files to keep.

        Returns:
            The list of matching files.
        """
        ...
    @overload
    def findFiles(self, path: str, patterns: List[str]) -> List[str]:
        """
        Find files in the given folder that matches one of the given glob patterns.

        Args:
            path: The path to search in (relative to the 'data' folder).
            patterns: List of glob patterns to match against.

        Returns:
            The list of matching files.
        """
        ...
    @overload
    def findFiles(self, path: str, pattern: str) -> List[str]:
        """
        Find files in the given folder that matches the given glob pattern.

        Args:
            path: The path to search in (relative to the 'data' folder).
            pattern: The glob pattern to use to filter files.

        Returns:
            The list of matching files.
        """
        ...
    def getFileOrigins(self, filename: str) -> List[str]:
        """
        Retrieve the file origins for the speicified file.

        The origins are listed with their internal name. The internal name of a mod can differ
        from the display name for disambiguation.

        Args:
            filename: Path to the file to retrieve origins for (relative to the 'data' folder).

        Returns:
            The list of origins that contain the specified file, sorted by their priority.
        """
        ...
    def getGame(self, name: str) -> "IPluginGame":
        """
        Retrieve the game plugin matching the given name.

        Args:
            name: Name of the game (short name).

        Returns:
            The plugin for the given game, or `None` if none was found.
        """
        ...
    def getMod(self, name: str) -> "IModInterface":
        """
        Retrieve an interface to a mod using its name.

        Args:
            name: Name of the mod to retrieve.

        Returns:
            An interface to the given mod, or `None` if there is no mod with this name
        """
        ...
    def installMod(self, filename: str, name_suggestion: str = "") -> "IModInterface":
        """
        Install a mod archive at the specified location.

        Args:
            filename: Absolute filepath to the archive to install.
            name_suggestion: Suggested name for this mod. This can still be changed by the user.

        Returns:
            An interface to the new installed mod, or `None` if no installation took place (canceled or failure).
        """
        ...
    def listDirectories(self, directory: str) -> List[str]:
        """
        Retrieve the list of (virtual) subdirectories in the given path.

        Args:
            directory: Path to the directory to list (relative to the 'data' folder).

        Returns:
            The list of directories in the given directory.
        """
        ...
    def managedGame(self) -> "IPluginGame":
        """
        Returns:
            The plugin corresponding to the current game.
        """
        ...
    def modDataChanged(self, mod: "IModInterface"):
        """
        Notify the organizer that the given mod has changed.

        Args:
            mod: The mod that has changed.
        """
        ...
    def modList(self) -> "IModList":
        """
        Returns:
            The interface to the mod list.
        """
        ...
    def modsPath(self) -> str:
        """
        Returns:
            The (absolute) path to the mods directory.
        """
        ...
    def modsSortedByProfilePriority(self) -> List[str]:
        """
        Returns:
            The list of mod (names), sorted according to the current profile priorities.
        """
        ...
    def onAboutToRun(self, callback: Callable[[str], bool]) -> bool:
        """
        Install a new handler to be called when an application is about to run.

        Multiple handlers can be installed. If any of the handler returns `False`, the application will
        not run.

        Args:
            callback: The function to call when an application is about to run. The parameter is the absolute path
                to the application to run. The function can return False to prevent the application from running.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onFinishedRun(self, callback: Callable[[str, int], None]) -> bool:
        """
        Install a new handler to be called when an application has finished running.

        Args:
            callback: The function to call when an application has finished running. The first parameter is the absolute
                path to the application, and the second parameter is the exit code of the application.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onModInstalled(self, callback: Callable[[str], None]) -> bool:
        """
        Install a new handler to be called when a new mod is installed.

        Args:
            callback: The function to call when a mod is installed. The parameter of the function is the name of the
                installed mod.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onPluginSettingChanged(
        self, callback: Callable[[str, str, MoVariant, MoVariant], None]
    ) -> bool:
        """
        Install a new handler to be called when a plugin setting is changed.

        Args:
            callback: The function to call when a plugin setting is changed. The parameters are: The name of the plugin, the
                name of the setting, the old value (or `None` if the setting did not exist before) and the new value
                of the setting (or `None` if the setting has been removed).

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onProfileChanged(
        self, callback: Callable[["IProfile", "IProfile"], None]
    ) -> bool:
        """
        Install a new handler to be called when the current profile is changed.

        The function is called when the profile is changed but some operations related to
        the profile might not be finished when this is called (e.g., the virtual file system
        might not be up-to-date).

        Args:
            callback: The function to call when the current profile is changed. The first parameter is the old profile (can
                be `None`, e.g. at startup), and the second parameter is the new profile (cannot be `None`).

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onUserInterfaceInitialized(
        self, callback: Callable[[PyQt5.QtWidgets.QMainWindow], None]
    ) -> bool:
        """
        Install a new handler to be called when the UI has been fully initialized.

        Args:
            callback: The function to call when the user-interface has been fully initialized. The parameter is the main
                window of the application (`QMainWindow`).

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def overwritePath(self) -> str:
        """
        Returns:
            The (absolute) path to the overwrite directory.
        """
        ...
    def persistent(
        self, plugin_name: str, key: str, default: MoVariant = None
    ) -> MoVariant:
        """
        Retrieve the specified persistent value for a plugin.

        A persistent is an arbitrary value that the plugin can set and retrieve that is persistently stored
        by the main application. There is no UI for the user to change this value but they can directly access
        the storage

        Args:
            plugin_name: Name of the plugin for which to retrieve the value. This should always be IPlugin::name() unless you have a
                really good reason to access data of another mod AND if you can verify that plugin is actually installed.
            key: Identifier of the setting.
            default: Default value to return if the key is not set (yet).

        Returns:
            The value corresponding to the given persistent setting, or `def` is the key is not found.
        """
        ...
    def pluginDataPath(self) -> str:
        """
        Retrieve the path to a directory where plugin data should be stored.

        For python plugins, it is recommended to use a dedicated folder (per plugin) if you need to
        store data (resources, or multiple python files).

        Returns:
            Path to a directory where plugin data should be stored.
        """
        ...
    def pluginList(self) -> "IPluginList":
        """
        Returns:
            The plugin list interface.
        """
        ...
    def pluginSetting(self, plugin_name: str, key: str) -> MoVariant:
        """
        Retrieve settings of plugins.

        Args:
            plugin_name: Name of the plugin to retrieve the setting for.
            key: Name of the setting to retrieve the value for.

        Returns:
            The value of the setting.
        """
        ...
    def profile(self) -> "IProfile":
        """
        Returns:
            The interface to the current profile.
        """
        ...
    def profileName(self) -> str:
        """
        Returns:
            The name of the current profile, or an empty string if no profile has been loaded (yet).
        """
        ...
    def profilePath(self) -> str:
        """
        Returns:
            The absolute path to the active profile or an empty string if no profile has been loaded (yet).
        """
        ...
    def refreshModList(self, save_changes: bool = True):
        """
        Refresh the mod list.

        Args:
            save_changes: If True, the relevant profile information is saved first (enabled mods and order of mods).
        """
        ...
    def removeMod(self, mod: "IModInterface") -> bool:
        """
        Remove a mod (from disc and from the UI).

        Args:
            mod: The mod to remove.

        Returns:
            True if the mod was removed, False otherwise.
        """
        ...
    def resolvePath(self, filename: str) -> str:
        """
        Resolves a path relative to the virtual data directory to its absolute real path.

        Args:
            filename: Path to resolve.

        Returns:
            The absolute real path, or an empty string if the path was not found.
        """
        ...
    def setPersistent(
        self, plugin_name: str, key: str, value: MoVariant, sync: bool = True
    ):
        """
        Set the specified persistent value for a plugin.

        This does not update the in-memory value for this setting, see `setPluginSetting()` for this.

        Args:
            plugin_name: Name of the plugin for which to change a value. This should always be IPlugin::name() unless you have a
                really good reason to access data of another mod AND if you can verify that plugin is actually installed.
            key: Identifier of the setting.
            value: New value for the setting.
            sync: If True, the storage is immediately written to disc. This costs performance but is safer against data loss.
        """
        ...
    def setPluginSetting(self, plugin_name: str, key: str, value: MoVariant):
        """
        Set the specified setting for a plugin.

        This automatically notify handlers register with `onPluginSettingChanged`, so you do not have to do it yourself.

        Args:
            plugin_name: Name of the plugin for which to change a value. This should always be IPlugin::name() unless you have a
                really good reason to access data of another mod AND if you can verify that plugin is actually installed.
            key: Identifier of the setting.
            value: New value for the setting.
        """
        ...
    def startApplication(
        self,
        executable: str,
        args: List[str] = [],
        cwd: str = "",
        profile: str = "",
        forcedCustomOverwrite: str = "",
        ignoreCustomOverwrite: bool = False,
    ) -> int:
        """
        Starts an application with virtual filesystem active.

        Args:
            executable: Name or path of the executable. If this is only a filename, it will only work if it has been configured
                in MO as an executable. If it is a relative path it is expected to be relative to the game directory.
            args: Arguments to pass to the executable. If the list is empty, and `executable` refers to a configured executable,
                the configured arguments are used.
            cwd: The working directory for the executable. If this is empty, the path to the executable is used unless `executable`
                referred to a configured MO executable, in which case the configured cwd is used.
            profile: Profile to use. If this is empty (the default) the current profile is used.
            forcedCustomOverwrite: The mod to set as the custom overwrite, regardless of what the profile has configured.
            ignoreCustomOverwrite: Set to true to ignore the profile's configured custom overwrite.

        Returns:
            The handle to the started application, or 0 if the application failed to start.
        """
        ...
    def waitForApplication(self, handle: int) -> Tuple[bool, int]:
        """
        Wait for the application corresponding to the given handle to finish.

        This will always show the lock overlay, regardless of whether the
        user has disabled locking in the setting, so use this with care.
        Note that the lock overlay will always allow the user to unlock, in
        which case this will return False.

        Args:
            handle: Handle of the application to wait for (as returned by `startApplication()`).

        Returns:
            A tuple `(result, exitcode)`, where `result` is a boolean indicating if the application
        completed successfully, and `exitcode` is the exit code of the application.
        """
        ...

class IPlugin(abc.ABC):
    """
    Base class for all plugins.
    """

    def __init__(self): ...
    @abc.abstractmethod
    def author(self) -> str:
        """
        Returns:
            The name of the plugin author.
        """
        ...
    @abc.abstractmethod
    def description(self) -> str:
        """
        Returns:
            The description for this plugin.
        """
        ...
    @abc.abstractmethod
    def init(self, organizer: "IOrganizer") -> bool:
        """
        Initialize this plugin.

        Args:
            organizer: The main organizer interface.

        Returns:
            True if the plugin was initialized correctly, False otherwise.
        """
        ...
    @abc.abstractmethod
    def isActive(self) -> bool:
        """
        Check if this plugin is active.

        It is possible to use a plugin setting (specified in `settings()`) here to allow
        users to manually enable/disable a plugin.

        Returns:
            True if this plugin is active, False otherwise.
        """
        ...
    def localizedName(self) -> str:
        """
        Retrieve the localized name of the plugin.

        Unlike `name()`, this method can (and should!) return a localized name for the plugin.
        This method returns name() by default.

        Returns:
            The localized name of the plugin.
        """
        ...
    def master(self) -> "IPlugin":
        """
        Retrieve the master plugin of this plugin.

        It is often easier to implement a functionality as multiple plugins in MO2, but ship the
        plugins together, e.g. as a Python module or using `createFunctions()`. In this case, having
        a master plugin (one of the plugin, or a separate one) tells MO2 that these plugins are
        linked and should also be displayed together in the UI. If MO2 ever implements automatic
        updates for plugins, the `master()` plugin will also be used for this purpose.

        Returns:
            The master plugin of this plugin, or a null pointer if this plugin does not have a master.
        """
        ...
    @abc.abstractmethod
    def name(self) -> str:
        """
        Retrieve the name of the plugin.

        The name of the plugin is used for internal storage purpose so it should not change,
        and it should be static. In particular, you should not use a localized string (`tr()`)
        for the plugin name.

        In the future, we will provide a way to localized plugin names using a distinct method,
        such as `localizedName()`.

        Returns:
            The name of the plugin.
        """
        ...
    @abc.abstractmethod
    def settings(self) -> List["PluginSetting"]:
        """
        Returns:
            A list of settings for this plugin.
        """
        ...
    @abc.abstractmethod
    def version(self) -> "VersionInfo":
        """
        Returns:
            The version of this plugin.
        """
        ...

class IPluginDiagnose(IPlugin):
    """
    Plugins that create problem reports to be displayed in the UI.

    This can be used to report problems related to the same plugin (which implements further
    interfaces) or as a stand-alone diagnosis tool.
    """

    def __init__(self): ...
    def _invalidate(self):
        """
        Invalidate the problems corresponding to this plugin.
        """
        ...
    @abc.abstractmethod
    def activeProblems(self) -> List[int]:
        """
        Retrieve the list of active problems found by this plugin.

        This method returns a list of problem IDs, that are then used when calling other methods
        such as `shortDescription()` or `hasGuidedFix()`.

        Returns:
            The list of active problems for this plugin.
        """
        ...
    @abc.abstractmethod
    def fullDescription(self, key: int) -> str:
        """
        Retrieve the full description of the problem corresponding to the given key.

        Args:
            key: ID of the problem.

        Returns:
            The full description of the problem.

        Raises:
            IndexError: If the key is not valid.
        """
        ...
    @abc.abstractmethod
    def hasGuidedFix(self, key: int) -> bool:
        """
        Check if the problem corresponding to the given key has a guided fix.

        Args:
            key: ID of the problem.

        Returns:
            True if there is a guided fix for the problem, False otherwise.

        Raises:
            IndexError: If the key is not valid.
        """
        ...
    @abc.abstractmethod
    def shortDescription(self, key: int) -> str:
        """
        Retrieve the short description of the problem corresponding to the given key.

        Args:
            key: ID of the problem.

        Returns:
            The short description of the problem.

        Raises:
            IndexError: If the key is not valid.
        """
        ...
    @abc.abstractmethod
    def startGuidedFix(self, key: int):
        """
        Starts a guided fix for the problem corresponding to the given key.

        This method should throw `ValueError` if there is no guided fix for the corresponding
        problem.

        Args:
            key: ID of the problem.

        Raises:
            IndexError: If the key is not valid.
            ValueError: If there is no guided fix for this problem.
        """
        ...

class IPluginFileMapper(IPlugin):
    """
    Plugins that adds virtual file links.
    """

    def __init__(self): ...
    @abc.abstractmethod
    def mappings(self) -> List["Mapping"]:
        """
        Returns:
            Mapping for the virtual file system (VFS).
        """
        ...

class IPluginGame(IPlugin):
    """
    Base classes for game plugins.

    Each game requires a specific game plugin. These plugins were initially designed for
    Bethesda games, so a lot of methods and attributes are irrelevant for other games. If
    you wish to write a plugin for a much simpler game, please consider the `basic_games`
    plugin: https://github.com/ModOrganizer2/modorganizer-basic_games
    """

    def __init__(self): ...
    @abc.abstractmethod
    def CCPlugins(self) -> List[str]:
        """
        Returns:
            The current list of active Creation Club plugins.
        """
        ...
    @abc.abstractmethod
    def DLCPlugins(self) -> List[str]:
        """
        Returns:
            The list of esp/esm files that are part of known DLCs.
        """
        ...
    @abc.abstractmethod
    def binaryName(self) -> str:
        """
        Returns:
            The name of the default executable to run (relative to the game folder).
        """
        ...
    @abc.abstractmethod
    def dataDirectory(self) -> PyQt5.QtCore.QDir:
        """
        Returns:
            The name of the directory containing data (relative to the game folder).
        """
        ...
    @abc.abstractmethod
    def documentsDirectory(self) -> PyQt5.QtCore.QDir:
        """
        Returns:
            The directory of the documents folder where configuration files and such for this game reside.
        """
        ...
    @abc.abstractmethod
    def executableForcedLoads(self) -> List["ExecutableForcedLoadSetting"]:
        """
        Returns:
            A list of automatically discovered libraries that can be force loaded with executables.
        """
        ...
    @abc.abstractmethod
    def executables(self) -> List["ExecutableInfo"]:
        """
        Returns:
            A list of automatically discovered executables of the game itself and tools surrounding it.
        """
        ...
    def feature(self, feature_type: Type[GameFeatureType]) -> GameFeatureType:
        """
        Retrieve a specified game feature from this plugin.

        Args:
            feature_type: The class of feature to retrieve.

        Returns:
            The game feature corresponding to the given type, or `None` if the feature is
        not implemented.
        """
        ...
    def featureList(self) -> Dict[Type[GameFeatureType], GameFeatureType]:
        """
        Retrieve the list of game features implemented for this plugin.

        Python plugin should not implement this method but `_featureList()`.

        Returns:
            A mapping from feature type to actual game features.
        """
        ...
    @abc.abstractmethod
    def gameDirectory(self) -> PyQt5.QtCore.QDir:
        """
        Returns:
            The directory containing the game installation.
        """
        ...
    @abc.abstractmethod
    def gameIcon(self) -> PyQt5.QtGui.QIcon:
        """
        Returns:
            The icon representing the game.
        """
        ...
    @abc.abstractmethod
    def gameName(self) -> str:
        """
        Returns:
            The name of the game (as displayed to the user).
        """
        ...
    @abc.abstractmethod
    def gameNexusName(self) -> str:
        """
        Returns:
            The name of the game identifier for Nexus.
        """
        ...
    @abc.abstractmethod
    def gameShortName(self) -> str:
        """
        Returns:
            The short name of the game.
        """
        ...
    @abc.abstractmethod
    def gameVariants(self) -> List[str]:
        """
        Retrieve the list of variants for this game.

        If there are multiple variants of a game (and the variants make a difference to the
        plugin), like a regular one and a GOTY-edition, the plugin can return a list of them
        and the user gets to chose which one he owns.

        Returns:
            The list of variants of the game.
        """
        ...
    @abc.abstractmethod
    def gameVersion(self) -> str:
        """
        Returns:
            The version of the game.
        """
        ...
    @abc.abstractmethod
    def getLauncherName(self) -> str:
        """
        Returns:
            The name of the launcher executable to run (relative to the game folder), or an
        empty string if there is no launcher.
        """
        ...
    @abc.abstractmethod
    def iniFiles(self) -> List[str]:
        """
        Returns:
            The list of INI files this game uses. The first file in the list should be the
        'main' INI file.
        """
        ...
    @abc.abstractmethod
    def initializeProfile(self, directory: PyQt5.QtCore.QDir, settings: int):
        """
        Initialize a profile for this game.

        The MO app does not yet support virtualizing only specific aspects but plugins should be written
        with this future functionality in mind.

        This function will be used to initially create a profile, potentially to repair it or upgrade/downgrade
        it so the implementations have to gracefully handle the case that the directory already contains files.

        Args:
            directory: The directory where the profile is to be initialized.
            settings: The parameters for how the profile should be initialized.
        """
        ...
    @abc.abstractmethod
    def isInstalled(self) -> bool:
        """
        Returns:
            True if this game has been discovered as installed, False otherwise.
        """
        ...
    @abc.abstractmethod
    def loadOrderMechanism(self) -> "LoadOrderMechanism":
        """
        Returns:
            The load order mechanism used by this game.
        """
        ...
    @abc.abstractmethod
    def looksValid(self, directory: PyQt5.QtCore.QDir) -> bool:
        """
        Check if the given directory looks like a valid game installation.

        Args:
            directory: Directory to check.

        Returns:
            True if the directory looks like a valid installation of this game, False otherwise.
        """
        ...
    @abc.abstractmethod
    def nexusGameID(self) -> int:
        """
        Retrieve the Nexus game ID for this game.

        Example: For Skyrim, the Nexus game ID is 110.

        Returns:
            The Nexus game ID for this game.
        """
        ...
    @abc.abstractmethod
    def nexusModOrganizerID(self) -> int:
        """
        Retrieve the Nexus mod ID of Mod Organizer for this game.

        Example: For Skyrim SE, the mod ID of MO2 is 6194. You can find the mod ID in the URL:
          https://www.nexusmods.com/skyrimspecialedition/mods/6194

        Returns:
            The Nexus mod ID of Mod Organizer for this game.
        """
        ...
    @abc.abstractmethod
    def primaryPlugins(self) -> List[str]:
        """
        Returns:
            The list of plugins that are part of the game and not considered optional.
        """
        ...
    @abc.abstractmethod
    def primarySources(self) -> List[str]:
        """
        Retrieve primary alternative 'short' names for this game.

        This is used to determine if a Nexus (or other) download source should be considered
        as a primary source for the game so that it is not flagged as an alternative one.

        Returns:
            The list of primary alternative 'short' names for this game, or an empty list.
        """
        ...
    @abc.abstractmethod
    def savegameExtension(self) -> str:
        """
        Returns:
            The file extension of save games for this game.
        """
        ...
    @abc.abstractmethod
    def savegameSEExtension(self) -> str:
        """
        Returns:
            The file extension of Script Extender saves for this game.
        """
        ...
    @abc.abstractmethod
    def savesDirectory(self) -> PyQt5.QtCore.QDir:
        """
        Returns:
            The directory where save games are stored.
        """
        ...
    @abc.abstractmethod
    def setGamePath(self, path: str):
        """
        Set the path to the managed game.

        This is called during instance creation if the game is not auto-detected and the user has
        to specify the installation location. This is not called if the game has been auto-detected,
        so `isInstalled()` should call this.

        Args:
            path: Path to the game installation.
        """
        ...
    @abc.abstractmethod
    def setGameVariant(self, variant: str):
        """
        Set the game variant.

        If there are multiple variants of game (as returned by `gameVariants()`), this will be
        called on start with the user-selected game variant.

        Args:
            variant: The game variant selected by the user.
        """
        ...
    @abc.abstractmethod
    def sortMechanism(self) -> "SortMechanism":
        """
        Returns:
            The sort mechanism for this game.
        """
        ...
    @abc.abstractmethod
    def steamAPPId(self) -> str:
        """
        Retrieve the Steam app ID for this game.

        If the game is not available on Steam, this should return an empty string.

        If a game is available in multiple versions, those might have different app ids. The plugin
        should try to return the right one

        Returns:
            The Steam app ID for this game. Should be empty for games not available on steam.
        """
        ...
    @abc.abstractmethod
    def validShortNames(self) -> List[str]:
        """
        Retrieve the valid 'short' names for this game.

        This is used to determine if a Nexus download is valid for the current game since not all
        game variants have their own nexus pages and others can handle downloads from other nexus
        game pages and should be allowed to do so (e.g., you can install some Skyrim LE mod even
        when using Skyrim SE).

        The short name should be considered the primary handler for a directly supported game
        for puroses of auto-launching an instance.

        Returns:
            The list of valid short names for this game.
        """
        ...

class IPluginInstaller(IPlugin):
    """
    This is the top-level class for installer. Actual installers should inherit either:

      - `IPluginInstallerSimple` if the installer can work directly with the archive. This is what
        most installers use.
      - `IPluginInstallerCustom` if the installer needs to perform custom operations. This is only
        used by the external NCC installer and the OMOD installer.
    """

    @abc.abstractmethod
    def isArchiveSupported(self, tree: "IFileTree") -> bool:
        """
        Check if the given file tree corresponds to a supported archive for this installer.

        Args:
            tree: The tree representing the content of the archive.

        Returns:
            True if this installer can handle the archive, False otherwise.
        """
        ...
    @abc.abstractmethod
    def isManualInstaller(self) -> bool:
        """
        Check if this installer is a manual installer.

        Returns:
            True if this installer is a manual installer, False otherwise.
        """
        ...
    @abc.abstractmethod
    def onInstallationEnd(self, result: "InstallResult", new_mod: "IModInterface"):
        """
        Method calls at the end of the installation process. This method is only called once
        per installation process, even for recursive installations (e.g. with the bundle installer).

        Args:
            result: The result of the installation.
            new_mod: If the installation succeeded (result is RESULT_SUCCESS), contains the newly
                installed mod, otherwise it contains a null pointer.
        """
        ...
    @abc.abstractmethod
    def onInstallationStart(
        self, archive: str, reinstallation: bool, current_mod: "IModInterface"
    ):
        """
        Method calls at the start of the installation process, before any other methods.
        This method is only called once per installation process, even for recursive
        installations (e.g. with the bundle installer).

        If `reinstallation` is true, then the given mod is the mod being reinstalled (the one
        selected by the user). If `reinstallation` is false and `currentMod` is not null, then
        it corresponds to a mod MO2 thinks corresponds to the archive (e.g. based on matching Nexus ID
        or name).

        The default implementation does nothing.

        Args:
            archive: Path to the archive that is going to be installed.
            reinstallation: True if this is a reinstallation, False otherwise.
            current_mod: A currently installed mod corresponding to the archive being installed, or None
                if there is no such mod.
        """
        ...
    @abc.abstractmethod
    def priority(self) -> int:
        """
        Retrieve the priority of this installer.

        If multiple installers are able to handle an archive, the one with the highest priority wins.

        Returns:
            The priority of this installer.
        """
        ...
    def setInstallationManager(self, manager: "IInstallationManager"):
        """
        Set the installation manager for this installer.

        Python plugins usually do not need to re-implement this and can directly access the installation
        manager using `_manager()`.

        Args:
            manager: The installation manager.
        """
        ...
    def setParentWidget(self, parent: PyQt5.QtWidgets.QWidget):
        """
        Set the parent widget for this installer.

        Python plugins usually do not need to re-implement this and can directly access the parent
        widget using `_parentWidget()` once the UI has been initialized.

        Args:
            parent: The parent widget.
        """
        ...

class IPluginInstallerCustom(IPluginInstaller):
    """
    Custom installer for mods. Custom installers receive the archive name and have to go
    from there. They have to be able to extract the archive themself.

    Example of such installers are the external NCC installer or the OMOD installer.
    """

    def __init__(self): ...
    def _manager(self) -> "IInstallationManager":
        """
        Returns:
            The installation manager.
        """
        ...
    def _parentWidget(self) -> PyQt5.QtWidgets.QWidget:
        """
        Returns:
            The parent widget.
        """
        ...
    @abc.abstractmethod
    def install(
        self,
        mod_name: "GuessedString",
        game_name: str,
        archive_name: str,
        version: str,
        nexus_id: int,
    ) -> "InstallResult":
        """
        Install the given archive.

        The mod needs to be created by calling `IOrganizer.createMod` first.

        Args:
            mod_name: Name of the mod to install. As an input parameter this is the suggested name
                (e.g. from meta data) The installer may change this parameter to rename the mod).
            game_name: Name of the game for which the mod is installed.
            archive_name: Name of the archive to install.
            version: Version of the mod. May be empty if the version is not yet known. The plugin is responsible
                for setting the version on the created mod.
            nexus_id: ID of the mod or -1 if unknown. The plugin is responsible for setting the mod ID for the
                created mod.

        Returns:
            The result of the installation process.
        """
        ...
    @abc.abstractmethod
    def isArchiveSupported(self, archive_name: str) -> bool:
        """
        Check if the given file is a supported archive for this installer.

        Args:
            archive_name: Name of the archive.

        Returns:
            True if this installer can handle the archive, False otherwise.
        """
        ...
    @abc.abstractmethod
    def supportedExtensions(self) -> List[str]:
        """
        Returns:
            A list of file extensions that this installer can handle.
        """
        ...

class IPluginInstallerSimple(IPluginInstaller):
    """
    Simple installer for mods. Simple installers only deal with an in-memory structure
    representing the archive and can modify what to install and where by editing this structure.
    Actually extracting the archive is handled by the manager.
    """

    def __init__(self): ...
    def _manager(self) -> "IInstallationManager":
        """
        Returns:
            The installation manager.
        """
        ...
    def _parentWidget(self) -> PyQt5.QtWidgets.QWidget:
        """
        Returns:
            The parent widget.
        """
        ...
    @abc.abstractmethod
    def install(
        self, name: "GuessedString", tree: "IFileTree", version: str, nexus_id: int
    ) -> Union[
        "InstallResult", "IFileTree", Tuple["InstallResult", "IFileTree", str, int]
    ]:
        """
        Install a mod from an archive filetree.

        The installer can modify the given tree and use the manager to extract or create new
        files.

        This method returns different type of objects depending on the actual result of the
        installation. The C++ bindings for this method always returns a tuple (result, tree,
        version, id).

        Args:
            name: Name of the mod to install. As an input parameter this is the suggested name
                (e.g. from meta data) The installer may change this parameter to rename the mod).
            tree: In-memory representation of the archive content.
            version: Version of the mod, or an empty string is unknown.
            nexus_id: ID of the mod, or -1 if unknown.

        Returns:
            In case of failure, the result of the installation, otherwise the modified tree or
        a tuple (result, tree, version, id) containing the result of the installation, the
        modified tree, the new version and the new ID. The tuple can be returned even if the
        installation did not succeed.
        """
        ...

class IPluginList:
    """
    Primary interface to the list of plugins.
    """

    def isMaster(self, name: str) -> bool:
        """
        Check if a plugin is a master file (basically a library, referenced by other plugins).

        In gamebryo games, a master file will usually have a .esm file extension but technically
        an esp can be flagged as master and an esm might not be.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            True if the given plugin is a master plugin, False otherwise or if the file does not exist.
        """
        ...
    def loadOrder(self, name: str) -> int:
        """
        Retrieve the load order of a plugin.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            The load order of the plugin (the order in which the game loads it). If all plugins are enabled this
        is the same as the priority but disabled plugins will have a load order of -1. This also returns -1
        if the plugin does not exist.
        """
        ...
    def masters(self, name: str) -> List[str]:
        """
        Retrieve the list of masters required for a plugin.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            The list of masters for the plugin (filenames with extension, no path).
        """
        ...
    def onPluginMoved(self, callback: Callable[[str, int, int], None]) -> bool:
        """
        Install a new handler to be called when a plugin is moved.

        Args:
            callback: The function to call when a plugin is moved. The first parameter is the plugin name, the
                second the old priority of the plugin and the third one the new priority.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onPluginStateChanged(self, callback: Callable[[str, int], None]) -> bool:
        """
        Install a new handler to be called when a plugin state changes.

        Args:
            callback: The function to call when a plugin state changes. The first parameter is the plugin name, the
                second the new state of the plugin.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def onRefreshed(self, callback: Callable[[None], None]) -> bool:
        """
        Install a new handler to be called when the list of plugins is refreshed.

        Args:
            callback: The function to call when the list of plugins is refreshed.

        Returns:
            True if the handler was installed properly (there are currently no reasons for this to fail).
        """
        ...
    def origin(self, name: str) -> str:
        """
        Retrieve the origin of a plugin. This is either the (internal) name of a mod, `"overwrite"` or `"data"`.

        The internal name of a mod can differ from the display name for disambiguation.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            The name of the origin of the plugin, or an empty string if the plugin does not exist.
        """
        ...
    def pluginNames(self) -> List[str]:
        """
        Returns:
            The list of all plugin names.
        """
        ...
    def priority(self, name: str) -> int:
        """
        Retrieve the priority of a plugin.

        The higher the priority, the more important.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            The priority of the given plugin, or -1 if the plugin does not exist.
        """
        ...
    def setLoadOrder(self, loadorder: List[str]):
        """
        Set the load order.

        Plugins not included in the list will be placed at highest priority in the order they
        were before.

        Args:
            loadorder: The new load order, specified by the list of plugin names, sorted.
        """
        ...
    def setPriority(self, name: str, priority: int) -> bool:
        """
        Change the priority of a plugin.

        Args:
            name: Filename of the plugin (without path but with file extension).
            priority: New priority of the plugin.

        Returns:
            True on success, False if the priority change was not possible. This is usually because
        one of the parameters is invalid. The function returns true even if the plugin was not moved
        at the specified priority (e.g. when trying to move a non-master plugin before a master one).
        """
        ...
    def setState(self, name: str, state: int):
        """
        Set the state of a plugin.

        Args:
            name: Filename of the plugin (without path but with file extension).
            state: New state of the plugin (`INACTIVE` or `ACTIVE`).
        """
        ...
    def state(self, name: str) -> int:
        """
        Retrieve the state of a plugin.

        Args:
            name: Filename of the plugin (without path but with file extension).

        Returns:
            The state of the plugin.
        """
        ...

class IPluginModPage(IPlugin):
    def __init__(self): ...
    def _parentWidget(self) -> PyQt5.QtWidgets.QWidget:
        """
        Returns:
            The parent widget.
        """
        ...
    @abc.abstractmethod
    def displayName(self) -> str:
        """
        Returns:
            The name of the page as displayed in the UI.
        """
        ...
    @abc.abstractmethod
    def handlesDownload(
        self,
        page_url: PyQt5.QtCore.QUrl,
        download_url: PyQt5.QtCore.QUrl,
        fileinfo: "ModRepositoryFileInfo",
    ) -> bool:
        """
        Check if the plugin handles the specified download.

        Args:
            page_url: URL of the page that contains the download link.
            download_url: The download URL.
            fileinfo: Not usable in python.

        Returns:
            True if this plugin wants to handle the specified download, False otherwise.
        """
        ...
    @abc.abstractmethod
    def icon(self) -> PyQt5.QtGui.QIcon:
        """
        Returns:
            The icon to display with the page.
        """
        ...
    @abc.abstractmethod
    def pageURL(self) -> PyQt5.QtCore.QUrl:
        """
        Returns:
            The URL to open when the user wants to visit this mod page.
        """
        ...
    def setParentWidget(self, parent: PyQt5.QtWidgets.QWidget):
        """
        Set the parent widget for this mod page.

        Python plugins usually do not need to re-implement this and can directly access the parent
        widget using `_parentWidget()` once the UI has been initialized.

        Args:
            parent: The parent widget.
        """
        ...
    @abc.abstractmethod
    def useIntegratedBrowser(self) -> bool:
        """
        Indicates if the page should be displayed in the integrated browser.

        Unless the page provides a special means of starting downloads (like the nxm:// url schema
        on nexus),  it will not be possible to handle downloads unless the integrated browser is used!

        Returns:
            True if the page should be opened in the integrated browser, False otherwise.
        """
        ...

class IPluginPreview(IPlugin):
    """
    These plugins add support for previewing files in the data pane. Right now all image formats supported
    by qt are implemented (including dds) but no audio files and no 3d mesh formats.
    """

    def __init__(self): ...
    @abc.abstractmethod
    def genFilePreview(
        self, filename: str, max_size: PyQt5.QtCore.QSize
    ) -> PyQt5.QtWidgets.QWidget:
        """
        Generate a preview for the specified file.

        Args:
            filename: Path to the file to preview.
            max_size: Maximum size of the generated widget.

        Returns:
            The widget showing a preview of the file.
        """
        ...
    @abc.abstractmethod
    def supportedExtensions(self) -> List[str]:
        """
        Returns:
            The list of file extensions that are supported by this preview plugin.
        """
        ...

class IPluginTool(IPlugin):
    """
    This is the simplest of plugin interfaces. Such plugins simply place an icon inside the tools submenu
    and get invoked when the user clicks it. They are expected to have a user interface of some sort. These
    are almost like independent applications except they can access all Mod Organizer interfaces like querying
    and modifying the current profile, mod list, load order, use MO to install mods and so on. A tool plugin
    can (and should!) integrate its UI as a window inside MO and thus doesn't have to initialize a windows
    application itself.
    """

    def __init__(self): ...
    def _parentWidget(self) -> PyQt5.QtWidgets.QWidget:
        """
        Returns:
            The parent widget.
        """
        ...
    @abc.abstractmethod
    def display(self):
        """
        Called when the user starts the tool.
        """
        ...
    @abc.abstractmethod
    def displayName(self) -> str:
        """
        Returns:
            The display name for this tool, as shown in the tool menu.
        """
        ...
    @abc.abstractmethod
    def icon(self) -> PyQt5.QtGui.QIcon:
        """
        Returns:
            The icon for this tool, or a default-constructed QICon().
        """
        ...
    def setParentWidget(self, parent: PyQt5.QtWidgets.QWidget):
        """
        Set the parent widget for this tool.

        Python plugins usually do not need to re-implement this and can directly access the parent
        widget using `_parentWidget()` once the UI has been initialized.

        Args:
            parent: The parent widget.
        """
        ...
    @abc.abstractmethod
    def tooltip(self) -> str:
        """
        Returns:
            The tooltip for this tool.
        """
        ...

class IProfile:
    def absolutePath(self) -> str: ...
    def invalidationActive(self) -> Tuple[bool, bool]: ...
    def localSavesEnabled(self) -> bool: ...
    def localSettingsEnabled(self) -> bool: ...
    def name(self) -> str: ...

class ISaveGame:
    """
    Base class for information about what is in a save game.
    """

    def __init__(self): ...
    def allFiles(self) -> List[str]:
        """
        Returns:
            The list of all files related to this save.
        """
        ...
    def getCreationTime(self) -> PyQt5.QtCore.QDateTime:
        """
        Retrieve the creation time of the save.

        The creation time of a save is not always the same as the creation time of
        the file containing the save.

        Returns:
            The creation time of the save.
        """
        ...
    def getFilename(self) -> str:
        """
        Returns:
            The name of the (main) save file.
        """
        ...
    def getSaveGroupIdentifier(self) -> str:
        """
        Retrieve the name of the group this files belong to.

        The name can be used to identify sets of saves to transfer between profiles. For
        RPG games, this is usually the name of a character.

        Returns:
            The group identifier for this save game.
        """
        ...
    def hasScriptExtenderFile(self) -> bool:
        """
        Returns:
            True if this save game has an associated script extender save, False otherwise.
        """
        ...

class ISaveGameInfoWidget(PyQt5.QtWidgets.QWidget):
    """
    Base class for a save game info widget.
    """

    def __init__(self, parent: PyQt5.QtWidgets.QWidget = None):
        """
        Args:
            parent: Parent widget.
        """
        ...
    def _widget(self) -> PyQt5.QtWidgets.QWidget:
        """
        Returns:
            The underlying `QWidget`.
        """
        ...
    @abc.abstractmethod
    def setSave(self, save: str):
        """
        Set the save file to display in this widget.

        Args:
            save: Path to the save file.
        """
        ...

class LocalSavegames(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def mappings(self, profile_save_dir: PyQt5.QtCore.QDir) -> List["Mapping"]: ...
    @abc.abstractmethod
    def prepareProfile(self, profile: "IProfile") -> bool: ...

class Mapping:
    @property
    def createTarget(self) -> bool: ...
    @createTarget.setter
    def createTarget(self, arg0: bool): ...
    @property
    def destination(self) -> str: ...
    @destination.setter
    def destination(self, arg0: str): ...
    @property
    def isDirectory(self) -> bool: ...
    @isDirectory.setter
    def isDirectory(self, arg0: bool): ...
    @property
    def source(self) -> str: ...
    @source.setter
    def source(self, arg0: str): ...
    def __init__(self):
        """
        Creates an empty Mapping.
        """
        ...

class ModDataChecker(abc.ABC):
    """
    Game feature that is used to check the content of a data tree.
    """

    class CheckReturn(Enum):
        INVALID = ...
        FIXABLE = ...
        VALID = ...
        def __and__(self, other: int) -> bool: ...
        def __or__(self, other: int) -> bool: ...
        def __rand__(self, other: int) -> bool: ...
        def __ro__(self, other: int) -> bool: ...
    FIXABLE: "ModDataChecker.CheckReturn" = ...
    INVALID: "ModDataChecker.CheckReturn" = ...
    VALID: "ModDataChecker.CheckReturn" = ...
    def __init__(self): ...
    @abc.abstractmethod
    def dataLooksValid(self, filetree: "IFileTree") -> "ModDataChecker.CheckReturn":
        """
        Check that the given filetree represent a valid mod layout, or can be easily
        fixed.

        This method is mainly used during installation (to find which installer should
        be used or to recurse into multi-level archives), or to quickly indicates to a
        user if a mod looks valid.

        This method does not have to be exact, it only has to indicate if the given tree
        looks like a valid mod or not by quickly checking the structure (heavy operations
        should be avoided).

        If the tree can be fixed by the `fix()` method, this method should return `FIXABLE`.
        `FIXABLE` should only be returned when it is guaranteed that `fix()` can fix the tree.

        Args:
            filetree: The tree starting at the root of the "data" folder.

        Returns:
            Whether the tree is invalid, fixable or valid.
        """
        ...
    def fix(self, filetree: "IFileTree") -> Optional["IFileTree"]:
        """
        Try to fix the given tree.

        This method is used during installation to try to fix invalid archives and will only be
        called if dataLooksValid returned `FIXABLE`.

        Args:
            filetree: The tree to try to fix. Can be modified during the process.

        Returns:
            The fixed tree, or a null pointer if the tree could not be fixed.
        """
        ...

class ModDataContent(abc.ABC):
    """
    The ModDataContent feature is used (when available) to indicate to users the content
    of mods in the "Content" column.

    The feature exposes a list of possible content types, each associated with an ID, a name
    and an icon. The icon is the path to either:

      - A Qt resource or;
      - A file on the disk.

    In order to facilitate the implementation, MO2 already provides a set of icons that can
    be used. Those icons are all under ``:/MO/gui/content`` (e.g. ``:/MO/gui/content/plugin`` or ``:/MO/gui/content/music`` `).

    The list of available icons is:

      - ``plugin``: |plugin-icon|
      - ``skyproc``: |skyproc-icon|
      - ``texture``: |texture-icon|
      - ``music``: |music-icon|
      - ``sound``: |sound-icon|
      - ``interface``: |interface-icon|
      - ``skse``: |skse-icon|
      - ``script``: |script-icon|
      - ``mesh``: |mesh-icon|
      - ``string``: |string-icon|
      - ``bsa``: |bsa-icon|
      - ``menu``: |menu-icon|
      - ``inifile``: |inifile-icon|
      - ``modgroup``: |modgroup-icon|

    .. |plugin-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/jigsaw-piece.png
    .. |skyproc-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/hand-of-god.png
    .. |texture-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/empty-chessboard.png
    .. |music-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/double-quaver.png
    .. |sound-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/lyre.png
    .. |interface-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/usable.png
    .. |skse-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/checkbox-tree.png
    .. |script-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/tinker.png
    .. |mesh-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/breastplate.png
    .. |string-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/conversation.png
    .. |bsa-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/locked-chest.png
    .. |menu-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/config.png
    .. |inifile-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/feather-and-scroll.png
    .. |modgroup-icon| image:: https://raw.githubusercontent.com/ModOrganizer2/modorganizer/master/src/resources/contents/xedit.png
    """

    class Content:
        @property
        def icon(self) -> str: ...
        @property
        def id(self) -> int: ...
        @property
        def name(self) -> str: ...
        def __init__(self, id: int, name: str, icon: str, filter_only: bool = False):
            """
            Args:
                id: ID of this content.
                name: Name of this content.
                icon: Path to the icon for this content. Can be either a path
                    to an image on the disk, or to a resource. Can be an empty string if filterOnly
                    is true.
                filter_only: Indicates if the content should only be show in the filter
                    criteria and not in the actual Content column.
            """
            ...
        def isOnlyForFilter(self) -> bool:
            """
            Returns:
                True if this content is only meant to be used as a filter criteria.
            """
            ...
    def __init__(self): ...
    @abc.abstractmethod
    def getAllContents(self) -> List["ModDataContent.Content"]:
        """
        Returns:
            The list of all possible contents for the corresponding game.
        """
        ...
    @abc.abstractmethod
    def getContentsFor(self, filetree: "IFileTree") -> List[int]:
        """
        Retrieve the list of contents in the given tree.

        Args:
            filetree: The tree corresponding to the mod to retrieve contents for.

        Returns:
            The IDs of the content in the given tree.
        """
        ...

class ModRepositoryFileInfo:
    @property
    def categoryID(self) -> int: ...
    @categoryID.setter
    def categoryID(self, arg0: int): ...
    @property
    def description(self) -> str: ...
    @description.setter
    def description(self, arg0: str): ...
    @property
    def fileCategory(self) -> int: ...
    @fileCategory.setter
    def fileCategory(self, arg0: int): ...
    @property
    def fileID(self) -> int: ...
    @fileID.setter
    def fileID(self, arg0: int): ...
    @property
    def fileName(self) -> str: ...
    @fileName.setter
    def fileName(self, arg0: str): ...
    @property
    def fileSize(self) -> int: ...
    @fileSize.setter
    def fileSize(self, arg0: int): ...
    @property
    def fileTime(self) -> PyQt5.QtCore.QDateTime: ...
    @fileTime.setter
    def fileTime(self, arg0: PyQt5.QtCore.QDateTime): ...
    @property
    def gameName(self) -> str: ...
    @gameName.setter
    def gameName(self, arg0: str): ...
    @property
    def modID(self) -> int: ...
    @modID.setter
    def modID(self, arg0: int): ...
    @property
    def modName(self) -> str: ...
    @modName.setter
    def modName(self, arg0: str): ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, arg0: str): ...
    @property
    def newestVersion(self) -> "VersionInfo": ...
    @newestVersion.setter
    def newestVersion(self, arg0: "VersionInfo"): ...
    @property
    def repository(self) -> str: ...
    @repository.setter
    def repository(self, arg0: str): ...
    @property
    def uri(self) -> str: ...
    @uri.setter
    def uri(self, arg0: str): ...
    @property
    def userData(self) -> MoVariant: ...
    @userData.setter
    def userData(self, arg0: MoVariant): ...
    @property
    def version(self) -> "VersionInfo": ...
    @version.setter
    def version(self, arg0: "VersionInfo"): ...
    @overload
    def __init__(self, other: "ModRepositoryFileInfo"): ...
    @overload
    def __init__(
        self, game_name: str = None, mod_id: int = None, file_id: int = None
    ): ...
    def __str__(self) -> str: ...
    @staticmethod
    def createFromJson(data: str) -> "ModRepositoryFileInfo": ...

class PluginSetting:
    """
    Class to hold the user-configurable parameters a plugin accepts. The purpose of this class is
    only to inform the application what settings to offer to the user, it does not hold the actual value.
    """

    @property
    def default_value(self) -> MoVariant: ...
    @default_value.setter
    def default_value(self, arg0: MoVariant): ...
    @property
    def description(self) -> str: ...
    @description.setter
    def description(self, arg0: str): ...
    @property
    def key(self) -> str: ...
    @key.setter
    def key(self, arg0: str): ...
    def __init__(self, key: str, description: str, default_value: MoVariant):
        """
        Args:
            key: Name of the setting.
            description: Description of the setting.
            default_value: Default value of the setting.
        """
        ...

class SaveGameInfo(abc.ABC):
    """
    Feature to get hold of stuff to do with save games.
    """

    def __init__(self): ...
    @abc.abstractmethod
    def getMissingAssets(self, filepath: str) -> Dict[str, List[str]]:
        """
        Retrieve missing assets from the save.

        Args:
            filepath: Path to the save file.

        Returns:
            A collection of missing assets and the modules that can supply those assets.
        """
        ...
    @abc.abstractmethod
    def getSaveGameInfo(self, filepath: str) -> "ISaveGame":
        """
        Retrieve the information about the supplied save game.

        Args:
            filepath: Path to the save file.

        Returns:
            A SaveGame corresponding to the given save file.
        """
        ...
    @abc.abstractmethod
    def getSaveGameWidget(
        self, parent: PyQt5.QtWidgets.QWidget
    ) -> Optional["ISaveGameInfoWidget"]:
        """
        Retrieve a widget to display over the save game list.

        This method is allowed to return `None` in case no widget has been implemented.

        Args:
            parent: The parent widget.

        Returns:
            A SaveGameInfoWidget to display information about save game.
        """
        ...
    @abc.abstractmethod
    def hasScriptExtenderSave(self, filepath: str) -> bool:
        """
        Check whether or not the save has a paired script extender save.

        Args:
            filepath: Path to the save file.

        Returns:
            True if the given save file has a paired script extender save, False otherwise.
        """
        ...

class ScriptExtender(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def BinaryName(self) -> str:
        """
        Returns:
            The name of the script extender binary.
        """
        ...
    @abc.abstractmethod
    def PluginPath(self) -> str:
        """
        Returns:
            The script extender plugin path, relative to the data folder.
        """
        ...
    @abc.abstractmethod
    def getArch(self) -> int:
        """
        Returns:
            The CPU platform of the extender.
        """
        ...
    @abc.abstractmethod
    def getExtenderVersion(self) -> str:
        """
        Returns:
            The version of the script extender.
        """
        ...
    @abc.abstractmethod
    def isInstalled(self) -> bool:
        """
        Returns:
            True if the script extender is installed, False otherwise.
        """
        ...
    @abc.abstractmethod
    def loaderName(self) -> str:
        """
        Returns:
            The loader to use to ensure the game runs with the script extender.
        """
        ...
    @abc.abstractmethod
    def loaderPath(self) -> str:
        """
        Returns:
            The fullpath to the script extender loader.
        """
        ...
    @abc.abstractmethod
    def saveGameAttachmentExtensions(self) -> List[str]:
        """
        Returns:
            Additional savegame attachments.
        """
        ...

class UnmanagedMods(abc.ABC):
    def __init__(self): ...
    @abc.abstractmethod
    def displayName(self, mod_name: str) -> str:
        """
        Retrieve the display name of a given mod.

        Args:
            mod_name: Internal name of the mod.

        Returns:
            The display name of the mod.
        """
        ...
    @abc.abstractmethod
    def mods(self, official_only: bool) -> List[str]:
        """
        Retrieve the list of unmanaged mods for the corresponding game.

        Args:
            official_only: Retrieve only unmanaged official mods.

        Returns:
            The list of unmanaged mods (internal names).
        """
        ...
    @abc.abstractmethod
    def referenceFile(self, mod_name: str) -> PyQt5.QtCore.QFileInfo:
        """
        Retrieve the reference file for the requested mod.

        Example: For Bethesda games, the reference file may be the main
        plugin (esp or esm) for the game or a DLCs.

        Args:
            mod_name: Internal name of the mod.

        Returns:
            The reference file (absolute path) for the requested mod.
        """
        ...
    @abc.abstractmethod
    def secondaryFiles(self, mod_name: str) -> List[str]:
        """
        Retrieve the secondary files for the requested mod.

        Example: For Bethesda games, the secondary files may be the archives
        corresponding to the reference file.

        Args:
            mod_name: Internal name of the mod.

        Returns:
            The secondary files (absolute paths) for the request mod.
        """
        ...

class VersionInfo:
    """
    Represents the version of a mod or plugin.
    """

    @overload
    def __init__(self):
        """
        Construct an invalid VersionInfo.
        """
        ...
    @overload
    def __init__(self, value: str, scheme: "VersionScheme" = VersionScheme.DISCOVER):
        """
        Construct a VersionInfo by parsing the given string according to the given scheme.

        Args:
            value: String to parse.
            scheme: Scheme to use to parse the string.
        """
        ...
    @overload
    def __init__(
        self,
        major: int,
        minor: int,
        subminor: int,
        subsubminor: int,
        release_type: "ReleaseType" = ReleaseType.FINAL,
    ):
        """
        Construct a VersionInfo using the given elements.

        Args:
            major: Major version.
            minor: Minor version.
            subminor: Subminor version.
            subsubminor: Subsubminor version.
            release_type: Type of release.
        """
        ...
    @overload
    def __init__(
        self,
        major: int,
        minor: int,
        subminor: int,
        release_type: "ReleaseType" = ReleaseType.FINAL,
    ):
        """
        Construct a VersionInfo using the given elements.

        Args:
            major: Major version.
            minor: Minor version.
            subminor: Subminor version.
            release_type: Type of release.
        """
        ...
    @overload
    def __eq__(self, arg2: "VersionInfo") -> bool: ...
    @overload
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, arg2: "VersionInfo") -> bool: ...
    def __gt__(self, arg2: "VersionInfo") -> bool: ...
    def __le__(self, arg2: "VersionInfo") -> bool: ...
    def __lt__(self, arg2: "VersionInfo") -> bool: ...
    @overload
    def __ne__(self, arg2: "VersionInfo") -> bool: ...
    @overload
    def __ne__(self, other: object) -> bool: ...
    def __str__(self) -> str:
        """
        Returns:
            See `canonicalString()`.
        """
        ...
    def canonicalString(self) -> str:
        """
        Returns:
            A canonical string representing this version, that can be stored and then parsed using the parse() method.
        """
        ...
    def clear(self):
        """
        Resets this VersionInfo to an invalid version.
        """
        ...
    def displayString(self, forced_segments: int = 2) -> str:
        """
        Args:
            forced_segments: The number of version segments to display even if the version is 0. 1 is major, 2 is major
                and minor, etc. The only implemented ranges are (-inf,2] for major/minor, [3] for major/minor/subminor,
                and [4,inf) for major/minor/subminor/subsubminor. This only versions with a regular scheme.

        Returns:
            A string for display to the user. The returned string may not contain enough information to reconstruct this version info.
        """
        ...
    def isValid(self) -> bool:
        """
        Returns:
            True if this VersionInfo is valid, False otherwise.
        """
        ...
    def parse(
        self,
        value: str,
        scheme: "VersionScheme" = VersionScheme.DISCOVER,
        manual_input: bool = False,
    ):
        """
        Update this VersionInfo by parsing the given string using the given scheme.

        Args:
            value: String to parse.
            scheme: Scheme to use to parse the string.
            manual_input: True if the given string should be treated as user input.
        """
        ...
    def scheme(self) -> "VersionScheme":
        """
        Returns:
            The version scheme in effect for this VersionInfo.
        """
        ...
