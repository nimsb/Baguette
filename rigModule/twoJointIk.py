from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/twoBonesIkWidgetOptions.ui'


class TwoJointIkWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(TwoJointIkWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Scapula', 'ScapulaUp']
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
        self.setControlerShape(self.controlers[0], 'arrow4way', 13, axe='x', radius=1)
        self.setControlerShape(self.controlers[1], 'arrow1way', 13, axe='y', radius=1)

        self.addJoint(self.controlers[0])
        self.addSknJnt(self.controlers[0])

        # add twist option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
        cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

    def updateNumTwist(self, value):
        cmds.setAttr(self.templateGrp + '.numTwist', value)
        self.setState(1)

    def options(self):
        super(TwoJointIkWidget, self).options()
        # add here any Qt options to the self.options_Qgb you would like to see

        # this happen after the item and the node are created.
        if cmds.objExists(self.templateGrp):
            if not cmds.objExists(self.templateGrp + '.numTwist'):
                cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
                cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)
            numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
            self.qtOptions.numTwist_box.setValue(numTwist)

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

        self.qtOptions.numTwist_box.valueChanged.connect(partial(self.updateNumTwist))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

        # fix old nodes
        if len(self.joints[self.controlers[0]]) != 2:
            self.addJoint(self.controlers[0])
            self.addSknJnt(self.controlers[0])

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * 3

        for i in range(2):
            self.templateControlers[i] = cmds.createNode('joint', n='{}_{}_template'.format(node, self.controlers[i]),
                                                         p=self.templateGrp)
            cmds.setAttr(self.templateControlers[i] + '.radius', 1)

        self.templateControlers[2] = cmds.spaceLocator(n='{}_poleVector_template'.format(node))[0]
        # cmds.parent(self.templateControlers[2], self.templateControlers[0])
        cmds.parent(self.templateControlers[1], self.templateControlers[2], self.templateControlers[0])
        cmds.setAttr(self.templateControlers[1] + '.tx', 7.5)
        cmds.setAttr(self.templateControlers[2] + '.ty', 3)

        cmds.select(self.templateGrp)

    def defaultWidget(self):
        pass

    def rig(self):
        '''
        well ...
        '''
        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        # positions from template transforms/joints

        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')

        preName = ''
        if prependName:
            preName = prependNameTxt

        positions = [None] * 3
        controlGrp = [None] * 2
        control = [None] * 2
        jnt = [None] * 3
        sknJnt = [None] * 3
        side = self.getInfoControl(self.controlers[0])[1]

        for i in range(3):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        for i in range(2):
            jnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                    name=preName + self.joints[self.controlers[i]][0], parent=self.rigGrp, node=node,
                                    side=side)
            sknJnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                       name=preName + self.sknJnts[self.controlers[i]][0], parent=jnt[i], node=node,
                                       side=side)
            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(sknJnt[i] + '.radius', 0.35)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

            ctrlInfo = self.getInfoControl(self.controlers[i])
            controlGrp[i], control[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=self.rigGrp, position=self.templateControlers[i],
                                                         rotation=self.templateControlers[i], node=node, \
                                                         lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'])

            rigUtils.setConnectedJointControlRelation(control[i], jnt[i])
            rigUtils.setConnectedJointControlRelation(control[i], sknJnt[i])

        self.mayaControlers = control

        scapJnt = rigUtils.joint(position=self.templateControlers[0], name=preName + self.joints[self.controlers[0]][1],
                                 parent=control[0], node=node, side=side, connectedCtrl=control[0])
        sknJnt[2] = rigUtils.joint(position=self.templateControlers[0],
                                   name=preName + self.sknJnts[self.controlers[0]][1], parent=scapJnt, node=node,
                                   side=side, connectedCtrl=control[0])
        cmds.setAttr(scapJnt + '.drawStyle', 2)
        cmds.setAttr(sknJnt[2] + '.radius', 0.43)
        cmds.connectAttr(assemblyAsset + '.joints', sknJnt[2] + '.v')
        worldUp = 1
        if positions[0][0] >= -0.001:
            cmds.delete(cmds.aimConstraint(jnt[0], jnt[1], aim=(1, 0, 0), u=(0, 1, 0), wut='none'))
            cmds.delete(cmds.aimConstraint(jnt[1], jnt[0], aim=(-1, 0, 0), u=(0, 1, 0), wut='none'))
            cmds.delete(cmds.aimConstraint(jnt[1], scapJnt, aim=(-1, 0, 0), u=(0, 1, 0), wut='none'))
        else:
            cmds.delete(cmds.aimConstraint(jnt[0], jnt[1], aim=(-1, 0, 0), u=(0, 1, 0), wut='none'))
            cmds.delete(cmds.aimConstraint(jnt[1], jnt[0], aim=(1, 0, 0), u=(0, 1, 0), wut='none'))
            cmds.delete(cmds.aimConstraint(jnt[1], scapJnt, aim=(1, 0, 0), u=(0, 1, 0), wut='none'))
            worldUp = -1

        rigUtils.setJointParent(jnt[0], jnt[1])
        cmds.parent(jnt[1], jnt[0])
        ikh = rigUtils.ikHandle(node, jnt[0], jnt[1], parent=self.rigGrp)[0]

        cmds.parentConstraint(control[1], ikh)
        cmds.parentConstraint(control[0], jnt[0], mo=True)

        # if we need a pole vector
        jnt[2] = rigUtils.joint(position=self.templateControlers[2], orientation=self.templateControlers[2],
                                name='{}_ScapulaUp_jnt'.format(node), parent=scapJnt, node=node, side=side)
        cmds.poleVectorConstraint(jnt[2], ikh)
        cmds.pointConstraint(control[1], jnt[2], mo=True)
        cmds.hide(jnt[2])

        # if we need to make it stretchy
        objA = jnt[0]
        objB = control[1]

        disNode = cmds.createNode('distanceBetween', n=preName + '{}_distNode'.format(node))

        cmds.connectAttr(objA + '.parentMatrix', disNode + ".inMatrix1")
        cmds.connectAttr(objB + '.parentMatrix', disNode + ".inMatrix2")
        for axis in ['X', 'Y', 'Z']:
            cmds.connectAttr(objA + '.translate' + axis, disNode + '.point1' + axis)
            cmds.connectAttr(objB + '.translate' + axis, disNode + '.point2' + axis)

        valueOrig = cmds.getAttr(disNode + '.distance')
        mdNode = cmds.createNode('multiplyDivide', n=preName + '{}_mdn'.format(node))

        cmds.connectAttr(disNode + '.distance', mdNode + '.input1X')
        # cmds.setAttr(mdNode+'.input2X', valueOrig)
        cmds.setAttr(mdNode + '.operation', 2)

        blendTwoAttrNode = cmds.createNode('blendTwoAttr', n=preName + '{}_blendTwoAttr'.format(node))
        cmds.connectAttr(blendTwoAttrNode + '.current', blendTwoAttrNode + '.input[0]')
        cmds.setAttr(blendTwoAttrNode + '.current', 1)
        cmds.connectAttr(mdNode + '.outputX', blendTwoAttrNode + '.input[1]')

        cmds.connectAttr(blendTwoAttrNode + '.output', '{}.scaleX'.format(objA))

        cmds.addAttr(control[1], ln='stretch', at='double', min=0, max=1)
        cmds.setAttr(control[1] + '.stretch', e=True, k=True)

        cmds.connectAttr(control[1] + '.stretch', blendTwoAttrNode + '.attributesBlender')

        # scale
        mdnNodeModule = cmds.createNode('multiplyDivide', n=preName + '{}_Module_mdn'.format(node))
        cmds.setAttr(mdnNodeModule + '.operation', 1)
        cmds.setAttr(mdnNodeModule + '.input2X', valueOrig)
        cmds.connectAttr(self.rigGrp + '.scale', mdnNodeModule + '.input1')
        cmds.connectAttr(mdnNodeModule + '.output', mdNode + '.input2')

        # twist joint
        if numTwist:
            side = ''
            if ctrlInfo[1] != 'None':
                side = ctrlInfo[1] + '_'

            worldUpFirstTwist = rigUtils.duplicate(scapJnt, name=preName + "{}{}Twist_worldUp".format(side, node),
                                                   parent=scapJnt, noChildren=True)
            cmds.setAttr(worldUpFirstTwist + '.ty', 1)

            twistJntsUp, firstTwistJnt = rigUtils.twist(name=preName + "{}{}UpTwist".format(side, node),
                                                        control=control[0], parent=jnt[0], \
                                                        count=numTwist, stable=scapJnt, _twist=jnt[1],
                                                        wu=(0, worldUp, 0), wuo=worldUpFirstTwist, \
                                                        scale=jnt[0])

            for twistJnt in twistJntsUp:
                sknTwistJntName = twistJnt.replace('_jnt', '_sknJnt')
                if side:
                    sknTwistJntName = sknTwistJntName.replace(side, '')
                sknTwistJnt = rigUtils.joint(position=twistJnt, orientation=twistJnt, name=preName + sknTwistJntName,
                                             parent=twistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                             radius=0.35)
                cmds.connectAttr(assemblyAsset + '.joints', sknTwistJnt + '.v')
                sknJnt.append(sknTwistJnt)

            cmds.orientConstraint(control[1], jnt[1], mo=True)

        else:
            if positions[0][0] >= -0.001:
                cmds.aimConstraint(control[0], control[1], aim=(1, 0, 0), u=(0, 1, 0), wut='none')
            else:
                cmds.aimConstraint(control[0], control[1], aim=(-1, 0, 0), u=(0, 1, 0), wut='none')
            for a in ['rx', 'ry', 'rz']: cmds.setAttr(control[1] + '.' + a, k=False, cb=False)
            for a in ['r']: cmds.setAttr(control[1] + '.' + a, l=True)

        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        cmds.select(control)
        cmds.refresh()

        return sknJnt
