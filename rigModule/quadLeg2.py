from __future__ import absolute_import
from maya import cmds
from . import nodeBase, simpleIk, foot
from ..utils import rigUtils, matrix, mathUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/legWidgetOptions.ui'


class QuadLeg2Widget(simpleIk.SimpleIkWidget):
    def __init__(self, parent=None):
        super(QuadLeg2Widget, self).__init__(parent)

        self.footWidget = foot.FootWidget()
        self.footWidget.controlers = self.footWidget.controlers[2:]

        self.controlers = self.controlers + self.footWidget.controlers + ['ClavicleIk', 'ClavicleQuadPv']
        self.initiateMayaNodes(self.controlers)

    # 	def addControlers(self):
    # 		super(QuadLeg2Widget, self).addControlers()

    def addData(self):
        super(QuadLeg2Widget, self).addData()

        self.setControlerShape('ClavicleIk', 'arrowWrap', 14, axe='y')
        self.setControlerShape('ClavicleQuadPv', 'cube', 7, axe='y', radius=0.2)

        self.footWidget.controlers = self.controlers
        self.footWidget.templateGrp = self.templateGrp
        self.footWidget.initialName(self.getNode())
        self.footWidget.addData()

    def updateKnee(self, state):
        super(QuadLeg2Widget, self).updateKnee(state, num=1)

    def updateNumTwist(self, value):
        super(QuadLeg2Widget, self).updateNumTwist(value)

    def options(self):
        super(QuadLeg2Widget, self).options()
        self.qtOptions.doubleJoint_ckb.setText('double Knee')

        self.qtOptions.ikTmpRot_widget.setVisible(False)

    def template(self):
        super(QuadLeg2Widget, self).template(pos=[(0, 14, -1), (0, 9, 1.5), (0, 5, -2)])

        self.footWidget.template(self.getNode() + 'Foot')
        # 		cmds.delete(self.templateControlers[2])
        cmds.parent(self.footWidget.templateControlers[0], self.templateControlers[2])

        self.templateControlers = self.templateControlers + self.footWidget.templateControlers

    def defaultWidget(self):
        super(QuadLeg2Widget, self).defaultWidget()

    def rig(self):
        # set manually the self.rigGrp here
        rigUtils.snapTranslation(self.templateControlers[0], self.rigGrp)

        # rigging the foot
        listFootControlers = [self.controlers[0]] + self.controlers[4:]
        self.footWidget.controlers = self.controlers
        self.footWidget.initiateMayaNodes(self.controlers)
        self.footWidget.templateGrp = self.templateGrp
        self.footWidget.initialName(self.getNode())
        isDoubleKnee = cmds.getAttr(self.templateGrp + '.doubleJoint')
        num = 0
        if isDoubleKnee:
            num = 1
        self.footWidget.templateControlers = self.templateControlers[3 + num:]
        footRigSknJnt = self.footWidget.rig(listControlers=[self.controlers[0]] + self.controlers[4:])

        # rigging the simple ik
        footIk = self.footWidget.mayaControlers[2]
        attributSettingShape = self.footWidget.attributeShape
        endJnts = self.footWidget.startJnts
        ballLiftCtrl = self.footWidget.ballLiftCtrl
        simpleIkRigSknJnt = super(QuadLeg2Widget, self).rig(templateControlers=self.templateControlers[1:4 + num],
                                                            mainIk=footIk, attributSettingShape=attributSettingShape, \
                                                            endJnts=endJnts, ballLiftCtrl=ballLiftCtrl, rigGrpPos=None)

        simpleIkRigSknJnt.insert(4 + num, footRigSknJnt[1])
        if isDoubleKnee:
            # we put the knee at the end to keep the order and the skinning from the knee to the kneeBis
            simpleIkRigSknJnt.append(simpleIkRigSknJnt.pop(1))

        ### adding clavicle on the simpleIk.rig() ###
        node = self.getNode()
        clavicleJnt = cmds.duplicate(self.parentBaseJnt, po=True)[0]
        cmds.delete(cmds.pointConstraint(self.templateControlers[0], clavicleJnt))

        if self.positionCenter >= -0.001:
            cmds.delete(cmds.aimConstraint(self.parentBaseJnt, clavicleJnt, aim=(1, 0, 0), u=(0, 0, 1), wut='object',
                                           wuo=self.templateControlers[2]))
        else:
            cmds.delete(cmds.aimConstraint(self.parentBaseJnt, clavicleJnt, aim=(-1, 0, 0), u=(0, 0, -1), wut='object',
                                           wuo=self.templateControlers[2]))

        firstFkCtrlGrp = cmds.listConnections(self.fkCtrl[0] + '.ctrlGrp')[0]

        ctrlInfo = self.getInfoControl(self.controlers[-2])
        clavicleCtrlGrp, clavicleCtrl = rigUtils.control(name=self.preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=self.rigGrp, position=clavicleJnt,
                                                         rotation=firstFkCtrlGrp, node=node, \
                                                         lockAttr=['t', 's'],
                                                         hideAttr=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'])
        clavicleCtrlGrpOffset = self.side + self.preName + self.grpOffsets[self.controlers[-2]][0]
        rigUtils.snapNodes(clavicleJnt, clavicleCtrl)
        self.fkCtrl.append(clavicleCtrl)

        # new based rotation for fkCtrl[0]
        tmpNode = cmds.createNode('transform', p=self.rigGrp)
        rigUtils.snapRotation(self.fkCtrl[0], tmpNode)
        rigUtils.snapRotation(clavicleCtrl, firstFkCtrlGrp)
        rigUtils.snapRotation(tmpNode, self.fkCtrl[0])

        for ctrl in self.fkCtrl:
            rigUtils.setDefaultPosition(ctrl)

        cmds.parent(self.attributeShape, clavicleCtrl, add=True, s=True)
        cmds.parent([self.parentBaseJnt, self.startBase], clavicleCtrl)

        clavicleRigJnt = rigUtils.joint(position=clavicleJnt, orientation=clavicleJnt,
                                        name='{}{}_0_jnt'.format(self.preName, self.controlers[-2]), \
                                        parent=clavicleCtrl, node=node, typeJnt='', side=ctrlInfo[1],
                                        radius=ctrlInfo[7] * 0.5, connectedCtrl=clavicleCtrl)
        clavicleSknJnt = rigUtils.joint(position=clavicleJnt, orientation=clavicleJnt,
                                        name='{}{}_0_sknJnt'.format(self.preName, self.controlers[-2]), \
                                        parent=clavicleRigJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                        radius=ctrlInfo[7] * 0.5, connectedCtrl=clavicleCtrl)
        cmds.setAttr(clavicleRigJnt + '.drawStyle', 2)
        # add to main sknJnts
        simpleIkRigSknJnt.append(clavicleSknJnt)

        # set one jnt hierarchy and ctrl tags parent
        rigUtils.setJointParent(clavicleRigJnt, self.rigJnt[0])
        rigUtils.setCtrlParent(clavicleCtrl, self.ikCtrl[0])
        rigUtils.setCtrlParent(clavicleCtrl, self.fkCtrl[0])

        # new based position for footIk
        rigUtils.snapTranslation(footIk, tmpNode)
        for ctrl in self.fkCtrl:
            rigUtils.goToZeroPosition(ctrl)
        rigUtils.snapTranslation(endJnts[1], self.mainIkGrp)
        rigUtils.snapTranslation(tmpNode, footIk)
        rigUtils.setDefaultPosition(footIk)
        for ctrl in self.fkCtrl:
            rigUtils.goToDefaultPosition(ctrl)
        cmds.delete(tmpNode)

        quadJnts = []
        for jnt in [clavicleRigJnt] + self.rigJnt:
            quadJnt = rigUtils.joint(position=jnt, orientation=jnt, name=jnt.replace('_jnt', '_quadJnt'), \
                                     parent=self.rigGrp, node=node, typeJnt='', radius=1)
            quadJnts.append(quadJnt)
            cmds.setAttr(quadJnt + '.drawStyle', 2)
        for i in range(1, len(quadJnts)):
            quadJnts[i] = cmds.parent(quadJnts[i], quadJnts[i - 1])[0]
        quadJntGrp = cmds.createNode('transform', n='{}_quad_jntGrp'.format(node), p=self.rigGrp)
        rigUtils.snapNodes(clavicleCtrlGrp, quadJntGrp)
        cmds.parent(quadJnts[0], quadJntGrp)

        actualRot = matrix.getRotation(matrix.getMatrix(quadJnts[0]))
        # create ik spring
        if cmds.pluginInfo("ikSpringSolver", q=True, l=True) is False:
            cmds.loadPlugin("ikSpringSolver")
        springSolver = '{}_springSolver'.format(node)
        if not cmds.objExists(springSolver):
            cmds.createNode('ikSpringSolver', s=True, n=springSolver)
        ikSpring = cmds.ikHandle(sj=quadJnts[0], ee=quadJnts[-1], sol='ikRPsolver', n='{}_quad_ikh'.format(node))[0]
        cmds.ikHandle(ikSpring, e=True, sol=springSolver)
        offsetVector = cmds.getAttr(ikSpring + '.poleVector')[0]

        cmds.parent(ikSpring, ballLiftCtrl)
        cmds.hide(ikSpring)
        cmds.setAttr(quadJnts[0] + '.jo', 0, 0, 0)

        # ik spring can completly be flipped joint the other side so I'm comparing before I set the ikSpring and give a tolerance of 10 degres
        newRotAfterIkSpring = matrix.getRotation(matrix.getMatrix(quadJnts[0]))
        differenceRot = ((actualRot[0] - newRotAfterIkSpring[0]) % 360, (actualRot[1] - newRotAfterIkSpring[1]) % 360,
                         (actualRot[2] - newRotAfterIkSpring[2]) % 360)
        twist = False
        # 		for value in differenceRot:
        # 			if value > 10:
        # 				twist = True
        # 		if twist:
        # 			cmds.setAttr(ikSpring+'.twist', 180)

        # new pole Vector not used by anim
        ctrlInfo = self.getInfoControl(self.controlers[-1])
        quadPoleVectorGrp, quadPoleVector = rigUtils.control(name=self.preName + self.controlers[-1], side=ctrlInfo[1],
                                                             shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                             radius=ctrlInfo[7], \
                                                             axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                             parent=self.ikCtrl[1], node=node, \
                                                             lockAttr=['r', 's'],
                                                             hideAttr=['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                                             parentCtrl=self.ikCtrl[1])
        cmds.parent(self.attributeShape, quadPoleVector, add=True, s=True)

        # position of new pole vector (should have used this method for the other PV, it has more accuracy)
        mult = 1.2
        ptAPos = matrix.getTranslation(matrix.getMatrix(quadJnts[0]))
        ptBPos = matrix.getTranslation(matrix.getMatrix(self.fkCtrl[1]))
        ptMidPos = matrix.getTranslation(matrix.getMatrix(self.fkCtrl[0]))
        ptABaverage = mathUtils.averagePosition(ptAPos, ptBPos)
        posResult = (
        (ptMidPos[0] - ptABaverage[0]) * mult + ptMidPos[0], (ptMidPos[1] - ptABaverage[1]) * mult + ptMidPos[1],
        (ptMidPos[2] - ptABaverage[2]) * mult + ptMidPos[2])
        cmds.xform(quadPoleVectorGrp, t=posResult, ws=True)
        cmds.poleVectorConstraint(quadPoleVector, ikSpring)

        # create new grpOffset the clavicle to blend rotation with the quad
        blendClavicleGrpOffset = cmds.createNode('transform', p=clavicleCtrlGrp,
                                                 n=clavicleCtrlGrpOffset.replace('_0_grpOffset', '_1_grpOffset'))
        rigUtils.snapRotation(quadJnts[0], blendClavicleGrpOffset)
        if twist:
            cmds.setAttr(blendClavicleGrpOffset + '.rotateX', cmds.getAttr(blendClavicleGrpOffset + '.rotateX') * -1)
            cmds.setAttr(blendClavicleGrpOffset + '.rotateY', cmds.getAttr(blendClavicleGrpOffset + '.rotateY') * -1)
            cmds.setAttr(blendClavicleGrpOffset + '.rotateZ', cmds.getAttr(blendClavicleGrpOffset + '.rotateZ') * -1)

        cmds.parent(clavicleCtrlGrpOffset, blendClavicleGrpOffset)

        clavicleBlendColor = cmds.createNode('blendColors', n='{}_quad_blendColor'.format(node))
        if twist:
            inverseRotation = cmds.createNode('multiplyDivide', n='{}_quad_mdn'.format(node))
            cmds.connectAttr(quadJnts[0] + '.rotate', inverseRotation + '.input1')
            cmds.setAttr(inverseRotation + '.input2', -1, -1, -1)
            cmds.connectAttr(inverseRotation + '.output', clavicleBlendColor + '.color1')
            quadRot = cmds.getAttr(inverseRotation + '.output')[0]
        else:
            cmds.connectAttr(quadJnts[0] + '.rotate', clavicleBlendColor + '.color1')
            quadRot = cmds.getAttr(quadJnts[0] + '.rotate')[0]
        cmds.setAttr(clavicleBlendColor + '.color2', quadRot[0], quadRot[1], quadRot[2])

        cmds.connectAttr(clavicleBlendColor + '.output', blendClavicleGrpOffset + '.rotate')
        revIkFk = cmds.createNode('reverse', n='{}IkFk_revNode')
        cmds.connectAttr(self.attributeShape + '.IkFk', revIkFk + '.inputX')
        cmds.connectAttr(revIkFk + '.outputX', clavicleBlendColor + '.blender')

        # adding TWIST
        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
        if numTwist:
            # put the rotationUpTwistGrp from the simple rig under the new clavicle ctrl
            cmds.parent(self.rotationUpTwistGrp, clavicleCtrl)

            # create the twist jnts
            rotationQuadUpTwistGrp = cmds.createNode('transform',
                                                     n="{}{}{}rotationQuadUpTwist_grp".format(self.side, self.preName,
                                                                                              self.controlers[-2]),
                                                     parent=self.rigGrp)
            rigUtils.snapNodes(clavicleJnt, rotationQuadUpTwistGrp)
            aim = (1, 0, 0)
            if self.positionCenter >= -0.001:
                aim = (-1, 0, 0)

            twistQuadJntsUp, firstTwistQuadJnt = rigUtils.twist(
                name="{}{}{}Twist".format(self.side, self.preName, self.controlers[-2]),
                control=self.rotationUpTwistGrp, parent=clavicleRigJnt, \
                count=numTwist, stable=clavicleRigJnt, _twist=self.rotationUpTwistGrp, aim=aim, wu=(0, 0, 1),
                wuo=rotationQuadUpTwistGrp, \
                scale=clavicleRigJnt)

            for twistJnt in twistQuadJntsUp:
                rigUtils.setJointParent(clavicleRigJnt, twistJnt)
                rigUtils.setConnectedJointControlRelation(clavicleCtrl, twistJnt)

                sknTwistJntName = twistJnt.replace('_jnt', '_sknJnt')
                connectedCtrl = clavicleCtrl
                if self.side:
                    sknTwistJntName = sknTwistJntName.replace(self.side, '')
                sknTwistJnt = rigUtils.joint(position=twistJnt, orientation=twistJnt, name=sknTwistJntName,
                                             parent=twistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                             radius=0.35, connectedCtrl=connectedCtrl)
                cmds.connectAttr(self.assemblyAsset + '.joints', sknTwistJnt + '.v')
                simpleIkRigSknJnt.append(sknTwistJnt)

            # adding first up joint to sknJnts
            rigUtils.setJointParent(clavicleRigJnt, firstTwistQuadJnt)
            firstTwistQuadSknJnt = rigUtils.joint(position=firstTwistQuadJnt, orientation=firstTwistQuadJnt,
                                                  name="{}{}Twist0_sknJnt".format(self.preName, self.controlers[-2]), \
                                                  parent=firstTwistQuadJnt, node=node, typeJnt='sknJnt',
                                                  side=ctrlInfo[1], radius=0.35, connectedCtrl=clavicleCtrl)
            simpleIkRigSknJnt.append(firstTwistQuadSknJnt)

        # ready for ikFk switch
        cmds.addAttr(self.attributeShape, ln='clavicleIkCtrl', at='message')
        cmds.addAttr(clavicleCtrl, ln='clavicleIkCtrl', at='message')
        cmds.connectAttr(clavicleCtrl + '.clavicleIkCtrl', self.attributeShape + '.clavicleIkCtrl')
        cmds.addAttr(self.attributeShape, ln='quadPv', at='message')
        cmds.addAttr(quadPoleVector, ln='quadPv', at='message')
        cmds.connectAttr(quadPoleVector + '.quadPv', self.attributeShape + '.quadPv')

        # clean
        cmds.delete(clavicleJnt)

        # add to all mayaControlers to set the tag ctrl
        self.mayaControlers = self.mayaControlers + [clavicleCtrl, quadPoleVector]

        return simpleIkRigSknJnt
