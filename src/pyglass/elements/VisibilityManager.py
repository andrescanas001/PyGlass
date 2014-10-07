# VisibilityManager.py
# (C)2014
# Scott Ernst

#___________________________________________________________________________________________________ VisibilityManager
class VisibilityManager(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, target, rawState =True):
        """Creates a new instance of VisibilityManager."""
        self._rawState     = rawState
        self._lock         = False
        self._target       = target
        self._muteRequests = []
        self._showRequests = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: target
    @property
    def target(self):
        return self._target

#___________________________________________________________________________________________________ GS: isVisible
    @property
    def isVisible(self):
        return self.rawState and (len(self._showRequests) > 0 or len(self._muteRequests) == 0)

#___________________________________________________________________________________________________ GS: rawState
    @property
    def rawState(self):
        return self._rawState
    @rawState.setter
    def rawState(self, value):
        if not self._lock:
            self._rawState = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ clearMuteRequests
    def clearMuteRequests(self):
        if len(self._muteRequests) == 0:
            return

        self._muteRequests = []
        self._updateTarget()

#___________________________________________________________________________________________________ addMuteRequest
    def addMuteRequest(self, target):
        """Doc..."""
        if target.instanceUid in self._muteRequests:
           return
        self._muteRequests.append(target.instanceUid)
        self._updateTarget()

#___________________________________________________________________________________________________ removeMuteRequest
    def removeMuteRequest(self, target):
        if not target.instanceUid in self._muteRequests:
            return
        self._muteRequests.remove(target.instanceUid)
        self._updateTarget()

#___________________________________________________________________________________________________ clearShowRequests
    def clearShowRequests(self):
        if len(self._showRequests) == 0:
            return
        self._showRequests = []
        self._updateTarget()

#___________________________________________________________________________________________________ addShowRequest
    def addShowRequest(self, target):
        """Doc..."""
        if target.instanceUid in self._showRequests:
           return
        self._showRequests.append(target.instanceUid)
        self._updateTarget()

#___________________________________________________________________________________________________ removeShowRequest
    def removeShowRequest(self, target):
        if not target.instanceUid in self._showRequests:
            return
        self._showRequests.remove(target.instanceUid)
        self._updateTarget()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _internalMethod
    def _updateTarget(self):
        """Doc..."""
        self._lock = True
        self._target.setVisible(self.isVisible)
        self._lock = False

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
