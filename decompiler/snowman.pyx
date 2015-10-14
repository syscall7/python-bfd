    
# ------------------------------------------------------------------------------
# PROTOTYPES
# ------------------------------------------------------------------------------

cdef extern int snowman_decompile(char *filename, char *function)

# ------------------------------------------------------------------------------
# MODULE-LEVEL FUNCTONS
# ------------------------------------------------------------------------------
def decompile(filename, function):
    print 'About to decompile function %s from %s' % (function, filename)
    snowman_decompile(filename, function)

