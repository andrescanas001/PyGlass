# GridListElement.py
# (C)2014
# Scott Ernst

import math

from PySide import QtCore
from PySide import QtGui

from pyglass.elements.PyGlassElement import PyGlassElement

#___________________________________________________________________________________________________ GridListElement
class GridListElement(PyGlassElement):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent =None, **kwargs):
        """Creates a new instance of GridListElement."""
        super(GridListElement, self).__init__(parent=parent, **kwargs)
        self._items = []

        self._maxColumnWidth = 1024.0
        self._lastColumnCount = -1
        self._lastItemCount = 0
        self._updating = False

        layout = QtGui.QGridLayout()
        self.setLayout(layout)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: maxColumnWidth
    @property
    def maxColumnWidth(self):
        return self._maxColumnWidth
    @maxColumnWidth.setter
    def maxColumnWidth(self, value):
        if self._maxColumnWidth == value:
            return
        self._maxColumnWidth = value
        self.update()

#___________________________________________________________________________________________________ GS: columnCount
    @property
    def columnCount(self):
        wMax = self.maxColumnWidth
        if wMax <= 0:
            return 1

        w = self.size().width()
        return float(max(1, math.ceil(float(w)/float(wMax))))

#___________________________________________________________________________________________________ GS: items
    @property
    def items(self):
        return self._items

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getGridCoordinatesFromIndex
    def getGridCoordinatesFromIndex(self, index):
        cols = self.columnCount
        return math.floor(float(index)/cols), index % cols

#___________________________________________________________________________________________________ update
    def update(self):
        if self._updating:
            return
        self._updating = True
        index = 0
        layout = self.layout()

        count = self.columnCount

        for item in self._items:
            coordinate = self.getGridCoordinatesFromIndex(index)
            layout.removeWidget(item[0])
            layout.addWidget(item[0], coordinate[0], coordinate[1])
            item[0].setVisible(True)
            index += 1

        self._lastColumnCount = count
        self._lastItemCount = len(self._items)
        self._updating = False

#___________________________________________________________________________________________________ insertItem
    def insertItems(self, index, *widgets):
        for widget in widgets:
            item = self.getWidgetItem(widget)
            if item:
                if self._items.index(item) == index:
                    return
                self._items.remove(item)
            self._items.insert(index, (widget, None))
            widget.setParent(self)
            index += 1
        self.update()

#___________________________________________________________________________________________________ addItem
    def addItems(self, *widgets):
        """Doc..."""
        for widget in widgets:
            item = self.getWidgetItem(widget)
            if item:
                self._items.remove(item)
            self._items.append((widget, None))
            widget.setParent(self)
        self.update()

#___________________________________________________________________________________________________ removeItem
    def removeItems(self, *widgets):
        for widget in widgets:
            item = self.getWidgetItem(widget)
            if not item:
                continue
            self._items.remove(item)

            widget.setParent(None)
            self.layout().removeWidget(widget)
        self.update()

#___________________________________________________________________________________________________ clear
    def clear(self):
        while len(self._items) > 0:
            item = self._items.pop()
            widget = item[0]
            self.layout().removeWidget(widget)
            widget.setParent(None)
        self.update()

#___________________________________________________________________________________________________ getWidgetItem
    def getWidgetItem(self, widget):
        index = self.getIndexOfWidget(widget)
        if index == -1:
            return None
        return self._items[index]

#___________________________________________________________________________________________________ getIndexOfWidget
    def getIndexOfWidget(self, widget):
        index = 0
        for item in self._items:
            if item[0] == widget:
                return index
            index += 1
        return -1

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _resizeImpl
    def _resizeImpl(self, *args, **kwargs):
        super(GridListElement, self)._resizeImpl(*args, **kwargs)

        # Only update if the column count changes for performance
        count = self.columnCount
        if count != self._lastColumnCount or len(self._items) != self._lastItemCount:
            self.update()
