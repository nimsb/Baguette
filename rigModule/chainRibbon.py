from __future__ import absolute_import
from maya import cmds
# import pymel.core 
from . import nodeBase
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/chainRibbonWidgetOptions.ui'


class ChainRibbonWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(ChainRibbonWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['RibbonChain', 'RibbonChain2', 'RibbonChain3']
        self.initiateMayaNodes(self.controlers)
        # 		self.shapes = {}
        '''
        self.controlName
        self.grpOffsets
        self.joints
        self.sknJnts
        '''
        self.surfaceRibbon = None
        self.oldSurfaceRibbon = None

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

        # add numJoint option to the templateGrp
        cmds.addAttr(self.templateGrp, ln='numJoint', at='long')
        cmds.setAttr(self.templateGrp + '.numJoint', e=True, keyable=True)
        cmds.setAttr(self.templateGrp + '.numJoint', 3)
        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='scalable', at='bool')
        cmds.setAttr(self.templateGrp + '.scalable', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='locTemplate', dt='string')
        cmds.setAttr(self.templateGrp + '.locTemplate', e=True, keyable=True)

    def options(self):
        super(ChainRibbonWidget, self).options()
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

            if not cmds.objExists(self.templateGrp + '.scalable'):
                cmds.addAttr(self.templateGrp, ln='scalable', at='bool')
                cmds.setAttr(self.templateGrp + '.scalable', e=True, keyable=True)
            scalable = cmds.getAttr(self.templateGrp + '.scalable')
            self.options_Qgb.scalable_chbx.setChecked(scalable)

            if not cmds.objExists(self.templateGrp + '.oldRibbonSurface'):
                cmds.addAttr(self.templateGrp, ln='oldRibbonSurface', dt='string')
                cmds.setAttr(self.templateGrp + '.oldRibbonSurface', e=True, keyable=True)

            if not cmds.objExists(self.templateGrp + '.locTemplate'):
                cmds.addAttr(self.templateGrp, ln='locTemplate', dt='string')
                cmds.setAttr(self.templateGrp + '.locTemplate', e=True, keyable=True)
            cmds.setAttr(self.templateGrp + '.locTemplate',
                         [self.templateControlers[0] + '_locA', self.templateControlers[0] + '_locB',
                          self.templateControlers[0] + '_locC'], type='string')

        if cmds.objExists(self.rigGrp):
            if not cmds.objExists(self.rigGrp + '.ribbonSurface'):
                cmds.addAttr(self.rigGrp, ln='ribbonSurface', dt='string')
                cmds.setAttr(self.rigGrp + '.ribbonSurface', e=True, keyable=True)

        self.qtOptions.numJoint_num.valueChanged.connect(partial(self.updateNumJoint))
        self.qtOptions.numJoint_slider.sliderMoved.connect(partial(self.updateNumJointFromSlider))
        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))
        self.options_Qgb.scalable_chbx.stateChanged.connect(partial(self.updateScalable))

        # remove all the controler in the widget because we don't need them
        for i in reversed(range(1, isNumJoint)):
            self.controlers_layout.takeAt(i).widget().deleteLater()
            self.allControlerWidget.pop(i)

        self.controlers_layout.itemAt(0).widget().controlerName_lineEdit.editingFinished.connect(
            self.updateNumTemplateCtrl)

    # self.updateNumTemplateCtrl()

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
        # 		oldNumCtrl = len(self.controlers)
        oldNumCtrl = len(self.templateControlers)

        infoCtrl = self.getInfoControl(self.controlers[0])

        doAdd = False
        numToAdd = isNumJoint - oldNumCtrl
        if numToAdd > 0:
            doAdd = True

        # add or remove controlers
        if doAdd:
            for i in range(oldNumCtrl, isNumJoint):
                controler = '{}{}'.format(self.controlers[0], str(i + 1))
                # add controler
                # 				self.controlers.append(controler)
                # 				#setup mayaNode
                # 				self.setControlerShape(controler, type = infoCtrl[2], color = infoCtrl[3]+1, cmd = infoCtrl[4], axe = infoCtrl[5], radius = infoCtrl[7])
                # 				#setup widget
                # 				ctrlWidget = self.setupWidgetControler(controler)
                # 				self.allControlerWidget.append(ctrlWidget)
                # setup template ctrls
                templateCtrl = cmds.createNode('joint', n='{}_{}_template'.format(node, controler),
                                               p=self.templateControlers[i - 1])
                cmds.setAttr(templateCtrl + '.radius', 1)
                cmds.setAttr(templateCtrl + '.tx', 3)
                self.templateControlers.append(templateCtrl)

        else:
            for i in reversed(list(range(isNumJoint, oldNumCtrl))):
                # 				self.controlers.pop(i)
                # clean maya node
                cmds.removeMultiInstance('{}.controlers[{}]'.format(node, str(i)))
                # 				self.controlers_layout.takeAt(i).widget().deleteLater()
                # 				self.allControlerWidget.pop(i)
                # remove template
                cmds.delete(self.templateControlers[i])
                self.templateControlers.pop(i)

        firstCtrl = self.controlers[0]
        self.controlers = []
        self.controlers.append(firstCtrl)
        for i in range(1, isNumJoint):
            self.controlers.append(self.controlers[0] + str(i))

        self.initiateMayaNodes(self.controlers)
        self.initializeControlerName()

        # 		self.setLastNode(self.joints[self.controlers[-1]][0])

        self.controlersList_qcb.clear()
        for controler in self.controlers:
            self.controlersList_qcb.addItem(controler)

        cmds.setAttr(self.templateGrp + '.isTemplate', str(self.templateControlers), type='string')

        self.setState(1)

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        node = self.getNode()
        self.templateControlers = [None]

        self.templateControlers[0] = cmds.createNode('joint', n='{}_{}1_template'.format(node, self.controlers[0]),
                                                     p=self.templateGrp)
        cmds.setAttr(self.templateControlers[0] + '.radius', 1)

        for i in range(2):
            templateCtrl = cmds.createNode('joint', n='{}_{}{}_template'.format(node, self.controlers[0], i + 2),
                                           p=self.templateControlers[i])
            cmds.setAttr(templateCtrl + '.radius', 1)
            cmds.setAttr(templateCtrl + '.tx', 3)
            self.templateControlers.append(templateCtrl)

        self.postTemplate()

        cmds.select(self.templateGrp)

    def postTemplate(self, mirror=False):

        locA = self.templateControlers[0] + '_locA'
        if not cmds.objExists(locA):
            locA = cmds.spaceLocator(n=locA)[0]
            cmds.setAttr(locA + '.localScale', 0.5, 0.5, 0.5)
            cmds.parent(locA, self.templateControlers[0])
            cmds.setAttr(locA + '.t', 0, 0, 1.5)
            cmds.setAttr(locA + '.r', 0, 0, 0)

        locB = self.templateControlers[0] + '_locB'
        if not cmds.objExists(locB):
            locB = cmds.spaceLocator(n=locB)[0]
            cmds.setAttr(locB + '.localScale', 0.5, 0.5, 0.5)
            cmds.parent(locB, self.templateControlers[0])
            cmds.setAttr(locB + '.t', 0, 0, 0)
            cmds.setAttr(locB + '.r', 0, 0, 0)

        locC = self.templateControlers[0] + '_locC'
        if not cmds.objExists(locC):
            locC = cmds.spaceLocator(n=locC)[0]
            cmds.setAttr(locC + '.localScale', 0.5, 0.5, 0.5)
            cmds.parent(locC, self.templateControlers[0])
            cmds.setAttr(locC + '.t', 0, 0, -1.5)
            cmds.setAttr(locC + '.r', 0, 0, 0)

        if mirror:
            locA_t = cmds.getAttr(locA + '.t')[0]
            cmds.setAttr(locA + '.t', locA_t[0], locA_t[1] * -1, locA_t[2] * -1)

        aimCstr = self.templateControlers[0] + '_aimCstr'
        if cmds.objExists(aimCstr):
            cmds.delete(aimCstr)
        aimCstr = cmds.aimConstraint(locA, locB, aim=(0, 1, 0), u=(0, 1, 0), wut='scene', n=aimCstr)

        mdNode = cmds.createNode('multiplyDivide', n=locC + '_mdn')
        cmds.connectAttr(locA + '.t', mdNode + '.input1', f=True)
        cmds.setAttr(mdNode + '.input2X', -1)
        cmds.setAttr(mdNode + '.input2Y', -1)
        cmds.setAttr(mdNode + '.input2Z', -1)

        cmds.connectAttr(mdNode + '.output', locC + '.t', f=True)

        cmds.setAttr(self.templateGrp + '.locTemplate', [locA, locB, locC], type='string')

    def defaultWidget(self):
        pass

    def rig(self):
        '''
        well ...
        '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        node = self.getNode()
        count = len(self.templateControlers)
        # positions from template transforms/joints
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt
        scalable = cmds.getAttr(self.templateGrp + '.scalable')

        ctrlInfo = self.getInfoControl(self.controlers[0])

        positions = [None] * count
        jnt = [None] * count
        sknJnt = [None] * count

        for i in range(count):
            positions[i] = cmds.xform(self.templateControlers[i], q=True, rp=True, ws=True)

        # create surface
        curvDeg1 = cmds.curve(degree=1, p=positions)
        curvDeg3 = cmds.fitBspline(curvDeg1, ch=False, tol=0.001)[0]
        curvDeg3 = \
        cmds.rebuildCurve(curvDeg3, ch=False, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int(count / 1.5), d=3,
                          tol=0.01)[0]

        curvBaseDeg1 = cmds.curve(degree=1,
                                  p=[cmds.xform(self.templateControlers[0] + '_locC', q=True, rp=True, ws=True), \
                                     cmds.xform(self.templateControlers[0] + '_locA', q=True, rp=True, ws=True)])

        follGrp = cmds.createNode('transform', n=node + '_noxform', p=self.rigGrp)

        self.surfaceRibbon = \
        cmds.extrude(curvBaseDeg1, curvDeg3, et=True, fpt=False, upn=True, rotation=0, scale=1, ch=False,
                     n=node + 'Ribbon_surface')[0]
        self.surfaceRibbon = cmds.parent(self.surfaceRibbon, follGrp)[0]

        cmds.addAttr(self.rigGrp, ln='ribbonSurface', dt='string')
        cmds.setAttr(self.rigGrp + '.ribbonSurface', e=True, keyable=True)
        cmds.setAttr(self.rigGrp + '.ribbonSurface', self.surfaceRibbon, type='string')

        allFollicle = []
        for i in range(count):
            foll = rigUtils.createFollicleAtExactPosition(self.surfaceRibbon, self.templateControlers[i])
            allFollicle.append(foll)

            jnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                    name=preName + self.joints[self.controlers[i]][0], parent=self.rigGrp, node=node,
                                    side=ctrlInfo[1])
            sknJnt[i] = rigUtils.joint(position=self.templateControlers[i], orientation=self.templateControlers[i],
                                       name=preName + self.sknJnts[self.controlers[i]][0], parent=jnt[i], node=node,
                                       side=ctrlInfo[1])

            if i:
                rigUtils.setJointParent(jnt[i - 1], jnt[i])

            if scalable:
                cmds.connectAttr(self.rigDefaultNode + '.scaleRig', jnt[i] + '.scale')

            cmds.parentConstraint(foll, jnt[i], mo=False)
            cmds.setAttr(jnt[i] + '.drawStyle', 2)
            cmds.setAttr(sknJnt[i] + '.radius', 0.35)
            cmds.connectAttr(assemblyAsset + '.joints', sknJnt[i] + '.v')

        for foll in allFollicle:
            foll = cmds.parent(foll, follGrp)[0]

        rigUtils.selectable(assemblyAsset + '.editJoints', sknJnt)

        # connect scaleRig to jntRig
        for jntRig in jnt:
            cmds.connectAttr(self.rigGrp + '.scaleRig', jntRig + '.scale')

        # clean
        cmds.delete([curvDeg1, curvDeg3, curvBaseDeg1])

        cmds.refresh()
        return sknJnt

    def preRig(self):
        if not cmds.objExists(self.rigGrp):
            super(ChainRibbonWidget, self).preRig()
            return

        self.oldSurfaceRibbon = cmds.getAttr(self.rigGrp + '.ribbonSurface')
        self.oldSurfaceRibbon = cmds.rename(self.oldSurfaceRibbon,
                                            self.oldSurfaceRibbon.replace('_surface', '_oldSurface'))
        self.oldSurfaceRibbon = cmds.parent(self.oldSurfaceRibbon, self.templateGrp)[0]

        cmds.setAttr(self.templateGrp + '.oldRibbonSurface', self.oldSurfaceRibbon, type='string')

        super(ChainRibbonWidget, self).preRig()

    def postRig(self):
        self.surfaceRibbon = cmds.getAttr(self.rigGrp + '.ribbonSurface')
        self.oldSurfaceRibbon = cmds.getAttr(self.templateGrp + '.oldRibbonSurface')

        if not self.oldSurfaceRibbon:
            super(ChainRibbonWidget, self).postRig()
            return

        if rigUtils.findSkinCluster(self.oldSurfaceRibbon):
            # Transfert skin from oldSurface to new surfaceRibbon
            rigUtils.copySkin(self.oldSurfaceRibbon, [self.surfaceRibbon])
            cmds.select(self.surfaceRibbon)
        # 			pymel.core.mel.removeUnusedInfluences()

        cmds.delete(self.oldSurfaceRibbon)
        cmds.setAttr(self.templateGrp + '.oldRibbonSurface', '', type='string')

        # find first joint of the skinned surface

        # closest point on surface to know which parents!

        super(ChainRibbonWidget, self).postRig()
