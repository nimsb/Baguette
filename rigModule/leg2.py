from __future__ import absolute_import
from maya import cmds
from . import nodeBase, simpleIk, foot
from ..utils import rigUtils
import os
from operator import add
from ..utils.Qt import QtCompat, QtWidgets

fileUi = os.path.dirname(os.path.abspath(__file__)) + '/legWidgetOptions.ui'


class Leg2Widget(simpleIk.SimpleIkWidget):
    def __init__(self, parent=None):
        super(Leg2Widget, self).__init__(parent)

        self.footWidget = foot.FootWidget()
        self.footWidget.controlers = self.footWidget.controlers[2:]

        self.controlers = self.controlers + self.footWidget.controlers
        self.initiateMayaNodes(self.controlers)

    # 	def addControlers(self):
    # 		super(Leg2Widget, self).addControlers()

    def addData(self):
        super(Leg2Widget, self).addData()

        self.footWidget.controlers = self.controlers
        self.footWidget.templateGrp = self.templateGrp
        self.footWidget.initialName(self.getNode())
        self.footWidget.addData()

    def updateKnee(self, state):
        super(Leg2Widget, self).updateKnee(state)

    def updateNumTwist(self, value):
        super(Leg2Widget, self).updateNumTwist(value)

    def options(self):
        super(Leg2Widget, self).options()
        self.qtOptions.doubleJoint_ckb.setText('double Knee')

        self.qtOptions.ikTmpRot_widget.setVisible(False)

    def template(self):
        super(Leg2Widget, self).template()

        self.footWidget.template(self.getNode() + 'Foot')
        cmds.delete(self.templateControlers[2])
        self.templateControlers[2] = cmds.parent(self.footWidget.templateControlers[0], self.templateControlers[1])[0]

        self.templateControlers = self.templateControlers + self.footWidget.templateControlers[1:]

    def defaultWidget(self):
        super(Leg2Widget, self).defaultWidget()

    def rig(self):
        # set manually the self.rigGrp here
        rigUtils.snapTranslation(self.templateControlers[0], self.rigGrp)

        listFootControlers = [self.controlers[0]] + self.controlers[4:]
        self.footWidget.controlers = self.controlers
        self.footWidget.initiateMayaNodes(self.controlers)
        self.footWidget.templateGrp = self.templateGrp
        self.footWidget.initialName(self.getNode())
        isDoubleKnee = cmds.getAttr(self.templateGrp + '.doubleJoint')
        num = 2
        if isDoubleKnee:
            num = 3

        self.footWidget.templateControlers = self.templateControlers[num:]

        footRigSknJnt = self.footWidget.rig(listControlers=[self.controlers[0]] + self.controlers[4:])
        footIk = self.footWidget.mayaControlers[2]
        attributSettingShape = self.footWidget.attributeShape
        endJnts = self.footWidget.startJnts
        ballLiftCtrl = self.footWidget.ballLiftCtrl
        simpleIkRigSknJnt = super(Leg2Widget, self).rig(mainIk=footIk, attributSettingShape=attributSettingShape, \
                                                        endJnts=endJnts, ballLiftCtrl=ballLiftCtrl, rigGrpPos=None)

        simpleIkRigSknJnt.insert(num + 1, footRigSknJnt[1])
        if isDoubleKnee:
            # we put the knee at the end to keep the order and the skinning from the knee to the kneeBis
            simpleIkRigSknJnt.append(simpleIkRigSknJnt.pop(1))

        return simpleIkRigSknJnt
