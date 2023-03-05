from __future__ import absolute_import
from maya import cmds
from . import nodeBase, simpleIk, foot
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets
from six.moves import range

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/legWidgetOptions.ui'


class Arm2Widget(simpleIk.SimpleIkWidget):
    def __init__(self, parent=None):
        super(Arm2Widget, self).__init__(parent)

        self.controlers = ['HandIk', 'ElbowPv', 'ClavicleIk', 'Shoulder', 'Elbow', 'HandFk']
        self.initiateMayaNodes(self.controlers)

    # 	def addControlers(self):
    # 		super(Arm2Widget, self).addControlers()

    def addData(self):
        super(Arm2Widget, self).addData()
        self.setControlerShape('HandIk', 'cube', 7, axe='x')
        self.setControlerShape('ElbowPv', 'cube', 7, axe='x', radius=0.2)
        self.setControlerShape('ClavicleIk', 'cube', 7, axe='x')
        self.setControlerShape('Shoulder', 'circle', 14, axe='x')
        self.setControlerShape('Elbow', 'circle', 14, axe='x')
        self.setControlerShape('HandFk', 'circle', 14, axe='x')

        cmds.setAttr(self.templateGrp + '.orientationX', 1)
        cmds.setAttr(self.templateGrp + '.orientationY', 0)
        cmds.setAttr(self.templateGrp + '.orientationZ', 0)
        cmds.setAttr(self.templateGrp + '.reverseOrientation', 0)

    def updateKnee(self, state):
        super(Arm2Widget, self).updateKnee(state)

    def updateNumTwist(self, value):
        super(Arm2Widget, self).updateNumTwist(value)

    def options(self):
        super(Arm2Widget, self).options()
        self.qtOptions.doubleJoint_ckb.setText('double Elbow')

    def template(self):
        # super(Arm2Widget, self).template()

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
        self.setLastNode(self.joints[self.controlers[4]][0])
        # reorder templateCtrl order to match simpleIk.rig()
        self.templateControlers.append(self.templateControlers.pop(0))

    def defaultWidget(self):
        super(Arm2Widget, self).defaultWidget()

    def rig(self):
        templateControlers = eval(cmds.getAttr(self.templateGrp + '.isTemplate'))
        sknJnts = super(Arm2Widget, self).rig(fkIncrement=True, rigGrpPos=templateControlers[0])

        ### adding clavicle on the simpleIk.rig() ###
        node = self.getNode()
        clavicleJnt = cmds.duplicate(self.parentBaseJnt, po=True)[0]
        cmds.delete(cmds.pointConstraint(self.templateControlers[-1], clavicleJnt))

        if self.positionCenter >= -0.001:
            cmds.delete(cmds.aimConstraint(self.parentBaseJnt, clavicleJnt, aim=(1, 0, 0), u=(0, 0, 1), wut='object',
                                           wuo=self.templateControlers[2]))
        else:
            cmds.delete(cmds.aimConstraint(self.parentBaseJnt, clavicleJnt, aim=(-1, 0, 0), u=(0, 0, -1), wut='object',
                                           wuo=self.templateControlers[2]))

        ctrlInfo = self.getInfoControl(self.controlers[2])
        clavicleCtrlGrp, clavicleCtrl = rigUtils.control(name=self.preName + ctrlInfo[0], side=ctrlInfo[1],
                                                         shape=ctrlInfo[2], color=ctrlInfo[3], command=ctrlInfo[4],
                                                         radius=ctrlInfo[7], \
                                                         axeShape=ctrlInfo[5], grpOffsets=ctrlInfo[6],
                                                         parent=self.rigGrp, position=clavicleJnt, rotation=clavicleJnt,
                                                         node=node, \
                                                         lockAttr=['s'], hideAttr=['sx', 'sy', 'sz', 'v'])
        cmds.parent(self.attributeShape, clavicleCtrl, add=True, s=True)
        cmds.parent([self.parentBaseJnt, self.mainIkGrp, self.startBase], clavicleCtrl)

        clavicleRigJnt = rigUtils.joint(position=clavicleJnt, orientation=clavicleJnt,
                                        name='{}{}_0_jnt'.format(self.preName, self.controlers[2]), \
                                        parent=clavicleCtrl, node=node, typeJnt='', side=ctrlInfo[1],
                                        radius=ctrlInfo[7] * 0.5, connectedCtrl=clavicleCtrl)
        clavicleSknJnt = rigUtils.joint(position=clavicleJnt, orientation=clavicleJnt,
                                        name='{}{}_0_sknJnt'.format(self.preName, self.controlers[2]), \
                                        parent=clavicleRigJnt, node=node, typeJnt='sknJnt', side=ctrlInfo[1],
                                        radius=ctrlInfo[7] * 0.5, connectedCtrl=clavicleCtrl)
        cmds.setAttr(clavicleRigJnt + '.drawStyle', 2)

        # set one jnt hierarchy and ctrl tags parent
        rigUtils.setJointParent(clavicleRigJnt, self.rigJnt[0])
        rigUtils.setCtrlParent(clavicleCtrl, self.ikCtrl[0])
        rigUtils.setCtrlParent(clavicleCtrl, self.fkCtrl[0])

        # clean
        cmds.delete(clavicleJnt)

        # keep order from previous arm module
        sknJnts.insert(0, clavicleSknJnt)

        # add to all mayaControlers to set the tag ctrl
        self.mayaControlers.append(clavicleCtrl)

        return sknJnts
