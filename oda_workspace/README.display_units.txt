A Display Unit represents a contiguous sequence of bytes that can be uniformly displayed.  The Display Unit can be
commented and labeled.

class DisplayUnit
  prop address   // absolute virtual memory address
  prop rawBytes  // the sequence of raw bytes that make up the display unit
  prop section   // name of the section in which it is found
  prop comment   // user comment (or NULL)
  prop label     // user label (or NULL)

class InstrDisplayUnit : inherits DisplayUnit
  prop opcode    // instruction mnemonic
  prop operands  // instruction operands
  prop funcStart // TRUE if this instruction begins a function
  prop funcEnd   // TRUE if this instruction ends a function

class DataDisplayUnit : inherits DisplayUnit
  prop type      // type of data
  prop num       // number of elements (if greater than 1, than this is an array of the given type)
