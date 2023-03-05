from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import map
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/spineWidgetOptions.ui'

'''
10/22/2018
This module is deprecated and shouldn't be used. It won't be maintained.
Please use a chain and a ribbon instead
'''


class SpineWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(SpineWidget, self).__init__(parent)

        # self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['BaseSpine', 'Torso', 'Chest', 'Neck1', 'Neck2']
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

        self.addJoint(self.controlers[3])
        self.addSknJnt(self.controlers[3])

        # set here default value for the controlers and shape.
        self.setControlerShape(self.controlers[0], 'circle', 18, axe='x', radius=3)
        self.setControlerShape(self.controlers[1], 'circle', 18, axe='x', radius=3)
        self.setControlerShape(self.controlers[2], 'circle', 18, axe='x', radius=3)
        self.setControlerShape(self.controlers[3], 'circle', 14, axe='x')
        self.setControlerShape(self.controlers[4], 'circle', 14, axe='x')

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

    def options(self):
        super(SpineWidget, self).options()
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
        self.templateControlers = [None] * 6
        pos = [(0, 1, 0), (0, 3, 0), (0, 5, 0), (0, 9, 0), (0, 10, 0), (0, 11, 0)]
        for i in range(6):
            name = '{}_{}_template'.format(node, str(i + 1))
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode("joint", n=name, p=self.templateGrp)

                cmds.setAttr(self.templateControlers[i] + ".t", pos[i][0], pos[i][1], pos[i][2])
                if i:
                    self.templateControlers[i] = \
                    cmds.parent(self.templateControlers[i], self.templateControlers[i - 1])[0]

    # cmds.setAttr(ik[i]+".radius", radius)

    # cmds.select(ik[0])

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ... '''
        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        node = self.getNode()
        radius = 1
        # positions from template transforms/joints
        positions = [None] * 6
        for i in range(6):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        #
        # joints, part 1
        #

        ik = [None] * 9
        cmds.select(cl=True)
        ik[0] = cmds.joint(p=positions[0], n=node + '_ik1_off')
        ik[2] = cmds.joint(p=positions[1], n=node + '_ik2')
        cmds.joint(ik[0], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        # insert an 'offset' joint for proper ik spline twist
        ik[3] = cmds.joint(p=[i * 0.5 for i in map(add, positions[1], positions[2])], n=node + '_ik3_off')
        cmds.joint(ik[2], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        ik[4] = cmds.joint(p=positions[2], n=node + '_ik3')
        cmds.joint(ik[3], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        ik[5] = cmds.joint(p=positions[3], n=node + '_ik4')
        cmds.joint(ik[4], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        ik[6] = cmds.joint(p=positions[4], n=node + '_ik5')
        cmds.joint(ik[5], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        cmds.setAttr(ik[6] + '.jo', 0, 0, 0)
        # insert an 'offset' joint for proper ik spline twist
        ik[7] = cmds.joint(p=[i * 0.5 for i in map(add, positions[4], positions[5])], n=node + '_ik6_off')
        cmds.joint(ik[6], e=True, oj='xyz', sao='xup', ch=False, zso=True)
        ik[8] = cmds.joint(p=positions[5], n=node + '_ik6')
        cmds.joint(ik[7], e=True, oj='xyz', sao='xup', ch=False, zso=True)

        ik[1] = cmds.duplicate(ik[0])[0]
        ik[1] = cmds.rename(ik[1], node + '_ik1')
        cmds.delete(cmds.listRelatives(ik[1], pa=True, ad=True))
        ik[1] = cmds.parent(ik[1], ik[0])[0]

        for n in ik: cmds.setAttr(n + '.radius', radius * 0.5)
        for n in [ik[0], ik[3], ik[7]]: cmds.setAttr(n + '.drawStyle', 2)

        #
        # controls
        #

        ctrl_grp = [None] * 5
        ctrl = [None] * 5

        ctrlInfo = self.getInfoControl(self.controlers[0])
        ctrl_grp[0], ctrl[0] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                position=ik[0], rotation=ik[0], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])
        # 		cmds.addAttr(ctrl[0], ln='joints', at='bool', dv=True, k=True)
        # 		cmds.addAttr(ctrl[0], ln='editJoints', at='bool', k=True)

        ctrlInfo = self.getInfoControl(self.controlers[1])
        ctrl_grp[1], ctrl[1] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[0],
                                                position=ik[2], rotation=ik[2], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])

        ctrlInfo = self.getInfoControl(self.controlers[2])
        ctrl_grp[2], ctrl[2] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[1],
                                                position=ik[4], rotation=ik[4], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])
        cmds.addAttr(ctrl[2], ln='stretchAbove', at='bool', k=True)
        cmds.addAttr(ctrl[2], ln='stretchBelow', at='bool', k=True)

        ctrlInfo = self.getInfoControl(self.controlers[3])
        ctrl_grp[3], ctrl[3] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[2],
                                                position=ik[6], rotation=ik[6], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])
        anchor = cmds.createNode('transform', n=node + '_ik4_anchor', p=ik[4])
        cmds.delete(cmds.parentConstraint(ik[5], anchor))
        c = cmds.parentConstraint(anchor, ctrl_grp[3], mo=True)[0]
        cmds.rename(c, ctrl_grp[3] + '_parcon')

        ctrlInfo = self.getInfoControl(self.controlers[4])
        ctrl_grp[4], ctrl[4] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ctrl[3],
                                                position=ik[8], rotation=ik[8], node=node, \
                                                lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])
        cmds.addAttr(ctrl[4], ln='stretch', at='bool', k=True)

        md = cmds.createNode('multiplyDivide')
        cmds.setAttr(md + '.operation', 2)
        cmds.setAttr(md + '.input1X', 1)
        cmds.connectAttr(ik[4] + '.sx', md + '.input2X')
        cmds.connectAttr(md + '.outputX', anchor + '.sx')

        #
        # joints, part 2
        #

        c = cmds.orientConstraint(ctrl[2], ik[4], mo=True)[0]
        cmds.rename(c, ik[4] + '_oricon')

        #
        # ik handles
        #

        cmds.select(ik[0], ik[4])
        ikh, eff, crv = cmds.ikHandle(sol='ikSplineSolver')
        crv = cmds.parent(crv, self.rigGrp)[0]
        cmds.setAttr(crv + '.it', False)
        cmds.setAttr(ikh + '.dTwistControlEnable', True)
        cmds.setAttr(ikh + '.dWorldUpType', 4)
        cmds.setAttr(ikh + '.dWorldUpAxis', 3)
        cmds.setAttr(ikh + '.dWorldUpVector', 0, 0, -1)
        cmds.setAttr(ikh + '.dWorldUpVectorEnd', 0, 0, -1)
        ikh = cmds.parent(ikh, self.rigGrp)[0]
        cmds.hide(ikh, crv)
        ikh = cmds.rename(ikh, node + '_ikh#')
        cmds.rename(eff, node + '_eff#')

        # adjust 'offset' joint position for proper ik spline twist
        cmds.move(positions[2][0], positions[2][1], positions[2][2], ik[3] + '.scalePivot', ik[3] + '.rotatePivot')
        cmds.move(0, -0.001, 0, ik[3] + '.scalePivot', ik[3] + '.rotatePivot', r=True)

        c1 = cmds.cluster(crv + '.cv[0]')[1]
        c2 = cmds.cluster(crv + '.cv[1]', crv + '.cv[2]')[1]
        c3 = cmds.cluster(crv + '.cv[3]')[1]
        cmds.hide(c1, c2, c3)
        cmds.parent(c1, ctrl[0])
        cmds.parent(c2, ctrl[1])
        cmds.parent(c3, ctrl[2])

        cmds.connectAttr(ctrl[0] + '.worldMatrix', ikh + '.dWorldUpMatrix')
        cmds.connectAttr(ctrl[2] + '.worldMatrix', ikh + '.dWorldUpMatrixEnd')

        cmds.select(ik[5], ik[8])
        ikh, eff, crv2 = cmds.ikHandle(sol='ikSplineSolver')
        crv2 = cmds.parent(crv2, self.rigGrp)[0]
        cmds.setAttr(crv2 + '.t', 0, 0, 0)
        cmds.setAttr(crv2 + '.r', 0, 0, 0)
        cmds.setAttr(crv2 + '.s', 1, 1, 1)
        cmds.setAttr(crv2 + '.it', False)
        cmds.setAttr(ikh + '.dTwistControlEnable', True)
        cmds.setAttr(ikh + '.dWorldUpType', 4)
        cmds.setAttr(ikh + '.dWorldUpAxis', 3)
        cmds.setAttr(ikh + '.dWorldUpVector', 0, 0, -1)
        cmds.setAttr(ikh + '.dWorldUpVectorEnd', 0, 0, -1)
        ikh = cmds.parent(ikh, self.rigGrp)[0]
        cmds.hide(ikh, crv2)
        ikh = cmds.rename(ikh, node + '_ikh#')
        cmds.rename(eff, node + '_eff#')

        # adjust 'offset' joint position for proper ik spline twist
        cmds.move(positions[5][0], positions[5][1], positions[5][2], ik[7] + '.scalePivot', ik[7] + '.rotatePivot')
        cmds.move(0, -0.001, 0, ik[7] + '.scalePivot', ik[7] + '.rotatePivot', r=True)

        c1 = cmds.cluster(crv2 + '.cv[0]')[1]
        c2 = cmds.cluster(crv2 + '.cv[1]', crv2 + '.cv[2]')[1]
        c3 = cmds.cluster(crv2 + '.cv[3]')[1]
        cmds.hide(c1, c2, c3)
        cmds.parent(c1, ik[4])
        cmds.parent(c2, ctrl[3])
        cmds.parent(c3, ctrl[4])

        cmds.connectAttr(ctrl[2] + '.worldMatrix', ikh + '.dWorldUpMatrix')
        cmds.connectAttr(ctrl[4] + '.worldMatrix', ikh + '.dWorldUpMatrixEnd')

        cmds.delete(cmds.ls(typ='tweak'))

        c = cmds.orientConstraint(ctrl[0], ik[1], mo=True)[0]
        cmds.rename(c, ik[1] + '_oricon')
        c = cmds.orientConstraint(ctrl[4], ik[8], mo=True)[0]
        cmds.rename(c, ik[8] + '_oricon')

        #
        # stretch math
        #

        ci = cmds.createNode('curveInfo')
        cmds.connectAttr(crv + '.worldSpace', ci + '.inputCurve')

        ci2 = cmds.createNode('curveInfo')
        cmds.connectAttr(crv2 + '.worldSpace', ci2 + '.inputCurve')

        n = cmds.listRelatives(crv, pa=True, s=True)[1]
        tg = cmds.createNode('transformGeometry')
        cmds.connectAttr(n + '.worldSpace', tg + '.inputGeometry')
        cmds.connectAttr(self.rigGrp + '.worldMatrix', tg + '.transform')
        ci3 = cmds.createNode('curveInfo')
        cmds.connectAttr(tg + '.outputGeometry', ci3 + '.inputCurve')

        n = cmds.listRelatives(crv2, pa=True, s=True)[1]
        tg = cmds.createNode('transformGeometry')
        cmds.connectAttr(n + '.worldSpace', tg + '.inputGeometry')
        cmds.connectAttr(self.rigGrp + '.worldMatrix', tg + '.transform')
        ci4 = cmds.createNode('curveInfo')
        cmds.connectAttr(tg + '.outputGeometry', ci4 + '.inputCurve')

        md1 = cmds.createNode('multiplyDivide')
        cmds.setAttr(md1 + '.operation', 2)
        cmds.connectAttr(ci + '.arcLength', md1 + '.input1X')
        cmds.connectAttr(ci3 + '.arcLength', md1 + '.input2X')
        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(md1 + '.outputX', md2 + '.input1X')
        cmds.connectAttr(ctrl[2] + '.stretchBelow', md2 + '.input2X')
        c = cmds.createNode('condition')
        cmds.setAttr(c + '.secondTerm', 1)
        cmds.setAttr(c + '.operation', 3)
        cmds.connectAttr(md1 + '.outputX', c + '.colorIfTrueR')
        cmds.connectAttr(md2 + '.outputX', c + '.firstTerm')
        cmds.connectAttr(c + '.outColorR', ik[0] + '.sx')
        cmds.connectAttr(c + '.outColorR', ik[2] + '.sx')

        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(md1 + '.outputX', md2 + '.input1X')
        cmds.connectAttr(ctrl[2] + '.stretchAbove', md2 + '.input2X')
        c = cmds.createNode('condition')
        cmds.setAttr(c + '.secondTerm', 1)
        cmds.setAttr(c + '.operation', 3)
        cmds.connectAttr(md1 + '.outputX', c + '.colorIfTrueR')
        cmds.connectAttr(md2 + '.outputX', c + '.firstTerm')
        cmds.connectAttr(c + '.outColorR', ik[4] + '.sx')

        md1 = cmds.createNode('multiplyDivide')
        cmds.setAttr(md1 + '.operation', 2)
        cmds.connectAttr(ci2 + '.arcLength', md1 + '.input1X')
        cmds.connectAttr(ci4 + '.arcLength', md1 + '.input2X')
        md2 = cmds.createNode('multiplyDivide')
        cmds.connectAttr(md1 + '.outputX', md2 + '.input1X')
        cmds.connectAttr(ctrl[4] + '.stretch', md2 + '.input2X')
        c = cmds.createNode('condition')
        cmds.setAttr(c + '.secondTerm', 1)
        cmds.setAttr(c + '.operation', 3)
        cmds.connectAttr(md1 + '.outputX', c + '.colorIfTrueR')
        cmds.connectAttr(md2 + '.outputX', c + '.firstTerm')
        cmds.connectAttr(c + '.outColorR', ik[5] + '.sx')
        cmds.connectAttr(c + '.outColorR', ik[6] + '.sx')

        jnt = [None] * 6
        sknJnt = [None] * 6
        joints = []
        sknJnts = []
        for controler in self.controlers:
            for thisJnt in self.joints[controler]:
                joints.append(thisJnt)
            for thisJnt in self.sknJnts[controler]:
                sknJnts.append(thisJnt)

        j = 0
        for i in range(1, 9):
            if i == 3 or i == 7: continue

            jnt[j] = rigUtils.joint(position=ik[i], orientation=ik[i], name=preName + joints[j], parent=self.rigGrp,
                                    node=node, side=ctrlInfo[1])
            sknJnt[j] = rigUtils.joint(position=ik[i], orientation=ik[i], name=preName + sknJnts[j], parent=jnt[j],
                                       node=node, side=ctrlInfo[1])

            cmds.setAttr(sknJnt[j] + '.radius', radius * 0.35)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[j] + '.v')
            c = cmds.parentConstraint(ik[i], jnt[j])[0]
            cmds.rename(c, node + '_jnt' + str(j) + '_parcon')
            j += 1

        for joint in jnt:
            cmds.setAttr(joint + '.drawStyle', 2)
        # selection sets
        # common.sets(name, jnt, None, ctrl)

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        ik[0] = cmds.parent(ik[0], self.rigGrp)[0]
        cmds.hide(ik[0])
        cmds.select(self.rigGrp)
        cmds.refresh()

        return sknJnt
