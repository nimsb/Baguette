from __future__ import absolute_import
from . import itemGraphic
from ..rigModule import nodeBase, main, spine, head, leg, leg2, quadLeg, quadLeg2, foot, arm, arm2, hand, \
    oneJoint, twoJointIk, simpleIk, spaceSwitch, chain, chainRibbon, faceOneJoint, faceMain

MayaNodes = {}


def getMayaNodes(force=False, mainPath=""):
    '''
    All nodes will go into MayaNodes
    Make sure to add least one category node for each list.
    '''

    myPath = mainPath + "/src/images/"
    rigPresetPath = mainPath + "/rigPreset/"

    if MayaNodes and not force:
        return MayaNodes

    MayaNodes["a_mainNode"] = itemGraphic.NodeBase(
        dictKey="a_mainNode",
        displayText="Main",
        imagePath=myPath + "mainNodeIcon.svg",
        description="MAIN :\nCreate the base of any rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=main.MainWidget,
        path=myPath,
    )

    # 	MayaNodes["b_spineNode"] = itemGraphic.NodeBase(
    # 		dictKey = "b_spineNode",
    # 		displayText = "Spine",
    # 		imagePath = myPath+"spineNodeIcon.svg",
    # 		description = "SPINE :\nCreate a spine rig",
    # 		listWidgetName = "createRigList",
    # 		nodeType = "rigmodule",
    # 		widgetMenu = spine.SpineWidget,
    # 		path=myPath,
    # 	)

    MayaNodes["c_headNode"] = itemGraphic.NodeBase(
        dictKey="c_headNode",
        displayText="Head",
        imagePath=myPath + "headNodeIcon.svg",
        description="HEAD :\nCreate a head rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=head.HeadWidget,
        path=myPath,
    )

    # 	MayaNodes["d_legNode"] = itemGraphic.NodeBase(
    # 		dictKey = "d_legNode",
    # 		displayText = "Leg",
    # 		imagePath = myPath+"legNodeIcon.svg",
    # 		description = "OLD LEG :\nDEPRECATED",
    # 		listWidgetName = "createOldList",
    # 		nodeType = "rigmodule",
    # 		widgetMenu = leg.LegWidget,
    # 		path=myPath,
    # 	)

    MayaNodes["d_leg2Node"] = itemGraphic.NodeBase(
        dictKey="d_leg2Node",
        displayText="Leg",
        imagePath=myPath + "legNodeIcon.svg",
        description="LEG :\nCreate a leg rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=leg2.Leg2Widget,
        path=myPath,
    )

    MayaNodes["da_foot"] = itemGraphic.NodeBase(
        dictKey="da_foot",
        displayText="Foot",
        imagePath=myPath + "footNodeIcon.svg",
        description="Foot :\nCreate a foot rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=foot.FootWidget,
        path=myPath,
    )

    # 	MayaNodes["d_quadLegNode"] = itemGraphic.NodeBase(
    # 		dictKey = "d_quadLegNode",
    # 		displayText = "QuadLeg",
    # 		imagePath = myPath+"quadLegNodeIcon.svg",
    # 		description = "OLD QUAD LEG :\nDEPRECATED",
    # 		listWidgetName = "createOldList",
    # 		nodeType = "rigmodule",
    # 		widgetMenu = quadLeg.QuadLegWidget,
    # 		path=myPath,
    # 	)

    MayaNodes["d_quadLeg2Node"] = itemGraphic.NodeBase(
        dictKey="d_quadLeg2Node",
        displayText="QuadLeg",
        imagePath=myPath + "quadLegNodeIcon.svg",
        description="QUAD LEG :\nCreate a quad leg rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=quadLeg2.QuadLeg2Widget,
        path=myPath,
    )

    MayaNodes["e_armNode"] = itemGraphic.NodeBase(
        dictKey="e_armNode",
        displayText="Arm",
        imagePath=myPath + "armNodeIcon.svg",
        description="OLD ARM :\nDEPRECATED",
        listWidgetName="",
        nodeType="rigmodule",
        widgetMenu=arm.ArmWidget,
        path=myPath,
    )

    MayaNodes["e_arm2Node"] = itemGraphic.NodeBase(
        dictKey="e_arm2Node",
        displayText="Arm",
        imagePath=myPath + "armNodeIcon.svg",
        description="ARM :\nCreate a arm rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=arm2.Arm2Widget,
        path=myPath,
    )

    MayaNodes["f_handNode"] = itemGraphic.NodeBase(
        dictKey="f_handNode",
        displayText="Hand",
        imagePath=myPath + "handNodeIcon.svg",
        description="HAND :\nCreate a hand rig with fingers",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=hand.HandWidget,
        path=myPath,
    )

    MayaNodes["g_oneJointNode"] = itemGraphic.NodeBase(
        dictKey="g_oneJointNode",
        displayText="One",
        imagePath=myPath + "oneNodeIcon.svg",
        description="ONE JOINT :\nCreate a one joint rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=oneJoint.OneJointWidget,
        path=myPath,
    )

    MayaNodes["g_twoJointIkNode"] = itemGraphic.NodeBase(
        dictKey="g_twoJointIkNode",
        displayText="TwoJointIk",
        imagePath=myPath + "twoJointIkNodeIcon.svg",
        description="TWO JOINT IK :\nCreate a two joint rig with an IK and a aim constraint",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=twoJointIk.TwoJointIkWidget,
        path=myPath,
    )

    MayaNodes["g_simpleIk"] = itemGraphic.NodeBase(
        dictKey="g_simpleIk",
        displayText="SimpleIk",
        imagePath=myPath + "simpleIkNodeIcon.svg",
        description="SIMPLE IK :\nCreate 3 joint rig with an IK/FK system",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=simpleIk.SimpleIkWidget,
        path=myPath,
    )

    MayaNodes["h_chainNode"] = itemGraphic.NodeBase(
        dictKey="h_chainNode",
        displayText="Chain",
        imagePath=myPath + "chainNodeIcon.svg",
        description="CHAIN :\nCreate a FK chain rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=chain.ChainWidget,
        path=myPath,
    )

    MayaNodes["i_chainRibbonNode"] = itemGraphic.NodeBase(
        dictKey="i_chainRibbonNode",
        displayText="Ribbon",
        imagePath=myPath + "ribbonNodeIcon.svg",
        description="RIBBON CHAIN :\nCreate a FK chain rig",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=chainRibbon.ChainRibbonWidget,
        path=myPath,
    )

    MayaNodes["a_spaceSwitch"] = itemGraphic.NodeBase(
        dictKey="a_spaceSwitch",
        displayText="Space",
        imagePath=myPath + "spaceNodeIcon.svg",
        description="SPACE SWITCH :\nCreate a space switching between nodes",
        listWidgetName="createRigList",
        nodeType="rigmodule",
        widgetMenu=spaceSwitch.SpaceSwitchWidget,
        path=myPath,
    )

    MayaNodes["a_biped"] = itemGraphic.NodeBase(
        dictKey="a_biped",
        displayText="Biped",
        imagePath=myPath + "bodyPresetIcon.svg",
        description="BIPED : Create full biped rig",
        listWidgetName="createPresetList",
        nodeType="rigpreset",
        widgetMenu="",
        path=rigPresetPath,
    )

    MayaNodes["a_face"] = itemGraphic.NodeBase(
        dictKey="a_face",
        displayText="Face",
        imagePath=myPath + "headNodeIcon.svg",
        description="FACE : Create full face rig",
        listWidgetName="createPresetList",
        nodeType="rigpreset",
        widgetMenu="",
        path=rigPresetPath,
    )

    # MayaNodes["b_quadriped"] = itemGraphic.NodeBase(
    #     dictKey="b_quadriped",
    #     displayText="Quad",
    #     imagePath=myPath + "quadPresetIcon.svg",
    #     description="QUADRIPED : Create full quadriped rig",
    #     listWidgetName="createPresetList",
    #     nodeType="rigpreset",
    #     widgetMenu="",
    #     path=rigPresetPath,
    # )
    # 	MayaNodes["c_car"] = itemGraphic.NodeBase(
    # 		dictKey = "c_car",
    # 		displayText = "Car",
    # 		imagePath = myPath+"carPresetIcon.svg",
    # 		description = "CAR : Create full car rig",
    # 		listWidgetName = "createPresetList",
    # 		nodeType = "rigpreset",
    # 		widgetMenu = "",
    # 		path=rigPresetPath,
    # 	)
    # MayaNodes["d_plane"] = itemGraphic.NodeBase(
    #     dictKey="d_plane",
    #     displayText="Plane",
    #     imagePath=myPath + "planePresetIcon.svg",
    #     description="PLANE : Create full plane rig",
    #     listWidgetName="createPresetList",
    #     nodeType="rigpreset",
    #     widgetMenu="",
    #     path=rigPresetPath,
    # )
    MayaNodes["a_faceMainNode"] = itemGraphic.NodeBase(
        dictKey="a_faceMainNode",
        displayText="Main",
        imagePath=myPath + "faceMainNodeIcon.svg",
        description="MAIN :\nCreate the base of any face rig",
        listWidgetName="createFaceList",
        nodeType="rigmodule",
        widgetMenu=faceMain.FaceMainWidget,
        path=myPath,
    )
    MayaNodes["g_faceOneJointNode"] = itemGraphic.NodeBase(
        dictKey="g_faceOneJointNode",
        displayText="One",
        imagePath=myPath + "faceOneNodeIcon.svg",
        description="ONE JOINT :\nCreate a one face joint rig",
        listWidgetName="createFaceList",
        nodeType="rigmodule",
        widgetMenu=faceOneJoint.FaceOneJointWidget,
        path=myPath,
    )

    return MayaNodes
