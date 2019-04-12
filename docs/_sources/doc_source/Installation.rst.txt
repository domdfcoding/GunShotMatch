.. _chapter01:

************
Installation
************

.. contents:: Table of Contents


GunShotMatch is a Python_ program for analysis of Organic GunShot Residue.
Some of its functionality depends on other Python libraries,
such as 'NumPy_' (the Python library for numerical computing),
or 'Matplotlib_' (the Python library for plotting).
In general, GunShotMatch is available for all operating systems.

.. _Python: https://www.python.org/
.. _NumPy: http://www.numpy.org/
.. _Matplotlib: https://matplotlib.org/

There are several ways to install GunShotMatch depending your computer
configuration and personal preferences. These installation
instructions assume that Python is already installed and can be
invoked with the ``python3`` command. Modify the instructions
given if your Python installation is invoked with a different
command, such as ``py`` on Windows.

Installation with pip
======================

GunShotMatch depends on the following packages:

.. literalinclude:: ../requirements.txt

The recommended installation method is to use ``pip`` with the following command:

.. code-block:: bash

    $ python3 -m pip --user install -r requirements.txt

or:

.. code-block:: bash

    $ python3 -m pip --user install sklearn, numpy, pandas, openpyxl, matplotlib, scipy, PyMassSpec

Additionally, GunShotMatch requires wxPython. Use the following commands to install it:

Windows and macOS
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ python3 -m pip --user install wxPython

Linux
^^^^^^^^

.. code-block:: bash

    $ python3 -m pip --user install \
        -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 \
        wxPython

