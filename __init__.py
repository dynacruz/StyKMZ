# -*- coding: utf-8 -*-
def classFactory(iface):
    from .stykmz import StyKMZ
    return StyKMZ(iface)
