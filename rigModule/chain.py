from __future__ import absolute_import
from maya import cmds
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/chainWidgetOptions.ui'


class ChainWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(ChainWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Chain1']
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
        for controler in self.controlers:
            self.setControlerShape(controler, 'circle', 13, axe='x')

        # add elbow option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='numJoint', at='long')
        cmds.setAttr(self.templateGrp + '.numJoint', e=True, keyable=True)
        cmds.setAttr(self.templateGrp + '.numJoint', 1)

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='ikPins', at='bool')
        cmds.setAttr(self.templateGrp + '.ikPins', e=True, keyable=True)

    def options(self):
        super(ChainWidget, self).options()
        # this happen after the item and the node are created.
        if cmds.objExists(self.templateGrp):
            isNumJoint = cmds.getAttr(self.templateGrp + '.numJoint')
            self.qtOptions.numJoint_num.setValue(isNumJoint)
            self.qtOptions.numJoint_slider.setSliderPosition(isNumJoint)

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

            if not cmds.objExists(self.templateGrp + '.ikPins'):
                cmds.addAttr(self.templateGrp, ln='ikPins', at='bool')
                cmds.setAttr(self.templateGrp + '.ikPins', e=True, keyable=True)
            prependName = cmds.getAttr(self.templateGrp + '.ikPins')
            self.qtOptions.ikPins_chbx.setChecked(prependName)
            if prependName:
                # lock num joint numJoint_num QSpinBox numJoint_slider QSlider
                self.qtOptions.jointNum_widget.setEnabled(False)
            else:
                self.qtOptions.jointNum_widget.setEnabled(True)

        self.qtOptions.numJoint_num.valueChanged.connect(partial(self.updateNumJoint))
        self.qtOptions.numJoint_slider.sliderMoved.connect(partial(self.updateNumJointFromSlider))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))
        self.qtOptions.ikPins_chbx.stateChanged.connect(partial(self.updateIkPins))

    def updateNumJoint(self, *args):
        numJoint = self.qtOptions.numJoint_num.value()
        cmds.setAttr(self.templateGrp + '.numJoint', numJoint)
        self.qtOptions.numJoint_slider.setSliderPosition(numJoint)
        self.updateNumTemplateCtrl()

    def updateNumJointFromSlider(self, *args):
        numJointSlider = self.qtOptions.numJoint_slider.sliderPosition()
        self.qtOptions.numJoint_num.setValue(numJointSlider)
        self.updateNumTemplateCtrl()

    def updateNumTemplateCtrl(self, *args):
        node = self.getNode()
        isNumJoint = cmds.getAttr(self.templateGrp + '.numJoint')
        doIkPins = cmds.getAttr(self.templateGrp + '.ikPins')
        infoCtrl = self.getInfoControl(self.controlers[0])

        allPinControler = []
        allNonPinControler = []
        for controler in self.controlers:
            if self.getInfoControl(controler)[8]:
                allPinControler.append(controler)
            else:
                allNonPinControler.append(controler)
        oldNumCtrl = len(allNonPinControler)

        numPinToAdd = isNumJoint - len(allPinControler)

        doAddPin = False
        if numPinToAdd > 0:
            doAddPin = True

        doAdd = False
        remove = False
        numToAdd = isNumJoint - oldNumCtrl
        if numToAdd > 0:
            doAdd = True
        if numToAdd < 0:
            remove = True

        # add or remove controlers
        if doAdd:
            for i in range(oldNumCtrl, isNumJoint):
                controler = '{}{}'.format(node, str(i + 1))
                # add controler
                self.controlers.append(controler)
                allNonPinControler.append(controler)
                # setup mayaNode
                self.setControlerShape(controler, type=infoCtrl[2], color=infoCtrl[3] + 1, cmd=infoCtrl[4],
                                       axe=infoCtrl[5], radius=infoCtrl[7], isPinIk=0)
                # setup widget
                ctrlWidget = self.setupWidgetControler(controler)
                self.allControlerWidget.append(ctrlWidget)
                # setup template ctrls
                templateCtrl = cmds.createNode('joint', n='{}_{}_template'.format(node, controler),
                                               p=self.templateControlers[i - 1])
                cmds.setAttr(templateCtrl + '.radius', 1)
                cmds.setAttr(templateCtrl + '.tx', 3)
                self.templateControlers.append(templateCtrl)

        if remove:
            ctrls = []
            for index in reversed(list(range(isNumJoint, oldNumCtrl))):
                ## remove correct controler AND his associated pinIk##
                controler = allNonPinControler[index]
                ctrls.append(controler)
                if doIkPins:
                    controlerPin = allPinControler[index]
                    ctrls.append(controlerPin)

                for ctrl in ctrls:
                    try:
                        i = self.controlers.index(ctrl)
                        self.controlers.pop(i)
                        # clean maya node
                        cmds.removeMultiInstance('{}.controlers[{}]'.format(node, str(i)))
                        self.controlers_layout.takeAt(i).widget().deleteLater()
                        self.allControlerWidget.pop(i)
                    except:
                        pass
                    try:
                        # remove template
                        cmds.delete(self.templateControlers[i])
                        self.templateControlers.pop(i)
                    except:
                        pass

        if doIkPins and doAddPin:
            for i in range(len(allPinControler), isNumJoint):
                controlerIk = '{}Ik{}'.format(node, str(i + 1))
                # add controler
                self.controlers.append(controlerIk)
                allPinControler.append(controlerIk)
                # setup mayaNode
                self.setControlerShape(controlerIk, type='pin', color=19, cmd=infoCtrl[4], axe='z', radius=infoCtrl[7],
                                       isPinIk=1)
                # setup widget
                ctrlWidget = self.setupWidgetControler(controlerIk)
                self.allControlerWidget.append(ctrlWidget)

        if not doIkPins and len(allPinControler):
            # remove all pin controler
            allIdx = []
            for ctrl in allPinControler:
                idx = self.controlers.index(ctrl)
                allIdx.append(idx)
            allIdx.sort()
            for i in allIdx[::-1]:
                self.controlers.pop(i)
                # clean maya node
                cmds.removeMultiInstance('{}.controlers[{}]'.format(node, str(i)))
                self.controlers_layout.takeAt(i).widget().deleteLater()
                self.allControlerWidget.pop(i)

        self.initiateMayaNodes(self.controlers)
        self.initializeControlerName()

        self.setLastNode(self.joints[self.controlers[-1]][0])

        self.controlersList_qcb.clear()
        for controler in self.controlers:
            self.controlersList_qcb.addItem(controler)

        cmds.setAttr(self.templateGrp + '.isTemplate', str(self.templateControlers), type='string')

        self.doTemplate()

    def updateIkPins(self, value, *args):
        if value > 0:
            value = 1
        cmds.setAttr(self.templateGrp + '.ikPins', value)
        self.updateNumTemplateCtrl()

        if value:
            # lock num joint numJoint_num QSpinBox numJoint_slider QSlider
            self.qtOptions.jointNum_widget.setEnabled(False)
        else:
            self.qtOptions.jointNum_widget.setEnabled(True)

        self.setState(1)

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
        node = self.getNode()
        count = len(self.templateControlers)
        isIkPin = cmds.getAttr(self.templateGrp + '.ikPins')

        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt
        self.mayaControlers = []

        # positions from template transforms/joints
        # 		positions = [None]*count
        control = [None] * count
        controlIk = [None] * count
        controlGrp = [None] * count
        controlIkGrp = [None] * count
        jnt = [None] * count
        jntIk = [None] * count
        sknJnt = [None] * count

        for i in range(count):
            # 			positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)
            ctrlInfo = self.getInfoControl(self.controlers[i])
            parentToUse = self.rigGrp
            parentCtrl = None
            if i:
                parentToUse = jnt[i - 1]
                parentCtrl = control[i - 1]

            controlGrp[i], control[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=parentToUse, position=self.templateControlers[i],
                                                         rotation=self.templateControlers[i], node=node, \
                                                         lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'],
                                                         parentCtrl=parentCtrl)

            self.mayaControlers.append(control[i])

            jnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                    name=preName + self.joints[self.controlers[i]][0], parent=control[i], \
                                    node=node, side=ctrlInfo[1], connectedCtrl=control[i])
            jointParent = jnt[i]
            ctrlParent = control[i]

            if isIkPin:
                ctrlInfo = self.getInfoControl(self.controlers[i + count])
                parentCtrl = None
                if i:
                    parentCtrl = controlIk[i - 1]

                controlIkGrp[i], controlIk[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1],
                                                                 shape=ctrlInfo[2], color=ctrlInfo[3],
                                                                 command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                                 axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                                 parent=control[i], position=self.templateControlers[i],
                                                                 rotation=self.templateControlers[i], node=node, \
                                                                 lockAttr=['s'], hideAttr=['sx', 'sy', 'sz', 'v'],
                                                                 parentCtrl=parentCtrl)
                self.mayaControlers.append(controlIk[i])

                jntIk[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                          name=preName + self.joints[self.controlers[i + count]][0],
                                          parent=controlIk[i], \
                                          node=node, side=ctrlInfo[1], connectedCtrl=controlIk[i])
                jointParent = jntIk[i]
                ctrlParent = None
                cmds.setAttr(jntIk[i] + '.drawStyle', 2)
                if i:
                    rigUtils.setJointParent(jntIk[i - 1], jntIk[i])

                    upObj = cmds.createNode('transform', n=controlIk[i].replace('_ctrl', '_loc'), p=controlIk[i])
                    cmds.setAttr(upObj + '.translateX', -10)
            # cmds.aimConstraint(jntIk[i], jntIk[i-1], mo = True, weight = 1, aimVector = (1,0,0), upVector = (0,1,0), worldUpType = "object", worldUpObject = upObj)

            else:
                if i:
                    rigUtils.setJointParent(jnt[i - 1], jnt[i])

            sknJnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                       name=preName + self.sknJnts[self.controlers[i]][0], parent=jointParent, \
                                       node=node, side=ctrlInfo[1], connectedCtrl=ctrlParent)

            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(sknJnt[i] + '.radius', 0.35)

            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

        if isIkPin:
            cmds.addAttr(control[0], ln='showIks', at='bool')
            cmds.setAttr(control[0] + '.showIks', e=True, k=True)
            for ctrlIk in controlIk:
                cmds.connectAttr(control[0] + '.showIks', ctrlIk + '.v')

        self.setLastNode(jnt[-1])
        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        cmds.select(control)
        cmds.refresh()

        return sknJnt
