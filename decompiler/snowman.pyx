    
# ------------------------------------------------------------------------------
# PROTOTYPES
# ------------------------------------------------------------------------------

cdef extern const char* snowman_decompile(char *filename, char *function)

# ------------------------------------------------------------------------------
# MODULE-LEVEL FUNCTONS
# ------------------------------------------------------------------------------
def decompile(filename, function):
    ret = snowman_decompile(filename, function)
    return ret

