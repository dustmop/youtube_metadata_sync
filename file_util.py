#!/usr/bin/env python

"""Utilites for filesystem."""

import errno
import os
import sys


def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError:
    e = sys.exc_info()[1]
    if e.errno == errno.EEXIST:
      pass
    else:
      raise
