from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/spineWidgetOptions.ui'


class HandWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(HandWidget, self).__init__(parent)

        # self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Hand']
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

        for i in range(5):
            if i:
                cnt = 4
            else:
                cnt = 3
            for j in range(cnt):
                self.addJoint(self.controlers[i])
                self.addSknJnt(self.controlers[i])
        # 		self.addJoint(self.controlers[3])
        # 		self.addSknJnt(self.controlers[3])

        # set here default value for the controlers and shape.
        self.setControlerShape('Thumb', 'circle', 13, 'x', 0.3)
        self.setControlerShape('Index', 'circle', 13, 'x', 0.3)
        self.setControlerShape('Middle', 'circle', 13, 'x', 0.3)
        self.setControlerShape('Ring', 'circle', 13, 'x', 0.3)
        self.setControlerShape('Pinky', 'circle', 13, 'x', 0.3)
        self.setControlerShape('Hand', 'circle', 18, 'x', 2)

        # prependName
        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='locTemplate', dt='string')
        cmds.setAttr(self.templateGrp + '.locTemplate', e=True, keyable=True)

    def options(self):
        super(HandWidget, self).options()
        # add here any Qt options to the self.options_Qgb you would like to see
        # this happen after the item and the node are created.
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

            if not cmds.objExists(self.templateGrp + '.locTemplate'):
                cmds.addAttr(self.templateGrp, ln='locTemplate', dt='string')
                cmds.setAttr(self.templateGrp + '.locTemplate', e=True, keyable=True)
            allLoc = []
            for i in range(5):
                cnt = 5
                if i:
                    a = 1
                else:
                    cnt = 4
                    a = 0
                locA = self.templateControlers[i][a] + '_locA'
                locB = self.templateControlers[i][a] + '_locB'
                allLoc.append(locA)
                allLoc.append(locB)
            cmds.setAttr(self.templateGrp + '.locTemplate', allLoc, type='string')

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * 6
        pos = [[(0.25, -0.45, 0.65), (1, -0.45, 0.65), (1.75, -0.45, 0.65), (2.5, -0.45, 0.65)], \
               [(0.25, 0, 0.35), (1, 0, 0.35), (1.75, 0, 0.35), (2.5, 0, 0.35), (3.25, 0, 0.35)], \
               [(0.25, 0, 0), (1, 0, 0), (1.75, 0, 0), (2.5, 0, 0), (3.25, 0, 0)], \
               [(0.25, 0, -0.35), (1, 0, -0.35), (1.75, 0, -0.35), (2.5, 0, -0.35), (3.25, 0, -0.35)], \
               [(0.25, 0, -0.7), (1, 0, -0.7), (1.75, 0, -0.7), (2.5, 0, -0.7), (3.25, 0, -0.7)],
               (0, 0, 0)]

        self.templateControlers[5] = cmds.createNode('joint', n='{}_{}_template'.format(node, self.controlers[5]),
                                                     p=self.templateGrp)
        cmds.setAttr(self.templateControlers[5] + '.radius', 0.25)

        for i in range(5):
            if i:
                cnt = 5
            else:
                cnt = 4
            self.templateControlers[i] = [None] * cnt
            for j in range(cnt):
                name = '{}_{}_{}_template'.format(node, self.controlers[i], str(j + 1))
                if cmds.objExists(name):
                    self.templateControlers[i][j] = name
                else:
                    self.templateControlers[i][j] = cmds.createNode('joint', n=name, p=self.templateGrp)

                    cmds.setAttr(self.templateControlers[i][j] + '.t', pos[i][j][0], pos[i][j][1], pos[i][j][2])

                    if j:
                        self.templateControlers[i][j] = \
                        cmds.parent(self.templateControlers[i][j], self.templateControlers[i][j - 1])[0]
                    else:
                        self.templateControlers[i][j] = \
                        cmds.parent(self.templateControlers[i][j], self.templateControlers[5])[0]

                cmds.setAttr(self.templateControlers[i][j] + '.radius', 0.25)

        self.postTemplate()

        cmds.setAttr(self.templateControlers[0][0] + '.r', 80, -15, -15)

        cmds.select(self.templateGrp)

    def postTemplate(self, mirror=False):
        allLoc = []
        for i in range(5):
            if i:
                a = 1
            else:
                a = 0

            locA = self.templateControlers[i][a] + '_locA'
            if not cmds.objExists(locA):
                locA = cmds.spaceLocator(n=locA)[0]
                cmds.setAttr(locA + '.s', 0.1, 0.1, 0.1)
                cmds.parent(locA, self.templateControlers[i][a])
                cmds.setAttr(locA + '.t', 0, 0.7, 0)
                cmds.setAttr(locA + '.r', 0, 0, 0)
            allLoc.append(locA)

            locB = self.templateControlers[i][a] + '_locB'
            if not cmds.objExists(locB):
                locB = cmds.spaceLocator(n=locB)[0]
                cmds.setAttr(locB + '.s', 0.1, 0.1, 0.1)
                cmds.parent(locB, self.templateControlers[i][a])
                cmds.setAttr(locB + '.t', 0, 0, 0)
                cmds.setAttr(locB + '.r', 0, 0, 0)
            allLoc.append(locB)

            if mirror:
                locA_t = cmds.getAttr(locA + '.t')[0]
                cmds.setAttr(locA + '.t', locA_t[0], locA_t[1] * -1, locA_t[2] * -1)

            aimCstr = self.templateControlers[i][a] + '_aimCstr'
            if cmds.objExists(aimCstr):
                cmds.delete(aimCstr)
            aimCstr = cmds.aimConstraint(locA, locB, aim=(0, 1, 0), u=(0, 1, 0), wut='scene', n=aimCstr)

            cmds.setAttr(self.templateGrp + '.locTemplate', allLoc, type='string')

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ...
        TODO >
        add joint for foot side,
        add joint for pv position
        use aimConstraint to orient joints
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt
        self.mayaControlers = []
        radius = 0.5
        # positions from template transforms/joints

        # snap hand to default position
        rigUtils.snapTranslation(self.templateControlers[5], self.rigGrp)

        positions = [None] * 5
        fk = [None] * 5

        for i in range(5):
            cnt = 5
            if i:
                a = 1
            else:
                cnt = 4
                a = 0
            positions[i] = [None] * cnt
            fk[i] = [None] * cnt

            for j in range(cnt):
                positions[i][j] = cmds.xform(self.templateControlers[i][j], q=True, rp=True, ws=True)
                fk[i][j] = cmds.createNode('joint', n='{}_{}_{}_fk'.format(node, str(i), str(j)))
                cmds.setAttr(fk[i][j] + '.radius', radius * 0.3)
                cmds.setAttr(fk[i][j] + '.t', positions[i][j][0], positions[i][j][1], positions[i][j][2])
                fk[i][j] = cmds.parent(fk[i][j], self.rigGrp)[0]

            upVector = self.templateControlers[i][a] + '_locA'
            cmds.delete(cmds.aimConstraint(fk[i][1], fk[i][0], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))
            cmds.delete(cmds.aimConstraint(fk[i][2], fk[i][1], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))
            cmds.delete(cmds.aimConstraint(fk[i][3], fk[i][2], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))
            cmds.delete(cmds.aimConstraint(fk[i][2], fk[i][3], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))
            if cnt == 5:
                cmds.delete(
                    cmds.aimConstraint(fk[i][4], fk[i][3], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))
                cmds.delete(
                    cmds.aimConstraint(fk[i][3], fk[i][4], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=upVector))

        jnt = [None] * 6
        sknJnt = [None] * 6
        allJnt = []

        ctrlInfo = self.getInfoControl(self.controlers[5])
        side = ctrlInfo[1]
        controlGrp, control = rigUtils.control(name=preName + ctrlInfo[0], side=side, shape=ctrlInfo[2],
                                               color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                               axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                               position=self.templateControlers[5], rotation=self.templateControlers[5],
                                               node=node, \
                                               lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])

        self.mayaControlers.append(control)

        jnt[5] = rigUtils.joint(position=self.templateControlers[5], orientation=self.templateControlers[5],
                                name='{}{}_0_jnt'.format(preName, ctrlInfo[0]), parent=control, \
                                node=node, typeJnt='', side=side, radius=radius * 0.5, connectedCtrl=control)
        cmds.setAttr(jnt[5] + '.drawStyle', 2)
        sknJnt[5] = rigUtils.joint(position=jnt[5], orientation=jnt[5],
                                   name='{}{}_0_sknJnt'.format(preName, ctrlInfo[0]), parent=jnt[5], node=node,
                                   typeJnt='sknJnt', \
                                   side=side, radius=radius * 0.5, connectedCtrl=control)
        cmds.connectAttr(assemblyAsset + '.joints', sknJnt[5] + '.v')
        if not cmds.objExists(control + '.fingerControls'):
            cmds.addAttr(control, ln='fingerControls', at='bool', dv=True, k=True)
        if not cmds.objExists(control + '.bend'):
            cmds.addAttr(control, ln='bend', at='double', min=-10, max=10, k=True)
        if not cmds.objExists(control + '.splay'):
            cmds.addAttr(control, ln='splay', at='double', min=-10, max=10, k=True)

        md1 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(control + '.bend', md1 + '.input1.input1X')
        cmds.connectAttr(control + '.bend', md1 + '.input1.input1Y')
        cmds.connectAttr(control + '.bend', md1 + '.input1.input1Z')
        cmds.setAttr(md1 + '.input2X', 6)
        cmds.setAttr(md1 + '.input2Y', 9)
        cmds.setAttr(md1 + '.input2Z', 9)
        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(control + '.bend', md2 + '.input1.input1X')
        cmds.connectAttr(control + '.bend', md2 + '.input1.input1Y')
        cmds.connectAttr(control + '.bend', md2 + '.input1.input1Z')
        cmds.setAttr(md2 + '.input2X', 8)
        cmds.setAttr(md2 + '.input2Y', 11)
        cmds.setAttr(md2 + '.input2Z', 7.5)

        ctrl_grp = [None] * 5
        ctrl = [None] * 5
        for i in range(5):
            cmds.select(cl=True)
            ctrlInfo = self.getInfoControl(self.controlers[i])

            if i:
                cnt = 4
            else:
                cnt = 3

            ctrl_grp[i] = [None] * cnt
            ctrl[i] = [None] * cnt
            jnt[i] = [None] * cnt
            sknJnt[i] = [None] * cnt

            for j in range(cnt):
                lockAttr = ('t', 'rx', 'rz', 's', 'v')
                hideAttr = ('tx', 'ty', 'tz', 'rx', 'rz', 'sx', 'sy', 'sz', 'v')

                if (i and j == 1) or (not i and not j):
                    lockAttr = ('s', 'v')
                    hideAttr = ('sx', 'sy', 'sz', 'v')

                if i and not j:
                    lockAttr = ('s', 'v', 't')
                    hideAttr = ('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

                if j:
                    _parent = ctrl[i][j - 1]
                else:
                    _parent = control

                if not i and not j:
                    numOffsetGroups = ctrlInfo[6]
                else:
                    numOffsetGroups = None

                ctrl_grp[i][j], ctrl[i][j] = rigUtils.control(name=preName + ctrlInfo[0], num='_' + str(j), side=side,
                                                              shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                              radius=ctrlInfo[7], \
                                                              axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                              parent=_parent, position=fk[i][j], rotation=fk[i][j],
                                                              node=node, \
                                                              lockAttr=lockAttr, hideAttr=hideAttr, parentCtrl=_parent)

                self.mayaControlers.append(ctrl[i][j])

                if cmds.listRelatives(ctrl[i][j], pa=True, s=True):
                    cmds.connectAttr(control + '.fingerControls',
                                     cmds.listRelatives(ctrl[i][j], pa=True, s=True)[0] + '.v')

                jnt[i][j] = rigUtils.joint(position=fk[i][j], orientation=fk[i][j],
                                           name=preName + self.joints[self.controlers[i]][j], parent=ctrl[i][j],
                                           node=node, typeJnt='', side=side, \
                                           radius=radius * 0.5, connectedCtrl=ctrl[i][j])
                cmds.setAttr(jnt[i][j] + '.drawStyle', 2)
                cmds.setAttr(jnt[i][j] + '.jo', 0, 0, 0)

                sknJnt[i][j] = rigUtils.joint(position=jnt[i][j], orientation=jnt[i][j],
                                              name=preName + self.sknJnts[self.controlers[i]][j], parent=jnt[i][j],
                                              node=node, typeJnt='sknJnt', \
                                              side=side, radius=radius * 0.5, connectedCtrl=ctrl[i][j])
                cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i][j] + '.v')
                allJnt.append(sknJnt[i][j])
                if j:
                    rigUtils.setJointParent(jnt[i][j - 1], jnt[i][j])
                else:
                    rigUtils.setJointParent(jnt[5], jnt[i][j])

                cmds.setAttr(jnt[i][j] + '.radius', radius * 0.3)

                # bend
                if j:
                    cmds.connectAttr(md2 + '.outputX', ctrl_grp[i][j] + '.ray')

            if i:
                c = \
                cmds.aimConstraint(jnt[i][1], jnt[i][0], aim=(1, 0, 0), u=(0, 0, 1), wut='objectrotation', wuo=control)[
                    0]
                cmds.rename(c, jnt[i][0] + '_aimcon')

        allJnt.append(sknJnt[5])

        # splay
        md1 = cmds.createNode('multiplyDivide', n='{}Splay1_mdn'.format(node))
        cmds.connectAttr(control + '.splay', md1 + '.input1.input1X')
        cmds.connectAttr(control + '.splay', md1 + '.input1.input1Y')
        cmds.connectAttr(control + '.splay', md1 + '.input1.input1Z')
        cmds.setAttr(md1 + '.input2X', -1.5)
        cmds.setAttr(md1 + '.input2Y', -3)
        cmds.setAttr(md1 + '.input2Z', -6)
        md2 = cmds.createNode('multiplyDivide', n='{}Splay2_mdn'.format(node))
        cmds.connectAttr(control + '.splay', md2 + '.input1.input1X')
        cmds.connectAttr(control + '.splay', md2 + '.input1.input1Y')
        cmds.connectAttr(control + '.splay', md2 + '.input1.input1Z')
        cmds.setAttr(md2 + '.input2X', 1.5)
        cmds.setAttr(md2 + '.input2Y', 3)
        cmds.setAttr(md2 + '.input2Z', 6)

        # cmds.connectAttr(md1+'.outputX', cmds.listRelatives(ctrl[0][0], pa=True, p=True)[0]+'.ray')
        if positions[i][2][0] >= -0.001:
            cmds.connectAttr(md1 + '.outputZ', ctrl_grp[0][0] + '.ray')
            cmds.connectAttr(md1 + '.outputX', ctrl_grp[1][0] + '.raz')
            cmds.connectAttr(md2 + '.outputX', ctrl_grp[3][0] + '.raz')
            cmds.connectAttr(md2 + '.outputY', ctrl_grp[4][0] + '.raz')
        else:
            rev = cmds.createNode('reverse', n='{}Reverse1_mdn'.format(node))
            rev2 = cmds.createNode('reverse', n='{}Reverse2_mdn'.format(node))
            cmds.connectAttr(md1 + '.outputX', rev + '.inputX')
            cmds.connectAttr(md2 + '.outputZ', rev2 + '.inputZ')
            cmds.connectAttr(md2 + '.outputX', rev + '.inputY')
            cmds.connectAttr(md2 + '.outputY', rev + '.inputZ')
            cmds.connectAttr(rev2 + '.outputZ', ctrl_grp[0][0] + '.ray')
            cmds.connectAttr(rev + '.outputX', ctrl_grp[1][0] + '.raz')
            cmds.connectAttr(rev + '.outputY', ctrl_grp[3][0] + '.raz')
            cmds.connectAttr(rev + '.outputZ', ctrl_grp[4][0] + '.raz')

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', allJnt)

        for fkJnt in fk:
            cmds.delete(fkJnt)

        for joint in allJnt:
            cmds.setAttr(joint + '.jo', 0, 0, 0)

        cmds.select(control)
        cmds.refresh()

        return allJnt
