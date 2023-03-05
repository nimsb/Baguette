from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/armWidgetOptions.ui'


class ArmWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(ArmWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['HandIk', 'ElbowPv', 'ClavicleFk', 'Shoulder', 'Elbow', 'HandFk', 'ClavicleIk']
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

        # 		for i in range(3,6):
        # 			self.rmvGrpOffset(self.controlers[i])

        # set here default value for the controlers and shape.
        self.setControlerShape('HandIk', 'cube', 7, axe='x')
        self.setControlerShape('ElbowPv', 'cube', 7, axe='x', radius=0.2)
        self.setControlerShape('ClavicleFk', 'circle', 14, axe='x')
        self.setControlerShape('Shoulder', 'circle', 14, axe='x')
        self.setControlerShape('Elbow', 'circle', 14, axe='x')
        self.setControlerShape('HandFk', 'circle', 14, axe='x')
        self.setControlerShape('ClavicleIk', 'cube', 7, axe='x')

        # add elbow option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='doubleElbow', at='bool')
        cmds.setAttr(self.templateGrp + '.doubleElbow', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
        cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='defaultHandRot', at='bool')
        cmds.setAttr(self.templateGrp + '.defaultHandRot', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

    def updateElbow(self, state):
        node = self.getNode()
        if state:
            # create jnt and parent it
            name = '{}_{}_template'.format(node, '3bis')
            jnt = cmds.createNode('joint', n=name, p=self.templateControlers[2])
            cmds.setAttr(jnt + '.radius', cmds.getAttr(self.templateControlers[2] + '.radius'))
            pos = cmds.getAttr(self.templateControlers[3] + '.t')[0]
            cmds.setAttr(jnt + '.t', pos[0] / 5, pos[1] / 5, 0)
            self.templateControlers.insert(3, jnt)
            cmds.parent(self.templateControlers[4], jnt)
            cmds.setAttr(self.templateGrp + '.doubleElbow', True)


        else:
            # reparent the jnt and delete the doubleKnee
            if len(self.templateControlers) == 5:
                cmds.parent(self.templateControlers[4], self.templateControlers[2])
                cmds.delete(self.templateControlers[3])
                self.templateControlers.pop(3)
                cmds.setAttr(self.templateGrp + '.doubleElbow', False)

        cmds.setAttr(self.templateGrp + '.isTemplate', str(self.templateControlers), type='string')
        cmds.select(self.templateGrp)

        if cmds.objExists('{}_TEMP_sknJnt_grp'.format(node)):
            cmds.delete('{}_TEMP_sknJnt_grp'.format(node))

        self.setState(1)

    def updateNumTwist(self, value):
        cmds.setAttr(self.templateGrp + '.numTwist', value)
        self.setState(1)

    def updateHandRot(self, value):
        if value: value = 1
        cmds.setAttr(self.templateGrp + '.defaultHandRot', value)
        self.setState(1)

    def options(self):
        super(ArmWidget, self).options()
        # this happen after the item and the node are created.
        if cmds.objExists(self.templateGrp):
            if not cmds.objExists(self.templateGrp + '.doubleElbow'):
                cmds.addAttr(self.templateGrp, ln='doubleElbow', at='bool')
                cmds.setAttr(self.templateGrp + '.doubleElbow', e=True, keyable=True)
            if not cmds.objExists(self.templateGrp + '.numTwist'):
                cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
                cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)
            isDoubleElbow = cmds.getAttr(self.templateGrp + '.doubleElbow')
            self.qtOptions.doubleElbow_ckb.setChecked(isDoubleElbow)
            numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
            self.qtOptions.numTwist_box.setValue(numTwist)

            if not cmds.objExists(self.templateGrp + '.defaultHandRot'):
                cmds.addAttr(self.templateGrp, ln='defaultHandRot', at='bool')
                cmds.setAttr(self.templateGrp + '.defaultHandRot', e=True, keyable=True)
            isDefaultHandRot = cmds.getAttr(self.templateGrp + '.defaultHandRot')
            self.qtOptions.defaultHandRotation_ckb.setChecked(isDefaultHandRot)

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

        self.qtOptions.doubleElbow_ckb.stateChanged.connect(partial(self.updateElbow))
        self.qtOptions.defaultHandRotation_ckb.stateChanged.connect(partial(self.updateHandRot))
        self.qtOptions.numTwist_box.valueChanged.connect(partial(self.updateNumTwist))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * 4
        pos = [(0.5, 0, 0), (2, 0, 0), (5, 0, -0.25), (8, 0, 0)]
        for i in range(4):
            name = '{}_{}_template'.format(node, str(i + 1))
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode('joint', n=name)

                cmds.setAttr(self.templateControlers[i] + '.t', pos[i][0], pos[i][1], pos[i][2])
                if i:
                    self.templateControlers[i] = \
                    cmds.parent(self.templateControlers[i], self.templateControlers[i - 1])[0]
                else:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateGrp)[0]

            cmds.setAttr(self.templateControlers[i] + '.radius', 0.5)

        # set lastNode
        self.setLastNode(self.joints[self.controlers[5]][0])

    def defaultWidget(self):
        pass

    def rig(self):
        '''
        TO DO : remove groups who are not used anymore
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        radius = 1
        isDoubleElbow = cmds.getAttr(self.templateGrp + '.doubleElbow')
        isDefaultHandRot = cmds.getAttr(self.templateGrp + '.defaultHandRot')
        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')

        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        # positions from template transforms/joints
        count = len(self.templateControlers)
        positions = [None] * count
        for i in range(count):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        #
        # joints
        #

        ik = [None] * count
        # first ik joint
        ik[0] = cmds.createNode("joint", n=node + "_ik1")
        cmds.setAttr(ik[0] + ".t", positions[0][0], positions[0][1], positions[0][2])

        for i in range(1, count):
            ik[i] = cmds.createNode('joint', n=node + '_ik' + str(i + 1), p=self.rigGrp)
            cmds.setAttr(ik[i] + '.t', positions[i][0], positions[i][1], positions[i][2])

        mid = cmds.createNode('transform')
        c = cmds.pointConstraint(ik[1], ik[-1], mid)

        if positions[1][0] >= -0.001:
            cmds.delete(cmds.aimConstraint(ik[2], ik[1], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[3]))
            cmds.delete(cmds.aimConstraint(ik[3], ik[2], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=mid))
            cmds.delete(cmds.aimConstraint(ik[2], ik[3], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[1]))
            if isDoubleElbow:
                cmds.delete(cmds.aimConstraint(ik[4], ik[3], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[1]))
                cmds.delete(cmds.aimConstraint(ik[3], ik[4], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=ik[1]))

        else:
            cmds.delete(cmds.aimConstraint(ik[2], ik[1], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[3]))
            cmds.delete(cmds.aimConstraint(ik[3], ik[2], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=mid))
            cmds.delete(cmds.aimConstraint(ik[2], ik[3], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[1]))
            if isDoubleElbow:
                cmds.delete(cmds.aimConstraint(ik[4], ik[3], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[1]))
                cmds.delete(cmds.aimConstraint(ik[3], ik[4], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=ik[1]))

        if isDefaultHandRot:
            cmds.delete(cmds.orientConstraint(self.templateControlers[-1], ik[-1]))

        cmds.delete(mid)

        for i in range(1, count):
            r = cmds.getAttr(ik[i] + '.r')[0]
            cmds.setAttr(ik[i] + '.jo', r[0], r[1], r[2])
            cmds.setAttr(ik[i] + '.r', 0, 0, 0)
            cmds.setAttr(ik[i] + '.radius', radius * 0.5)

        n = cmds.createNode('transform')
        cmds.delete(cmds.pointConstraint(ik[0], n))
        cmds.setAttr(n + '.tz', cmds.getAttr(n + '.tz') - 1)
        if positions[1][0] >= -0.001:
            cmds.delete(cmds.aimConstraint(ik[1], ik[0], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=n))
        else:
            cmds.delete(cmds.aimConstraint(ik[1], ik[0], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=n))
        cmds.delete(n)
        r = cmds.getAttr(ik[0] + '.r')[0]
        cmds.setAttr(ik[0] + '.jo', r[0], r[1], r[2])
        cmds.setAttr(ik[0] + '.r', 0, 0, 0)

        #
        # ik controls
        #

        ik_ctrl_grp = [None] * 3
        ik_ctrl = [None] * 3

        ctrlInfo = self.getInfoControl(self.controlers[0])
        ik_ctrl_grp[1], ik_ctrl[1] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                      position=ik[-1], node=node, \
                                                      lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'],
                                                      controlType='')

        # 		cmds.addAttr(ik_ctrl[1], ln='joints', at='bool', dv=True, k=True)
        # 		cmds.addAttr(ik_ctrl[1], ln='editJoints', at='bool', k=True)
        cmds.addAttr(ik_ctrl[1], ln='fkControls', at='bool', dv=True, k=True)
        cmds.addAttr(ik_ctrl[1], ln='ikControls', at='bool', dv=True, k=True)
        cmds.addAttr(ik_ctrl[1], ln='stretch', at='bool', k=True)

        ctrlInfo = self.getInfoControl(self.controlers[1])
        ik_ctrl_grp[2], ik_ctrl[2] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                      position=ik[2], rotation=ik[2], node=node, \
                                                      lockAttr=['r', 's'],
                                                      hideAttr=['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                                      controlType='')

        distance = rigUtils.getDistance(ik[2], ik[-1])
        if positions[1][0] >= -0.001:
            cmds.move(0, 0, distance, ik_ctrl_grp[2], os=True, r=True, wd=True)
        else:
            cmds.move(0, 0, -distance, ik_ctrl_grp[2], os=True, r=True, wd=True)
        cmds.connectAttr(ik_ctrl[1] + '.ikControls', ik_ctrl[2] + '.v')

        #
        # ik stretch joints
        #

        ik2 = [None] * count
        for i in range(count):
            ik2[i] = cmds.duplicate(ik[i])[0]
            ik2[i] = cmds.rename(ik2[i], node + '_ik' + str(i + 1) + '_str')
            # 			if not i:
            # 				ik2[i] = cmds.parent(ik2[i], self.rigGrp)[0]
            if i:
                ik2[i] = cmds.parent(ik2[i], ik2[i - 1])[0]
                if i < count - 1:
                    c = cmds.parentConstraint(ik[i], ik2[i])[0]
                    cmds.rename(c, node + '_ik' + str(i + 1) + '_str_parcon')
                else:
                    c = cmds.pointConstraint(ik[i], ik2[i])[0]
                    cmds.rename(c, node + '_ik' + str(i + 1) + '_str_pntcon')
                if i == 2 or (count == 5 and (i == 2 or i == 3)): cmds.connectAttr(ik[i] + '.r', ik2[i] + '.r')
            else:
                cmds.delete(cmds.listRelatives(ik2[i], pa=True, s=True))
            cmds.setAttr(ik2[i] + '.jo', 0, 0, 0)

        cmds.delete(cmds.orientConstraint(ik[-1], ik2[-1]))
        c = cmds.orientConstraint(ik_ctrl[1], ik2[-1], mo=True)[0]
        cmds.rename(c, ik2[-1].split('|')[-1] + '_oricon')

        #
        # fk joints and controls
        #

        fk_ctrlGrp = [None] * count
        fk_ctrl = [None] * count
        jnt = [None] * count
        sknJnt = [None] * count
        for i in range(count):
            o = i
            sub = ''
            if count == 5:
                if i == 3:
                    o = 2
                    sub = 'Bis'
                if i > 3:
                    o = i - 1

            if i:

                ctrlInfo = self.getInfoControl(self.controlers[o + 2])
                fk_ctrlGrp[i], fk_ctrl[i] = rigUtils.control(name=preName + ctrlInfo[0] + sub, side=ctrlInfo[1],
                                                             shape=ctrlInfo[2], color=ctrlInfo[3], \
                                                             command=ctrlInfo[4], radius=ctrlInfo[7],
                                                             axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], \
                                                             parent=self.rigGrp, position=ik[i], rotation=ik[i],
                                                             node=node, \
                                                             lockAttr=[], hideAttr=[], controlType='joint')

                cmds.connectAttr(ik2[i] + '.t', fk_ctrlGrp[i] + '.t')
                cmds.connectAttr(ik2[i] + '.r', fk_ctrlGrp[i] + '.jo')
                cmds.setAttr(fk_ctrlGrp[i] + '.r', 0, 0, 0)
                if cmds.listRelatives(fk_ctrl[i], pa=True, s=True):
                    cmds.connectAttr(ik_ctrl[1] + '.fkControls',
                                     cmds.listRelatives(fk_ctrl[i], pa=True, s=True)[0] + '.v')

            else:
                ctrlInfo = self.getInfoControl(self.controlers[-1])
                fk_ctrlGrp[i], fk_ctrl[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                             shape=ctrlInfo[2], color=ctrlInfo[3], \
                                                             command=ctrlInfo[4], radius=ctrlInfo[7],
                                                             axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], \
                                                             parent=self.rigGrp, position=ik[0], rotation=ik[0],
                                                             node=node, \
                                                             lockAttr=[], hideAttr=[], controlType='joint')
                # the first fk control becomes ik one
                if cmds.listRelatives(fk_ctrl[i], pa=True, s=True):
                    cmds.connectAttr(ik_ctrl[1] + '.ikControls',
                                     cmds.listRelatives(fk_ctrl[i], pa=True, s=True)[0] + '.v')

            # 			if i == 1:
            # 				fk_ctrl[i] = cmds.parent(fk_ctrlGrp[i], self.rigGrp)[0]

            if i > 1:
                fk_ctrlGrp[i] = cmds.parent(fk_ctrlGrp[i], fk_ctrl[i - 1])[0]

                # now let's find his real ctrl in case we have several module with the same name
                obj = cmds.listRelatives(fk_ctrlGrp[i], ad=True, type='transform')[::-1][len(ctrlInfo[6])]
                allObj = cmds.ls(obj)
                if len(allObj) > 1:
                    for ctrl in allObj:
                        if fk_ctrlGrp[i] in ctrl:
                            fk_ctrl[i] = ctrl
                            break
                else:
                    fk_ctrl[i] = obj

            cmds.setAttr(fk_ctrl[i] + '.drawStyle', 2)

            # fk joints

            jnt[i] = rigUtils.joint(position=ik[i], orientation=ik[i],
                                    name='{}{}{}_0_jnt'.format(preName, self.controlers[o + 2], sub), parent=None,
                                    node=node, typeJnt='', side=ctrlInfo[1], radius=ctrlInfo[7] * 0.5)
            sknJnt[i] = rigUtils.joint(position=ik[i], orientation=ik[i],
                                       name='{}{}{}_0_sknJnt'.format(preName, self.controlers[o + 2], sub),
                                       parent=jnt[i], node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                       radius=ctrlInfo[7] * 0.5)

            # 			jnt[i] = cmds.duplicate(ik[i])[0]
            if i:
                jnt[i] = cmds.parent(jnt[i], fk_ctrl[i])[0]
            else:
                jnt[i] = cmds.parent(jnt[i], ik[0])[0]
            # 			jnt[i] = cmds.rename(jnt[i], node+'_jnt'+str(i+1))
            for a in ['t', 'r', 'jo']:
                cmds.setAttr(jnt[i] + '.' + a, 0, 0, 0)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(jnt[i] + '.radius', radius * 0.5)

        # the first ik joint becomes fk control
        ctrlInfo = self.getInfoControl(self.controlers[2])
        clavicleFkGrp, clavicleFk = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                     position=ik[0], rotation=ik[0], node=node, \
                                                     lockAttr=[], hideAttr=[], controlType='joint')

        jnt[0] = cmds.parent(jnt[0], clavicleFk)[0]

        r = cmds.getAttr(ik[0] + '.jo')[0]
        cmds.setAttr(clavicleFk + '.jo', r[0], r[1], r[2])
        cmds.setAttr(clavicleFk + '.r', 0, 0, 0)

        if cmds.listRelatives(clavicleFk, pa=True, s=True):
            cmds.connectAttr(ik_ctrl[1] + '.fkControls', cmds.listRelatives(clavicleFk, pa=True, s=True)[0] + '.v')

        cmds.setAttr(clavicleFk + '.drawStyle', 2)

        fk1_ctrl_grp = cmds.createNode('joint', n=node + '_fk1_ctrl_grp', p=self.rigGrp)
        cmds.delete(cmds.parentConstraint(clavicleFk, fk1_ctrl_grp))
        # 		r = cmds.getAttr(ik[0]+'.jo')[0]
        cmds.setAttr(fk1_ctrl_grp + '.jo', r[0], r[1], r[2])
        cmds.connectAttr(fk_ctrl[0] + '.r', fk1_ctrl_grp + '.r')
        cmds.setAttr(fk1_ctrl_grp + '.drawStyle', 2)
        cmds.setAttr(clavicleFk + '.jo', 0, 0, 0)

        c = cmds.orientConstraint(fk_ctrl[0], ik2[0], mo=True)[0]
        cmds.rename(c, node + '_ik' + str(i + 1) + '_str_oricon')

        fk2_ctrl_grp = cmds.createNode('joint', n=node + '_fk2_ctrl_grp')
        cmds.setAttr(fk2_ctrl_grp + '.drawStyle', 2)

        #
        # ik handles
        #

        for i in range(2, count): ik[i] = cmds.parent(ik[i], ik[i - 1])[0]
        cmds.select(ik[1:]);
        cmds.SetPreferredAngle()

        ikh = rigUtils.ikHandle(node, ik[1], ik[-1], parent=ik_ctrl[1])[0]
        pvc = cmds.poleVectorConstraint(ik_ctrl[2], ikh)[0]
        cmds.rename(pvc, node + '_pvcon')

        #
        # stretch math
        #

        n = cmds.createNode('transform', n='str_grp', p=fk_ctrl[0])
        cmds.delete(cmds.pointConstraint(ik[1], n))
        db1 = cmds.createNode('distanceBetween')
        cmds.connectAttr(n + '.worldMatrix', db1 + '.inMatrix1')
        cmds.connectAttr(ik_ctrl[1] + '.worldMatrix', db1 + '.inMatrix2')
        db2 = cmds.createNode('distanceBetween')
        cmds.connectAttr(n + '.worldMatrix', db2 + '.inMatrix1')
        cmds.connectAttr(ik_ctrl_grp[1] + '.worldMatrix', db2 + '.inMatrix2')
        md1 = cmds.createNode('multiplyDivide')
        cmds.setAttr(md1 + '.operation', 2)
        cmds.connectAttr(db1 + '.distance', md1 + '.input1X')
        cmds.connectAttr(db2 + '.distance', md1 + '.input2X')
        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(md1 + '.outputX', md2 + '.input1X')
        cmds.connectAttr(ik_ctrl[1] + '.stretch', md2 + '.input2X')
        c = cmds.createNode('condition')
        cmds.setAttr(c + '.secondTerm', 1)
        cmds.setAttr(c + '.operation', 3)
        cmds.connectAttr(md1 + '.outputX', c + '.colorIfTrueR')
        cmds.connectAttr(md2 + '.outputX', c + '.firstTerm')

        cmds.connectAttr(c + '.outColorR', ik[1] + '.sx')
        cmds.connectAttr(c + '.outColorR', ik[2] + '.sx')
        if isDoubleElbow:
            cmds.connectAttr(c + '.outColorR', ik[3] + '.sx')

        cmds.parentConstraint(ik_ctrl[1], ik_ctrl_grp[2], mo=True)

        #
        # lock and hide attributes
        #

        for i in range(count):
            for a in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius']:
                cmds.setAttr(fk_ctrl[i] + '.' + a, l=True, k=False, cb=False)
        cmds.setAttr(fk_ctrl[2] + '.rx', l=True, k=False, cb=False)
        cmds.setAttr(fk_ctrl[2] + '.rz', l=True, k=False, cb=False)
        if isDoubleElbow:
            cmds.setAttr(fk_ctrl[3] + '.rx', l=True, k=False, cb=False)
            cmds.setAttr(fk_ctrl[3] + '.rz', l=True, k=False, cb=False)

        for a in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v', 'radius']:
            cmds.setAttr(clavicleFk + '.' + a, l=True, k=False, cb=False)

        # selection sets
        ik_ctrl[0] = fk_ctrl.pop(0)
        toDelete = ik.pop(0)
        fk_ctrl.insert(0, clavicleFk)
        # 		common.sets(node, jnt, fk_ctrl, ik_ctrl)

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        # fk to ik bake ready
        for i in range(count):
            cmds.addAttr(ik_ctrl[1], ln='fk' + str(i + 1), at='message', h=True)
            cmds.addAttr(fk_ctrl[i], ln='fk', at='message', h=True)
            cmds.connectAttr(ik_ctrl[1] + '.fk' + str(i + 1), fk_ctrl[i] + '.fk')
        cmds.addAttr(ik_ctrl[1], ln='ik1', at='message', h=True)
        cmds.addAttr(ik_ctrl[0], ln='ik', at='message', h=True)
        cmds.connectAttr(ik_ctrl[1] + '.ik1', ik_ctrl[0] + '.ik')
        cmds.addAttr(ik_ctrl[1], ln='ik2', at='message', h=True)
        cmds.addAttr(ik_ctrl[2], ln='ik', at='message', h=True)
        cmds.connectAttr(ik_ctrl[1] + '.ik2', ik_ctrl[2] + '.ik')

        # organize
        cmds.parent(fk_ctrlGrp[1], fk2_ctrl_grp)
        fk2_ctrl_grp = cmds.parent(fk2_ctrl_grp, fk_ctrl[0])[0]
        cmds.setAttr(fk2_ctrl_grp + '.t', 0, 0, 0)
        cmds.parent(clavicleFkGrp, fk1_ctrl_grp)

        ##twist joint
        if numTwist:
            side = ''
            if ctrlInfo[1] != 'None':
                side = ctrlInfo[1] + '_'
            aim = (-1, 0, 0)
            if positions[1][0] >= -0.001:
                aim = (1, 0, 0)

            upTwistGrp = cmds.createNode('transform', n="{}{}UpTwist_grp".format(side, node))
            upTwistGrp = cmds.parent(upTwistGrp, clavicleFk)[0]
            cmds.delete(cmds.parentConstraint(fk_ctrl[1], upTwistGrp, mo=False))
            twistJntsUp, firstTwistJnt = rigUtils.twist(name="{}{}UpTwist".format(side, node), control=ik_ctrl[1],
                                                        parent=upTwistGrp, \
                                                        count=numTwist, stable=fk_ctrl[1], _twist=fk_ctrl[2], aim=aim, \
                                                        scale=ik[1])
            cmds.orientConstraint(firstTwistJnt, jnt[1], mo=True)
            twistJntsLo = rigUtils.twist(name="{}{}LoTwist".format(side, node), control=ik_ctrl[1], parent=fk_ctrl[-2], \
                                         count=numTwist, stable=fk_ctrl[-2], _twist=fk_ctrl[-1], aim=aim, skip=aim, \
                                         scale=ik[1])[0]
            for twistJnt in twistJntsUp + twistJntsLo:
                sknTwistJntName = twistJnt.replace('_jnt', '_sknJnt')
                if side:
                    sknTwistJntName = sknTwistJntName.replace(side, '')
                sknTwistJnt = rigUtils.joint(position=twistJnt, orientation=twistJnt, name=preName + sknTwistJntName,
                                             parent=twistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                             radius=0.35)
                cmds.connectAttr(assemblyAsset + '.joints', sknTwistJnt + '.v')
                sknJnt.append(sknTwistJnt)

        # set lastNode
        self.setLastNode(jnt[-1])
        cmds.hide(ik[0], ik2[0])
        cmds.parent(ik[0], ik_ctrl[0])
        cmds.parent(ik2[0], self.rigGrp)
        cmds.delete(toDelete)
        cmds.select(self.rigGrp)
        cmds.refresh()

        return sknJnt
