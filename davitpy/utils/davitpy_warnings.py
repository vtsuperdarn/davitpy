class DavitpyTimeRangeWarning(Warning):
    """
    Davitpy warning when time recorded in the file is not within range
    of the specified time for the file.

    Parameters
    ----------
    msg: message of the error [string]

    Author: Marina Schmidt 20180313
    """
    def __init__(self,msg):
        self.message=msg
        Warning.__init__(self, self.message)
