.. _ml-quickstart:

Machine Learning Quickstart
---------------------------

This document is a short introduction to running privacy-preserving
logistic regression in MP-SPDZ. It assumes that you have the framework
already installed as explained in the `installation instructions
<https://mp-spdz.readthedocs.io/en/latest/readme.html#tl-dr-binary-distribution-on-linux-or-source-distribution-on-macos>`_.
For more information on how to run machine learning algorithms in MP-SPDZ,
see the `full machine learning section
<https://mp-spdz.readthedocs.io/en/latest/machine-learning.html>`_.

The easiest way to use is to put Python code in an ``.mpc`` in
``Programs/Source``, for example ``Programs/Source/foo.mpc``. Put the
following code there to use the breast cancer dataset::

  X = sfix.input_tensor_via(0, [[1, 2, 3], # 2 samples
                                [11, 12, 13]])
  y = sint.input_tensor_via(0, [0, 1]) # 2 labels

  from Compiler import ml
  log = ml.SGDLogistic(100)
  log.fit(X, y)

  print_ln('%s', log.predict(X).reveal())

The first two lines make the data available to the secure
computation. The next lines create a logistic regression instance and
train it (for one hundred epochs). Finally, the last line uses the
instances for predictions and outputs the results.

After adding all the above code to ``Programs/Source/foo.mpc``, you
can run it either insecurely:

.. code-block:: console

  Scripts/compile-emulate.py foo

or securely with three parties on the same machine:

.. code-block:: console

  Scripts/compile-run.py -E ring foo

The first call should give the following output:

.. code-block:: console

  $ Scripts/compile-emulate.py foo
  Default bit length for compilation: 63
  Default security parameter for compilation: 40
  Compiling file Programs/Source/foo.mpc
  Writing binary data to Player-Data/Input-Binary-P0-0
  Setting learning rate to 0.01
  Using SGD
  Initializing dense weights in [-1.224745,1.224745]
  Writing to Programs/Bytecode/foo-TruncPr(3)_47_16-2.bc
  Writing to Programs/Bytecode/foo-multithread-1.bc
  2 runs per epoch
  Writing to Programs/Bytecode/foo-TruncPr(1)_47_16-5.bc
  Writing to Programs/Bytecode/foo-Dense-forward-4.bc
  Writing to Programs/Bytecode/foo-TruncPr(1)_45_14-7.bc
  Writing to Programs/Bytecode/foo-exp2_fx(1)_31_16_False-9.bc
  Writing to Programs/Bytecode/foo-log2_fx(1)_31_16-11.bc
  Writing to Programs/Bytecode/foo-TruncPr(1)_46_15-13.bc
  Writing to Programs/Bytecode/foo-Output-forward-6.bc
  Writing to Programs/Bytecode/foo-multithread-15.bc
  Writing to Programs/Bytecode/foo-multithread-16.bc
  Writing to Programs/Bytecode/foo-TruncPr(3)_46_15-18.bc
  Writing to Programs/Bytecode/foo-multithread-17.bc
  Initializing dense weights in [-1.224745,1.224745]
  Writing to Programs/Bytecode/foo-multithread-19.bc
  Writing to Programs/Bytecode/foo-TruncPr(2)_47_16-22.bc
  Writing to Programs/Bytecode/foo-multithread-21.bc
  Writing to Programs/Bytecode/foo-multithread-23.bc
  Writing to Programs/Bytecode/foo-Dense-forward-20.bc
  Writing to Programs/Bytecode/foo-FPDiv(1)_31_16-24.bc
  Writing to Programs/Schedules/foo.sch
  Writing to Programs/Bytecode/foo-0.bc
  Hash: 8227349c6796977e0035cd9e925585603531eb9aa98ac586440c1abd360ae712
  Program requires at most:
  8 integer inputs from player 0
  2402 integer opens
  67654 integer bits
  204509 integer triples
  200 matrix multiplications (1x3 * 3x1)
  200 matrix multiplications (3x1 * 1x1)
  1 matrix multiplications (2x3 * 3x1)
  37109 virtual machine rounds
  Compilation finished, running program...
  Using statistical security parameter 40
  Trying to run 64-bit computation
  Using SGD
  done with epoch 99
  [0, 1]
  The following benchmarks are including preprocessing (offline phase).
  Time = 0.0390132 seconds 

See `the documentation
<https://mp-spdz.readthedocs.io/en/latest/readme.html#running-computation>`_
for further
options such as different protocols or running remotely and `the
machine learning section
<https://mp-spdz.readthedocs.io/en/latest/machine-learning.html>`_ for
other machine learning methods.
