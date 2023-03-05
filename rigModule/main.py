from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/mainWidgetOptions.ui'


class MainWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Global', 'Local', 'Root', 'Cog']
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
        # 		self.addGrpOffset(self.controlers[0], name = 'default')
        # 		self.addGrpOffset(self.controlers[0], name = 'default')
        # 		self.addSknJnt(self.controlers[3], name = 'specialSkTest_sknJnt')

        # set here default value for the controlers and shape.
        self.setControlerShape('Global', 'tileMain', 18, 'y')
        self.setControlerShape('Local', 'tileGimbal', 23, 'y')
        self.setControlerShape('Root', 'tileOffset', 17, 'y')
        self.setControlerShape('Cog', 'diamond', 14, 'y', 2)

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='scalable', at='bool')
        cmds.setAttr(self.templateGrp + '.scalable', e=True, keyable=True)

    def options(self):
        super(MainWidget, self).options()
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

            if not cmds.objExists(self.templateGrp + '.scalable'):
                cmds.addAttr(self.templateGrp, ln='scalable', at='bool')
                cmds.setAttr(self.templateGrp + '.scalable', e=True, keyable=True)
            scalable = cmds.getAttr(self.templateGrp + '.scalable')
            self.options_Qgb.scalable_chbx.setChecked(scalable)

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))
        self.options_Qgb.scalable_chbx.stateChanged.connect(partial(self.updateScalable))

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        self.templateControlers = [None] * 2
        self.templateControlers[0] = cmds.createNode('joint', n=self.getNode() + '_root_template', p=self.templateGrp)
        self.templateControlers[1] = cmds.createNode('joint', n=self.getNode() + '_cog_template', p=self.templateGrp)
        cmds.setAttr(self.templateControlers[1] + '.translateY', 15)

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ...  '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        scalable = cmds.getAttr(self.templateGrp + '.scalable')
        for axe in ['X', 'Y', 'Z']:
            cmds.setAttr("{}.scaleRig{}".format(self.rigDefaultNode, axe), 1)

        node = self.getNode()
        num = 4
        jnt = [None] * num
        sknJnt = [None] * num
        ctrls = [None] * num
        ctrls_grp = [None] * num

        for i in range(num):
            parentCtrl = None
            parentDirect = self.rigGrp
            position = self.templateControlers[0]
            if i:
                parentCtrl = ctrls[i - 1]
                parentDirect = jnt[i - 1]
            if i == 3:
                position = self.templateControlers[1]

            ctrlInfo = self.getInfoControl(self.controlers[i])
            ctrls_grp[i], ctrls[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=parentDirect,
                                                      position=position, rotation=position, \
                                                      lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'], node=node,
                                                      parentCtrl=parentCtrl)
            jnt[i] = rigUtils.joint(position=position, name=preName + self.joints[self.controlers[i]][0],
                                    parent=ctrls[i], node=node, side=ctrlInfo[1], connectedCtrl=ctrls[i])
            sknJnt[i] = rigUtils.joint(position=position, name=preName + self.sknJnts[self.controlers[i]][0],
                                       parent=jnt[i], node=node, side=ctrlInfo[1], connectedCtrl=ctrls[i])

        for i in range(1, 4):
            rigUtils.setJointParent(jnt[i - 1], jnt[i])

        for joint in jnt + sknJnt:
            cmds.setAttr(joint + '.drawStyle', 2)

        # create scale
        if scalable:
            cmds.addAttr(ctrls[0], ln='scaleRig', at='double', dv=1)
            cmds.setAttr(ctrls[0] + '.scaleRig', e=True, keyable=True)
            for axe in ['X', 'Y', 'Z']:
                cmds.connectAttr(ctrls[0] + '.scaleRig', "{}.scaleRig{}".format(self.rigDefaultNode, axe))

        cmds.connectAttr(self.rigDefaultNode + '.scaleRig', self.rigGrp + '.scale')
        self.mayaControlers = ctrls

        cmds.select(ctrls)
        cmds.refresh()

        return sknJnt
