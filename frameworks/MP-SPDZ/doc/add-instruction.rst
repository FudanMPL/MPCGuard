Adding an Instruction
---------------------

If you want to add functionality that isn't captured by the current
virtual machine design, you might need to add further
instructions. This section explains how the virtual machine is built
on both the frontend (Python) and the backend (C++).


Frontend
========

The instructions are defined as classes in
:download:`../Compiler/instructions.py` and
:download:`../Compiler/GC/instructions.py`. Every class requires the
attributes :py:obj:`opcode` and :py:obj:`arg_format` to be
set. Consider the example of :py:class:`~Compiler.instructions.prefixsums`::

  @base.vectorize
  class prefixsums(base.Instruction):
    """ Prefix sum.

    :param: result (sint)
    :param: input (sint)

    """
    __slots__ = []
    code = base.opcodes['PREFIXSUMS']
    arg_format = ['sw','s']

:py:obj:`opcode` is set from :py:obj:`opcodes` in
:download:`../Compiler/instructions_base.py`. This is simply for
convenience as it allow copying from the C++ code (see below). The
only requirement for opcodes is that they are unique 10-bit integers.

:py:obj:`arg_format` has to be iterable over strings indicating the
nature of arguments. In the example, ``sw`` indicates that a secret
integer register is written to, and ``s`` indicates that a secret
integer register is read from. :py:obj:`ArgFormats` defines all
possible argument types::

  ArgFormats = {
    'c': ClearModpAF,
    's': SecretModpAF,
    'cw': ClearModpAF,
    'sw': SecretModpAF,
    'cg': ClearGF2NAF,
    'sg': SecretGF2NAF,
    'cgw': ClearGF2NAF,
    'sgw': SecretGF2NAF,
    'ci': ClearIntAF,
    'ciw': ClearIntAF,
    '*': AnyRegAF,
    '*w': AnyRegAF,
    'i': ImmediateModpAF,
    'ig': ImmediateGF2NAF,
    'int': IntArgFormat,
    'long': LongArgFormat,
    'p': PlayerNoAF,
    'str': String,
    'varstr': VarString,
  }

The values of this dictionary are classes defined in
:download:`../Compiler/instructions_base.py` which can encode them
into bytes to written to the bytecode files. Most types are encoded as
four-byte values except ``long``, which uses eight bytes, and
``varstr``, which has a variable length. The type classes also define
functionality to check arguments for correctness such as Python type.

By default, register arguments are understood as single registers. The
:py:obj:`vectorize` decorator is an easy way to allow vector arguments
if all register arguments have the same length. The vector size is
stored independently of the arguments. The decorator creates two
instructions, a base version for single registers and a vectorized
version, which is called as follows in the example for length
:py:obj:`n`::

  vprefixsums(n, result, operand)

At the higher level, the vector length is usually derived from the
input using the :py:obj:`vectorize` decorator as in
:py:func:`~Compiler.types.sint.prefix_sum`::

  @vectorize
  def prefix_sum(self):
      """ Prefix sum. """
      res = sint()
      prefixsums(res, self)
      return res

All instruction classes should inherit from :py:obj:`Instruction` in
:download:`../Compiler/instructions_base.py`.


Backend
=======

.. default-domain:: cpp

The backend functionality has three aspects:

1. Parsing the bytecode and creating an internal representation
2. Figuring out the resource requirements of the instruction
   (registers and memory)
3. Execution


Parsing
~~~~~~~

The internal representation is done via the :cpp:class:`Instruction`
class defined in :download:`../Processor/Instruction.h`. The arguments
are parsed in :cpp:func:`parse_operands` defined in
:download:`../Processor/Instruction.hpp`. It contains a large switch
statement covering all opcodes. Sticking to the example of
:py:class:`~Compiler.instructions.prefixsums`, the relevant code there
is as follows::

  case PREFIXSUMS:
    ...
    get_ints(r, s, 2);
    break;

This puts the two integer values corresponding to the two arguments
into ``r[0]`` and ``r[1]`` within the :cpp:class:`Instruction`
object. :cpp:member:`r` is an array of four 32-bit integers, which is
enough for many simple instructions. More complex instruction use
:cpp:member:`start`, which is a variable-length C++ vector of 32-bit
integers.


Resourcing
~~~~~~~~~~

Because the number of registers depends on the programs, the virtual
machine has to find out the requirements for every single
instruction. The main function for this is :cpp:func:`get_max_reg` in
:download:`../Processor/Instruction.hpp`, which returns the maximum
register that is written to for a particular register type. It
contains two switch statements. The first one contains special
treatment for instructions that write to more than one register type
such as :py:class:`~Compiler.instructions.dabit`. However, for most
instruction including :py:class:`~Compiler.instructions.prefixsums`,
it checks the type currently queried against the type defined by
:cpp:func:`get_reg_type` and returns 0 if there is a
mismatch. :cpp:func:`get_reg_type` makes use of the fact that the
opcodes are grouped. For :py:class:`prefixsums`, it returns ``SINT``,
which is the default.

The second switch statement then treats further special cases
where :cpp:class:`start` is used or `r` contains registers of
different types. None of this applies for :py:class:`prefixsums`, so
the return value is simply the maximum over :cpp:member:`r` and
:cpp:member:`start` plus the vector size::

  unsigned res = 0;
  for (auto x : start)
    res = max(res, (unsigned)x);
  for (auto x : r)
	res = max(res, (unsigned)x);
  return res + size;


Execution
~~~~~~~~~

Execution is again defined by several switch statements over the
opcode, the outermost of which is in :py:func:`Program::execute`
defined in :download:`../Processor/Instruction.hpp`. It uses the `X
macro <https://en.wikipedia.org/wiki/X_macro>`_ pattern for a compact
representation. :py:class:`~Compiler.instructions.prefixsums` is
implemented in :download:`../Processor/instructions.h` as follows::

  X(PREFIXSUMS, auto dest = &Procp.get_S()[r[0]]; auto op1 = &Procp.get_S()[r[1]]; \
    sint s, \
    s += *op1++; *dest++ = s) \

This macro has three arguments: the opcode, the setup step, and vector
loop step. The setup step involves getting pointers according to the
register addresses ``r[0]`` and ``r[1]`` as well as initializing a
running variable. The loop step then adds the next input element to
the running variable and stores in the destination.

Another important switch statement is in
:cpp:member:`Instruction::execute`. See :ref:`execution` for further
examples.
