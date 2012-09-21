# profileUtils
"""
*******************************
        PROFILEUTILS
*******************************
This subpackage is a wrapper for cProfile
DEV: functions/modules/classes with a * have not been developed yet

*******************************
"""
import cProfile
import pstats

def run(fun):
    """
Run and display a profile of the function FUN

INPUT:
    fun: function to be profiled in quotes
OUTPUT:
    p: pstat output
    """
    from os import remove
    
    # Generate profile
    cProfile.run(fun,'funprof')
    # Read profile
    p = pstats.Stats('funprof')
    pOut = p
    # Print profile in the most useful format
    p.strip_dirs().sort_stats('cumulative').print_callees()
    # Remove temp file
    remove('funprof')
    
    return pOut