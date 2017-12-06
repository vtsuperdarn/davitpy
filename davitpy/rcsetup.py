# -*- coding: utf-8 -*-
"""The rcsetup module.

The rcsetup module contains the default values and the validation code for
customization using davitpy's rc settings.

Each rc setting is assigned a default value and a function used to validate
any attempted changes to that setting. The default values and validation
functions are defined in the rcsetup module, and are used to construct the
rcParams global object which stores the settings and is referenced throughout
davitpy.

These default values should be consistent with the default davitpyrc file
that actually reflects the values given here. Any additions or deletions to
the parameter set listed here should also be visited to the :file:`davitpyrc`
in davitpy's root source directory.

"""


import six
import os
import warnings


class ValidateInStrings(object):
    """Class used to validate strings in rcParams.

    This class builds a validator that can be used to check whether a string
    is a valid option with :func:`davitpy.rcParams.validate`.

    Example
    -------
    Build a validator for the "swallow" option.

    >>> validate_swallows = ValidateInStrings('swallow',
                                              ['african','european'],
                                              ignorecase=True)

    """


    def __init__(self, key, valid, ignorecase=False):
        """Initialize the ValidInStrings validator.

        Parameters
        ----------
        key : str
            The option in rcParams being validated.
        valid : List[str]
            A list of "legal" values for `key`.
        ignorecase : Optional[bool]
            Specifies is case-sensitive validator.

        """
        self.key = key
        self.ignorecase = ignorecase

        def func(s):
            if ignorecase:
                return s.lower()
            else:
                return s
        self.valid = dict([(func(k), k) for k in valid])


    def __call__(self, s):
        if self.ignorecase:
            s = s.lower()
        if s in self.valid:
            return self.valid[s]
        raise ValueError('Unrecognized %s string "%s": valid strings are %s'
                         % (self.key, s, list(six.itervalues(self.valid))))


def validate_any(s):
    return s


def validate_path_exists(s):
    """If s is a path, return s, else False"""
    if s is None:
        return None
    if os.path.exists(s):
        return s
    else:
        raise RuntimeError('"%s" should be a path but it does not exist' % s)


def validate_bool(b):
    """Convert b to a boolean or raise"""
    if isinstance(b, six.string_types):
        b = b.lower()
    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True):
        return True
    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False):
        return False
    else:
        raise ValueError('Could not convert "%s" to boolean' % b)


def validate_bool_maybe_none(b):
    'Convert b to a boolean or raise'
    if isinstance(b, six.string_types):
        b = b.lower()
    if b is None or b == 'none':
        return None
    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True):
        return True
    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False):
        return False
    else:
        raise ValueError('Could not convert "%s" to boolean' % b)


def validate_float(s):
    """convert s to float or raise"""
    try:
        return float(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float' % s)


def validate_string(s):
    """convert s to string or raise"""
    try:
        return str(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to string' % s)


def validate_float_or_None(s):
    """convert s to float or raise"""
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float' % s)


def validate_int(s):
    """convert s to int or raise"""
    try:
        return int(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to int' % s)


_seq_err_msg = ('You must supply exactly {n:d} values, you provided '
                '{num:d} values: {s}')

_str_err_msg = ('You must supply exactly {n:d} comma-separated values, '
                'you provided '
                '{num:d} comma-separated values: {s}')


class validate_nseq_float(object):

    def __init__(self, n):
        self.n = n

    def __call__(self, s):
        """return a seq of n floats or raise"""
        if isinstance(s, six.string_types):
            s = s.split(',')
            err_msg = _str_err_msg
        else:
            err_msg = _seq_err_msg

        if len(s) != self.n:
            raise ValueError(err_msg.format(n=self.n, num=len(s), s=s))

        try:
            return [float(val) for val in s]
        except ValueError:
            raise ValueError('Could not convert all entries to floats')


class validate_nseq_int(object):

    def __init__(self, n):
        self.n = n

    def __call__(self, s):
        """return a seq of n ints or raise"""
        if isinstance(s, six.string_types):
            s = s.split(',')
            err_msg = _str_err_msg
        else:
            err_msg = _seq_err_msg

        if len(s) != self.n:
            raise ValueError(err_msg.format(n=self.n, num=len(s), s=s))

        try:
            return [int(val) for val in s]
        except ValueError:
            raise ValueError('Could not convert all entries to ints')


def validate_stringlist(s):
    'return a list'
    if isinstance(s, six.string_types):
        return [six.text_type(v.strip()) for v in s.split(',') if v.strip()]
    elif type(s) in (list, tuple):
        return [six.text_type(v) for v in s if v]
    else:
        msg = "'s' must be of type [ string | list | tuple ]"
        raise ValueError(msg)


validate_verbose = ValidateInStrings(
    'verbose',
    ['silent', 'helpful', 'debug', 'debug-annoying'])


# determine install location of model coefficients
path = os.path.split(os.path.dirname(__file__))[0]
model_coeffs_dir = os.path.join(path, 'tables/')

if not os.path.exists(model_coeffs_dir):
    print "WARNING, location of model coefficients could not be determined!"
    print model_coeffs_dir


# a map from key -> value, converter
defaultParams = {
    'AACGM_DAVITPY_DAT_PREFIX':	[model_coeffs_dir + 'aacgm/aacgm_coeffs-12-',
                                 validate_string],
    'IGRF_DAVITPY_COEFF_FILE':	[model_coeffs_dir + 'igrf/igrf12coeffs.txt',
                                 validate_string],
    'DAVITPY_PATH':             [path, validate_path_exists],

    # the verbosity setting for logging
    #'verbose.level': ['silent', validate_verbose],
    #'verbose.fileo': ['sys.stdout', six.text_type],

    # sftp address and user info for data fetching
    'DB':			['sd-data.ece.vt.edu', validate_string],
    'DBREADUSER':		['sd_dbread', validate_string],
    'DBREADPASS':		['5d', validate_string],
    'DB_PORT':			['22', validate_string],
    # database
    'SDDB':			['sd-work9.ece.vt.edu:27017', validate_string],
    'SDBREADUSER':		['sd_dbread', validate_string],
    'SDBREADPASS':		['5d', validate_string],
    'DBWRITEUSER':		['', validate_string],
    'DBWRITEPASS':		['', validate_string],
    # temporary directory
    'DAVIT_TMPDIR':		['/tmp/sd/', validate_string],
    # radar data file fetching
    'DAVIT_REMOTE_DIRFORMAT':	['data/{year}/{ftype}/{radar}/',
                               validate_string],
    'DAVIT_REMOTE_FNAMEFMT':	['{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}', validate_string],
    'DAVIT_LOCAL_DIRFORMAT':	['/sd-data/{year}/{ftype}/{radar}/',
                              validate_string],
    'DAVIT_LOCAL_FNAMEFMT':	['{date}.{hour}......{radar}.{ftype},{date}.{hour}......{radar}.{channel}.{ftype}', validate_string],
    'DAVIT_REMOTE_TIMEINC':	['2', validate_string],
    'DAVIT_LOCAL_TIMEINC':	['2', validate_string],
    # map file fetching
    'DAVIT_SD_REMOTE_DIRFORMAT': ['data/{year}/{ftype}/{hemi}/', validate_string],
    'DAVIT_SD_REMOTE_FNAMEFMT':	['{date}.{hemi}.{ftype}', validate_string],
    'DAVIT_SD_LOCAL_DIRFORMAT':	['/sd-data/{year}/{ftype}/{hemi}/',
                                 validate_string],
    'DAVIT_SD_LOCAL_FNAMEFMT':	['{date}.{hemi}.{ftype}', validate_string],
    'DAVIT_SD_REMOTE_TIMEINC':	['24', validate_string],
    'DAVIT_SD_LOCAL_TIMEINC':	['24', validate_string],
    'verbosity':                ['helpful',validate_verbose]
}


if __name__ == '__main__':
    rc = defaultParams
    rc['datapath'][0] = '/'
    for key in rc:
        if not rc[key][1](rc[key][0]) == rc[key][0]:
            print("%s: %s != %s" % (key, rc[key][1](rc[key][0]), rc[key][0]))
