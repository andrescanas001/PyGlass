# PyGlassWidget.py
# (C)2012-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtGui
from pyaid.dict.DictUtils import DictUtils
from pyaid.string.StringUtils import StringUtils

from pyglass.elements.PyGlassElement import PyGlassElement
from pyglass.gui.PyGlassBackgroundParent import PyGlassBackgroundParent
from pyglass.gui.UiFileLoader import UiFileLoader

#___________________________________________________________________________________________________ PyGlassWidget
class PyGlassWidget(PyGlassElement):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    # Complete relative path from the widget folder to the widget file to load
    RESOURCE_WIDGET_FILE   = None

    # Prefix folder path relative to the widget folder
    RESOURCE_FOLDER_PREFIX = None
    RESOURCE_FOLDER_NAME   = None

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent =None, **kwargs):
        """Creates a new instance of PyGlassWidget."""
        PyGlassElement.__init__(self, parent, **kwargs)
        if kwargs.get('verbose', False):
            print('CREATING: %s | PARENTED TO: %s' % (self, parent))
        self.setStyleSheet(self.owner.styleSheetPath)

        self._displayCount  = 0
        self._widgetClasses = kwargs.get('widgets', dict())
        self._widgetParent  = None
        self._currentWidget = None
        self._widgets       = dict()
        self._widgetFlags   = kwargs.get('widgetFlags')
        self._widgetID      = kwargs.get('widgetID')
        self._lastChildWidgetID  = None
        self._lastPeerWidgetID   = None

        widgetFile = kwargs.get('widgetFile', True)

        if widgetFile:
            parts = self.RESOURCE_WIDGET_FILE
            if parts:
                if StringUtils.isStringType(parts):
                    parts = parts.split('/')[-1:]
                elif parts:
                    parts = parts[-1:]
            self._widgetData = UiFileLoader.loadWidgetFile(self, names=parts)
        else:
            self._widgetData = None

        name = kwargs.get('containerWidgetName')
        self._containerWidget = getattr(self, name) if name and hasattr(self, name) else None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: lastPeerWidgetID
    @property
    def lastPeerWidgetID(self):
        """ The ID of the widget that was replaced by this widget or None if not applicable. """
        return self._lastPeerWidgetID

#___________________________________________________________________________________________________ GS: lastChildWidgetID
    @property
    def lastChildWidgetID(self):
        return self._lastChildWidgetID

#___________________________________________________________________________________________________ GS: currentChildWidgetID
    @property
    def currentChildWidgetID(self):
        if not self._currentWidget:
            return None
        for key, widget in DictUtils.iter(self._widgets):
            if widget == self._currentWidget:
                return key
        return None

#___________________________________________________________________________________________________ GS: displayCount
    @property
    def displayCount(self):
        return self._displayCount

#___________________________________________________________________________________________________ GS: allowsOwnership
    @property
    def allowsOwnership(self):
        return True

#___________________________________________________________________________________________________ GS: styleSheetPath
    @property
    def styleSheetPath(self):
        return self.owner.styleSheetPath

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getChildWidget
    def getChildWidget(self, widgetID, allowCreation =True):
        """getChildWidget doc..."""
        if not widgetID:
            return None

        if widgetID not in self._widgets:
            if not allowCreation:
                return None
            self.loadWidgets(widgetID)
        return self._widgets[widgetID]

#___________________________________________________________________________________________________ addWidgetChild
    def addWidgetChild(self, key, widgetClass, setActive =False):
        self._widgetClasses[key] = widgetClass
        if setActive:
            return self.setActiveWidget(key)
        return True

#___________________________________________________________________________________________________ refresh
    def refresh(self, **kwargs):
        for widgetID, widget in DictUtils.iter(self._widgets):
            widget.refresh(**kwargs)

#___________________________________________________________________________________________________ clearActiveWidget
    def clearActiveWidget(self, containerWidget =None, doneArgs =None):
        if not self._currentWidget:
            return

        if doneArgs is None:
            doneArgs = dict()
        self._currentWidget.deactivateWidgetDisplay(**doneArgs)

        try:
            containerWidget.layout().removeWidget(self._currentWidget)
        except Exception:
            p = self._currentWidget.parent()
            if p:
                p.layout().removeWidget(self._currentWidget)

        self._lastChildWidgetID = self._currentWidget.widgetID
        self._currentWidget.setParent(self._widgetParent)
        self._currentWidget = None

#___________________________________________________________________________________________________ setActiveWidget
    def setActiveWidget(self, widgetID, containerWidget =None, force =False, args =None, doneArgs =None):
        if widgetID and not widgetID in self._widgetClasses:
            print(StringUtils.dedent("""
                [WARNING]: Invalid widget ID "%s" in %s. No such widget assigned
                """ % (widgetID, self)))
            return False

        if containerWidget is None:
            containerWidget = self._containerWidget
        if containerWidget is None:
            print('[WARNING]: %s has no specified container widget' % self)
            return False

        if not force and self._currentWidget and self._currentWidget.widgetID == widgetID:
            return True

        if widgetID:
            widget = self.getChildWidget(widgetID, allowCreation=True)
        else:
            widget = None

        containerLayout = containerWidget.layout()
        if not containerLayout:
            containerLayout = self._getLayout(containerWidget, QtGui.QVBoxLayout)

        self.clearActiveWidget(containerWidget=containerWidget, doneArgs=doneArgs)
        self._currentWidget = widget

        if widget:
            containerLayout.addWidget(widget)
            containerWidget.setContentsMargins(0, 0, 0, 0)

        self.refreshGui()
        if args is None:
            args = dict()

        if widget and self._isWidgetActive:
            widget.activateWidgetDisplay(lastPeerWidgetID=self._lastChildWidgetID, **args)

        return True

#___________________________________________________________________________________________________ loadWidgets
    def loadWidgets(self, widgetIdents =None):
        if not widgetIdents:
            widgetIdents = self._widgetClasses.keys()
        elif StringUtils.isStringType(widgetIdents):
            widgetIdents = [widgetIdents]

        if self._widgetParent is None:
            self._widgetParent = PyGlassBackgroundParent(proxy=self)

        for widgetID in widgetIdents:
            if widgetID in self._widgets:
                continue

            if widgetID not in self._widgetClasses:
                self._log.write(
                    'ERROR: Unrecognized widgetID "%s" in %s' % (str(widgetID), str(self)) )

            # noinspection PyCallingNonCallable
            widget = self._widgetClasses[widgetID](
                self._widgetParent, flags=self._widgetFlags, widgetID=widgetID)
            self._widgets[widgetID] = widget

#___________________________________________________________________________________________________ refreshWidgetDisplay
    def refreshWidgetDisplay(self):
        if self._currentWidget:
            self._currentWidget.refreshWidgetDisplay()
        self._refreshWidgetDisplayImpl()

#___________________________________________________________________________________________________ activateWidgetDisplay
    def activateWidgetDisplay(self, **kwargs):
        if self._isWidgetActive:
            return

        self._lastPeerWidgetID = kwargs.get('lastPeerWidgetID')

        self._displayCount += 1
        self._activateWidgetDisplayImpl(**kwargs)

        if self._currentWidget:
            self._currentWidget.activateWidgetDisplay(**kwargs)

        self._isWidgetActive = True
        self.updateGeometry()
        self.update()

#___________________________________________________________________________________________________ deactivateWidgetDisplay
    def deactivateWidgetDisplay(self, **kwargs):
        if not self._isWidgetActive:
            return

        self._deactivateWidgetDisplayImpl(**kwargs)

        if self._currentWidget:
            self._currentWidget.deactivateWidgetDisplay(**kwargs)

        self._isWidgetActive = False

#___________________________________________________________________________________________________ disposeWidgets
    def disposeWidgets(self, *widgetIDs):
        if not widgetIDs:
            widgetIDs = list(self._widgets.keys())

        for widgetID in widgetIDs:
            widget = self._widgets[widgetID]
            if self._currentWidget and self._currentWidget == widget:
                self.setActiveWidget(None)
            widget.setParent(None)
            widget.deleteLater()
            del self._widgets[widgetID]
