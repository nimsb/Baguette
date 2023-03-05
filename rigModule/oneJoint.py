from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/spineWidgetOptions.ui'


class OneJointWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(OneJointWidget, self).__init__(parent)

        # self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

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

    def options(self):
        super(OneJointWidget, self).options()
        # add here any Qt options to the self.options_Qgb you would like to see
        if cmds.objExists(self.templateGrp):

            if not cmds.objExists(self.templateGrp + '.prependName'):
                cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
                cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
            prependName = cmds.getAttr(self.templateGrp + '.prependName')
            self.prependName_chbx.setChecked(prependName)

            if not cmds.objExists(self.templateGrp + '.prependNameTxt'):
                cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
                cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)
            prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
            self.prependName_lineEdit.setText(prependNameTxt)

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

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

        jnt = rigUtils.joint(position=self.templateControlers[0], name=preName + self.joints[self.controlers[0]][0],
                             parent=control, node=node, side=ctrlInfo[1], connectedCtrl=control)
        sknJnt = rigUtils.joint(position=self.templateControlers[0], name=preName + self.sknJnts[self.controlers[0]][0],
                                parent=jnt, node=node, side=ctrlInfo[1], connectedCtrl=control)

        self.mayaControlers = [control]

        self.setLastNode(jnt)
        cmds.setAttr(jnt + '.drawStyle', 2)
        cmds.setAttr(sknJnt + '.radius', 0.35)
        cmds.connectAttr(assemblyAsset + '.joints', sknJnt + '.v')
        rigUtils.selectable(assemblyAsset + '.editJoints', [sknJnt])

        cmds.select(control)
        cmds.refresh()

        return [sknJnt]
