from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets, QtCore, QtGui
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/spaceWidgetOptions.ui'


class SpaceSwitchWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(SpaceSwitchWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = []
        # 		self.initiateMayaNodes(self.controlers)
        # 		self.shapes = {}
        '''
        self.controlName
        self.grpOffsets
        self.joints
        self.sknJnts
        '''
        self.side_widget.setVisible(False)
        self.controlers_widget.setVisible(False)
        self.prependName_widget.setVisible(False)
        self.priorityOrder_widget.setVisible(False)

        self.qtOptions.nameAttribut_treeWidget.itemChanged.connect(partial(self.updateEnum))
        self.qtOptions.addItem_btn.pressed.connect(partial(self.addItemTree))
        self.qtOptions.removeItem_btn.pressed.connect(partial(self.removeItemTree))
        self.qtOptions.typeSpace_qcb.currentIndexChanged.connect(partial(self.updateParentType))
        self.newConnected.connect(partial(self.updateTreeFromConnection))

    def addData(self):
        '''
        It's where you define controle shapes, grpOffset and skinning joint.
        You need to add them to the node info to be able to use them before it's actually rigged.
        It's only called when the node is created the first time.
        '''

        cmds.addAttr(self.getNode(), ln='enum', at='compound', nc=2, m=True)
        cmds.addAttr(self.getNode(), ln='enumName', dataType='string', p='enum')
        cmds.addAttr(self.getNode(), ln='connected', dataType='string', p='enum')

        cmds.setAttr(self.getNode() + '.enum[0].enumName', 'Local', type='string')
        cmds.setAttr(self.getNode() + '.enum[0].connected', 'ControlGrp', type='string')
        cmds.setAttr(self.getNode() + '.enum[1].enumName', 'Global', type='string')
        cmds.setAttr(self.getNode() + '.enum[2].enumName', 'Cog', type='string')

    def options(self):
        super(SpaceSwitchWidget, self).options()
        ''' this update the widget when the ui is called '''
        # auto update to new spaceSwitch when rebuild
        if not cmds.objExists(self.getNode() + '.spaceType'):
            # at long
            cmds.addAttr(self.getNode(), ln='spaceType', at='long', dv=0)

        indexSpaceType = cmds.getAttr(self.getNode() + '.spaceType')
        self.qtOptions.typeSpace_qcb.setCurrentIndex(indexSpaceType)

        numIdx = self.qtOptions.nameAttribut_treeWidget.topLevelItemCount()
        for i in reversed(range(numIdx)):
            item = self.qtOptions.nameAttribut_treeWidget.topLevelItem(i)
            # print i, item.text(1)
            self.qtOptions.nameAttribut_treeWidget.takeTopLevelItem(i)

        numEnum = len(cmds.ls('{}.enum[*]'.format(self.getNode())))
        for i in range(numEnum):
            txtEnum = cmds.getAttr('{}.enum[{}].enumName'.format(self.getNode(), str(i)))
            txtConnected = cmds.getAttr('{}.enum[{}].connected'.format(self.getNode(), str(i)))

            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

            item.setText(0, txtConnected)
            item.setText(1, txtEnum)

            self.qtOptions.nameAttribut_treeWidget.addTopLevelItem(item)

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = []

        # 		self.templateControlers[0] = cmds.createNode('joint', n='{}_{}_template'.format(node, self.controlers[0]), p = self.templateGrp)
        # 		cmds.setAttr(self.templateControlers[0]+'.radius', 0.25)

        self.setFirstNode('None')
        cmds.select(self.templateGrp)

    def defaultWidget(self):
        pass

    def rig(self):
        '''
        well ...
        '''

        pass

    def updateTreeFromConnection(self):
        node = self.getNode()
        firstNodeInput = cmds.getAttr(self.getNode() + '.firstNodeInputName')
        numIdx = self.qtOptions.nameAttribut_treeWidget.topLevelItemCount()

        if not firstNodeInput:
            # cleaning the whole tree
            for i in range(1, numIdx):
                item = self.qtOptions.nameAttribut_treeWidget.topLevelItem(i)
                item.setText(0, '')
            return

        fullString = eval(firstNodeInput)[0]
        elements = fullString.split('|')
        elements = [a for a in elements if a != '']
        elementsToConnect = elements
        emptySpot = []
        for i in range(1, numIdx):
            connectedName = cmds.getAttr('{}.enum[{}].connected'.format(node, str(i)))
            if not connectedName:
                emptySpot.append(i)
            if connectedName in elements:
                elementsToConnect.remove(connectedName)
            else:
                cmds.setAttr('{}.enum[{}].connected'.format(node, str(i)), '', type='string')

        if elementsToConnect and emptySpot:
            for spot in emptySpot:
                if elementsToConnect:
                    cmds.setAttr('{}.enum[{}].connected'.format(node, str(spot)), elementsToConnect[0], type='string')
                    elementsToConnect.pop(0)

        for i in range(1, numIdx):
            item = self.qtOptions.nameAttribut_treeWidget.topLevelItem(i)
            enumName = cmds.getAttr('{}.enum[{}].enumName'.format(node, str(i)))
            connectedName = cmds.getAttr('{}.enum[{}].connected'.format(node, str(i)))
            item.setText(1, enumName)
            item.setText(0, connectedName)

    def removeItemTree(self):
        numIdx = self.qtOptions.nameAttribut_treeWidget.topLevelItemCount()
        self.qtOptions.nameAttribut_treeWidget.takeTopLevelItem(numIdx - 1)
        cmds.removeMultiInstance('{}.enum[{}]'.format(self.getNode(), str(numIdx - 1)))

    def addItemTree(self):
        item = QtWidgets.QTreeWidgetItem()
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.setText(1, 'Enum')
        numIdx = self.qtOptions.nameAttribut_treeWidget.topLevelItemCount()
        cmds.setAttr('{}.enum[{}].enumName'.format(self.getNode(), str(numIdx)), 'Enum', type='string')

        self.qtOptions.nameAttribut_treeWidget.addTopLevelItem(item)
        self.updateTreeFromConnection()

    def updateEnum(self, item, column):
        idx = self.qtOptions.nameAttribut_treeWidget.indexOfTopLevelItem(item)
        if column:
            cmds.setAttr('{}.enum[{}].enumName'.format(self.getNode(), str(idx)), item.text(1), type='string')
        else:
            cmds.setAttr('{}.enum[{}].connected'.format(self.getNode(), str(idx)), item.text(0), type='string')

    def updateParentType(self, index):
        cmds.setAttr('{}.spaceType'.format(self.getNode()), index)
