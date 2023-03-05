from __future__ import absolute_import
from __future__ import print_function
from maya import cmds
from . import nodeBase
from ..utils import rigUtils, faceUtils
import os
from ..utils.Qt import QtCompat, QtWidgets, QtCore
from six.moves import range
from functools import partial

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/faceMainWidgetOptions.ui'


class FaceMainWidget(nodeBase.BaseWidget):
    def __init__(self, parent=None):
        super(FaceMainWidget, self).__init__(parent)

        self.qtOptions = QtCompat.loadUi(fileUi, self.options_Qgb)

        # we define the name of the controlers here
        self.controlers = ['Global', 'Local', 'Root', 'Cog']
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

        # set here default value for the controlers and shape.
        self.setControlerShape('Global', 'tileMain', 18, 'y')
        self.setControlerShape('Local', 'tileGimbal', 23, 'y')
        self.setControlerShape('Root', 'tileOffset', 17, 'y')
        self.setControlerShape('Cog', 'diamond', 14, 'y', 2)

        cmds.addAttr(self.templateGrp, ln='prependName', at='bool')
        cmds.setAttr(self.templateGrp + '.prependName', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='prependNameTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.prependNameTxt', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='scalable', at='bool')
        cmds.setAttr(self.templateGrp + '.scalable', e=True, keyable=True)

        cmds.addAttr(self.templateGrp, ln='faceMeshTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.faceMeshTxt', e=True, keyable=True)
        cmds.addAttr(self.templateGrp, ln='facsBsTxt', dt='string')
        cmds.setAttr(self.templateGrp + '.facsBsTxt', e=True, keyable=True)

    def options(self):
        super(FaceMainWidget, self).options()
        # add here any Qt options to the self.options_Qgb you would like to see
        if cmds.objExists(self.templateGrp):
            prependName = cmds.getAttr(self.templateGrp + '.prependName')
            self.prependName_chbx.setChecked(prependName)

            prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
            self.prependName_lineEdit.setText(prependNameTxt)

            scalable = cmds.getAttr(self.templateGrp + '.scalable')
            self.options_Qgb.scalable_chbx.setChecked(scalable)

            faceMeshTxt = cmds.getAttr(self.templateGrp + '.faceMeshTxt')
            self.options_Qgb.faceMesh_lineEdit.setText(faceMeshTxt)

            facsBsTxt = cmds.getAttr(self.templateGrp + '.facsBsTxt')
            self.options_Qgb.facsBs_lineEdit.setText(facsBsTxt)

            self.updateFACSBlendshapeList()

        self.prependName_chbx.stateChanged.connect(partial(self.updatePrependName))
        self.prependName_lineEdit.textChanged.connect(partial(self.updatePrependNameTxt))
        self.options_Qgb.scalable_chbx.stateChanged.connect(partial(self.updateScalable))

        self.options_Qgb.faceMeshSelection_btn.clicked.connect(partial(self.faceMeshSelection))
        self.options_Qgb.faceBsSelection_btn.clicked.connect(partial(self.facsBlendshapeNodeSelection))
        self.options_Qgb.createShapes_btn.clicked.connect(partial(self.createFACSblendshape))
        self.options_Qgb.updateBsList_btn.clicked.connect(partial(self.updateFACSBlendshapeList))
        self.options_Qgb.connectSelected_btn.clicked.connect(partial(self.connectBlendshape))
        self.options_Qgb.rmvBlendshape_btn.clicked.connect(partial(self.removeBlendshape))
        self.options_Qgb.extractSelected_btn.clicked.connect(partial(self.extractBlendshape))
        self.options_Qgb.faceMesh_lineEdit.textChanged.connect(partial(self.updateFaceMeshNameMayaAttr))
        self.options_Qgb.facsBs_lineEdit.textChanged.connect(partial(self.updateFACSNameMayaAttr))

    def updateFaceMeshNameMayaAttr(self, *args):
        faceMeshTxt = self.options_Qgb.faceMesh_lineEdit.text()
        cmds.setAttr(self.templateGrp + '.faceMeshTxt', faceMeshTxt, type='string')

    def faceMeshSelection(self):
        sel = cmds.ls(sl=True)
        if not sel:
            return

        self.options_Qgb.faceMesh_lineEdit.setText(sel[0])
        # check for FACS blendshape
        for input in cmds.listHistory(sel[0], levels=1):
            print(input)
            if cmds.nodeType(input) == 'blendShape':
                self.options_Qgb.facsBs_lineEdit.setText(input)
                return

    def updateFACSNameMayaAttr(self, *args):
        facsBsTxt = self.options_Qgb.facsBs_lineEdit.text()
        cmds.setAttr(self.templateGrp + '.facsBsTxt', facsBsTxt, type='string')

        self.updateFACSBlendshapeList()

    def facsBlendshapeNodeSelection(self):
        sel = cmds.ls(sl=True)
        if not sel:
            return
        self.options_Qgb.facsBs_lineEdit.setText(sel[0])

    def updateFACSBlendshapeList(self):
        facsBsTxt = self.options_Qgb.facsBs_lineEdit.text()
        if not facsBsTxt or not cmds.objExists(facsBsTxt):
            return

        if not cmds.nodeType(facsBsTxt) == 'blendShape':
            cmds.warning('{} is not a blendshape'.format(facsBsTxt))
            return

        self.qtOptions.updateBsList_treeWidget.clear()

        targetIndexFaceBlendshape = faceUtils.getBlendshapeTargetIndexDict(facsBsTxt)
        targetIndexFaceBlendshapeIndex = list(targetIndexFaceBlendshape.values())
        targetIndexFaceBlendshapeIndex.sort()

        for idx in targetIndexFaceBlendshapeIndex:
            target = list(targetIndexFaceBlendshape.keys())[list(targetIndexFaceBlendshape.values()).index(idx)]
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(item.flags())
            item.setText(0, target)
            self.qtOptions.updateBsList_treeWidget.addTopLevelItem(item)

    def connectBlendshape(self, selections=[]):
        faceMeshTxt = self.options_Qgb.faceMesh_lineEdit.text()
        facsBsTxt = self.options_Qgb.facsBs_lineEdit.text()
        targetIndexFaceBlendshape = faceUtils.getBlendshapeTargetIndexDict(facsBsTxt)
        targetNameList = list(targetIndexFaceBlendshape.keys())

        if not selections:
            selections = cmds.ls(sl=True)
        if not selections:
            cmds.warning('please select some shape to add or connect to {}'.format(facsBsTxt))
            return

        for geo in selections:
            geoShape = faceUtils.getShape(geo)
            if not geoShape:
                continue

            if '|' in geo:
                geo = geo.split('|')[-1]

            if geo in targetNameList:
                # connect shape to blendshape
                index = targetIndexFaceBlendshape[geo]
                target_attr = 'worldMesh[0]'
                cmds.connectAttr('{}.{}'.format(geoShape, target_attr),
                                 '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputGeomTarget'.format(
                                     facsBsTxt, index
                                 ),
                                 f=True
                                 )
                print('{} is connected to {}'.format(geo, facsBsTxt))
            else:
                # add blendshape
                targetIndexFaceBlendshapeIndex = list(targetIndexFaceBlendshape.values())
                targetIndexFaceBlendshapeIndex.sort()
                addIndex = targetIndexFaceBlendshapeIndex[-1] + 1
                cmds.blendShape(facsBsTxt, edit=True, target=[faceMeshTxt, addIndex, geo, 1])
                print('added target {} to {}'.format(geo, facsBsTxt))

        self.updateFACSBlendshapeList()

    def removeBlendshape(self):
        faceMeshTxt = self.options_Qgb.faceMesh_lineEdit.text()
        facsBsTxt = self.options_Qgb.facsBs_lineEdit.text()
        targetIndexFaceBlendshape = faceUtils.getBlendshapeTargetIndexDict(facsBsTxt)

        items = self.qtOptions.updateBsList_treeWidget.selectedItems()
        if items:
            for item in items:
                target = item.text(0)
                index = targetIndexFaceBlendshape[target]
                # remove any lock
                isNotLocked = cmds.getAttr('{}.{}'.format(facsBsTxt, target), settable=True)
                if not isNotLocked:
                    cmds.setAttr('{}.{}'.format(facsBsTxt, target), lock=False)

                cmds.removeMultiInstance('{}.weight[{}]'.format(facsBsTxt, index), b=True)
                cmds.removeMultiInstance('{}.inputTarget[0].inputTargetGroup[{}]'.format(facsBsTxt, index), b=True)
                cmds.aliasAttr('{}.weight[{}]'.format(facsBsTxt, index), rm=True)
                # cmds.blendShape(facsBsTxt, edit = True, remove = True, target = [faceMeshTxt, index, target, 1])

                print('removed {} from {}'.format(target, facsBsTxt))

        self.updateFACSBlendshapeList()

    def extractBlendshape(self):
        faceMeshTxt = self.options_Qgb.faceMesh_lineEdit.text()
        facsBsTxt = self.options_Qgb.facsBs_lineEdit.text()
        targetIndexFaceBlendshape = faceUtils.getBlendshapeTargetIndexDict(facsBsTxt)
        topModelGrp = cmds.ls('*.rigModelGrp', objectsOnly=True)[0]

        items = self.qtOptions.updateBsList_treeWidget.selectedItems()
        allExtracted = []
        if items:
            for item in items:
                target = item.text(0)
                index = targetIndexFaceBlendshape[target]
                extractedSculpt = cmds.sculptTarget(facsBsTxt, e=1, regenerate=1, target=index)
                if extractedSculpt:
                    if not cmds.ls('*.extractedFaceGrp'):
                        extractedFaceGrp = cmds.createNode('transform', n='*.extractedFaceGrp', p=topModelGrp)
                        cmds.addAttr(extractedFaceGrp, ln='extractedFaceGrp', dt='string')
                    else:
                        extractedFaceGrp = cmds.ls('*.extractedFaceGrp', objectsOnly=True)[0]
                    extractedSculpt = cmds.parent(extractedSculpt, extractedFaceGrp)[0]
                    extractedSculpt = cmds.rename(extractedSculpt, target)

                if not extractedSculpt:
                    extractedSculpt = cmds.listConnections(
                        '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputGeomTarget'.format(facsBsTxt,
                                                                                                              index),
                        source=True, plugs=False)[0]
                allExtracted.append(extractedSculpt)
        cmds.select(allExtracted, r=True)

    def createFACSblendshape(self):
        faceShapesList = [u'angryMouth', u'browSqzUp', u'chinDn', u'chinRaiser', u'chinTension', u'disgussMouth',
                          u'fearMouth', u'happyMouth',
                          u'headSkinSlide', u'lf_browSqz', u'lf_cheeckLower', u'lf_cheeckPuff', u'lf_cheeckRaiser',
                          u'lf_cheeckSuck', u'lf_dimpler',
                          u'lf_disgust', u'lf_eyeSqueeze', u'lf_eyeWideOpen', u'lf_innerBrowLower',
                          u'lf_innerBrowRaiser', u'lf_innerLowerLidUp',
                          u'lf_innerUpperLidDn', u'lf_lidTightener', u'lf_lipCornerPuller', u'lf_lipCornerThin',
                          u'lf_lipDepressoer', u'lf_lipNarrow',
                          u'lf_lipPucker', u'lf_lipStretch', u'lf_lipWide', u'lf_lowLidDn', u'lf_lowLidUp',
                          u'lf_lowerLipDn', u'lf_lowerLipFunneler',
                          u'lf_lowerLipSuck', u'lf_lowerO', u'lf_lwrLipCornerCorrective', u'lf_lwrLipThinner',
                          u'lf_mouthPuff', u'lf_neckTension',
                          u'lf_noseForrow', u'lf_nostrilDeep', u'lf_outterBrowLower', u'lf_outterBrowRaiser',
                          u'lf_outterUpperLidDn', u'lf_smile',
                          u'lf_upperLidDn', u'lf_upperLidDn_50', u'lf_upperLidUp', u'lf_upperLipCornerCorrective',
                          u'lf_upperLipDn',
                          u'lf_upperLipFunneler', u'lf_upperLipSuck', u'lf_upperLipThinner', u'lf_upperO', u'lipsApart',
                          u'lipsIn', u'lipsOut',
                          u'lipsPress', u'lipsTightener', u'lowerLipBack', u'lowerLipFwd', u'lowerLipLeft',
                          u'lowerLipRight', u'lowerMidLipDn',
                          u'mouthDn', u'mouthLeft', u'mouthPuff', u'mouthRight', u'mouthUp', u'neckMuscle',
                          u'noseCompress', u'noseDliator',
                          u'rt_browSqz', u'rt_cheeckLower', u'rt_cheeckPuff', u'rt_cheeckRaiser', u'rt_cheeckSuck',
                          u'rt_dimpler', u'rt_disgust',
                          u'rt_eyeSqueeze', u'rt_eyeWideOpen', u'rt_innerBrowLower', u'rt_innerBrowRaiser',
                          u'rt_innerLowerLidUp', u'rt_innerUpperLidDn',
                          u'rt_lidTightener', u'rt_lipCornerPuller', u'rt_lipCornerThin', u'rt_lipDepressoer',
                          u'rt_lipNarrow', u'rt_lipPucker',
                          u'rt_lipStretch', u'rt_lipWide', u'rt_lowLidDn', u'rt_lowLidUp', u'rt_lowerLipDn',
                          u'rt_lowerLipFunneler', u'rt_lowerLipSuck',
                          u'rt_lowerO', u'rt_lwrLipCornerCorrective', u'rt_lwrLipThinner', u'rt_mouthPuff',
                          u'rt_neckTension', u'rt_noseForrow',
                          u'rt_nostrilDeep', u'rt_outterBrowLower', u'rt_outterBrowRaiser', u'rt_outterUpperLidDn',
                          u'rt_smile', u'rt_upperLidDn',
                          u'rt_upperLidUp', u'rt_upperLipCornerCorrective', u'rt_upperLipDn', u'rt_upperLipFunneler',
                          u'rt_upperLipSuck',
                          u'rt_upperLipThinner', u'rt_upperO', u'upperLipBack', u'upperLipFwd', u'upperMidLipUpper',
                          u'jawOpen', u'surpriseMouth',
                          u'sadMouth', u'jawOpen_notReverted', u'lf_eyeDn', u'lf_eyeUp', u'lf_eyeRight', u'lf_eyeLeft',
                          u'rt_eyeLeft', u'rt_eyeRight',
                          u'rt_eyeUp', u'rt_eyeDn', u'jawClawching', u'rt_lipClose', u'lf_lipClose']

        faceMeshTxt = self.options_Qgb.faceMesh_lineEdit.text()
        if not faceMeshTxt or not cmds.objExists(faceMeshTxt):
            cmds.warning('no face mesh is set or it doesn\'t exist')
            return

        topModelGrp = cmds.ls('*.rigModelGrp', objectsOnly=True)[0]
        if not cmds.ls('.faceShapesModelGrp'):
            faceShapesModelGrp = cmds.createNode('transform', n='faceShapesModelGrp', p=topModelGrp)
            cmds.addAttr(faceShapesModelGrp, ln='faceShapesModelGrp', dt='string')
        else:
            faceShapesModelGrp = cmds.ls('*.faceShapesModelGrp', objectsOnly=True)[0]

        allNewShapes = []
        for faceShape in faceShapesList:
            newFace = cmds.duplicate(faceMeshTxt, n=faceShape)
            newFace = cmds.parent(newFace, faceShapesModelGrp)[0]
            allNewShapes.append(newFace)

        cmds.hide(allNewShapes)
        allNewShapes.append(faceMeshTxt)
        facsBlendshape = cmds.blendShape(allNewShapes, n='FACS_blendshape')[0]
        self.options_Qgb.facsBs_lineEdit.setText(facsBlendshape)

        self.updateFACSBlendshapeList()

    def template(self):
        '''
        define here the template rig you need to build your rig.
        Store the template controlers in self.templateControlers
        '''
        self.templateControlers = [None] * 2
        self.templateControlers[0] = cmds.createNode('joint', n=self.getNode() + '_root_template', p=self.templateGrp)
        self.templateControlers[1] = cmds.createNode('joint', n=self.getNode() + '_cog_template', p=self.templateGrp)
        cmds.setAttr(self.templateControlers[1] + '.translateY', 15)

    def defaultWidget(self):
        pass

    def rig(self):
        ''' well ...  '''

        assemblyAsset = cmds.ls('*.rigAssetName')[0].split('.')[0]
        prependName = cmds.getAttr(self.templateGrp + '.prependName')
        prependNameTxt = cmds.getAttr(self.templateGrp + '.prependNameTxt')
        preName = ''
        if prependName:
            preName = prependNameTxt

        scalable = cmds.getAttr(self.templateGrp + '.scalable')
        for axe in ['X', 'Y', 'Z']:
            cmds.setAttr("{}.scaleRig{}".format(self.rigDefaultNode, axe), 1)

        node = self.getNode()
        num = 4
        jnt = [None] * num
        sknJnt = [None] * num
        ctrls = [None] * num
        ctrls_grp = [None] * num

        for i in range(num):
            parentCtrl = None
            parentDirect = self.rigGrp
            position = self.templateControlers[0]
            if i:
                parentCtrl = ctrls[i - 1]
                parentDirect = jnt[i - 1]
            if i == 3:
                position = self.templateControlers[1]

            ctrlInfo = self.getInfoControl(self.controlers[i])
            ctrls_grp[i], ctrls[i] = rigUtils.control(name=preName + ctrlInfo[0], side=ctrlInfo[1], shape=ctrlInfo[2],
                                                      color=ctrlInfo[3], command=ctrlInfo[4], radius=ctrlInfo[7], \
                                                      axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6], parent=parentDirect,
                                                      position=position, rotation=position, \
                                                      lockAttr=['s', 'v'], hideAttr=['sx', 'sy', 'sz', 'v'], node=node,
                                                      parentCtrl=parentCtrl)
            jnt[i] = rigUtils.joint(position=position, name=preName + self.joints[self.controlers[i]][0],
                                    parent=ctrls[i], node=node, side=ctrlInfo[1], connectedCtrl=ctrls[i])
            sknJnt[i] = rigUtils.joint(position=position, name=preName + self.sknJnts[self.controlers[i]][0],
                                       parent=jnt[i], node=node, side=ctrlInfo[1], connectedCtrl=ctrls[i])

        for i in range(1, 4):
            rigUtils.setJointParent(jnt[i - 1], jnt[i])

        for joint in jnt + sknJnt:
            cmds.setAttr(joint + '.drawStyle', 2)

        # create scale
        if scalable:
            cmds.addAttr(ctrls[0], ln='scaleRig', at='double', dv=1)
            cmds.setAttr(ctrls[0] + '.scaleRig', e=True, keyable=True)
            for axe in ['X', 'Y', 'Z']:
                cmds.connectAttr(ctrls[0] + '.scaleRig', "{}.scaleRig{}".format(self.rigDefaultNode, axe))

        cmds.connectAttr(self.rigDefaultNode + '.scaleRig', self.rigGrp + '.scale')
        self.mayaControlers = ctrls

        self.setLastNode(jnt[-1])
        cmds.select(ctrls)
        cmds.refresh()

        return sknJnt
