# RemoteThreadEvent.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.event.PyGlassSignalEvent import PyGlassSignalEvent

#___________________________________________________________________________________________________ RemoteThreadEvent
class RemoteThreadEvent(PyGlassSignalEvent):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, identifier, target, data =None):
        """Creates a new instance of RemoteThreadEvent."""
        self._id = identifier
        super(RemoteThreadEvent, self).__init__(target=target, data=data)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: success
    @property
    def success(self):
        return self.target.success

#___________________________________________________________________________________________________ GS: id
    @property
    def id(self):
        return self._id

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __getitem__
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        raise KeyError('No such key "%s" in event data' % key)
