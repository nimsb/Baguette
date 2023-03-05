from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range


# fileUi = os.path.dirname(os.path.abspath(__file__))+'/spineWidgetOptions.ui'

class HeadWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(HeadWidget, self).__init__(parent)

        # self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Head', 'Jaw', 'EyeFkLf', 'EyeFkRt', 'EyesIk']
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

        # 		self.addJoint(self.controlers[3])
        # 		self.addSknJnt(self.controlers[3])

        # set here default value for the controlers and shape.
        self.setControlerShape('Head', 'circle', 18, axe='y', radius=2)
        self.setControlerShape('Jaw', 'circle', 18, axe='x', radius=0.75)
        self.setControlerShape('EyeFkLf', 'sphere', 7, axe='z', radius=0.5)
        self.setControlerShape('EyeFkRt', 'sphere', 14, axe='z', radius=0.5)
        self.setControlerShape('EyesIk', 'cube', 15, axe='y', radius=0.5)

    def options(self):
        super(HeadWidget, self).options()

    # add here any Qt options to the self.options_Qgb you would like to see

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * 5
        pos = [(0, 0, 0), (0, -0.5, 0.25), (0.5, 0.5, 1), (-0.5, 0.5, 1), (0, 0.5, 4)]
        for i in range(5):
            name = '{}_{}_template'.format(node, self.controlers[i])
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode('joint', n=name, p=self.templateGrp)
                cmds.setAttr(self.templateControlers[i] + '.t', pos[i][0], pos[i][1], pos[i][2])
                if i:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateControlers[0])[0]
            cmds.setAttr(self.templateControlers[i] + '.radius', 0.5)

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ... '''
        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        # positions from template transforms/joints
        # 		positions = [None]*5
        # 		for i in range(5):
        # 			positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        ctrl_grp = [None] * 5
        ctrl = [None] * 5

        ctrlInfo = self.getInfoControl(self.controlers[0])
        ctrl_grp[0], ctrl[0] = rigUtils.control(name=ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                position=self.templateControlers[0],
                                                rotation=self.templateControlers[0], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])
        # 		cmds.addAttr(ctrl[0], ln='joints', at='bool', dv=True, k=True)
        # 		cmds.addAttr(ctrl[0], ln='editJoints', at='bool', k=True)
        cmds.addAttr(ctrl[0], ln='fkControls', at='bool', dv=True, k=True)
        cmds.addAttr(ctrl[0], ln='ikControls', at='bool', dv=True, k=True)

        ctrlInfo = self.getInfoControl(self.controlers[1])
        ctrl_grp[1], ctrl[1] = rigUtils.control(name=ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[0],
                                                position=self.templateControlers[1],
                                                rotation=self.templateControlers[1], node=node, \
                                                lockAttr=['t', 's', 'v'],
                                                hideAttr=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'], parentCtrl=ctrl[0])

        ctrlInfo = self.getInfoControl(self.controlers[4])
        ctrl_grp[4], ctrl[4] = rigUtils.control(name=ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[0],
                                                position=self.templateControlers[4],
                                                rotation=self.templateControlers[4], node=node, \
                                                lockAttr=['sy', 'sz', 'v'], hideAttr=['sy', 'sz', 'v'],
                                                parentCtrl=ctrl[0])

        ctrlInfo = self.getInfoControl(self.controlers[2])
        ctrl_grp[2], ctrl[2] = rigUtils.control(name=ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[0],
                                                position=self.templateControlers[2],
                                                rotation=self.templateControlers[2], node=node, \
                                                lockAttr=['t', 'rz', 's', 'v'],
                                                hideAttr=['tx', 'ty', 'tz', 'rz', 'sx', 'sy', 'sz', 'v'],
                                                parentCtrl=ctrl[4])

        ctrlInfo = self.getInfoControl(self.controlers[3])
        ctrl_grp[3], ctrl[3] = rigUtils.control(name=ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[0],
                                                position=self.templateControlers[3],
                                                rotation=self.templateControlers[3], node=node, \
                                                lockAttr=['t', 'rz', 's', 'v'],
                                                hideAttr=['tx', 'ty', 'tz', 'rz', 'sx', 'sy', 'sz', 'v'],
                                                parentCtrl=ctrl[4])

        self.mayaControlers = []
        for ctl in ctrl:
            self.mayaControlers.append(ctl)

        for n in [ctrl[1], ctrl[2], ctrl[3], ctrl[4]]:
            if cmds.listRelatives(n, pa=True, s=True):
                cmds.connectAttr(ctrl[0] + '.fkControls', cmds.listRelatives(n, pa=True, s=True)[0] + '.v')

        jnt = [None] * 5
        sknJnt = [None] * 5
        joints = []
        sknJnts = []

        for controler in self.controlers:
            for thisJnt in self.joints[controler]:
                joints.append(thisJnt)
            for thisJnt in self.sknJnts[controler]:
                sknJnts.append(thisJnt)

        for i in range(5):
            jnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                    name=joints[i], parent=ctrl[i], \
                                    node=node, side=ctrlInfo[1], connectedCtrl=ctrl[i])
            sknJnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                       name=sknJnts[i], parent=jnt[i], \
                                       node=node, side=ctrlInfo[1], connectedCtrl=ctrl[i])
            cmds.setAttr(jnt[i] + '.radius', 0.35)
            cmds.setAttr(sknJnt[i] + '.radius', 0.35)
            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

            if i:
                rigUtils.setJointParent(jnt[0], jnt[i])

        #
        # ik controls
        #

        eye_lf_aim = cmds.createNode('transform', n='eye_lf_aim', p=ctrl[4])
        cmds.delete(cmds.pointConstraint(jnt[2], eye_lf_aim))
        cmds.setAttr(eye_lf_aim + '.tz', 0)
        eye_rt_aim = cmds.createNode('transform', n='eye_rt_aim', p=ctrl[4])
        cmds.delete(cmds.pointConstraint(jnt[3], eye_rt_aim))
        cmds.setAttr(eye_rt_aim + '.tz', 0)

        n = cmds.listRelatives(ctrl[2], pa=True, p=True)[0]
        c = \
        cmds.aimConstraint(eye_lf_aim, n, aim=(0, 0, 1), u=(0, 1, 0), wut='objectrotation', wu=(0, 1, 0), wuo=ctrl[4],
                           mo=True)[0]
        cmds.rename(c, n + '_aimcon')
        n = cmds.listRelatives(ctrl[3], pa=True, p=True)[0]
        c = \
        cmds.aimConstraint(eye_rt_aim, n, aim=(0, 0, 1), u=(0, 1, 0), wut='objectrotation', wu=(0, 1, 0), wuo=ctrl[4],
                           mo=True)[0]
        cmds.rename(c, n + '_aimcon')

        # selection sets
        # 		common.sets(name, jnt, fk_ctrl, [ik_ctrl])

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        cmds.select(ctrl[0])
        cmds.refresh()

        return sknJnt
