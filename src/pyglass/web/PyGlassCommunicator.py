# PyGlassCommunicator.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtCore
from pyaid.json.JSON import JSON
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ PyGlassCommunicator
class PyGlassCommunicator(QtCore.QObject):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, webView =None, **kwargs):
        """Creates a new instance of PyGlassCommunicator."""
        QtCore.QObject.__init__(self)
        self._errors  = []
        self._webView = webView

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: javaScriptID
    @property
    def javaScriptID(self):
        return 'PYGLASS'

#___________________________________________________________________________________________________ GS: webView
    @property
    def webView(self):
        return self._webView
    @webView.setter
    def webView(self, value):
        self._webView = value

#___________________________________________________________________________________________________ GS: scriptFrame
    @property
    def scriptFrame(self):
        return self._webView.page().mainFrame()

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ callInitialize
    def callInitialize(self):
        self.scriptFrame.addToJavaScriptWindowObject(self.javaScriptID, self)
        self.callJavascript('initialize' + self.javaScriptID)

#___________________________________________________________________________________________________ callUpdate
    def callUpdate(self):
        self.callJavascript('update' + self.javaScriptID)

#___________________________________________________________________________________________________ callJavascript
    def callJavascript(self, function, data =None):
        frame = self._webView.page().mainFrame()
        frame.addToJavaScriptWindowObject(self.javaScriptID, self)
        frame.evaluateJavaScript(
            'try{ window.%s(%s); } catch (e) {}' % (function, JSON.asString(data) if data else ''))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _parseData
    def _parseData(self, data):
        if not data:
            return None

        try:
            return JSON.fromString(data)
        except Exception as err:
            return data

#___________________________________________________________________________________________________ _createSuccessResult
    def _createSuccessResult(self, payload):
        return JSON.asString(dict(
            success=True,
            error=False,
            payload=payload ))

#___________________________________________________________________________________________________ _createErrorResult
    def _createErrorResult(self, code =None, info =None, data=None):
        out = dict(
            success=False,
            error=True,
            code=code if code else 'COMMUNICATOR_ERROR',
            info=info if info else 'Unknown error occurred.',
            data=data )

        # Keep errors to the 50 most recent to prevent memory overloads on long sessions.
        while len(self._errors) > 49:
            self._errors.pop(0)
        self._errors.append(out)

        return JSON.asString(out)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
