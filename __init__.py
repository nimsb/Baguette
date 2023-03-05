from __future__ import absolute_import
from . import nodeGui, version
from .nodeGui import show
from six.moves import reload_module

__all__ = ['show', 'nodeGui']
__version__ = version.__version__

def reload_package():
    """force all files in package to reload"""
    from . import nodeGui
    nodeGui.close()

    from .utils import Qt
    from .ui import graphicsModule
    from .ui import mayaNodesList
    from .ui import itemGraphic
    from .ui import userListModule
    from .ui import geo
    from .ui import mayaShelf
    from .utils import rigUtils
    from .utils import faceUtils
    from .utils import ikfk
    from .utils import shelfBase
    from .rigModule import nodeBase
    from .rigModule import main
    from .rigModule import spine
    from .rigModule import head
    from .rigModule import leg
    from .rigModule import quadLeg
    from .rigModule import simpleIk
    from .rigModule import foot
    from .rigModule import arm
    from .rigModule import arm2
    from .rigModule import hand
    from .rigModule import oneJoint
    from .rigModule import twoJointIk
    from .rigModule import spaceSwitch
    from .rigModule import chain
    from .rigModule import chainRibbon
    from .rigModule import quadLeg2
    from .rigModule import leg2
    from .rigModule import faceOneJoint
    from .rigModule import faceMain

    reload_module(version)
    reload_module(Qt)
    reload_module(graphicsModule)
    reload_module(nodeGui)
    reload_module(mayaNodesList)
    reload_module(itemGraphic)
    reload_module(userListModule)
    reload_module(geo)
    reload_module(nodeBase)
    reload_module(rigUtils)
    reload_module(faceUtils)
    reload_module(ikfk)
    reload_module(shelfBase)
    reload_module(mayaShelf)
    reload_module(main)
    reload_module(spine)
    reload_module(head)
    reload_module(leg)
    reload_module(quadLeg)
    reload_module(simpleIk)
    reload_module(foot)
    reload_module(arm)
    reload_module(arm2)
    reload_module(hand)
    reload_module(oneJoint)
    reload_module(twoJointIk)
    reload_module(spaceSwitch)
    reload_module(chain)
    reload_module(chainRibbon)
    reload_module(quadLeg2)
    reload_module(leg2)
    reload_module(faceOneJoint)
    reload_module(faceMain)

    nodeGui.show()
