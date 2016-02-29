# -*- coding: utf-8 -*-
def sigObjCheck(vtsig):
    """Determines if the called signal is a vt sig or a vt sigStruct object.

    Parameters
    ----------
    vtsig

    Returns
    -------
    sigobj : vt sigStruct object

    """
    if hasattr(vtsig, 'data'):
        sigobj = vtsig
        vtsid = sigobj.parent
    else:
        sigobj = vtsig.active
    return sigobj


def prepForProc(vtsig):
    """Determines if the called signal is a vt sig or a vt sigStruct object.
    If it is a vt sig object, the active vtsig.active sigStruct object is
    returned. The signal is truncated to its current valid time limits if
    necessary. This also sets the called sigStruct to be the active sigStruct.

    Parameters
    ----------
    vtsig

    Returns
    -------
    sigobj : vt sigStruct object

    """
    sigobj = sigObjCheck(vtsig)

    # Remove times that are not valid.
    sigobj = sigobj.truncate()
    sigobj.setActive()
    return sigobj
