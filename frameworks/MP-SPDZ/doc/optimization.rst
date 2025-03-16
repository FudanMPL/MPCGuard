Compiler Optimizations
======================

A core tenet of MP-SPDZ is to reduce the number of communication
rounds by parallelizing operations. The are two mechanisms for this,
called merging and CISC. Merging is the more basic mechanism, doing
just round reduction and nothing else. CISC in addition uses
vectorization, which reduces the cost during compilation and the
footprint. In the following, we will explain the two mechanisms using
examples.


Merging
-------

Merging is the original mechanism forming the basis for `Keller et
al. <https://eprint.iacr.org/2013/143>`_ It is based on extending the
common three-operand instruction design to any number of argument
tuples. Consider the following high-level code::

  sint(1) * sint(2)
  sint(3) * sint(4)

Putting this into ``Programs/Source/2mul.py`` and running
``./compile.py 2mul -a debug`` results in the following content in
``debug-2mul-0``::

  # 2mul-0--0
  ldsi s2, 1 # 0
  ldsi s3, 2 # 1
  ldsi s4, 3 # 2
  ldsi s5, 4 # 3
  muls 8, 1, s0, s2, s3, 1, s1, s4, s5 # 4

You can see all the inputs loaded in the first few lines appear in the
last one. The arguments are follows (see also
:py:class:`Compiler.instructions.muls`): 8 indicates the number of
arguments to follow, and every four arguments correspond to one
multiplication. The first number withing every four arguments is the
vector size, following by the result register and the input
registers.

On the backend side, the multiplication is implemented in the
:cpp:func:`muls` member function in
:download:`../Processor/Processor.hpp`. Notice that
``protocol.exchange()`` (where the communication happens) is only
called once. See :ref:`low-level` for more information.

Within the compiler, the optimization is executed in the
:py:class:`Merger` class in :download:`../Compiler/allocator.py`. The
:py:func:`dependency_graph` member function builds a dependency graph
for all instructions, and instructions are merged in
:py:func:`longest_path_merge`.


CISC
----

This mechanism takes its name from `Complex Instruction Set Computer
<https://en.wikipedia.org/wiki/Complex_instruction_set_computer>`_,
which refers to the fact that more complex operations are treated as
instructions internally before being merged and spelled in vectorized
instructions. For a simple example, consider the following high-level
code::

  program.use_trunc_pr = True
  sfix(1) * sfix(2)
  sfix(3) * sfix(4)

The resulting file ``debug-2fmul-0`` starts similarly to the one
above::

  # 2fmul-0-cisc-1
  ldsi s8, 65536 # 0
  ldsi s9, 131072 # 1
  ldsi s10, 196608 # 2
  ldsi s11, 262144 # 3
  muls 8, 1, s0, s8, s9, 1, s7, s10, s11 # 4

This corresponds to the fact that fixed-point multiplication starts
with an integer multiplication before truncation. The file continues
as follows::

  # 2fmul-0--2
  concats 5, s3(2), 1, s0, 1, s7 # 5
  vmovs 2, s3(2), s3(2) # 6
  # 2fmul-0-update-3
  jmp 11 # 7

The first instruction creates a vector of size from the multiplication
results, and the last instruction jumps over the next code block just
to end up here::

  # 2fmul-0-end-TruncPr(2)_47_16-5
  ldint ci0, 3 # 19
  stmint ci0, 8192 # 20
  jmp -14 # 21

This code prepares for a function call. Functions are used for code
reusability, i.e., the same code only has to be compiled once per tape
and vector size. The last instruction jumps to the start of the
function here (the code block jumped over above)::

  # 2fmul-0-begin-TruncPr(2)_47_16-4
  ldarg ci1 # 8
  vldi 2, c0(2), 32768 # 9
  vmulci 2, c2(2), c0(2), 2147483647 # 10
  vaddci 2, c0(2), c2(2), 32768 # 11
  vaddm 2, s5(2), s3(2), c0(2) # 12
  vtrunc_pr 2, 4, s3(2), s5(2), 47, 16 # 13
  vsubsi 2, s5(2), s3(2), 1073741824 # 14
  vmovs 2, s3(2), s5(2) # 15
  vmovs 2, s1(2), s3(2) # 16
  ldmint ci1, 8192 # 17
  jmpi ci1 # 18

The actual truncation happens in the vectorized instructions starting
with v. The only communication-relevant instruction is (v)trunc_pr,
where truncation by 16 bits is done via a protocol defined in the
virtual machine. For example, the implementation for Rep3 is found in
:download:`../Protocols/Replicated.hpp`. The other vectorized
instructions are required to turn negative values into positive ones,
which is a precondition for the protocol. See Protocol in 3.1 in
`Catrina and Saxena <https://www.ifca.ai/pub/fc10/31_47.pdf>`_ for an
explanation. Lastly, the last two instructions load where to jump back
to, which is here::

  # 2fmul-0-call-TruncPr(2)_47_16-6
  picks s0, s1(2), 0, 1 # 22
  picks s0, s1(2), 1, 1 # 23

The two instructions extract the results from the vector, which makes
them available individually for further computation.

While this example saves relatively little by using the CISC
functionality, this isn't the case for other usages. For example,
removing ``program.use_trunc_pr`` results in several hundred
instructions, and more involved mathematical functions corresponds to
thousands of instructions.

Internally, the CISC functionality is in implemented in functions
decorators in :download:`../Compiler/instructions_base.py`. Our
example uses :py:func:`ret_cisc` on :py:func:`TruncPr` in
:download:`../Compiler/floatingpoint.py`. This is because
:py:func:`TruncPr` returns an :py:class:`sint`. Other decorators are
:py:func:`cisc` (the result is stored in the first argument, which
must be an :py:class:`sint`) and :py:func:`sfix_cisc` (the result and
all arguments are instances of :py:class:`sfix`).
