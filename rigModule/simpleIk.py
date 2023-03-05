from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils, matrix
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/limbWidgetOptions.ui'


class SimpleIkWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        self.simpleIkSuper = super(SimpleIkWidget, self)
        self.simpleIkSuper.__init__(parent)
        # 		super(SimpleIkWidget, self).simpleIkSuper.__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['LegIk', 'LegPv', 'UpLeg', 'Knee', 'FootEnd']
        self.initiateMayaNodes(self.controlers)

        '''
        self.controlName
        self.grpOffsets
        self.joints
        self.sknJnts
        '''

    # 	def addControlers(self):
    # 		print 'adding foot controlers'
    # 		newControlers = ['Heel', 'ToeSideRt', 'ToeSideLt', 'ToeTip', 'BallLift', 'Ball']
    # 		self.controlers = self.controlers + newControlers
    # 		self.initiateMayaNodes(self.controlers)
    #
    # 		self.setControlerShape('Heel', 'arrowFlatWrap3Quarter', 19, axe = 'x', radius = 0.2)
    # 		self.setControlerShape('ToeSideRt', 'arrowFlatWrapHalf', 19, axe = 'z', radius = 0.07)
    # 		self.setControlerShape('ToeSideLt', 'arrowFlatWrapHalf', 19, axe = 'z', radius = 0.07)
    # 		self.setControlerShape('ToeTip', 'sphere', 19, axe = 'x', radius = 0.2)
    # 		self.setControlerShape('BallLift', 'arrow1way', 19, axe = 'y', radius = 0.5)
    # 		self.setControlerShape('Ball', 'arrow1way', 19, axe = 'y', radius = 0.5)
    #
    # 		#setup widget
    # 		for controler in newControlers:
    # 			ctrlWidget = self.setupWidgetControler(controler)
    # 			self.allControlerWidget.append(ctrlWidget)
    # 			self.controlersList_qcb.addItem(controler)
    #
    # 		self.initializeControlerName()

    def addData(self):
        '''
        It's where you define controle shapes, grpOffset and skinning joint.
        You need to add them to the node info to be able to use them before it's actually rigged.
        It's only called when the node is created the first time.
        '''

        # set here default value for the controlers and shape.
        self.setControlerShape('LegIk', 'cube', 7, axe='x')
        self.setControlerShape('LegPv', 'cube', 7, axe='x', radius=0.2)
        self.setControlerShape('UpLeg', 'sphere', 14, axe='x')
        self.setControlerShape('Knee', 'circle', 14, axe='x')
        self.setControlerShape('FootEnd', 'circle', 14, axe='x')

        # add knee option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='doubleJoint', at='bool')
        cmds.setAttr(self.templateGrp + '.doubleJoint', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='numTwist', at='long')
        cmds.setAttr(self.templateGrp + '.numTwist', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

        rigUtils.addVectorAttr(self.templateGrp, attribute='orientation')
        cmds.setAttr(self.templateGrp + '.orientationY', 1)
        cmds.addAttr(self.templateGrp, ln='reverseOrientation', at='bool')
        cmds.setAttr(self.templateGrp + '.reverseOrientation', e=True, keyable=True)
        cmds.setAttr(self.templateGrp + '.reverseOrientation', 1)

    def updateKnee(self, state, num=0):
        node = self.getNode()

        if state:
            # create jnt and parent it
            name = '{}_{}_template'.format(node, '2bis')
            jnt = cmds.createNode('joint', n=name, p=self.templateControlers[1 + num])
            cmds.setAttr(jnt + '.radius', cmds.getAttr(self.templateControlers[1 + num] + '.radius'))
            pos = cmds.getAttr(self.templateControlers[2 + num] + '.t')[0]
            cmds.setAttr(jnt + '.t', pos[0] / 5, pos[1] / 5, 0)
            self.templateControlers.insert(2 + num, jnt)
            cmds.parent(self.templateControlers[3 + num], jnt)
            cmds.setAttr(self.templateGrp + '.doubleJoint', True)

        else:
            # reparent the jnt and delete the doubleJoint
            cmds.parent(self.templateControlers[3 + num], self.templateControlers[1 + num])
            cmds.delete(self.templateControlers[2 + num])
            self.templateControlers.pop(2 + num)
            cmds.setAttr(self.templateGrp + '.doubleJoint', False)

        cmds.setAttr(self.templateGrp + '.isTemplate', str(self.templateControlers), type='string')
        cmds.select(self.templateGrp)

        if cmds.objExists('{}_TEMP_sknJnt_grp'.format(node)):
            cmds.delete('{}_TEMP_sknJnt_grp'.format(node))

        self.setState(1)

    def updateNumTwist(self, value):
        cmds.setAttr(self.templateGrp + '.numTwist', value)
        self.setState(1)

    def updateOrientation(self):
        state = [None] * 3
        state[0] = self.qtOptions.defaultX_radioBtn.isChecked()
        state[1] = self.qtOptions.defaultY_radioBtn.isChecked()
        state[2] = self.qtOptions.defaultZ_radioBtn.isChecked()

        cmds.setAttr(self.templateGrp + '.orientation', state[0], state[1], state[2])
        self.setState(1)

    def updateRevOrientation(self, value):
        cmds.setAttr(self.templateGrp + '.reverseOrientation', bool(value))
        self.setState(1)

    def updateDefaultRotation(self, value):
        cmds.setAttr(self.templateGrp + '.defaultRot', bool(value))
        self.setState(1)

    def updateZeroPos(self, value):
        cmds.setAttr(self.templateGrp + '.zeroPos', bool(value))
        self.setState(1)

    def options(self):
        super(SimpleIkWidget, self).options()
        '''this happen after the item and the node are created.'''

        if not cmds.objExists(self.templateGrp + '.doubleJoint'):
            cmds.addAttr(self.templateGrp, ln='doubleJoint', at='bool')
            cmds.setAttr(self.templateGrp + '.doubleJoint', e=True, keyable=True)
        isDoubleJoint = cmds.getAttr(self.templateGrp + '.doubleJoint')
        self.qtOptions.doubleJoint_ckb.setChecked(isDoubleJoint)
        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
        self.qtOptions.numTwist_box.setValue(numTwist)
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        self.prependName_chbx.setChecked(prependName)
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        self.prependName_lineEdit.setText(prependNameTxt)

        if not cmds.objExists(self.templateGrp + '.orientation'):
            rigUtils.addVectorAttr(self.templateGrp, attribute='orientation')
            cmds.setAttr(self.templateGrp + '.orientationY', 1)
            cmds.addAttr(self.templateGrp, ln='reverseOrientation', at='bool')
            cmds.setAttr(self.templateGrp + '.reverseOrientation', e=True, keyable=True)
            cmds.setAttr(self.templateGrp + '.reverseOrientation', 1)

        if not cmds.objExists(self.templateGrp + '.defaultRot'):
            cmds.addAttr(self.templateGrp, ln='defaultRot', at='bool')
            cmds.setAttr(self.templateGrp + '.defaultRot', e=True, keyable=True)

        if not cmds.objExists(self.templateGrp + '.zeroPos'):
            cmds.addAttr(self.templateGrp, ln='zeroPos', at='bool')
            cmds.setAttr(self.templateGrp + '.zeroPos', e=True, keyable=True)

        ori = cmds.getAttr(self.templateGrp + '.orientation')[0]
        self.qtOptions.defaultX_radioBtn.setChecked(bool(ori[0]))
        self.qtOptions.defaultY_radioBtn.setChecked(bool(ori[1]))
        self.qtOptions.defaultZ_radioBtn.setChecked(bool(ori[2]))
        isReverse = cmds.getAttr(self.templateGrp + '.reverseOrientation')
        self.qtOptions.reverseOri_ckb.setChecked(isReverse)

        self.qtOptions.ikTmpRot_ckb.setChecked(cmds.getAttr(self.templateGrp + '.defaultRot'))
        self.qtOptions.zeroPos_ckb.setChecked(cmds.getAttr(self.templateGrp + '.zeroPos'))

        self.qtOptions.doubleJoint_ckb.stateChanged.connect(partial(self.updateKnee))
        self.qtOptions.numTwist_box.valueChanged.connect(partial(self.updateNumTwist))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))
        self.qtOptions.defaultX_radioBtn.toggled.connect(partial(self.updateOrientation))
        self.qtOptions.defaultY_radioBtn.toggled.connect(partial(self.updateOrientation))
        self.qtOptions.defaultZ_radioBtn.toggled.connect(partial(self.updateOrientation))
        self.qtOptions.reverseOri_ckb.stateChanged.connect(partial(self.updateRevOrientation))
        self.qtOptions.ikTmpRot_ckb.stateChanged.connect(partial(self.updateDefaultRotation))
        self.qtOptions.zeroPos_ckb.stateChanged.connect(partial(self.updateZeroPos))

    def template(self, num=3, pos=[(0, 9, 0), (0, 5, 0.25), (0, 0.5, 0)]):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None] * num
        pos = pos
        for i in range(num):
            name = '{}_{}_template'.format(node, str(i + 1))
            if cmds.objExists(name):
                self.templateControlers[i] = name
            else:
                self.templateControlers[i] = cmds.createNode('joint', n=name, p=self.templateGrp)
                cmds.setAttr(self.templateControlers[i] + '.t', pos[i][0], pos[i][1], pos[i][2])
                if i:
                    self.templateControlers[i] = \
                    cmds.parent(self.templateControlers[i], self.templateControlers[i - 1])[0]
            cmds.setAttr(self.templateControlers[i] + '.radius', 0.5)

        self.templateKnee = self.templateControlers[1]

    # cmds.select(oriJnt[0])

    def defaultWidget(self):
        pass

    def rig(self, templateControlers=None, mainIk=None, attributSettingShape=None, endJnts=None, ballLiftCtrl=None,
            footFk=None, fkIncrement=None, rigGrpPos='Default'):
        '''
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        radius = 1
        isDoubleJoint = cmds.getAttr(self.templateGrp + '.doubleJoint')
        numTwist = cmds.getAttr(self.templateGrp + '.numTwist')
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        isDefaultRotation = cmds.getAttr(self.templateGrp + '.defaultRot')
        isZeroPos = cmds.getAttr(self.templateGrp + '.zeroPos')
        preName = ''
        if prependName:
            preName = prependNameTxt
        self.mayaControlers = []
        side = cmds.getAttr(node + '.side')
        if side and side != 'None':
            side = side + '_'
        else:
            side = ''

        templateCtrl = eval(cmds.getAttr(self.templateGrp + '.isTemplate'))
        self.templateControlers
        if templateControlers:
            templateCtrl = templateControlers

        # position the self.rigGrp before anything.
        if rigGrpPos == 'Default':
            rigUtils.snapTranslation(templateCtrl[0], self.rigGrp)
        elif rigGrpPos:
            rigUtils.snapTranslation(rigGrpPos, self.rigGrp)

        # positions from template transforms/joints
        countA = 3
        if isDoubleJoint:
            countA += 1

        positions = [None] * countA
        worldTranslationMatrix = [None] * countA
        for i in range(countA):
            positions[i] = cmds.xform(templateCtrl[i], q=True, rp=True, ws=True)

            worldMatrix = matrix.getMatrix(templateCtrl[i])
            worldTranslationMatrix[i] = matrix.getTranslation(worldMatrix)

        self.positionCenter = positions[0][0]

        #
        # joints, part 1
        #
        count = countA
        oriJnt = [None] * count
        baseJnt = [None] * count

        for i in range(count):
            baseJnt[i] = cmds.createNode('joint', n=node + '_baseJnt' + str(i + 1), p=self.rigGrp)
            # 			cmds.setAttr(baseJnt[i]+'.t', positions[i][0], positions[i][1], positions[i][2])
            cmds.xform(baseJnt[i], t=worldTranslationMatrix[i], ws=True)

        if self.positionCenter >= -0.001:
            cmds.delete(
                cmds.aimConstraint(baseJnt[1], baseJnt[0], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=baseJnt[2]))
            cmds.delete(
                cmds.aimConstraint(baseJnt[2], baseJnt[1], aim=(1, 0, 0), u=(0, 0, -1), wut='object', wuo=baseJnt[0]))
            if isDoubleJoint:
                cmds.delete(cmds.aimConstraint(baseJnt[3], baseJnt[2], aim=(1, 0, 0), u=(0, 0, -1), wut='object',
                                               wuo=baseJnt[0]))
            cmds.delete(cmds.aimConstraint(baseJnt[-2], baseJnt[-1], aim=(-1, 0, 0), u=(0, 0, 1), wu=(0, 0, 1),
                                           wut='objectrotation', wuo=baseJnt[-2]))


        else:
            cmds.delete(
                cmds.aimConstraint(baseJnt[1], baseJnt[0], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=baseJnt[2]))
            cmds.delete(
                cmds.aimConstraint(baseJnt[2], baseJnt[1], aim=(-1, 0, 0), u=(0, 0, 1), wut='object', wuo=baseJnt[0]))
            if isDoubleJoint:
                cmds.delete(cmds.aimConstraint(baseJnt[3], baseJnt[2], aim=(-1, 0, 0), u=(0, 0, 1), wut='object',
                                               wuo=baseJnt[0]))
            cmds.delete(cmds.aimConstraint(baseJnt[-2], baseJnt[-1], aim=(1, 0, 0), u=(0, 0, 1), wu=(0, 0, 1),
                                           wut='objectrotation', wuo=baseJnt[-2]))

        for i in range(count):
            cmds.setAttr(baseJnt[i] + '.radius', radius * 0.5)
            oriJnt[i] = cmds.createNode('joint', n=node + '_oriJnt' + str(i + 1), p=self.rigGrp)
        # 			cmds.matchTransform(oriJnt[i], baseJnt[i])

        for i in range(1, count):
            oriJnt[i] = cmds.parent(oriJnt[i], oriJnt[i - 1])[0]
            cmds.makeIdentity(oriJnt[i], a=True, jo=True)

        for i in range(count):
            cmds.delete(cmds.parentConstraint(baseJnt[i], oriJnt[i]))

        # create a base where I parent all the joints ik fk jnt ...
        self.parentBaseJnt = cmds.duplicate(baseJnt[0], n=node + '_parentBaseJnt')[0]
        cmds.setAttr(self.parentBaseJnt + '.drawStyle', 2)

        normalXaxisDict = {
            'x': [0, 0, 0],
            '-x': [0, 0, 180],
            'y': [0, 0, 90],
            '-y': [0, 0, -90],
            'z': [0, -90, -90],
            '-z': [0, 90, -90]}

        reverseXaxisDict = {
            'x': [-180, 0, 180],
            '-x': [180, 0, 0],
            'y': [180, 0, -90],
            '-y': [180, 0, 90],
            'z': [180, 90, 90],
            '-z': [180, -90, 90]}

        defaultOrientation = cmds.getAttr(self.templateGrp + '.orientation')[0]
        reverse = cmds.getAttr(self.templateGrp + '.reverseOrientation')

        axis = 'x'
        if bool(defaultOrientation[1]):
            axis = 'y'
        if bool(defaultOrientation[2]):
            axis = 'z'
        if reverse:
            axis = '-' + axis

        # set the base
        if self.positionCenter >= -0.001:
            rot = normalXaxisDict[axis]
        else:
            rot = reverseXaxisDict[axis]

        # 		#get the closest perpendicular values
        # 		rot = [None]*3
        # 		oriVal = cmds.getAttr(oriJnt[0]+'.rotate')[0]
        # 		step = 90.0
        # 		for i in range(3):
        # 			rot[i] = int(round(oriVal[i]/step))*step

        if not isZeroPos:
            cmds.setAttr(oriJnt[0] + '.r', rot[0], rot[1], rot[2])
            # set the knee(s)
            for i in range(1, count):
                cmds.setAttr(oriJnt[i] + '.r', 0, 0, 0)

        ik_ctrlGrp = [None] * 2
        ik_ctrl = [None] * 2
        ctrlInfo = self.getInfoControl(self.controlers[0])
        if not mainIk:
            ik_ctrlGrp[0], ik_ctrl[0] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=self.rigGrp, position=oriJnt[-1], node=node, \
                                                         lockAttr=['s'], hideAttr=['sx', 'sy', 'sz', 'v'])
        else:
            ik_ctrl[0] = mainIk
            ik_ctrlGrp[0] = cmds.listConnections(ik_ctrl[0] + '.ctrlGrp')[0]
            cmds.delete(cmds.pointConstraint(oriJnt[-1], ik_ctrlGrp[0]))

        if not attributSettingShape:
            # create shape with attribute
            thisCircle = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), r=1, ch=0)[0]
            attributeShape = cmds.listRelatives(thisCircle, pa=True, s=True)[0]
            attributeShape = cmds.rename(attributeShape, '{}_settings'.format(node))
            cmds.parent(attributeShape, ik_ctrl[0], add=True, s=True)
            cmds.setAttr(attributeShape + '.overrideEnabled', 1)
            cmds.setAttr(attributeShape + '.overrideVisibility', 0)
            cmds.delete(thisCircle)
            # attributeShape = cmds.createNode('nurbsCurve', n = '{}_settings'.format(node), parent =  ik_ctrl[0])
            rigUtils.untag([attributeShape])

            cmds.addAttr(attributeShape, ln='fkControls', at='bool', dv=True, k=True)
            cmds.addAttr(attributeShape, ln='ikControls', at='bool', dv=True, k=True)
            cmds.addAttr(attributeShape, ln='IkStretch', at='double', min=0, max=1, dv=0, k=True)
            cmds.addAttr(attributeShape, ln='IkFk', at='double', min=0, max=1, dv=0, k=True)
            cmds.setAttr(attributeShape + '.fkControls', e=True, cb=True, k=False)
            cmds.setAttr(attributeShape + '.ikControls', e=True, cb=True, k=False)
        else:
            attributeShape = attributSettingShape

        ctrlInfo = self.getInfoControl(self.controlers[1])
        ik_ctrlGrp[1], ik_ctrl[1] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                     color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                     axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=self.rigGrp,
                                                     position=oriJnt[1], node=node, \
                                                     lockAttr=['r', 's'],
                                                     hideAttr=['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                                     parentCtrl=ik_ctrl[0])
        cmds.parent(attributeShape, ik_ctrl[1], add=True, s=True)

        distance = rigUtils.getDistance(oriJnt[1], oriJnt[-1])
        finalDistance = distance * (0.9)
        multDist = 1
        coordOri0 = cmds.xform(baseJnt[0], q=True, rp=True, ws=True)
        coordOri1 = cmds.xform(baseJnt[1], q=True, rp=True, ws=True)
        coordOri2 = cmds.xform(baseJnt[-1], q=True, rp=True, ws=True)

        zOri = coordOri0[2] - (coordOri0[2] - coordOri2[2]) / 2
        if coordOri1[2] < zOri:
            multDist = -1

        movX = 0
        movY = 0
        movZ = 0
        if 'x' in axis or 'y' in axis:
            movZ = finalDistance * multDist
        if 'z' in axis:
            movY = finalDistance * multDist
            if reverse:
                movY = movY * -1

        cmds.move(movX, movY, movZ, ik_ctrlGrp[1], os=True, r=True, wd=True)
        cmds.setAttr(ik_ctrlGrp[1] + '.r', 0, 0, 0)

        cmds.connectAttr(attributeShape + '.ikControls', ik_ctrl[0] + '.v', f=True)
        cmds.connectAttr(attributeShape + '.ikControls', ik_ctrl[1] + '.v', f=True)

        count = 3
        if isDoubleJoint:
            count += 1
        fk_ctrl = [None] * count
        fk_ctrlGrp = [None] * count
        jnt = [None] * count
        ikJnts = [None] * count
        fkJnts = [None] * count
        sknJnt = [None] * count

        for i in range(count):
            o = i
            sub = ''
            if count > 3:
                if i == 2:
                    o = 1
                    sub = 'Bis'
                if i > 2:
                    o = i - 1
            if fkIncrement:
                o += 1

            parentCtrl = None
            if i:
                parentCtrl = fk_ctrl[i - 1]

            if i == count - 1 and endJnts:
                fk_ctrl[-1] = cmds.listConnections(endJnts[2] + '.connectedCtrl')[0]
                fk_ctrlGrp[-1] = cmds.listConnections(fk_ctrl[i] + '.ctrlGrp')[0]
            # 				rigUtils.snapNodes(oriJnt[i], fk_ctrlGrp[-1])
            else:
                ctrlInfo = self.getInfoControl(self.controlers[o + 2])
                fk_ctrlGrp[i], fk_ctrl[i] = rigUtils.control(name=preName + ctrlInfo[0] + sub, side=ctrlInfo[1],
                                                             shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                             radius=ctrlInfo[7], \
                                                             axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                             parent=self.parentBaseJnt, position=oriJnt[i],
                                                             rotation=oriJnt[i], node=node, \
                                                             lockAttr=[], hideAttr=[], controlType='joint',
                                                             parentCtrl=parentCtrl)

                cmds.parent(attributeShape, fk_ctrl[i], add=True, s=True)

                if cmds.listRelatives(fk_ctrl[i], pa=True, s=True):
                    cmds.connectAttr(attributeShape + '.fkControls',
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

            cmds.setAttr(fk_ctrl[i] + '.drawStyle', 2)

            if i == count - 1 and endJnts:
                jnt[i] = endJnts[2]
                sknJnt[i] = cmds.listConnections(jnt[i] + '.sknJnt')[0]
                ikJnts[i] = endJnts[0]
                fkJnts[i] = endJnts[1]
            else:
                # ik joints and fkJnts
                ikJnts[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                           name='{}{}{}_0_ikJnt'.format(preName, self.controlers[o + 2], sub),
                                           parent=self.parentBaseJnt, node=node, typeJnt='', side=ctrlInfo[1],
                                           radius=ctrlInfo[7] * 0.5)
                fkJnts[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                           name='{}{}{}_0_fkJnt'.format(preName, self.controlers[o + 2], sub),
                                           parent=self.parentBaseJnt, node=node, typeJnt='', side=ctrlInfo[1],
                                           radius=ctrlInfo[7] * 0.5)

                cmds.parentConstraint(fk_ctrl[i], fkJnts[i], mo=False)

                # blended joints
                jnt[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                        name='{}{}{}_0_jnt'.format(preName, self.controlers[o + 2], sub), \
                                        parent=self.parentBaseJnt, node=node, typeJnt='', side=ctrlInfo[1],
                                        radius=ctrlInfo[7] * 0.5, connectedCtrl=fk_ctrl[i])
                sknJnt[i] = rigUtils.joint(position=oriJnt[i], orientation=oriJnt[i],
                                           name='{}{}{}_0_sknJnt'.format(preName, self.controlers[o + 2], sub), \
                                           parent=jnt[i], node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                           radius=ctrlInfo[7] * 0.5, connectedCtrl=fk_ctrl[i])

            if i:
                ikJnts[i] = cmds.parent(ikJnts[i], ikJnts[i - 1])[0]
                fkJnts[i] = cmds.parent(fkJnts[i], fkJnts[i - 1])[0]
                rigUtils.setJointParent(jnt[i - 1], jnt[i])
                jnt[i] = cmds.parent(jnt[i], jnt[i - 1])[0]

            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v', f=True)

            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(jnt[i] + '.radius', radius * 0.5)

        if endJnts:
            rigUtils.snapNodes(jnt[-1], fk_ctrlGrp[-1])
            rigUtils.snapNodes(jnt[-1], fk_ctrl[-1])
            cmds.rotate(0, (cmds.getAttr(ik_ctrl[0] + '.ry')) * -1, 0, fk_ctrlGrp[-1], ws=True, fo=True, r=True)

        #
        # ik handles
        #
        for i in range(count):
            rigUtils.snapNodes(baseJnt[i], ikJnts[i])
        cmds.joint(ikJnts[0], e=True, spa=True, ch=True)
        for i in range(count):
            cmds.delete(cmds.parentConstraint(oriJnt[i], ikJnts[i]))

        parentIk = ik_ctrl[0]
        if ballLiftCtrl:
            parentIk = ballLiftCtrl
        ikh = rigUtils.ikHandle(node, ikJnts[0], ikJnts[-1], parent=parentIk)[0]
        pvc = cmds.poleVectorConstraint(ik_ctrl[1], ikh)[0]
        cmds.rename(pvc, node + '_pvcon')

        # reset all joint orient to stay in the same local orient values
        for joint in [ikJnts[0], fkJnts[0], jnt[0], fk_ctrlGrp[0]]:
            cmds.setAttr(joint + '.jo', 0, 0, 0)

        # the ik change the default orientation so to maintain a ikFK transition we need to snap the value back to the Fks
        rigUtils.snapNodes(ikJnts[0], fk_ctrlGrp[0])

        # rotate/scale switch
        countB = count
        if endJnts:
            countB = count - 1
        for i in range(countB):
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

            cmds.connectAttr(attributeShape + '.IkFk', transBlendColor + '.blender')
            cmds.connectAttr(attributeShape + '.IkFk', rotBlendColor + '.blender')
            cmds.connectAttr(attributeShape + '.IkFk', scaleBlendColor + '.blender')

        # default parent
        cmds.parent(ik_ctrlGrp[1], ik_ctrl[0])

        #
        # stretch math
        #

        ikJntDist = 0
        for i in range(1, count):
            ikJntDist += abs(cmds.getAttr(ikJnts[i] + '.tx'))

        startBase = cmds.createNode('transform', n='{}_startBase'.format(node), p=fk_ctrlGrp[0])
        startBase = cmds.parent(startBase, self.rigGrp)[0]
        Arm_distBetween = cmds.createNode('distanceBetween', n='{}_distBet'.format(node))
        Arm_condition = cmds.createNode('condition', n='{}_cond'.format(node))
        Arm_multiplyDiv = cmds.createNode('multiplyDivide', n='{}_mdn'.format(node))
        ArmScaleModule_multiplyDiv = cmds.createNode('multiplyDivide', n='{}scaleModule_mdn'.format(node))
        ArmStretch_blendCol = cmds.createNode('blendColors', n='{}Stretch_blendCol'.format(node))
        cmds.setAttr(ArmScaleModule_multiplyDiv + '.input1X', ikJntDist)
        cmds.connectAttr(self.rigGrp + '.sx', ArmScaleModule_multiplyDiv + '.input2X')
        cmds.connectAttr(startBase + '.worldMatrix', Arm_distBetween + '.inMatrix1')
        cmds.connectAttr(ik_ctrl[0] + '.worldMatrix', Arm_distBetween + '.inMatrix2')
        cmds.connectAttr(Arm_distBetween + '.distance', Arm_multiplyDiv + '.input1X')
        cmds.connectAttr(ArmScaleModule_multiplyDiv + '.outputX', Arm_multiplyDiv + '.input2X')
        cmds.setAttr(Arm_multiplyDiv + '.operation', 2)
        cmds.connectAttr(Arm_distBetween + '.distance', Arm_condition + '.firstTerm')
        cmds.connectAttr(Arm_multiplyDiv + '.outputX', Arm_condition + '.colorIfTrueR')
        cmds.connectAttr(ArmScaleModule_multiplyDiv + '.outputX', Arm_condition + '.secondTerm')
        cmds.setAttr(Arm_condition + '.operation', 2)
        cmds.setAttr(ArmStretch_blendCol + '.color2R', 1)
        cmds.connectAttr(Arm_condition + '.outColor', ArmStretch_blendCol + '.color1')
        cmds.connectAttr(attributeShape + '.IkStretch', ArmStretch_blendCol + '.blender')

        for i in range(count - 1):
            cmds.connectAttr(ArmStretch_blendCol + '.outputR', ikJnts[i] + '.sx')
            cmds.setAttr(sknJnt[i] + '.segmentScaleCompensate', 1)

        #
        # lock and hide attributes
        #
        for i in range(count):
            listAttr = ['tx', 'ty', 'tz', 'sy', 'sz', 'v', 'radius']
            # if i == count - 1: listAttr.append('sx')
            if i == 1:
                listAttr.append('rx')
                listAttr.append('rz')
            if i == 2 and isDoubleJoint:
                listAttr.append('rx')
                listAttr.append('rz')
            for a in listAttr:
                cmds.setAttr(fk_ctrl[i] + '.' + a, l=True, k=False, cb=False)

        # fk / ik bake ready
        cmds.addAttr(attributeShape, ln='ikCtrl', at='message')
        cmds.addAttr(ik_ctrl[0], ln='ikCtrl', at='message')
        cmds.connectAttr(ik_ctrl[0] + '.ikCtrl', attributeShape + '.ikCtrl')
        cmds.addAttr(attributeShape, ln='pvCtrl', at='message')
        cmds.addAttr(ik_ctrl[1], ln='pvCtrl', at='message')
        cmds.connectAttr(ik_ctrl[1] + '.pvCtrl', attributeShape + '.pvCtrl')
        cmds.addAttr(attributeShape, ln='startFkCtrl', at='message')
        cmds.addAttr(fk_ctrl[0], ln='startFkCtrl', at='message')
        cmds.connectAttr(fk_ctrl[0] + '.startFkCtrl', attributeShape + '.startFkCtrl')
        cmds.addAttr(attributeShape, ln='midFkCtrl', at='message')
        cmds.addAttr(fk_ctrl[1], ln='midFkCtrl', at='message')
        cmds.connectAttr(fk_ctrl[1] + '.midFkCtrl', attributeShape + '.midFkCtrl')
        if isDoubleJoint:
            cmds.addAttr(attributeShape, ln='mid2FkCtrl', at='message')
            cmds.addAttr(fk_ctrl[2], ln='mid2FkCtrl', at='message')
            cmds.connectAttr(fk_ctrl[2] + '.mid2FkCtrl', attributeShape + '.mid2FkCtrl')
        cmds.addAttr(attributeShape, ln='endFkCtrl', at='message')
        cmds.addAttr(fk_ctrl[-1], ln='endFkCtrl', at='message')
        cmds.connectAttr(fk_ctrl[-1] + '.endFkCtrl', attributeShape + '.endFkCtrl')
        cmds.addAttr(attributeShape, ln='startIkJnt', at='message')
        cmds.addAttr(ikJnts[0], ln='startIkJnt', at='message')
        cmds.connectAttr(ikJnts[0] + '.startIkJnt', attributeShape + '.startIkJnt')
        cmds.addAttr(attributeShape, ln='midIkJnt', at='message')
        cmds.addAttr(ikJnts[1], ln='midIkJnt', at='message')
        cmds.connectAttr(ikJnts[1] + '.midIkJnt', attributeShape + '.midIkJnt')
        if isDoubleJoint:
            cmds.addAttr(attributeShape, ln='mid2IkJnt', at='message')
            cmds.addAttr(ikJnts[2], ln='mid2IkJnt', at='message')
            cmds.connectAttr(ikJnts[2] + '.mid2IkJnt', attributeShape + '.mid2IkJnt')
        cmds.addAttr(attributeShape, ln='endIkJnt', at='message')
        cmds.addAttr(ikJnts[-1], ln='endIkJnt', at='message')
        cmds.connectAttr(ikJnts[-1] + '.endIkJnt', attributeShape + '.endIkJnt')

        ##twist joint
        if numTwist:
            side = ''
            if ctrlInfo[1] != 'None':
                side = ctrlInfo[1] + '_'

            self.rotationUpTwistGrp = cmds.createNode('transform', n="{}{}rotationUpTwist_grp".format(side,
                                                                                                      jnt[0].replace(
                                                                                                          side,
                                                                                                          '').split(
                                                                                                          '_')[0]),
                                                      parent=self.rigGrp)
            rigUtils.snapNodes(jnt[0], self.rotationUpTwistGrp)
            aim = (1, 0, 0)
            if self.positionCenter >= -0.001:
                aim = (-1, 0, 0)

            twistJntsUp, firstTwistJnt = rigUtils.twist(
                name="{}{}Twist".format(side, jnt[0].replace(side, '').split('_')[0]), control=jnt[-2], parent=jnt[0], \
                count=numTwist, stable=jnt[0], _twist=jnt[1], aim=aim, wu=(0, 0, 1), wuo=self.rotationUpTwistGrp, \
                scale=jnt[0])
            # cmds.orientConstraint(firstTwistJnt, jnt[0] , mo = True)
            twistJntsLo = \
            rigUtils.twist(name="{}{}Twist".format(side, jnt[-2].replace(side, '').split('_')[0]), control=jnt[-2],
                           parent=jnt[-2], \
                           count=numTwist, stable=jnt[-2], _twist=jnt[-1], \
                           scale=jnt[-2])[0]

            for twistJnt in twistJntsUp:
                rigUtils.setJointParent(jnt[0], twistJnt)
                rigUtils.setConnectedJointControlRelation(fk_ctrl[0], twistJnt)
            for twistJnt in twistJntsLo:
                rigUtils.setJointParent(jnt[-2], twistJnt)
                rigUtils.setConnectedJointControlRelation(fk_ctrl[-2], twistJnt)

            for twistJnt in twistJntsUp + twistJntsLo:
                sknTwistJntName = twistJnt.replace('_jnt', '_sknJnt')
                connectedCtrl = cmds.listConnections(twistJnt + '.connectedCtrl')[0]
                if side:
                    sknTwistJntName = sknTwistJntName.replace(side, '')
                sknTwistJnt = rigUtils.joint(position=twistJnt, orientation=twistJnt, name=sknTwistJntName,
                                             parent=twistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                             radius=0.35, connectedCtrl=connectedCtrl)
                cmds.connectAttr(assemblyAsset + '.joints', sknTwistJnt + '.v')
                sknJnt.append(sknTwistJnt)

            # adding first up joint to sknJnts
            rigUtils.setJointParent(jnt[0], firstTwistJnt)
            firstTwistSknJnt = rigUtils.joint(position=firstTwistJnt, orientation=firstTwistJnt,
                                              name="{}Twist0_sknJnt".format(jnt[0].replace(side, '').split('_')[0]), \
                                              parent=firstTwistJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                              radius=0.35, connectedCtrl=fk_ctrl[0])
            sknJnt.append(firstTwistSknJnt)

        # set to default pose
        tmpParentCstr = None
        tmpsDefaultRotate = None
        tmpLastJntBase = cmds.duplicate(fkJnts[-1])[0]
        tmpLastJntBase = cmds.parent(tmpLastJntBase, self.rigGrp)[0]

        if not mainIk:
            skip = []
            if endJnts:
                skip = ['x', 'z']
            if isDefaultRotation:
                tmpParentCstr = cmds.orientConstraint(templateCtrl[2], ik_ctrl[0], mo=False, skip=skip)
            else:
                tmpsDefaultRotate = cmds.createNode('transform', n=self.rigGrp + '_defaultRotIk', p=self.rigGrp)
                tmpsDefaultRotate = cmds.parent(tmpsDefaultRotate, tmpLastJntBase)[0]
                rigUtils.snapTranslation(tmpLastJntBase, tmpsDefaultRotate)
                rigUtils.snapNodes(baseJnt[-1], tmpLastJntBase)
                # 			#get the closest perpendicular values
                # 			rot = [None]*3
                # 			oriVal = cmds.getAttr(tmpLastJntBase+'.rotate')[0]
                # 			step = 90.0
                # 			for i in range(3):
                # 				rot[i] = int(round(oriVal[i]/step))*step
                # 			cmds.setAttr(tmpLastJntBase+'.rotate', rot[0], rot[1], rot[2])

                tmpParentCstr = cmds.orientConstraint(tmpsDefaultRotate, ik_ctrl[0], mo=False, skip=skip)

        rigUtils.snapTranslation(baseJnt[-1], ik_ctrl[0])

        if tmpParentCstr:
            cmds.delete(tmpParentCstr)
        if tmpsDefaultRotate:
            cmds.delete(tmpsDefaultRotate)

        rigUtils.snapNodes(ik_ctrl[0], ik_ctrl[0])

        tmpPv = cmds.createNode('transform', n=self.rigGrp + '_tmpPv', p=baseJnt[1])

        if self.positionCenter <= -0.001:
            finalDistance = finalDistance * -1

        cmds.move(0, 0, finalDistance, tmpPv, os=True, r=True, wd=True)
        cmds.delete(cmds.pointConstraint(tmpPv, ik_ctrl[1]))

        # set default fk ctrls
        for i in range(countB):
            rigUtils.snapNodes(ikJnts[i], fk_ctrl[i])

        if endJnts:
            rigUtils.snapNodes(jnt[-1], fk_ctrl[-1])
        if numTwist:
            # snap rotation up twist grp again
            rigUtils.snapNodes(jnt[0], self.rotationUpTwistGrp)

        # constraint last ik joints to the ik controller
        mainIkJnt = rigUtils.joint(position=ikJnts[-1], orientation=ikJnts[-1],
                                   name='{}{}_0_jnt'.format(preName, self.controlers[0]), \
                                   parent=ik_ctrl[0], node=node, typeJnt='', side=ctrlInfo[1], radius=1,
                                   connectedCtrl=ik_ctrl[0])
        cmds.setAttr(mainIkJnt + '.drawStyle', 2)
        cmds.orientConstraint(mainIkJnt, ikJnts[-1], mo=True)

        # save default position
        for ctrl in ik_ctrl + fk_ctrl:
            if not ctrl:
                continue
            rigUtils.setDefaultPosition(ctrl)

        # selectable joints
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        # create last joint for other module if needed
        # on hold since jnt[-1] seems enough
        # 		self.lastRigJoint = rigUtils.joint(position = jnt[-1], orientation = jnt[-1], name = '{}{}LastJoint_0_jnt'.format(preName, self.controlers[-1]), \
        # 									parent = jnt[-1], node = node, typeJnt = '', side = ctrlInfo[1], radius = 1)
        # 		cmds.setAttr(self.lastRigJoint+'.drawStyle', 2)
        # 		rigUtils.setJointParent(jnt[-1], self.lastRigJoint)

        # needed for inheritance
        self.attributeShape = attributeShape
        self.preName = preName
        self.mainIkGrp = ik_ctrlGrp[0]
        self.startBase = startBase
        self.rigJnt = jnt
        self.fkCtrl = fk_ctrl
        self.ikCtrl = ik_ctrl
        self.side = side
        self.assemblyAsset = assemblyAsset

        #
        self.mayaControlers = fk_ctrl + ik_ctrl

        self.setLastNode(jnt[-1])
        cmds.hide(ikJnts + fkJnts)
        cmds.delete(oriJnt, baseJnt, tmpLastJntBase)
        cmds.select(self.rigGrp)
        cmds.refresh()

        return sknJnt
