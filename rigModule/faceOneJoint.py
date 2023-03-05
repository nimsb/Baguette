from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils, faceUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets, QtCore
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/faceOneWidgetOptions.ui'


class FaceOneJointWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(FaceOneJointWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['UseMe']
        self.initiateMayaNodes(self.controlers)
        # 		self.shapes = {}
        '''
        self.controlName
        self.grpOffsets
        self.joints
        self.sknJnts
        '''

    def addData(self):
        '''
        It's where you define controle shapes, grpOffset and skinning joint.
        You need to add them to the node info to be able to use them before it's actually rigged.
        It's only called when the node is created the first time.
        '''

        # add two other grpOffsets to the Global and 1 more sknJnts to the Cog

        # set here default value for the controlers and shape.
        self.setControlerShape('UseMe', 'square', 13, axe='y', radius=4)

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln="typeFollicleCtrl", at="double3")
        cmds.addAttr(self.templateGrp, ln="typeFollicleCtrlX", at="double", p="typeFollicleCtrl")
        cmds.addAttr(self.templateGrp, ln="typeFollicleCtrlY", at="double", p="typeFollicleCtrl")
        cmds.addAttr(self.templateGrp, ln="typeFollicleCtrlZ", at="double", p="typeFollicleCtrl")
        cmds.setAttr(self.templateGrp + ".typeFollicleCtrl", 0, 1, 0, type="double3")

        cmds.addAttr(self.templateGrp, ln="limitMinTrans", at="double3")
        cmds.addAttr(self.templateGrp, ln="limitMinTransX", at="double", p="limitMinTrans")
        cmds.addAttr(self.templateGrp, ln="limitMinTransY", at="double", p="limitMinTrans")
        cmds.addAttr(self.templateGrp, ln="limitMinTransZ", at="double", p="limitMinTrans")
        cmds.setAttr(self.templateGrp + ".limitMinTrans", 1, 1, 1, type="double3")
        cmds.addAttr(self.templateGrp, ln="limitMaxTrans", at="double3")
        cmds.addAttr(self.templateGrp, ln="limitMaxTransX", at="double", p="limitMaxTrans")
        cmds.addAttr(self.templateGrp, ln="limitMaxTransY", at="double", p="limitMaxTrans")
        cmds.addAttr(self.templateGrp, ln="limitMaxTransZ", at="double", p="limitMaxTrans")
        cmds.setAttr(self.templateGrp + ".limitMaxTrans", 1, 1, 1, type="double3")
        cmds.addAttr(self.templateGrp, ln="valueMinTrans", at="double3")
        cmds.addAttr(self.templateGrp, ln="valueMinTransX", at="double", p="valueMinTrans")
        cmds.addAttr(self.templateGrp, ln="valueMinTransY", at="double", p="valueMinTrans")
        cmds.addAttr(self.templateGrp, ln="valueMinTransZ", at="double", p="valueMinTrans")
        cmds.setAttr(self.templateGrp + ".valueMinTrans", -1, -1, -1, type="double3")
        cmds.addAttr(self.templateGrp, ln="valueMaxTrans", at="double3")
        cmds.addAttr(self.templateGrp, ln="valueMaxTransX", at="double", p="valueMaxTrans")
        cmds.addAttr(self.templateGrp, ln="valueMaxTransY", at="double", p="valueMaxTrans")
        cmds.addAttr(self.templateGrp, ln="valueMaxTransZ", at="double", p="valueMaxTrans")
        cmds.setAttr(self.templateGrp + ".valueMaxTrans", 1, 1, 1, type="double3")

        cmds.addAttr(self.templateGrp, ln="hideLockTrans", at="double3")
        cmds.addAttr(self.templateGrp, ln="hideLockTransX", at="double", p="hideLockTrans")
        cmds.addAttr(self.templateGrp, ln="hideLockTransY", at="double", p="hideLockTrans")
        cmds.addAttr(self.templateGrp, ln="hideLockTransZ", at="double", p="hideLockTrans")
        cmds.setAttr(self.templateGrp + ".hideLockTrans", 0, 0, 0, type="double3")
        cmds.addAttr(self.templateGrp, ln="hideLockRot", at="double3")
        cmds.addAttr(self.templateGrp, ln="hideLockRotX", at="double", p="hideLockRot")
        cmds.addAttr(self.templateGrp, ln="hideLockRotY", at="double", p="hideLockRot")
        cmds.addAttr(self.templateGrp, ln="hideLockRotZ", at="double", p="hideLockRot")
        cmds.setAttr(self.templateGrp + ".hideLockRot", 0, 0, 0, type="double3")
        cmds.addAttr(self.templateGrp, ln="hideLockScale", at="double3")
        cmds.addAttr(self.templateGrp, ln="hideLockScaleX", at="double", p="hideLockScale")
        cmds.addAttr(self.templateGrp, ln="hideLockScaleY", at="double", p="hideLockScale")
        cmds.addAttr(self.templateGrp, ln="hideLockScaleZ", at="double", p="hideLockScale")
        cmds.setAttr(self.templateGrp + ".hideLockScale", 1, 1, 1, type="double3")

        cmds.addAttr(self.templateGrp, ln='lockAttribute', at='compound', nc=1, m=True)
        cmds.addAttr(self.templateGrp, ln='lockAttributeName', dataType='string', p='lockAttribute')
        cmds.setAttr(self.templateGrp + '.lockAttribute[0].lockAttributeName', 'rotateOrder', type='string')
        cmds.setAttr(self.templateGrp + '.lockAttribute[1].lockAttributeName', 'adjScale', type='string')

        cmds.addAttr(self.templateGrp, ln='targetCon', at='compound', nc=4, m=True)
        cmds.addAttr(self.templateGrp, ln='targetConName', dataType='string', p='targetCon')
        cmds.addAttr(self.templateGrp, ln='targetConAttribute', dataType='string', p='targetCon')
        cmds.addAttr(self.templateGrp, ln='targetConFrom', dataType='string', p='targetCon')
        cmds.addAttr(self.templateGrp, ln='targetConTo', dataType='string', p='targetCon')

        cmds.setAttr(self.templateGrp + '.targetCon[0].targetConName', 'targetNameLongTargetOn', type='string')
        cmds.setAttr(self.templateGrp + '.targetCon[0].targetConAttribute', 'attributeX', type='string')
        cmds.setAttr(self.templateGrp + '.targetCon[0].targetConFrom', '0.0', type='string')
        cmds.setAttr(self.templateGrp + '.targetCon[0].targetConTo', '-1.0', type='string')

    def options(self):
        super(FaceOneJointWidget, self).options()
        # add here any Qt options to the self.options_Qgb you would like to see
        if cmds.objExists(self.templateGrp):

            prependName = cmds.getAttr(self.templateGrp + '.prependName')
            self.prependName_chbx.setChecked(prependName)
            prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
            self.prependName_lineEdit.setText(prependNameTxt)

            typeFollicleCtrl = cmds.getAttr(self.templateGrp + '.typeFollicleCtrl')[0]
            if typeFollicleCtrl[0]:
                self.options_Qgb.follicle_rbtn.setChecked(True)
            if typeFollicleCtrl[1]:
                self.options_Qgb.facs_rbtn.setChecked(True)
            if typeFollicleCtrl[2]:
                self.options_Qgb.adjustement_rbtn.setChecked(True)

            limitMinTrans = cmds.getAttr(self.templateGrp + '.limitMinTrans')[0]
            limitMaxTrans = cmds.getAttr(self.templateGrp + '.limitMaxTrans')[0]
            valueMinTrans = cmds.getAttr(self.templateGrp + '.valueMinTrans')[0]
            valueMaxTrans = cmds.getAttr(self.templateGrp + '.valueMaxTrans')[0]
            hideLockTrans = cmds.getAttr(self.templateGrp + '.hideLockTrans')[0]
            hideLockRot = cmds.getAttr(self.templateGrp + '.hideLockRot')[0]
            hideLockScale = cmds.getAttr(self.templateGrp + '.hideLockScale')[0]

            self.options_Qgb.transLimitXMin_cbx.setChecked(bool(limitMinTrans[0]))
            self.options_Qgb.transLimitYMin_cbx.setChecked(bool(limitMinTrans[1]))
            self.options_Qgb.transLimitZMin_cbx.setChecked(bool(limitMinTrans[2]))
            self.options_Qgb.transLimitXMax_cbx.setChecked(bool(limitMaxTrans[0]))
            self.options_Qgb.transLimitYMax_cbx.setChecked(bool(limitMaxTrans[1]))
            self.options_Qgb.transLimitZMax_cbx.setChecked(bool(limitMaxTrans[2]))
            self.options_Qgb.transLimitXMin_dsbx.setValue(valueMinTrans[0])
            self.options_Qgb.transLimitYMin_dsbx.setValue(valueMinTrans[1])
            self.options_Qgb.transLimitZMin_dsbx.setValue(valueMinTrans[2])
            self.options_Qgb.transLimitXMax_dsbx.setValue(valueMaxTrans[0])
            self.options_Qgb.transLimitYMax_dsbx.setValue(valueMaxTrans[1])
            self.options_Qgb.transLimitZMax_dsbx.setValue(valueMaxTrans[2])
            self.options_Qgb.hideLockTX_cbx.setChecked(bool(hideLockTrans[0]))
            self.options_Qgb.hideLockTY_cbx.setChecked(bool(hideLockTrans[1]))
            self.options_Qgb.hideLockTZ_cbx.setChecked(bool(hideLockTrans[2]))
            self.options_Qgb.hideLockRX_cbx.setChecked(bool(hideLockRot[0]))
            self.options_Qgb.hideLockRY_cbx.setChecked(bool(hideLockRot[1]))
            self.options_Qgb.hideLockRZ_cbx.setChecked(bool(hideLockRot[2]))
            self.options_Qgb.hideLockSX_cbx.setChecked(bool(hideLockScale[0]))
            self.options_Qgb.hideLockSY_cbx.setChecked(bool(hideLockScale[1]))
            self.options_Qgb.hideLockSZ_cbx.setChecked(bool(hideLockScale[2]))

            lockAttributeNum = len(cmds.ls('{}.lockAttribute[*]'.format(self.templateGrp)))
            for i in range(lockAttributeNum):
                attrName = cmds.getAttr('{}.lockAttribute[{}].lockAttributeName'.format(self.templateGrp, str(i)))

                item = QtWidgets.QTreeWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

                item.setText(0, attrName)

                self.qtOptions.lockedAttribut_treeWidget.addTopLevelItem(item)

            targetConNum = len(cmds.ls('{}.targetCon[*]'.format(self.templateGrp)))
            for i in range(targetConNum):
                targetConName = cmds.getAttr('{}.targetCon[{}].targetConName'.format(self.templateGrp, str(i)))
                targetConAttribute = cmds.getAttr(
                    '{}.targetCon[{}].targetConAttribute'.format(self.templateGrp, str(i)))
                targetConFrom = cmds.getAttr('{}.targetCon[{}].targetConFrom'.format(self.templateGrp, str(i)))
                targetConTo = cmds.getAttr('{}.targetCon[{}].targetConTo'.format(self.templateGrp, str(i)))

                item = QtWidgets.QTreeWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

                item.setText(0, targetConName)
                item.setText(1, targetConAttribute)
                item.setText(2, targetConFrom)
                item.setText(3, targetConTo)

                self.qtOptions.targetBlendshapeConnection_treeWidget.addTopLevelItem(item)

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

        self.options_Qgb.follicle_rbtn.toggled.connect(partial(self.setTypeFollicleCtrl))
        self.options_Qgb.facs_rbtn.toggled.connect(partial(self.setTypeFollicleCtrl))
        self.options_Qgb.adjustement_rbtn.toggled.connect(partial(self.setTypeFollicleCtrl))
        self.options_Qgb.transLimitXMin_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitYMin_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitZMin_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitXMax_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitYMax_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitZMax_cbx.stateChanged.connect(partial(self.setLimits))
        self.options_Qgb.transLimitXMin_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.transLimitYMin_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.transLimitZMin_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.transLimitXMax_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.transLimitYMax_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.transLimitZMax_dsbx.valueChanged.connect(partial(self.setMinMaxValues))
        self.options_Qgb.hideLockTX_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockTY_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockTZ_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockRX_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockRY_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockRZ_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockSX_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockSY_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))
        self.options_Qgb.hideLockSZ_cbx.stateChanged.connect(partial(self.updateHideAndLockAttribute))

        self.qtOptions.lockedAttribut_treeWidget.itemChanged.connect(partial(self.updateHideAndLockList))
        self.qtOptions.targetBlendshapeConnection_treeWidget.itemChanged.connect(partial(self.updateTargetConnection))

        self.options_Qgb.addLockAttribute_btn.clicked.connect(partial(self.addLockAttribute))
        self.options_Qgb.rmvLockAttribute_btn.clicked.connect(partial(self.removeLockAttribute))
        self.options_Qgb.addTargetConnection_btn.clicked.connect(partial(self.addTargetConnection))
        self.options_Qgb.rmvTargetConnection_btn.clicked.connect(partial(self.removeTargetConnection))

    def setTypeFollicleCtrl(self, *args):
        if self.options_Qgb.follicle_rbtn.isChecked():
            cmds.setAttr(self.templateGrp + '.typeFollicleCtrl', 1, 0, 0)

        if self.options_Qgb.facs_rbtn.isChecked():
            cmds.setAttr(self.templateGrp + '.typeFollicleCtrl', 0, 1, 0)
            self.options_Qgb.transLimitXMin_cbx.setChecked(True)
            self.options_Qgb.transLimitYMin_cbx.setChecked(True)
            self.options_Qgb.transLimitZMin_cbx.setChecked(True)
            self.options_Qgb.transLimitXMax_cbx.setChecked(True)
            self.options_Qgb.transLimitYMax_cbx.setChecked(True)
            self.options_Qgb.transLimitZMax_cbx.setChecked(True)
            self.options_Qgb.transLimitXMin_dsbx.setValue(-1)
            self.options_Qgb.transLimitYMin_dsbx.setValue(-1)
            self.options_Qgb.transLimitZMin_dsbx.setValue(-1)
            self.options_Qgb.transLimitXMax_dsbx.setValue(1)
            self.options_Qgb.transLimitYMax_dsbx.setValue(1)
            self.options_Qgb.transLimitZMax_dsbx.setValue(1)

        if self.options_Qgb.adjustement_rbtn.isChecked():
            cmds.setAttr(self.templateGrp + '.typeFollicleCtrl', 0, 0, 1)

        if self.options_Qgb.follicle_rbtn.isChecked() or self.options_Qgb.adjustement_rbtn.isChecked():
            self.options_Qgb.transLimitXMin_cbx.setChecked(False)
            self.options_Qgb.transLimitYMin_cbx.setChecked(False)
            self.options_Qgb.transLimitZMin_cbx.setChecked(False)
            self.options_Qgb.transLimitXMax_cbx.setChecked(False)
            self.options_Qgb.transLimitYMax_cbx.setChecked(False)
            self.options_Qgb.transLimitZMax_cbx.setChecked(False)

    def setLimits(self, *args):
        cmds.setAttr(self.templateGrp + ".limitMinTrans", self.options_Qgb.transLimitXMin_cbx.isChecked(),
                     self.options_Qgb.transLimitYMin_cbx.isChecked(),
                     self.options_Qgb.transLimitZMin_cbx.isChecked(),
                     type="double3")

        cmds.setAttr(self.templateGrp + ".limitMaxTrans", self.options_Qgb.transLimitXMax_cbx.isChecked(),
                     self.options_Qgb.transLimitYMax_cbx.isChecked(),
                     self.options_Qgb.transLimitZMax_cbx.isChecked(),
                     type="double3")

    def setMinMaxValues(self, *args):
        cmds.setAttr(self.templateGrp + ".valueMinTrans", self.options_Qgb.transLimitXMin_dsbx.value(),
                     self.options_Qgb.transLimitYMin_dsbx.value(),
                     self.options_Qgb.transLimitZMin_dsbx.value(),
                     type="double3")

        cmds.setAttr(self.templateGrp + ".valueMaxTrans", self.options_Qgb.transLimitXMax_dsbx.value(),
                     self.options_Qgb.transLimitYMax_dsbx.value(),
                     self.options_Qgb.transLimitZMax_dsbx.value(),
                     type="double3")

    def updateHideAndLockAttribute(self, *args):
        cmds.setAttr(self.templateGrp + ".hideLockTrans", self.options_Qgb.hideLockTX_cbx.isChecked(),
                     self.options_Qgb.hideLockTY_cbx.isChecked(),
                     self.options_Qgb.hideLockTZ_cbx.isChecked(),
                     type="double3")

        cmds.setAttr(self.templateGrp + ".hideLockRot", self.options_Qgb.hideLockRX_cbx.isChecked(),
                     self.options_Qgb.hideLockRY_cbx.isChecked(),
                     self.options_Qgb.hideLockRZ_cbx.isChecked(),
                     type="double3")

        cmds.setAttr(self.templateGrp + ".hideLockScale", self.options_Qgb.hideLockSX_cbx.isChecked(),
                     self.options_Qgb.hideLockSY_cbx.isChecked(),
                     self.options_Qgb.hideLockSZ_cbx.isChecked(),
                     type="double3")

    def updateHideAndLockList(self, item, column, *args):
        idx = self.qtOptions.lockedAttribut_treeWidget.indexOfTopLevelItem(item)
        cmds.setAttr('{}.lockAttribute[{}].lockAttributeName'.format(self.templateGrp, str(idx)), item.text(0),
                     type='string')

    def addLockAttribute(self, *args):
        item = QtWidgets.QTreeWidgetItem()
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.setText(0, 'newAttribute')
        numIdx = self.qtOptions.lockedAttribut_treeWidget.topLevelItemCount()
        cmds.setAttr('{}.lockAttribute[{}].lockAttributeName'.format(self.templateGrp, str(numIdx)), 'newAttribute',
                     type='string')

        self.qtOptions.lockedAttribut_treeWidget.addTopLevelItem(item)

    def removeLockAttribute(self, *args):
        numIdx = self.qtOptions.lockedAttribut_treeWidget.topLevelItemCount()
        self.qtOptions.lockedAttribut_treeWidget.takeTopLevelItem(numIdx - 1)
        cmds.removeMultiInstance('{}.lockAttribute[{}]'.format(self.templateGrp, str(numIdx - 1)))

    def updateTargetConnection(self, item, column, *args):
        idx = self.qtOptions.targetBlendshapeConnection_treeWidget.indexOfTopLevelItem(item)

        if int(column) == 0:
            cmds.setAttr('{}.targetCon[{}].targetConName'.format(self.templateGrp, str(idx)), item.text(int(column)),
                         type='string')
        if int(column) == 1:
            cmds.setAttr('{}.targetCon[{}].targetConAttribute'.format(self.templateGrp, str(idx)),
                         item.text(int(column)), type='string')
        if int(column) == 2:
            cmds.setAttr('{}.targetCon[{}].targetConFrom'.format(self.templateGrp, str(idx)), item.text(int(column)),
                         type='string')
        if int(column) == 3:
            cmds.setAttr('{}.targetCon[{}].targetConTo'.format(self.templateGrp, str(idx)), item.text(int(column)),
                         type='string')

    def addTargetConnection(self, *args):
        item = QtWidgets.QTreeWidgetItem()
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.setText(0, 'newTarget')
        item.setText(1, 'newAttribute')
        item.setText(2, '0')
        item.setText(3, '10')
        numIdx = self.qtOptions.targetBlendshapeConnection_treeWidget.topLevelItemCount()
        cmds.setAttr('{}.targetCon[{}].targetConName'.format(self.templateGrp, str(numIdx)), 'newTarget', type='string')
        cmds.setAttr('{}.targetCon[{}].targetConAttribute'.format(self.templateGrp, str(numIdx)), 'newAttribute',
                     type='string')
        cmds.setAttr('{}.targetCon[{}].targetConFrom'.format(self.templateGrp, str(numIdx)), '0', type='string')
        cmds.setAttr('{}.targetCon[{}].targetConTo'.format(self.templateGrp, str(numIdx)), '10', type='string')

        self.qtOptions.targetBlendshapeConnection_treeWidget.addTopLevelItem(item)

    def removeTargetConnection(self, *args):
        numIdx = self.qtOptions.targetBlendshapeConnection_treeWidget.topLevelItemCount()
        self.qtOptions.targetBlendshapeConnection_treeWidget.takeTopLevelItem(numIdx - 1)
        cmds.removeMultiInstance('{}.targetCon[{}]'.format(self.templateGrp, str(numIdx - 1)))

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None]

        self.templateControlers[0] = cmds.createNode('joint', n='{}_{}_template'.format(node, self.controlers[0]),
                                                     p=self.templateGrp)
        cmds.setAttr(self.templateControlers[0] + '.radius', 1)

        cmds.select(self.templateGrp)

    def defaultWidget(self):
        pass

    def rig(self):
        '''
        well ...
        '''
        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        node = self.getNode()

        follicleCtrl = False
        FACSCtrl = False
        AdjustCtrl = False
        sknJnts = []
        if cmds.getAttr(self.templateGrp + '.typeFollicleCtrlX'): follicleCtrl = True
        if cmds.getAttr(self.templateGrp + '.typeFollicleCtrlY'): FACSCtrl = True
        if cmds.getAttr(self.templateGrp + '.typeFollicleCtrlZ'): AdjustCtrl = True

        # positions from template transforms/joints
        positions = [None]
        positions[0] = cmds.xform(self.templateControlers[0], q=True, rp=True, ws=True)

        ctrlInfo = self.getInfoControl(self.controlers[0])
        controlGrp, control = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                               color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                               axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                               position=self.templateControlers[0], rotation=self.templateControlers[0],
                                               node=node, \
                                               lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])

        if not AdjustCtrl:
            jnt = rigUtils.joint(position=self.templateControlers[0], name=preName + self.joints[self.controlers[0]][0],
                                 parent=control, node=node, side=ctrlInfo[1], connectedCtrl=control)
            sknJnt = rigUtils.joint(position=self.templateControlers[0],
                                    name=preName + self.sknJnts[self.controlers[0]][0], parent=jnt, node=node,
                                    side=ctrlInfo[1], connectedCtrl=control)
            sknJnts.append(sknJnt)
        else:
            # check pour un zeroAdjustmentSknJnt
            if not cmds.objExists('AdjustmentZeroSkin_RIG_grp'):
                self.createZeroAdjustmentNode()
            adjustZeroJnt = 'AdjustmentZero_jnt'
            adjustZeroSknJnt = 'AdjustmentZero_sknJnt'
            adjustZeroCtrl = 'AdjustmentZero_ctrl'
            controlSkinGrp, controlSkin = rigUtils.control(name=preName + 'Skin' + ctrlInfo[0], side=ctrlInfo[1],
                                                           shape='none', \
                                                           grpOffsets=['one'], parent=adjustZeroJnt,
                                                           position=self.templateControlers[0],
                                                           rotation=self.templateControlers[0], node=node, \
                                                           lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'],
                                                           parentCtrl=adjustZeroCtrl)

            jnt = rigUtils.joint(position=self.templateControlers[0],
                                 name=preName + 'Skin' + self.joints[self.controlers[0]][0], parent=controlSkin,
                                 node=node, side=ctrlInfo[1], connectedCtrl=controlSkin)
            sknJnt = rigUtils.joint(position=self.templateControlers[0],
                                    name=preName + 'Skin' + self.sknJnts[self.controlers[0]][0], parent=jnt, node=node,
                                    side=ctrlInfo[1], connectedCtrl=controlSkin)
            sknJnts.append(sknJnt)
            rigUtils.setJointParent(adjustZeroJnt, jnt)

            controlSkinGrpOffset = cmds.listRelatives(controlSkin, parent=True)[0]
            cmds.connectAttr('{}.translate'.format(control), '{}.translate'.format(controlSkinGrpOffset))
            cmds.connectAttr('{}.rotate'.format(control), '{}.rotate'.format(controlSkinGrpOffset))
            cmds.connectAttr('{}.scale'.format(control), '{}.scale'.format(controlSkinGrpOffset))

            rigUtils.setNodeCLeaner(self.rigGrp, controlSkinGrp)

        self.mayaControlers = [control]

        self.setLastNode(jnt)
        cmds.setAttr(jnt + '.drawStyle', 2)
        cmds.setAttr(sknJnt + '.radius', 0.35)
        cmds.connectAttr(assemblyAsset + '.joints', sknJnt + '.v')
        rigUtils.selectable(assemblyAsset + '.editJoints', [sknJnt])

        # 	def postRig(self):
        # looking for face mesh
        faceMesh = ''
        faceMeshes = cmds.ls('*.faceMeshTxt')
        if faceMeshes:
            faceMesh = cmds.getAttr(faceMeshes[0])

        attrDict = {}
        limitMinTrans = cmds.getAttr(self.templateGrp + '.limitMinTrans')[0]
        valueMinTrans = cmds.getAttr(self.templateGrp + '.valueMinTrans')[0]
        valueMaxTrans = cmds.getAttr(self.templateGrp + '.valueMaxTrans')[0]
        if limitMinTrans[0]:
            attrDict['tx'] = [valueMinTrans[0], valueMaxTrans[0]]
        if limitMinTrans[1]:
            attrDict['ty'] = [valueMinTrans[1], valueMaxTrans[1]]
        if limitMinTrans[2]:
            attrDict['tz'] = [valueMinTrans[2], valueMaxTrans[2]]

        attrToLockList = []
        hideLockTrans = cmds.getAttr(self.templateGrp + '.hideLockTrans')[0]
        hideLockRot = cmds.getAttr(self.templateGrp + '.hideLockRot')[0]
        hideLockScale = cmds.getAttr(self.templateGrp + '.hideLockScale')[0]
        if hideLockTrans[0]: attrToLockList.append('tx')
        if hideLockTrans[1]: attrToLockList.append('ty')
        if hideLockTrans[2]: attrToLockList.append('tz')
        if hideLockRot[0]: attrToLockList.append('rx')
        if hideLockRot[1]: attrToLockList.append('ry')
        if hideLockRot[2]: attrToLockList.append('rz')
        if hideLockScale[0]: attrToLockList.append('sx')
        if hideLockScale[1]: attrToLockList.append('sy')
        if hideLockScale[2]: attrToLockList.append('sz')

        lockAttributeNum = len(cmds.ls('{}.lockAttribute[*]'.format(self.templateGrp)))
        for i in range(lockAttributeNum):
            attrName = cmds.getAttr('{}.lockAttribute[{}].lockAttributeName'.format(self.templateGrp, str(i)))
            attrToLockList.append(attrName)

        if follicleCtrl:
            follicle = faceUtils.createFollicle(grpParent='RIG_grp', mesh=faceMesh, ctrl=control)
            faceUtils.constraintCtrl(constraintParent=follicle, constraintTarget=control, targetParentLevel=1)

        if FACSCtrl or AdjustCtrl:
            faceUtils.addAdjScale(control)
            faceUtils.solveDoubleTransform(control)
            faceUtils.setCtrlLimit(control, attrDict)
            follicle = faceUtils.createFollicle(grpParent='RIG_grp', mesh=faceMesh, ctrl=control)
            faceUtils.constraintCtrl(constraintParent=follicle, constraintTarget=control, targetParentLevel=3)

        rigUtils.lockAndHide([control], attrToLockList, lock=True, hide=True)

        cmds.select(control)
        cmds.refresh()

        return sknJnts

    def postRig(self):
        super(FaceOneJointWidget, self).postRig()

        control = self.mayaControlers[0]
        # looking for FACS blendshape
        FACSblendshape = ''
        FACSblendshapes = cmds.ls('*.facsBsTxt')
        if FACSblendshapes:
            FACSblendshape = cmds.getAttr(FACSblendshapes[0])

        targetConNum = len(cmds.ls('{}.targetCon[*]'.format(self.templateGrp)))
        for i in range(targetConNum):
            targetConName = cmds.getAttr('{}.targetCon[{}].targetConName'.format(self.templateGrp, str(i)))
            targetConAttribute = cmds.getAttr('{}.targetCon[{}].targetConAttribute'.format(self.templateGrp, str(i)))
            targetConFrom = cmds.getAttr('{}.targetCon[{}].targetConFrom'.format(self.templateGrp, str(i)))
            targetConTo = cmds.getAttr('{}.targetCon[{}].targetConTo'.format(self.templateGrp, str(i)))

            ctrlAttr = '{}.{}'.format(control, targetConAttribute)
            value = [float(targetConFrom), float(targetConTo)]
            faceUtils.setBsWeightAttr(FACSblendshape, targetConName, ctrlAttr, value)

    def createZeroAdjustmentNode(self):
        self.adjRigGrp = cmds.createNode('transform', n='AdjustmentZeroSkin_RIG_grp', p='RIG_grp')
        controlGrp, control = rigUtils.control(name='AdjustmentZero', side='', shape='none', \
                                               grpOffsets=['one'], parent=self.adjRigGrp, )

        jnt = rigUtils.joint(name='AdjustmentZero_jnt', parent=control, connectedCtrl=control)
        sknJnt = rigUtils.joint(name='AdjustmentZero_sknJnt', parent=jnt, connectedCtrl=control)
        cmds.setAttr('{}.drawStyle'.format(sknJnt), 2)
        cmds.parent(sknJnt, 'SKNJNTS_grp')
