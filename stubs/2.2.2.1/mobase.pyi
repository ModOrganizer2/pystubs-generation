__version__ = "2.2.2.1"

from enum import Enum
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Tuple,
    Union,
    Any,
    Optional,
    Callable,
    overload,
)
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

MoVariant = Union[bool, int, str, List[Any], Dict[str, Any]]

class InterfaceNotImplemented:
    pass

class GuessQuality(Enum):
    invalid = ...
    fallback = ...
    good = ...
    meta = ...
    preset = ...
    user = ...

class InstallResult(Enum):
    success = ...
    failed = ...
    canceled = ...
    manualRequested = ...
    notAttempted = ...

class LoadOrderMechanism(Enum):
    FileTime = ...
    PluginsTxt = ...

class ModState(Enum):
    exists = ...
    active = ...
    essential = ...
    empty = ...
    endorsed = ...
    valid = ...
    alternate = ...

class PluginState(Enum):
    missing = ...
    inactive = ...
    active = ...

class ProfileSetting(Enum):
    mods = ...
    configuration = ...
    savegames = ...
    preferDefaults = ...

class ReleaseType(Enum):
    prealpha = ...
    alpha = ...
    beta = ...
    candidate = ...
    final = ...

class SortMechanism(Enum):
    NONE = ...
    MLOX = ...
    BOSS = ...
    LOOT = ...

class VersionScheme(Enum):
    discover = ...
    regular = ...
    decimalmark = ...
    numbersandletters = ...
    date = ...
    literal = ...

class BSAInvalidation:
    def __init__(self):
        pass
    def activate(self, arg1: "IProfile"):
        pass
    def deactivate(self, arg1: "IProfile"):
        pass
    def isInvalidationBSA(self, arg1: str) -> bool:
        pass

class DataArchives:
    def __init__(self):
        pass
    def addArchive(self, arg1: "IProfile", arg2: int, arg3: str):
        pass
    def archives(self, arg1: "IProfile") -> List[str]:
        pass
    def removeArchive(self, arg1: "IProfile", arg2: str):
        pass
    def vanillaArchives(self) -> List[str]:
        pass

class ExecutableInfo:
    def __init__(self, arg1: str, arg2: PyQt5.QtCore.QFileInfo):
        pass
    def arguments(self) -> List[str]:
        pass
    def asCustom(self) -> "ExecutableInfo":
        pass
    def binary(self) -> PyQt5.QtCore.QFileInfo:
        pass
    def isCustom(self) -> bool:
        pass
    def isValid(self) -> bool:
        pass
    def steamAppID(self) -> str:
        pass
    def title(self) -> str:
        pass
    def withArgument(self, arg1: str) -> "ExecutableInfo":
        pass
    def withSteamAppId(self, arg1: str) -> "ExecutableInfo":
        pass
    def withWorkingDirectory(self, arg1: PyQt5.QtCore.QDir) -> "ExecutableInfo":
        pass
    def workingDirectory(self) -> PyQt5.QtCore.QDir:
        pass

class GamePlugins:
    def __init__(self):
        pass
    def getLoadOrder(self, arg1: List[str]):
        pass
    def lightPluginsAreSupported(self) -> bool:
        pass
    def readPluginLists(self, arg1: "IPluginList"):
        pass
    def writePluginLists(self, arg1: "IPluginList"):
        pass

class GuessedString:
    def __init__(self):
        pass
    def update(self, arg1: str, arg2: "GuessQuality") -> "GuessedString":
        pass
    def variants(self) -> List[str]:
        pass

class IDownloadManager(PyQt5.QtCore.QObject):
    downloadComplete: PyQt5.QtCore.pyqtSignal = ...  # downloadComplete[int]
    downloadPaused: PyQt5.QtCore.pyqtSignal = ...  # downloadPaused[int]
    downloadFailed: PyQt5.QtCore.pyqtSignal = ...  # downloadFailed[int]
    downloadRemoved: PyQt5.QtCore.pyqtSignal = ...  # downloadRemoved[int]
    def __init__(self):
        pass
    def downloadPath(self, arg1: int) -> str:
        pass
    def startDownloadNexusFile(self, arg1: int, arg2: int) -> int:
        pass
    def startDownloadURLs(self, arg1: List[str]) -> int:
        pass

class IInstallationManager:
    def __init__(self):
        pass
    def extractFile(self, arg1: str) -> str:
        pass
    def extractFiles(self, arg1: List[str], arg2: bool) -> List[str]:
        pass
    def installArchive(
        self, arg1: "GuessedString", arg2: str, arg3: int
    ) -> "InstallResult":
        pass
    def setURL(self, arg1: str):
        pass

class IModInterface:
    def __init__(self):
        pass
    def absolutePath(self) -> str:
        pass
    def addCategory(self, arg1: str):
        pass
    def addNexusCategory(self, arg1: int):
        pass
    def categories(self) -> List[str]:
        pass
    def name(self) -> str:
        pass
    def remove(self) -> bool:
        pass
    def removeCategory(self, arg1: str) -> bool:
        pass
    def setGameName(self, arg1: str):
        pass
    def setIsEndorsed(self, arg1: bool):
        pass
    def setName(self, arg1: str) -> bool:
        pass
    def setNewestVersion(self, arg1: VersionInfo):
        pass
    def setNexusID(self, arg1: int):
        pass
    def setVersion(self, arg1: VersionInfo):
        pass

class IModList:
    def __init__(self):
        pass
    def allMods(self) -> List[str]:
        pass
    def displayName(self, arg1: str) -> str:
        pass
    def onModMoved(self, arg1: Callable[[str, int, int], None]) -> bool:
        pass
    def onModStateChanged(self, arg1: Callable[[str, int], None]) -> bool:
        pass
    def priority(self, arg1: str) -> int:
        pass
    def setActive(self, arg1: str, arg2: bool) -> bool:
        pass
    def setPriority(self, arg1: str, arg2: int) -> bool:
        pass
    def state(self, arg1: str) -> int:
        pass

class IModRepositoryBridge(PyQt5.QtCore.QObject):
    descriptionAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # descriptionAvailable[str, int, QVariant, QVariant]
    filesAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # filesAvailable[str, int, QVariant, List[ModRepositoryFileInfo]]
    fileInfoAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # fileInfoAvailable[str, int, int, QVariant, QVariant]
    downloadURLsAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # downloadURLsAvailable[str, int, int QVariant, QVariant]
    endorsementsAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # endorsementsAvailable[QVariant, QVariant]
    endorsementToggled: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # endorsementToggled[str, int, QVariant, QVariant]
    trackedModsAvailable: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # trackedModsAvailable[QVariant, QVariant]
    trackingToggled: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # trackingToggled[str, int, QVariant, bool]
    requestFailed: PyQt5.QtCore.pyqtSignal = (
        ...
    )  # requestFailed[str, int, int, QVariant, NetworkError, str]
    def __init__(self):
        pass
    def requestDescription(self, arg1: str, arg2: int, arg3: MoVariant):
        pass
    def requestDownloadURL(self, arg1: str, arg2: int, arg3: int, arg4: MoVariant):
        pass
    def requestFileInfo(self, arg1: str, arg2: int, arg3: int, arg4: MoVariant):
        pass
    def requestFiles(self, arg1: str, arg2: int, arg3: MoVariant):
        pass
    def requestToggleEndorsement(
        self, arg1: str, arg2: int, arg3: str, arg4: bool, arg5: MoVariant
    ):
        pass

class IOrganizer:
    def __init__(self):
        pass
    def appVersion(self) -> VersionInfo:
        pass
    def basePath(self) -> str:
        pass
    def createMod(self, arg1: "GuessedString") -> "IModInterface":
        pass
    def createNexusBridge(self) -> "IModRepositoryBridge":
        pass
    def downloadManager(self) -> "IDownloadManager":
        pass
    def downloadsPath(self) -> str:
        pass
    def findFileInfos(
        self, arg1: str, arg2: Callable[[FileInfo], bool]
    ) -> List[FileInfo]:
        pass
    def findFiles(self, arg1: str, arg2: Callable[[str], bool]) -> List[str]:
        pass
    def getFileOrigins(self, arg1: str) -> List[str]:
        pass
    def getGame(self, arg1: str) -> "IPluginGame":
        pass
    def getMod(self, arg1: str) -> "IModInterface":
        pass
    def installMod(self, arg1: str, arg2: str = "") -> "IModInterface":
        pass
    def listDirectories(self, arg1: str) -> List[str]:
        pass
    def managedGame(self) -> "IPluginGame":
        pass
    def modDataChanged(self, arg1: "IModInterface"):
        pass
    def modList(self) -> "IModList":
        pass
    def modsPath(self) -> str:
        pass
    def modsSortedByProfilePriority(self) -> List[str]:
        pass
    def onAboutToRun(self, arg1: Callable[[str], bool]) -> bool:
        pass
    def onFinishedRun(self, arg1: Callable[[str, int], None]) -> bool:
        pass
    def onModInstalled(self, arg1: Callable[[str], None]) -> bool:
        pass
    def overwritePath(self) -> str:
        pass
    def persistent(self, arg1: str, arg2: str, arg3: MoVariant) -> MoVariant:
        pass
    def pluginDataPath(self) -> str:
        pass
    def pluginList(self) -> "IPluginList":
        pass
    def pluginSetting(self, arg1: str, arg2: str) -> MoVariant:
        pass
    def profile(self) -> "IProfile":
        pass
    def profileName(self) -> str:
        pass
    def profilePath(self) -> str:
        pass
    def refreshModList(self, arg1: bool):
        pass
    def removeMod(self, arg1: "IModInterface") -> bool:
        pass
    def resolvePath(self, arg1: str) -> str:
        pass
    def setPersistent(self, arg1: str, arg2: str, arg3: MoVariant, arg4: bool):
        pass
    def setPluginSetting(self, arg1: str, arg2: str, arg3: MoVariant):
        pass
    def startApplication(
        self,
        arg1: str,
        arg2: List[str] = None,
        arg3: str = "",
        arg4: str = "",
        arg5: str = "",
        arg6: bool = False,
    ) -> "object":
        pass
    @staticmethod
    def waitForApplication(arg0: "object", arg1: int) -> object:
        pass

class IPlugin:
    def __init__(self):
        pass

class IPluginDiagnose:
    def __init__(self):
        pass
    def _invalidate(self):
        pass
    def activeProblems(self) -> List[int]:
        pass
    def fullDescription(self, arg1: int) -> str:
        pass
    def hasGuidedFix(self, arg1: int) -> bool:
        pass
    def shortDescription(self, arg1: int) -> str:
        pass
    def startGuidedFix(self, arg1: int):
        pass

class IPluginFileMapper:
    def __init__(self):
        pass
    def mappings(self) -> List[Mapping]:
        pass

class IPluginGame:
    def __init__(self):
        pass
    def CCPlugins(self) -> List[str]:
        pass
    def DLCPlugins(self) -> List[str]:
        pass
    def author(self) -> str:
        pass
    def binaryName(self) -> str:
        pass
    def dataDirectory(self) -> PyQt5.QtCore.QDir:
        pass
    def description(self) -> str:
        pass
    def documentsDirectory(self) -> PyQt5.QtCore.QDir:
        pass
    def executables(self) -> List[ExecutableInfo]:
        pass
    def featureBSAInvalidation(self) -> "BSAInvalidation":
        pass
    def featureDataArchives(self) -> "DataArchives":
        pass
    def featureGamePlugins(self) -> "GamePlugins":
        pass
    def featureLocalSavegames(self) -> "LocalSavegames":
        pass
    def featureSaveGameInfo(self) -> "SaveGameInfo":
        pass
    def featureScriptExtender(self) -> "ScriptExtender":
        pass
    def featureUnmanagedMods(self) -> "UnmanagedMods":
        pass
    def gameDirectory(self) -> PyQt5.QtCore.QDir:
        pass
    def gameIcon(self) -> PyQt5.QtGui.QIcon:
        pass
    def gameName(self) -> str:
        pass
    def gameNexusName(self) -> str:
        pass
    def gameShortName(self) -> str:
        pass
    def gameVariants(self) -> List[str]:
        pass
    def gameVersion(self) -> str:
        pass
    def getLauncherName(self) -> str:
        pass
    def iniFiles(self) -> List[str]:
        pass
    def init(self, arg1: "IOrganizer") -> bool:
        pass
    def initializeProfile(self, arg1: PyQt5.QtCore.QDir, arg2: int):
        pass
    def isActive(self) -> bool:
        pass
    def isInstalled(self) -> bool:
        pass
    def loadOrderMechanism(self) -> "LoadOrderMechanism":
        pass
    def looksValid(self, arg1: PyQt5.QtCore.QDir) -> bool:
        pass
    def name(self) -> str:
        pass
    def nexusGameID(self) -> int:
        pass
    def nexusModOrganizerID(self) -> int:
        pass
    def primaryPlugins(self) -> List[str]:
        pass
    def primarySources(self) -> List[str]:
        pass
    def savegameExtension(self) -> str:
        pass
    def savegameSEExtension(self) -> str:
        pass
    def savesDirectory(self) -> PyQt5.QtCore.QDir:
        pass
    def setGamePath(self, arg1: str):
        pass
    def setGameVariant(self, arg1: str):
        pass
    def settings(self) -> List[PluginSetting]:
        pass
    def sortMechanism(self) -> "SortMechanism":
        pass
    def steamAPPId(self) -> str:
        pass
    def validShortNames(self) -> List[str]:
        pass
    def version(self) -> VersionInfo:
        pass

class IPluginInstallerCustom:
    def __init__(self):
        pass
    def setParentWidget(self, arg1: PyQt5.QtWidgets.QWidget):
        pass

class IPluginList:
    def __init__(self):
        pass
    def isMaster(self, arg1: str) -> bool:
        pass
    def loadOrder(self, arg1: str) -> int:
        pass
    def masters(self, arg1: str) -> List[str]:
        pass
    def onPluginMoved(self, arg1: Callable[[str, int, int], None]) -> bool:
        pass
    def onRefreshed(self, arg1: Callable[[None], None]) -> bool:
        pass
    def origin(self, arg1: str) -> str:
        pass
    def pluginNames(self) -> List[str]:
        pass
    def priority(self, arg1: str) -> int:
        pass
    def setLoadOrder(self, arg1: List[str]):
        pass
    def setState(self, arg1: str, arg2: int):
        pass
    def state(self, arg1: str) -> int:
        pass

class IPluginModPage:
    def __init__(self):
        pass
    def setParentWidget(self, arg1: PyQt5.QtWidgets.QWidget):
        pass

class IPluginPreview:
    def __init__(self):
        pass

class IPluginTool(IPlugin):
    def __init__(self):
        pass
    def setParentWidget(self, arg1: PyQt5.QtWidgets.QWidget):
        pass

class IProfile:
    def __init__(self):
        pass
    def absolutePath(self) -> str:
        pass
    def invalidationActive(self, arg1: InterfaceNotImplemented) -> bool:
        pass
    def localSavesEnabled(self) -> bool:
        pass
    def localSettingsEnabled(self) -> bool:
        pass
    def name(self) -> str:
        pass

class ISaveGame:
    def __init__(self):
        pass
    def allFiles(self) -> List[str]:
        pass
    def getCreationTime(self) -> PyQt5.QtCore.QDateTime:
        pass
    def getFilename(self) -> str:
        pass
    def getSaveGroupIdentifier(self) -> str:
        pass
    def hasScriptExtenderFile(self) -> bool:
        pass

class LocalSavegames:
    def __init__(self):
        pass
    def mappings(self, arg1: PyQt5.QtCore.QDir) -> List[Mapping]:
        pass
    def prepareProfile(self, arg1: "IProfile") -> bool:
        pass

class Mapping:
    @property
    def createTarget(self) -> bool:
        pass
    @createTarget.setter
    def createTarget(self, arg0: bool):
        pass
    @property
    def destination(self) -> str:
        pass
    @destination.setter
    def destination(self, arg0: str):
        pass
    @property
    def isDirectory(self) -> bool:
        pass
    @isDirectory.setter
    def isDirectory(self, arg0: bool):
        pass
    @property
    def source(self) -> str:
        pass
    @source.setter
    def source(self, arg0: str):
        pass
    def __init__(self):
        pass

class ModRepositoryBridge:
    @overload
    def __init__(self):
        pass
    @overload
    def __init__(self, arg1: "IModRepositoryBridge"):
        pass
    def onDescriptionAvailable(self, arg1: "object"):
        pass
    def onEndorsementToggled(self, arg1: "object"):
        pass
    def onFileInfoAvailable(self, arg1: "object"):
        pass
    def onFilesAvailable(self, arg1: "object"):
        pass
    def onRequestFailed(self, arg1: "object"):
        pass
    def requestDescription(self, arg1: str, arg2: int, arg3: MoVariant):
        pass
    def requestFileInfo(self, arg1: str, arg2: int, arg3: int, arg4: MoVariant):
        pass
    def requestFiles(self, arg1: str, arg2: int, arg3: MoVariant):
        pass
    def requestToggleEndorsement(
        self, arg1: str, arg2: int, arg3: str, arg4: bool, arg5: MoVariant
    ):
        pass

class ModRepositoryFileInfo:
    @property
    def categoryID(self) -> int:
        pass
    @categoryID.setter
    def categoryID(self, arg0: int):
        pass
    @property
    def description(self) -> str:
        pass
    @description.setter
    def description(self, arg0: str):
        pass
    @property
    def fileCategory(self) -> int:
        pass
    @fileCategory.setter
    def fileCategory(self, arg0: int):
        pass
    @property
    def fileID(self) -> int:
        pass
    @fileID.setter
    def fileID(self, arg0: int):
        pass
    @property
    def fileName(self) -> str:
        pass
    @fileName.setter
    def fileName(self, arg0: str):
        pass
    @property
    def fileSize(self) -> int:
        pass
    @fileSize.setter
    def fileSize(self, arg0: int):
        pass
    @property
    def fileTime(self) -> PyQt5.QtCore.QDateTime:
        pass
    @fileTime.setter
    def fileTime(self, arg0: PyQt5.QtCore.QDateTime):
        pass
    @property
    def gameName(self) -> str:
        pass
    @gameName.setter
    def gameName(self, arg0: str):
        pass
    @property
    def modID(self) -> int:
        pass
    @modID.setter
    def modID(self, arg0: int):
        pass
    @property
    def modName(self) -> str:
        pass
    @modName.setter
    def modName(self, arg0: str):
        pass
    @property
    def name(self) -> str:
        pass
    @name.setter
    def name(self, arg0: str):
        pass
    @property
    def newestVersion(self) -> VersionInfo:
        pass
    @newestVersion.setter
    def newestVersion(self, arg0: VersionInfo):
        pass
    @property
    def repository(self) -> str:
        pass
    @repository.setter
    def repository(self, arg0: str):
        pass
    @property
    def uri(self) -> str:
        pass
    @uri.setter
    def uri(self, arg0: str):
        pass
    @property
    def userData(self) -> MoVariant:
        pass
    @userData.setter
    def userData(self, arg0: MoVariant):
        pass
    @property
    def version(self) -> VersionInfo:
        pass
    @version.setter
    def version(self, arg0: VersionInfo):
        pass
    @overload
    def __init__(self):
        pass
    @overload
    def __init__(self, arg1: "ModRepositoryFileInfo"):
        pass
    @overload
    def __init__(self, arg1: str = None, arg2: int = None, arg3: int = None):
        pass
    @staticmethod
    def createFromJson(arg0: str) -> "ModRepositoryFileInfo":
        pass
    def toString(self) -> str:
        pass

class PluginSetting:
    def __init__(self, arg1: str, arg2: str, arg3: MoVariant):
        pass

class SaveGameInfo:
    def __init__(self):
        pass
    def getMissingAssets(self, arg1: str) -> Dict[str, List[str]]:
        pass
    def getSaveGameInfo(self, arg1: str) -> "ISaveGame":
        pass
    def getSaveGameWidget(
        self, arg1: PyQt5.QtWidgets.QWidget
    ) -> InterfaceNotImplemented:
        pass
    def hasScriptExtenderSave(self, arg1: str) -> bool:
        pass

class ScriptExtender:
    def __init__(self):
        pass
    def BinaryName(self) -> str:
        pass
    def PluginPath(self) -> str:
        pass
    def getArch(self) -> int:
        pass
    def getExtenderVersion(self) -> str:
        pass
    def isInstalled(self) -> bool:
        pass
    def loaderName(self) -> str:
        pass
    def loaderPath(self) -> str:
        pass
    def saveGameAttachmentExtensions(self) -> List[str]:
        pass

class UnmanagedMods:
    def __init__(self):
        pass
    def displayName(self, arg1: str) -> str:
        pass
    def mods(self, arg1: bool) -> List[str]:
        pass
    def referenceFile(self, arg1: str) -> PyQt5.QtCore.QFileInfo:
        pass
    def secondaryFiles(self, arg1: str) -> List[str]:
        pass

class VersionInfo:
    @overload
    def __init__(self):
        pass
    @overload
    def __init__(self, arg1: str):
        pass
    @overload
    def __init__(self, arg1: str, arg2: "VersionScheme"):
        pass
    @overload
    def __init__(self, arg1: int, arg2: int, arg3: int):
        pass
    @overload
    def __init__(self, arg1: int, arg2: int, arg3: int, arg4: "ReleaseType"):
        pass
    @overload
    def __init__(self, arg1: int, arg2: int, arg3: int, arg4: int):
        pass
    @overload
    def __init__(self, arg1: int, arg2: int, arg3: int, arg4: int, arg5: "ReleaseType"):
        pass
    @overload
    def __eq__(self, arg1: "VersionInfo") -> bool:
        pass
    @overload
    def __eq__(self, arg1: object) -> bool:
        pass
    def __ge__(self, arg1: "VersionInfo") -> bool:
        pass
    def __gt__(self, arg1: "VersionInfo") -> bool:
        pass
    def __le__(self, arg1: "VersionInfo") -> bool:
        pass
    def __lt__(self, arg1: "VersionInfo") -> bool:
        pass
    @overload
    def __ne__(self, arg1: "VersionInfo") -> bool:
        pass
    @overload
    def __ne__(self, arg1: object) -> bool:
        pass
    def canonicalString(self) -> str:
        pass
    def clear(self):
        pass
    def displayString(self, arg1: int) -> str:
        pass
    def isValid(self) -> bool:
        pass
    def parse(self, arg1: str, arg2: "VersionScheme", arg3: bool):
        pass
    def scheme(self) -> "VersionScheme":
        pass
