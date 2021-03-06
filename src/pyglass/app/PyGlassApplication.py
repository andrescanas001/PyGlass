# PyGlassApplication.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os
import inspect

import PySide
from PySide import QtCore
from PySide import QtGui
from pyaid.OsUtils import OsUtils
from pyaid.file.FileUtils import FileUtils
from pyaid.json.JSON import JSON
from pyaid.system.SystemUtils import SystemUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

try:
    import appdirs
except Exception as err:
    appdirs = None

#___________________________________________________________________________________________________ PyGlassApplication
class PyGlassApplication(QtCore.QObject):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _MIN_PYSIDE_VERSION = '1.2.1'
    _LOCATION_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of PyGlassApplication."""
        QtCore.QObject.__init__(self)
        self._qApplication      = None
        self._window            = None
        self._splashScreen      = None

        self.redirectLogOutputs()
        PyGlassEnvironment.initializeAppSettings(self)
        self.redirectLogOutputs()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: qApplication
    @property
    def qApplication(self):
        return self._qApplication

#___________________________________________________________________________________________________ GS: applicationCodePath
    @property
    def applicationCodePath(self):
        """ Determines the application code path where this file is located. the abspath enforces
            the absolute path with the correct os.sep to prevent issues with file path format in
            resources. """
        return os.path.abspath(os.path.dirname(inspect.getfile(self.__class__)))

#___________________________________________________________________________________________________ GS: debugRootResourcePath
    @property
    def debugRootResourcePath(self):
        return None

#___________________________________________________________________________________________________ GS: appGroupID
    @property
    def appGroupID(self):
        return self.__class__.__name__

#___________________________________________________________________________________________________ GS: appID
    @property
    def appID(self):
        return self.__class__.__name__

#___________________________________________________________________________________________________ GS: splashScreenUrl
    @property
    def splashScreenUrl(self):
        return None

#___________________________________________________________________________________________________ GS: mainWindowClass
    @property
    def mainWindowClass(self):
        return None

#___________________________________________________________________________________________________ GS: mainWindow
    @property
    def mainWindow(self):
        return self._window

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ redirectLogOutputs
    def redirectLogOutputs(self, prefix =None, logFolderPath =None):
        """ Sets a temporary standard out and error for deployed applications in a write allowed
            location to prevent failed write results. """

        if not PyGlassEnvironment.isDeployed:
            return

        if not prefix:
            prefix = self.appID

        if not prefix.endswith('_'):
            prefix += '_'

        if logFolderPath:
            logPath = logFolderPath
        elif PyGlassEnvironment.isInitialized:
            logPath = PyGlassEnvironment.getRootLocalResourcePath('logs', isDir=True)
        else:
            prefix += 'init_'
            if appdirs:
                logPath = appdirs.user_data_dir(self.appID, self.appGroupID)
            else:
                logPath = FileUtils.createPath(
                    os.path.expanduser('~'), '.pyglass', self.appGroupID, self.appID, isDir=True)

        FileUtils.getDirectoryOf(logPath, createIfMissing=True)
        try:
            sys.stdout.flush()
            sys.stdout.close()
        except Exception as err:
            pass
        sys.stdout = open(FileUtils.makeFilePath(logPath, prefix + 'out.log'), 'w+')

        try:
            sys.stderr.flush()
            sys.stderr.close()
        except Exception as err:
            pass
        sys.stderr = open(FileUtils.makeFilePath(logPath, prefix + 'error.log'), 'w+')

        return True

#___________________________________________________________________________________________________ getAppResourcePath
    def getAppResourcePath(self, *args, **kwargs):
        return PyGlassEnvironment.getRootResourcePath('apps', self.appID, *args, **kwargs)

#___________________________________________________________________________________________________ getLocalAppResourcePath
    def getLocalAppResourcePath(self, *args, **kwargs):
        return PyGlassEnvironment.getRootLocalResourcePath('apps', self.appID, *args, **kwargs)

#___________________________________________________________________________________________________ updateSplashScreen
    def updateSplashScreen(self, message =None):
        if not self._splashScreen:
            return False

        self._splashScreen.showMessage(
            message if message else 'Loading...', alignment=QtCore.Qt.AlignBottom)
        self._qApplication.processEvents()
        return True

#___________________________________________________________________________________________________ closeSplashScreen
    def closeSplashScreen(self):
        if not self._splashScreen:
            return False

        self._splashScreen.finish(self._window)
        self._splashScreen = None
        return True

#___________________________________________________________________________________________________ run
    def run(self, appArgs =None, **kwargs):
        """Doc..."""

        #-------------------------------------------------------------------------------------------
        # RESOURCE DEPLOYMENT
        try:
            self._deployResources()
        except Exception as err:
            raise

        # Checks the version of the PySide library being used. If the version is out-of-date,
        # raise a runtime error.
        minVersion = self._MIN_PYSIDE_VERSION.split('.')
        version = PySide.__version__.split('.')
        if int(version[0]) < int(minVersion[0]):
            if int(version[1]) < int(minVersion[1]):
                if int(version[2]) < minVersion[2]:
                    raise RuntimeError((
                        '[ERROR]: The installed PySide version of %s is below PyGlass\''
                        + ' minimum required version of %s.%s.%s. Please update the library.') % (
                        version, minVersion[0], minVersion[1], minVersion[2]))

        # Test for compatible Qt version installation and raise an error if an unsupported version
        # is being used
        qtVersion = QtCore.__version_info__
        if qtVersion[0] < 4 or qtVersion[1] < 8:
            raise Exception('ERROR: Unsupported Qt Version "%s"' % QtCore.__version__)

        qApp = QtGui.QApplication(appArgs if appArgs else [])
        self._qApplication = qApp

        # Add the resources path to the search directory
        QtCore.QDir.addSearchPath('AppResources', self.getAppResourcePath(isDir=True))
        QtCore.QDir.addSearchPath('LocalAppResources', self.getLocalAppResourcePath(isDir=True))

        if self.splashScreenUrl:
            self._showSplashScreen()

        self._runPreMainWindowImpl()

        windowClass = self.mainWindowClass
        if windowClass is None:
            raise RuntimeError('No Main Window Class was specified in your application class.')

        assert inspect.isclass(windowClass), (
            '%s.mainWindowClass getter must return a class for your main window' %
            self.__class__.__name__)

        self._window = windowClass(
            parent=None,
            qApp=self._qApplication,
            pyGlassApp=self,
            isMainWindow=True,
            **kwargs)
        self._window.initialize()

#___________________________________________________________________________________________________ runMainLoop
    def runMainLoop(self):
        """runMainLoop doc..."""

        self.mainWindow.preShow()
        self.mainWindow.show()

        self._qApplication.setQuitOnLastWindowClosed(False)
        self._qApplication.lastWindowClosed.connect(self._handleLastWindowClosed)
        result = self._qApplication.exec_()
        self._onPostApplication(result)
        sys.exit(result)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _redirectLogging
    @classmethod
    def _redirectLogging(cls):
        """_redirectLogging doc..."""
        pass

#___________________________________________________________________________________________________ _deployResources
    @classmethod
    def _deployResources(cls):
        """ On windows the resource folder data is stored within the application install directory.
            However, due to permissions issues, certain file types cannot be accessed from that
            directory without causing the program to crash. Therefore, the stored resources must
            be expanded into the user's AppData/Local folder. The method checks the currently
            deployed resources folder and deploys the stored resources if the existing resources
            either don't exist or don't match the currently installed version of the program. """

        if not OsUtils.isWindows() or not PyGlassEnvironment.isDeployed:
            return False

        storagePath       = PyGlassEnvironment.getInstallationPath('resource_storage', isDir=True)
        storageStampPath  = FileUtils.makeFilePath(storagePath, 'install.stamp')
        resourcePath      = PyGlassEnvironment.getRootResourcePath(isDir=True)
        resourceStampPath = FileUtils.makeFilePath(resourcePath, 'install.stamp')

        try:
            resousrceData = JSON.fromFile(resourceStampPath)
            storageData   = JSON.fromFile(storageStampPath)
            if resousrceData['CTS'] == storageData['CTS']:
                return False
        except Exception as err:
            pass

        SystemUtils.remove(resourcePath)
        FileUtils.mergeCopy(storagePath, resourcePath)
        return True

#___________________________________________________________________________________________________ _showSplashScreen
    def _showSplashScreen(self):
        """_showSplashScreen doc..."""
        parts = str(self.splashScreenUrl).split(':', 1)
        if len(parts) == 1 or parts[0].lower == 'app':
            splashImagePath = PyGlassEnvironment.getRootResourcePath(
                'apps', self.appID, parts[-1], isFile=True)
        else:
            splashImagePath = None

        if splashImagePath and os.path.exists(splashImagePath):
            splash = QtGui.QSplashScreen(QtGui.QPixmap(splashImagePath))
            splash.show()
            self._splashScreen = splash
            self.updateSplashScreen('Initializing User Interface')

#___________________________________________________________________________________________________ _runPreMainWindowImpl
    def _runPreMainWindowImpl(self):
        pass

#___________________________________________________________________________________________________ _intializeComplete
    def _intializeComplete(self):
        pass

#___________________________________________________________________________________________________ _onApplicationExit
    def _onApplicationExit(self, *args, **kwargs):
        pass

#___________________________________________________________________________________________________ _onPostApplication
    def _onPostApplication(self, resultCode):
        """_onPostApplication doc..."""
        pass

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleLastWindowClosed
    def _handleLastWindowClosed(self):
        """_handleLastWindowClosed doc..."""
        if self.mainWindow:
            self.mainWindow.postShow()
        self._onApplicationExit()
        self._qApplication.exit()

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
