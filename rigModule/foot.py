from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/legWidgetOptions.ui'


class FootWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        self.footSuper = super(FootWidget, self)
        self.footSuper.__init__(parent)
        # 		super(SimpleIkWidget, self).simpleIkSuper.__init__(parent)

        # self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['FootIk', 'Foot', 'Toe', 'Heel', 'ToeSideRt', 'ToeSideLt', 'ToeTip', 'BallLift', 'Ball']
        self.initiateMayaNodes(self.controlers)

        '''
        self.controlName
        self.grpOffsetsl
        self.joints
        self.sknJnts
        '''

    def addData(self):
        '''
        It's where you define controle shapes, grpOffset and skinning joint.
        You need to add them to the node info to be able to use them before it's actually rigged.
        It's only called when the node is created the first time.
        '''

        # set here default value for the controlers and shape.
        self.setControlerShape('FootIk', 'cube', 7, axe='x')
        self.setControlerShape('Foot', 'circle', 14, axe='x')
        self.setControlerShape('Toe', 'circle', 14, axe='x')
        self.setControlerShape('Heel', 'arrowFlatWrap3Quarter', 19, axe='x', radius=0.2)
        self.setControlerShape('ToeSideRt', 'arrowFlatWrapHalf', 19, axe='z', radius=0.07)
        self.setControlerShape('ToeSideLt', 'arrowFlatWrapHalf', 19, axe='z', radius=0.07)
        self.setControlerShape('ToeTip', 'sphere', 19, axe='x', radius=0.2)
        self.setControlerShape('BallLift', 'arrow1way', 19, axe='y', radius=0.5)
        self.setControlerShape('Ball', 'arrow1way', 19, axe='y', radius=0.5)

        # add knee option to the templateGrp
        if not cmds.objExists(self.templateGrp + '.prependName'):
            cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
            cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
            cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
            cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

    def options(self):
        super(FootWidget, self).options()
        # this happen after the item and the node are created.
        if cmds.objExists(self.templateGrp):
            prependName = cmds.getAttr(self.templateGrp + '.prependName')
            self.prependName_chbx.setChecked(prependName)
            prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
            self.prependName_lineEdit.setText(prependNameTxt)

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))

    def template(self, node=None):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        if not node:
            node = self.getNode()
        self.templateControlers = [None] * 6
        pos = [(0, 0.5, 0), (0, 0, 1.5), (0, 0, 2.5), (0, 0, -0.5), (-0.5, 0, 1.5), (0.5, 0, 1.5)]
        for i in range(6):
            name = '{}_{}_template'.format(node, str(i + 1))
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode('joint', n=name, p=self.templateGrp)

                cmds.setAttr(self.templateControlers[i] + '.t', pos[i][0], pos[i][1], pos[i][2])
                if i == 3:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateControlers[0])[0]
                elif i == 5 or i == 4:
                    self.templateControlers[i] = cmds.parent(self.templateControlers[i], self.templateControlers[1])[0]
                elif i:
                    self.templateControlers[i] = \
                    cmds.parent(self.templateControlers[i], self.templateControlers[i - 1])[0]
            cmds.setAttr(self.templateControlers[i] + '.radius', 0.5)

    # cmds.select(oriJnt[0])

    def defaultWidget(self):
        pass

    def rig(self, listControlers=None):
        '''
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        radius = 1
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt
        self.mayaControlers = []
        side = cmds.getAttr(node + '.side')
        if side and side != 'None':
            side = side + '_'
        else:
            side = ''
        if not listControlers:
            listControlers = self.controlers
        # positions from template transforms/joints
        countA = 6

        positions = [None] * countA
        for i in range(countA):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        #
        # joints, part 1
        #
        count = 3

        oriJnt = [None] * count
        baseJnt = [None] * count
        baseSecJnt = [None] * (countA - count)

        for i in range(count):
            baseJnt[i] = cmds.createNode('joint', n=node + '_baseJnt' + str(i + 1), p=self.rigGrp)
            cmds.setAttr(baseJnt[i] + '.t', positions[i][0], positions[i][1], positions[i][2])

        if positions[0][0] >= -0.001:
            cmds.delete(
                cmds.aimConstraint(baseJnt[1], baseJnt[0], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=baseJnt[2]))
            cmds.delete(
                cmds.aimConstraint(baseJnt[2], baseJnt[1], aim=(1, 0, 0), u=(0, 0, 1), wut='object', wuo=baseJnt[0]))
            cmds.delete(cmds.aimConstraint(baseJnt[1], baseJnt[2], aim=(-1, 0, 0), u=(0, 0, 1), wu=(0, 0, 1),
                                           wut='objectrotation', wuo=baseJnt[-2]))
        else:
            cmds.delete(
                cmds.aimConstraint(baseJnt[1], baseJnt[0], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=baseJnt[2]))
            cmds.delete(
                cmds.aimConstraint(baseJnt[2], baseJnt[1], aim=(-1, 0, 0), u=(0, 0, -1), wut='object', wuo=baseJnt[0]))
            cmds.delete(cmds.aimConstraint(baseJnt[1], baseJnt[2], aim=(1, 0, 0), u=(0, 0, -1), wu=(0, 0, -1),
                                           wut='objectrotation', wuo=baseJnt[-2]))

        for i in range(count):
            cmds.setAttr(baseJnt[i] + '.radius', radius * 0.5)
            oriJnt[i] = cmds.createNode('joint', n=node + '_oriJnt' + str(i + 1), p=self.rigGrp)

        for i in range(1, count):
            oriJnt[i] = cmds.parent(oriJnt[i], oriJnt[i - 1])[0]
            cmds.makeIdentity(oriJnt[i], a=True, jo=True)

        for i in range(count):
            cmds.delete(cmds.parentConstraint(baseJnt[i], oriJnt[i]))

        for i in range(countA - count):
            baseSecJnt[i] = cmds.createNode('joint', n=node + '_baseSecJnt' + str(i + 1), p=self.rigGrp)
            cmds.setAttr(baseSecJnt[i] + '.t', positions[i + count][0], positions[i + count][1],
                         positions[i + count][2])
            baseSecJnt[i] = cmds.parent(baseSecJnt[i], oriJnt[-1])[0]
            cmds.setAttr(baseSecJnt[i] + '.jointOrient', 0, 0, 0)

        # 		#set the base
        # 		if positions[0][0] >= -0.001:
        # 			cmds.setAttr(oriJnt[0]+'.r', 0,0,-90)
        # 		else:
        # 			cmds.setAttr(oriJnt[0]+'.r', 180,0,90)
        #
        # 		#set the knee(s)
        # 		for i in range(1,count-3):
        # 			cmds.setAttr(oriJnt[i]+'.r', 0,0,0)

        # set the foot
        cmds.delete(cmds.orientConstraint(baseJnt[0], oriJnt[0]))
        # dirty way of having yhe exact world one axis orientation rather than using the matrice
        tmpFoot1 = cmds.createNode('transform', n=self.rigGrp + '_tmpFoot1', p=self.rigGrp)
        tmpFoot2 = cmds.createNode('transform', n=self.rigGrp + '_tmpFoot2', p=self.rigGrp)
        cmds.delete(cmds.pointConstraint(oriJnt[0], tmpFoot1))
        cmds.delete(cmds.pointConstraint(oriJnt[1], tmpFoot2))
        posTmpFoot1 = cmds.getAttr(tmpFoot1 + '.translate')[0]
        cmds.setAttr(tmpFoot2 + '.translateY', posTmpFoot1[1])
        cmds.aimConstraint(tmpFoot2, tmpFoot1, aim=(0, 0, 1), u=(0, 1, 0), wut='scene')
        IkCtrl_valueRotate = cmds.getAttr(tmpFoot1 + '.rotateY')
        cmds.rotate(0, -1 * IkCtrl_valueRotate, 0, oriJnt[0], r=True, ws=True, fo=True)
        cmds.delete(tmpFoot1, tmpFoot2)

        ik_ctrlGrp = [None]
        ik_ctrl = [None]
        ctrlInfo = self.getInfoControl(listControlers[0])

        ik_ctrlGrp[0], ik_ctrl[0] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                     position=oriJnt[-3], node=node, \
                                                     lockAttr=['s'], hideAttr=['sx', 'sy', 'sz', 'v'])

        # create shape with attribute
        thisCircle = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), r=1, ch=0)[0]
        self.attributeShape = cmds.listRelatives(thisCircle, pa=True, s=True)[0]
        self.attributeShape = cmds.rename(self.attributeShape, '{}_settings'.format(node))
        cmds.parent(self.attributeShape, ik_ctrl[0], add=True, s=True)
        cmds.setAttr(self.attributeShape + '.overrideEnabled', 1)
        cmds.setAttr(self.attributeShape + '.overrideVisibility', 0)
        cmds.delete(thisCircle)
        # self.attributeShape = cmds.createNode('nurbsCurve', n = '{}_settings'.format(node), parent =  ik_ctrl[0])
        rigUtils.untag([self.attributeShape])

        cmds.addAttr(self.attributeShape, ln='fkControls', at='bool', dv=True, k=True)
        cmds.addAttr(self.attributeShape, ln='ikControls', at='bool', dv=True, k=True)
        cmds.addAttr(self.attributeShape, ln='IkStretch', at='double', min=0, max=1, dv=0, k=True)
        cmds.addAttr(self.attributeShape, ln='IkFk', at='double', min=0, max=1, dv=0, k=True)
        cmds.setAttr(self.attributeShape + '.fkControls', e=True, cb=True, k=False)
        cmds.setAttr(self.attributeShape + '.ikControls', e=True, cb=True, k=False)

        cmds.addAttr(ik_ctrl[0], ln='footRoll', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='footSide', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='heelTwist', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='ballTwist', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='ballUpDwn', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='ballLift', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='toeTwist', at='double', k=True)
        cmds.addAttr(ik_ctrl[0], ln='angleFootRoll', at='double', k=True, dv=55)
        cmds.setAttr(ik_ctrl[0] + '.angleFootRoll', e=True, cb=True, k=False)
        cmds.addAttr(ik_ctrl[0], ln='footControls', at='bool', dv=True, k=True)
        cmds.setAttr(ik_ctrl[0] + '.footControls', e=True, cb=True, k=False)
        # heel

        ctrlInfo = self.getInfoControl(listControlers[3])  # get side wrong
        heelCtrlGrp, heelCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                 color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                 axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=ik_ctrl[0],
                                                 position=baseSecJnt[0], rotation=ik_ctrl[0], node=node, \
                                                 lockAttr=['rz', 't', 's'],
                                                 hideAttr=['rz', 'tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                                 parentCtrl=ik_ctrl[0])

        heel = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', heelCtrl + '.v')

        cmds.connectAttr(ik_ctrl[0] + '.footRoll', heel + '.rx')
        cmds.connectAttr(ik_ctrl[0] + '.heelTwist', heel + '.ry')
        cmds.transformLimits(heel, rx=(0, 0), erx=(False, True))

        # side_rt
        ctrlInfo = self.getInfoControl(listControlers[4])
        shapeOri = (0, 0, 0)
        if ctrlInfo[2] != 'custom':
            if positions[0][0] >= -0.001:
                shapeOri = (0, 90, 0)
            else:
                shapeOri = (0, -90, 0)
        sideRtCtrlGrp, sideRtCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=heelCtrl,
                                                     position=baseSecJnt[1], rotation=ik_ctrl[0], node=node, \
                                                     lockAttr=['t', 'rx', 'ry', 's'],
                                                     hideAttr=['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'],
                                                     shapeOri=shapeOri, parentCtrl=heelCtrl)
        side_rt = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', sideRtCtrl + '.v')

        if positions[0][0] <= -0.001:
            rev = cmds.createNode('reverse')
            cmds.connectAttr(ik_ctrl[0] + '.footSide', rev + '.inputX')
            cmds.connectAttr(rev + '.outputX', side_rt + '.rz')
            cmds.transformLimits(side_rt, rz=(0, 0), erz=(False, True))
        else:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', side_rt + '.rz')
            cmds.transformLimits(side_rt, rz=(0, 0), erz=(True, False))

        # side_lf
        ctrlInfo = self.getInfoControl(listControlers[5])
        shapeOri = (0, 0, 0)
        if ctrlInfo[2] != 'custom':
            if positions[0][0] >= -0.001:
                shapeOri = (0, -90, 0)
            else:
                shapeOri = (0, 90, 0)
        sideLfCtrlGrp, sideLfCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=sideRtCtrl,
                                                     position=baseSecJnt[2], rotation=ik_ctrl[0], node=node, \
                                                     lockAttr=['t', 'rx', 'ry', 's'],
                                                     hideAttr=['tx', 'ty', 'tz', 'rx', 'ry', 'sx', 'sy', 'sz', 'v'],
                                                     shapeOri=shapeOri, parentCtrl=sideRtCtrl)
        side_lf = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', sideLfCtrl + '.v')

        if positions[0][0] <= -0.001:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', rev + '.inputY')
            cmds.connectAttr(rev + '.outputY', side_lf + '.rz')
            cmds.transformLimits(side_lf, rz=(0, 0), erz=(True, False))
        else:
            cmds.connectAttr(ik_ctrl[0] + '.footSide', side_lf + '.rz')
            cmds.transformLimits(side_lf, rz=(0, 0), erz=(False, True))

        # toeTip
        ctrlInfo = self.getInfoControl(listControlers[6])
        toeTipCtrlGrp, toeTipCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=sideLfCtrl,
                                                     position=oriJnt[-1], node=node, \
                                                     lockAttr=['s'], hideAttr=['sx', 'sy', 'sz', 'v'],
                                                     parentCtrl=sideLfCtrl)
        toe = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', toeTipCtrl + '.v')
        cmds.connectAttr(ik_ctrl[0] + '.toeTwist', toe + '.ry')

        # ballLift
        ctrlInfo = self.getInfoControl(listControlers[7])
        shapeOri = (0, 0, 0)
        shapeMove = (0, 0, 0)
        dist = rigUtils.getDistance(oriJnt[-2], oriJnt[-1]) / 3
        if ctrlInfo[2] != 'custom':
            if positions[0][0] >= -0.001:
                shapeOri = (90, 90, 180)
                shapeMove = (dist * -1, 0, dist)
            else:
                shapeOri = (90, 90, 0)
                shapeMove = (dist, 0, dist * -1)

        ballLiftCtrlGrp, ballLiftCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=toeTipCtrl, position=oriJnt[-2], rotation=oriJnt[-2],
                                                         node=node, \
                                                         lockAttr=['t', 's'],
                                                         hideAttr=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                                         shapeOri=shapeOri, shapeMove=shapeMove, parentCtrl=toeTipCtrl)
        ball = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', ballLiftCtrl + '.v')

        self.ballLiftCtrl = ballLiftCtrl
        # ball
        ctrlInfo = self.getInfoControl(listControlers[8])
        if ctrlInfo[2] != 'custom':
            if positions[0][0] >= -0.001:
                shapeOri = (90, 90, 0)
                shapeMove = (dist, 0, dist)
            else:
                shapeOri = (90, 90, 180)
                shapeMove = (dist * -1, 0, dist * -1)
        ballCtrlGrp, ballCtrl = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                 color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                 axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=toeTipCtrl,
                                                 position=oriJnt[-2], rotation=oriJnt[-2], node=node, \
                                                 lockAttr=['t', 's'],
                                                 hideAttr=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'], shapeOri=shapeOri,
                                                 shapeMove=shapeMove, parentCtrl=toeTipCtrl)
        ball2 = '{}{}{}'.format(side, preName, ctrlInfo[6][0])
        cmds.connectAttr(ik_ctrl[0] + '.footControls', ballCtrl + '.v')

        cmds.connectAttr(ik_ctrl[0] + '.ballLift', ball + '.ray')

        cmds.connectAttr(ik_ctrl[0] + '.ballTwist', ball + '.rz')
        cmds.connectAttr(ik_ctrl[0] + '.ballTwist', ball2 + '.rz')

        cmds.connectAttr(ik_ctrl[0] + '.ballUpDwn', ball2 + '.ry')

        # footRoll nodes setup. Part1 : connect the toe above the angle value
        footRoll = ik_ctrl[0] + '.footRoll'
        angleFootRoll = ik_ctrl[0] + '.angleFootRoll'
        toeSubstract = cmds.createNode('plusMinusAverage', n=node + '_toeSubstract_pmn')
        toeAboveValue = cmds.createNode('condition', n=node + '_toeAboveValue_cn')
        cmds.connectAttr(footRoll, toeSubstract + '.input1D[0]')
        cmds.connectAttr(angleFootRoll, toeSubstract + '.input1D[1]')
        cmds.setAttr(toeSubstract + '.operation', 2)
        cmds.connectAttr(angleFootRoll, toeAboveValue + '.secondTerm')
        cmds.connectAttr(footRoll, toeAboveValue + '.firstTerm')
        cmds.connectAttr(toeSubstract + '.output1D', toeAboveValue + '.colorIfTrueR')
        cmds.setAttr(toeAboveValue + '.colorIfFalseR', 0)
        cmds.connectAttr(toeAboveValue + '.outColorR', toe + '.rx')
        cmds.setAttr(toeAboveValue + '.operation', 3)

        # footRoll nodes setup. Part2 : connect the first part of the ball until the angle value
        ballBelowValue = cmds.createNode('condition', n=node + '_ballBelowValue_cn')
        cmds.setAttr(ballBelowValue + '.operation', 5)
        cmds.setAttr(ballBelowValue + '.colorIfFalseR', 0)
        cmds.connectAttr(footRoll, ballBelowValue + '.firstTerm')
        cmds.connectAttr(angleFootRoll, ballBelowValue + '.secondTerm')
        cmds.connectAttr(footRoll, ballBelowValue + '.colorIfTrueR')
        #
        ballTotalRotation = cmds.createNode('plusMinusAverage', n=node + '_ballTotalRotation_pmn')
        cmds.setAttr(ballTotalRotation + '.operation', 1)
        cmds.connectAttr(ballBelowValue + '.outColorR', ballTotalRotation + '.input1D[0]')
        cmds.connectAttr(ballTotalRotation + '.output1D', ball + '.ry')

        # footRoll nodes setup. Part3 : connect the second part of the ball from the angle value
        ballDivmdn = cmds.createNode('multiplyDivide', n=node + '_ballDiv_mdn')
        cmds.setAttr(ballDivmdn + '.operation', 2)
        cmds.connectAttr(footRoll, ballDivmdn + '.input1X')
        cmds.connectAttr(angleFootRoll, ballDivmdn + '.input2X')
        #
        ballReverse = cmds.createNode('reverse', n=node + '_ballReverse_rev')
        cmds.connectAttr(ballDivmdn + '.outputX', ballReverse + '.inputX')
        #
        ballMultmdn = cmds.createNode('multiplyDivide', n=node + '_ballMult_mdn')
        cmds.setAttr(ballMultmdn + '.operation', 1)
        cmds.connectAttr(ballReverse + '.outputX', ballMultmdn + '.input1X')
        cmds.connectAttr(angleFootRoll, ballMultmdn + '.input2X')
        #
        ballPlus = cmds.createNode('plusMinusAverage', n=node + '_ballPlus_pmn')
        cmds.setAttr(ballPlus + '.operation', 1)
        cmds.connectAttr(ballMultmdn + '.outputX', ballPlus + '.input1D[0]')
        cmds.connectAttr(angleFootRoll, ballPlus + '.input1D[1]')
        #
        ballAboveValue = cmds.createNode('condition', n=node + '_ballAboveValue_cn')
        cmds.setAttr(ballAboveValue + '.operation', 2)
        cmds.setAttr(ballAboveValue + '.colorIfFalseR', 0)
        cmds.connectAttr(footRoll, ballAboveValue + '.firstTerm')
        cmds.connectAttr(angleFootRoll, ballAboveValue + '.secondTerm')
        cmds.connectAttr(ballPlus + '.output1D', ballAboveValue + '.colorIfTrueR')
        #
        cmds.connectAttr(ballAboveValue + '.outColorR', ballTotalRotation + '.input1D[1]')
        #
        cmds.transformLimits(ball, ry=(0, 45), ery=(1, 0))

        # 		ctrlInfo = self.getInfoControl(listControlers[1])
        # 		ik_ctrlGrp[1], ik_ctrl[1] = rigUtils.control(name = preName+ctrlInfo[0], side = ctrlInfo[1], shape = ctrlInfo[2], color = ctrlInfo[3], command = ctrlInfo[4], radius = ctrlInfo[7],  \
        # 													axeShape = ctrlInfo[5], grpOffsets=ctrlInfo[6], parent= self.rigGrp, position= oriJnt[1], rotation=oriJnt[1], node = node, \
        # 													lockAttr=['r','s'], hideAttr=['rx','ry','rz','sx','sy','sz','v'], parentCtrl = ik_ctrl[0])
        # 		cmds.parent(self.attributeShape, ik_ctrl[1], add = True, s = True)
        #
        # 		distance = rigUtils.getDistance(oriJnt[1], oriJnt[-2])
        # 		finalDistance = distance*(0.9)
        # 		if positions[0][0] <= -0.001:
        # 			finalDistance = distance*(-0.9)
        #
        # 		cmds.move(0,0,finalDistance, ik_ctrlGrp[1], os=True, r=True, wd=True)
        # 		cmds.setAttr(ik_ctrlGrp[1]+'.r', 0,0,0)

        cmds.connectAttr(self.attributeShape + '.ikControls', ik_ctrl[0] + '.v')
        # 		cmds.connectAttr(self.attributeShape+'.ikControls', ik_ctrl[1]+'.v')

        #
        # ik stretch joints
        #

        count = 2

        fk_ctrl = [None] * count
        fk_ctrlGrp = [None] * count
        jnt = [None] * count
        ikJnts = [None] * (count + 1)
        fkJnts = [None] * (count + 1)
        sknJnt = [None] * count

        for i in range(count):
            o = i + 1
            sub = ''

            parentCtrl = None
            if i:
                parentCtrl = fk_ctrl[i - 1]

            ctrlInfo = self.getInfoControl(listControlers[o])
            fk_ctrlGrp[i], fk_ctrl[i] = rigUtils.control(name=preName + ctrlInfo[0] + sub, side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=self.rigGrp, position=oriJnt[i], rotation=oriJnt[i],
                                                         node=node, \
                                                         lockAttr=[], hideAttr=[], controlType='joint',
                                                         parentCtrl=parentCtrl)

            cmds.parent(self.attributeShape, fk_ctrl[i], add=True, s=True)

            if cmds.listRelatives(fk_ctrl[i], pa=True, s=True):
                cmds.connectAttr(self.attributeShape + '.fkControls',
                                 cmds.listRelatives(fk_ctrl[i], pa=True, s=True)[0] + '.v')

            if i:
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

            # 			else: fk_ctrlGrp[i] = cmds.parent(fk_ctrlGrp[i], self.rigGrp)[0]
            cmds.setAttr(fk_ctrl[i] + '.drawStyle', 2)

            # ik joints and fkJnts
            ikJnts[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                       name='{}{}{}_0_ikJnt'.format(preName, listControlers[o], sub),
                                       parent=self.rigGrp, node=node, typeJnt='', side=ctrlInfo[1],
                                       radius=ctrlInfo[7] * 0.5)
            fkJnts[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                       name='{}{}{}_0_fkJnt'.format(preName, listControlers[o], sub),
                                       parent=self.rigGrp, node=node, typeJnt='', side=ctrlInfo[1],
                                       radius=ctrlInfo[7] * 0.5)
            cmds.parentConstraint(fk_ctrl[i], fkJnts[i], mo=True)

            # blended joints
            jnt[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                    name='{}{}{}_0_jnt'.format(preName, listControlers[o], sub), \
                                    parent=self.rigGrp, node=node, typeJnt='', side=ctrlInfo[1],
                                    radius=ctrlInfo[7] * 0.5, connectedCtrl=fk_ctrl[i])
            sknJnt[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                       name='{}{}{}_0_sknJnt'.format(preName, listControlers[o], sub), \
                                       parent=jnt[i], node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                       radius=ctrlInfo[7] * 0.5, connectedCtrl=fk_ctrl[i])

            if i:
                ikJnts[i] = cmds.parent(ikJnts[i], ikJnts[i - 1])[0]
                fkJnts[i] = cmds.parent(fkJnts[i], fkJnts[i - 1])[0]
                rigUtils.setJointParent(jnt[i - 1], jnt[i])
                jnt[i] = cmds.parent(jnt[i], jnt[i - 1])[0]

            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(jnt[i] + '.radius', radius * 0.5)

        ikJnts[-1] = rigUtils.joint(position=oriJnt[-1], orientation=oriJnt[-1],
                                    name='{}{}{}_0_ikJnt'.format(preName, listControlers[o], 'End'), parent=ikJnts[-2],
                                    node=node, typeJnt='', side=ctrlInfo[1], radius=ctrlInfo[7] * 0.5)
        fkJnts[-1] = rigUtils.joint(position=oriJnt[-1], orientation=oriJnt[-1],
                                    name='{}{}{}_0_fkJnt'.format(preName, listControlers[o], 'End'), parent=fkJnts[-2],
                                    node=node, typeJnt='', side=ctrlInfo[1], radius=ctrlInfo[7] * 0.5)

        self.startJnts = [ikJnts[0], fkJnts[0], jnt[0]]
        #
        # ik handles
        #

        rigUtils.ikHandle(node + '_ball', ikJnts[-3], ikJnts[-2], parent=ballLiftCtrl)
        rigUtils.ikHandle(node + '_toe', ikJnts[-2], ikJnts[-1], parent=ballCtrl)
        cmds.parentConstraint(ballLiftCtrl, ikJnts[0], mo=True)

        # rotate/scale switch
        for i in range(count):
            transBlendColor = cmds.createNode('blendColors', n='{}{}_tBlendCol'.format(node, i))
            cmds.connectAttr(fkJnts[i] + '.translate', transBlendColor + '.color1')
            cmds.connectAttr(ikJnts[i] + '.translate', transBlendColor + '.color2')
            cmds.connectAttr(transBlendColor + '.output', jnt[i] + '.translate')

            rotBlendColor = cmds.createNode('blendColors', n='{}{}_rBlendCol'.format(node, i))
            cmds.connectAttr(fkJnts[i] + '.rotate', rotBlendColor + '.color1')
            cmds.connectAttr(ikJnts[i] + '.rotate', rotBlendColor + '.color2')
            cmds.connectAttr(rotBlendColor + '.output', jnt[i] + '.rotate')

            scaleBlendColor = cmds.createNode('blendColors', n='{}{}_sBlendCol'.format(node, i))
            cmds.connectAttr(fkJnts[i] + '.scale', scaleBlendColor + '.color1')
            cmds.connectAttr(ikJnts[i] + '.scale', scaleBlendColor + '.color2')
            cmds.connectAttr(scaleBlendColor + '.output', jnt[i] + '.scale')

            cmds.connectAttr(self.attributeShape + '.IkFk', transBlendColor + '.blender')
            cmds.connectAttr(self.attributeShape + '.IkFk', rotBlendColor + '.blender')
            cmds.connectAttr(self.attributeShape + '.IkFk', scaleBlendColor + '.blender')

        #
        # lock and hide attributes
        #
        for i in range(count):
            listAttr = ['tx', 'ty', 'tz', 'sy', 'sz', 'v', 'radius']
            # 			if i == 1 :
            # 				listAttr.append('rx')
            # 				listAttr.append('rz')
            for a in listAttr:
                cmds.setAttr(fk_ctrl[i] + '.' + a, l=True, k=False, cb=False)

        # set to default pose
        cmds.delete(cmds.pointConstraint(baseJnt[0], ik_ctrl[0]))
        cmds.setAttr(ik_ctrl[0] + '.rotateY', IkCtrl_valueRotate)

        for i in range(count):
            jntMatrix = cmds.xform(baseJnt[i], q=True, matrix=True, ws=True)
            cmds.xform(fk_ctrl[i], matrix=jntMatrix, ws=True)

        # save default position
        for ctrl in ik_ctrl + fk_ctrl:
            if not ctrl:
                continue
            rigUtils.setDefaultPosition(ctrl)

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        #
        self.mayaControlers = fk_ctrl + ik_ctrl + [heelCtrl, sideRtCtrl, sideLfCtrl, toeTipCtrl, ballLiftCtrl, ballCtrl]

        self.setLastNode(jnt[-1])
        cmds.hide(ikJnts + fkJnts)
        cmds.delete(oriJnt, baseJnt)
        cmds.select(self.rigGrp)
        cmds.refresh()

        return sknJnt
