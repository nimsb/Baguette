"""Ikfk class for ikfk switching.

"""

# Python Libraries.
from __future__ import absolute_import
import math
import logging
import os

# Maya Libraries.
from maya import cmds
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
from six.moves import range
from six.moves import zip

# Setup Logging
LOGGER = logging.getLogger('rigAPI')


def get_vector(node):
    return om.MVector(*cmds.xform(node, q=True, t=True, ws=True))


def get_xyz_list(vec):
    return (vec.x, vec.y, vec.z)


def get_matrix(obj):
    return om2.MMatrix(cmds.xform(obj, q=True, matrix=True, ws=True))


def get_pole_vector(p1, p2, p3):
    startPos = get_vector(p1)
    midPos = get_vector(p2)
    endPos = get_vector(p3)
    startV = endPos - startPos
    midV = midPos - startPos
    dotP = midV * startV
    startN = startV.normal()
    projV = startN * float(dotP) / float(startV.length())
    arrowV = midV - projV
    pvVec = arrowV + midPos
    nVec = pvVec - midPos
    nVec = nVec * (startV.length() / nVec.length())
    vec = nVec + midPos

    return vec


class Ikfk(object):

    def __init__(self):
        super(Ikfk, self).__init__()

        self.ik_vis = True
        self.fk_vis = True

        self.start_frame = int(cmds.playbackOptions(q=True, min=True))
        self.end_frame = int(cmds.playbackOptions(q=True, max=True))

        self._get_controls()

    def _set_visibility(self):
        curr = cmds.currentTime(q=True)
        selections = cmds.ls(os=True, fl=True)
        if not selections:
            cmds.warning('rigAPI: IkFk attribute not found. Aborting...')
            return

        else:
            selections = selections[-1]

        ikvAttr = '{}.ikControls'.format(selections)
        fkvAttr = '{}.fkControls'.format(selections)

        ik_vis = self.state
        fk_vis = not (self.state)

        cmds.setAttr(ikvAttr, ik_vis)
        cmds.setAttr(fkvAttr, fk_vis)

    def _get_controls(self):
        # Check selection.
        selections = cmds.ls(os=True, fl=True)
        if not selections:
            cmds.warning('rigAPI: IkFk attribute not found. Aborting...')
            return

        else:
            selections = selections[-1]

        ikfkAttr = cmds.ls('{}.IkFk'.format(selections))

        if not ikfkAttr:
            cmds.warning('rigAPI: IkFk attribute not found. Aborting...')
            return
        self.state = cmds.getAttr(ikfkAttr)

        self.sNode = ikfkAttr[-1].rsplit('.', 1)[0]
        msgList = [uda for uda in cmds.listAttr(self.sNode, ud=True)
                   if cmds.attributeQuery(uda, n=self.sNode, at=True) == 'message']

        for msg in msgList:
            attr = '{}.{}'.format(self.sNode, msg)
            if not cmds.ls(attr):
                cmds.warning('rigAPI: {} attribute is missing. Aborting...'.format(msg))
                return
            ctrl = cmds.listConnections(attr)[0]
            globals()[msg] = ctrl

        # Query ik group and attribute.
        self.ikGrp = cmds.listRelatives(ikCtrl, p=True)[0]
        self.ikAttr = cmds.ls('{}.IkFk'.format(ikCtrl))[0]

    def switch_fk_to_ik(self):
        # fk to ik
        # Get Rotation values.
        currPos = cmds.xform(ikCtrl, q=True, t=True, ws=True)
        pos = cmds.xform(endFkCtrl, q=True, t=True, ws=True)

        ikMatrix = get_matrix(ikCtrl)
        ikjMatrix = get_matrix(endIkJnt)
        fkMatrix = get_matrix(endFkCtrl)
        cmds.xform(self.ikGrp, matrix=ikjMatrix, ws=True)
        cmds.xform(ikCtrl, matrix=ikMatrix, ws=True)
        cmds.xform(self.ikGrp, matrix=fkMatrix, ws=True)
        cmds.xform(ikCtrl, t=pos, ws=True)

        finPos = cmds.xform(ikCtrl, q=True, rp=True, ws=True)
        finRot = cmds.xform(ikCtrl, q=True, ro=True, ws=True)

        cmds.xform(self.ikGrp, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.xform(ikCtrl, t=finPos, ro=finRot, ws=True)

        # Get Pivot Position.
        pvpos = get_xyz_list(get_pole_vector(startFkCtrl, midFkCtrl, endFkCtrl))
        cmds.xform(pvCtrl, t=pvpos, ws=True)
        cmds.setAttr(self.ikAttr, 0.0)
        self._set_visibility()

    def swtich_ik_to_fk(self):
        # ik to fk
        for fkCtrl, ikJnt in zip([startFkCtrl, midFkCtrl, endFkCtrl],
                                 [startIkJnt, midIkJnt, endIkJnt]):
            fkGrp = cmds.listRelatives(fkCtrl, p=True)[0]
            ikjMatrix = cmds.xform(ikJnt, q=True, matrix=True, ws=True)
            cmds.xform(fkGrp, matrix=ikjMatrix, ws=True)
            cmds.xform(fkCtrl, ro=(0, 0, 0))

            mat = cmds.xform(fkCtrl, q=True, matrix=True, ws=True)
            cmds.xform(fkGrp, ro=(0, 0, 0))
            cmds.xform(fkCtrl, matrix=mat, ws=True)

        cmds.setAttr(self.ikAttr, 1.0)
        self._set_visibility()

    def bake_to_ik(self, frame):
        # bake fk to ik
        cmds.currentTime(frame)
        pos = cmds.xform(endFkCtrl, q=True, t=True, ws=True)
        ikMatrix = get_matrix(ikCtrl)
        ikjMatrix = get_matrix(endIkJnt)
        fkMatrix = get_matrix(endFkCtrl)
        cmds.xform(self.ikGrp, matrix=ikjMatrix, ws=True)
        cmds.xform(ikCtrl, matrix=ikMatrix, ws=True)
        cmds.xform(self.ikGrp, matrix=fkMatrix, ws=True)
        cmds.xform(ikCtrl, t=pos, ws=True)
        finPos = cmds.xform(ikCtrl, q=True, rp=True, ws=True)
        finRot = cmds.xform(ikCtrl, q=True, ro=True, ws=True)
        cmds.xform(self.ikGrp, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.xform(ikCtrl, t=finPos, ro=finRot, ws=True)

        # Get Pivot Position.
        pvpos = get_xyz_list(get_pole_vector(startFkCtrl, midFkCtrl, endFkCtrl))
        cmds.xform(pvCtrl, t=pvpos, ws=True)
        cmds.setAttr(self.ikAttr, 0.0)
        cmds.setKeyframe(ikCtrl, t=frame, dd=True)
        cmds.setKeyframe(pvCtrl, t=frame, dd=True)
        cmds.setKeyframe(self.ikAttr, t=frame)

        cmds.filterCurve(ikCtrl)

    def bake_to_fk(self, frame):
        # bake ik to fk
        cmds.currentTime(frame)
        shoulderVal = cmds.xform(startIkJnt, q=True, ro=True)
        elbowVal = cmds.xform(midIkJnt, q=True, ro=True)
        wristVal = cmds.xform(endIkJnt, q=True, ro=True)

        for fkCtrl, ikJnt in zip([startFkCtrl, midFkCtrl, endFkCtrl],
                                 [startIkJnt, midIkJnt, endIkJnt]):
            fkGrp = cmds.listRelatives(fkCtrl, p=True)[0]

            ikjMatrix = cmds.xform(ikJnt, q=True, matrix=True, ws=True)
            cmds.xform(fkGrp, matrix=ikjMatrix, ws=True)
            cmds.xform(fkCtrl, ro=(0, 0, 0))
            mat = cmds.xform(fkCtrl, q=True, matrix=True, ws=True)
            cmds.xform(fkGrp, ro=(0, 0, 0))
            cmds.xform(fkCtrl, matrix=mat, ws=True)
            cmds.setAttr(self.ikAttr, 1.0)

            cmds.setKeyframe(fkCtrl, t=frame)
            cmds.setKeyframe(self.ikAttr, t=frame)

        cmds.filterCurve(fkCtrl)

    def bake_fk_to_ik(self, smart=True):
        skeys = cmds.keyframe(startFkCtrl, q=True)
        mkeys = cmds.keyframe(midFkCtrl, q=True)
        ekeys = cmds.keyframe(endFkCtrl, q=True)

        if not skeys or not mkeys or not ekeys:
            cmds.warning(
                'cannot bake to all IK if all controlers : {} {} {} don\'t have a key'.format(startFkCtrl, midFkCtrl,
                                                                                              endFkCtrl))
            return

        keys = list(set(skeys + mkeys + ekeys))

        try:
            cmds.refresh(su=True)
            cmds.undoInfo(ock=True)

            if not smart:
                for i in range(self.start_frame, self.end_frame + 1):
                    self.bake_to_ik(frame=i)
            else:
                for i in keys:
                    self.bake_to_ik(frame=i)

            cmds.undoInfo(cck=True)
            cmds.refresh(su=False)

        except ValueError as ve:
            LOGGER.error(ve)
            cmds.undoInfo(cck=True)
            cmds.refresh(su=False)

        cmds.dgdirty(a=True)
        self._set_visibility()

    def bake_ik_to_fk(self, smart=True):
        ikeys = cmds.keyframe(ikCtrl, q=True)
        pkeys = cmds.keyframe(pvCtrl, q=True)

        if not ikeys or not pkeys:
            cmds.warning('cannot bake to all FK if all controlers : {} {} don\'t have a key'.format(ikCtrl, pvCtrl))
            return

        keys = list(set(ikeys + pkeys))

        try:
            cmds.refresh(su=True)
            cmds.undoInfo(ock=True)

            if not smart:
                for i in range(self.start_frame, self.end_frame + 1):
                    self.bake_to_fk(frame=i)

            else:
                for i in keys:
                    self.bake_to_fk(frame=i)

            cmds.refresh(su=False)
            cmds.undoInfo(cck=True)

        except ValueError as ve:
            LOGGER.error(ve)
            cmds.undoInfo(cck=True)
            cmds.refresh(su=False)

        cmds.dgdirty(a=True)
        self._set_visibility()

    def ikfk(self):
        if not hasattr(self, 'state'):
            return

        if self.state:
            self.switch_fk_to_ik()

        elif not self.state:
            self.swtich_ik_to_fk()

        else:
            cmds.warning('rigAPI: Conditions are not met to perform ikfk switch. Aborting...')
            return
        cmds.dgdirty(a=True)
        LOGGER.info('ikfk switching complete.')
