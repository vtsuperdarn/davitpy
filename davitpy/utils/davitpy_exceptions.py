class DavitpyNoFoundError(Exception):
    """
    Davitpy Exception for when there is not data found in the database or given.

    Parameters
    ----------
    msg : message for the error [string]
        Make it detailed.

    Author: Marina Schmidt 20180312
    """
    def __init__(self,msg):
        self.message=msg
        Exception.__init__(self, self.message)

class DavitpyTimeRangeError(Exception):
    """
    Davitpy exception when time recorded in the file is not within range
    of the specified time for the file.

    Parameters
    ----------
    msg: message of the error [string]

    Author: Marina Schmidt 20180313
    """
    def __init__(self,msg):
        self.message=msg
        Exception.__init__(self, self.message)
