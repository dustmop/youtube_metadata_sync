#!/usr/bin/env python

"""Obfuscator for the client_secrets.

This is a completely insecure obfuscator for the clients_secrets file. It is
used only to fight against the temptation to simply copying the secrets and
reuse them for some other Youtube API project. Please do not do this, instead
create your own client_secrets, it's not that difficult."""

import os
import sys
import tempfile


class SecretObfuscator(object):
  def __init__(self):
    self.temp_pathname = None

  def make_cleartext(self, obfuscated_file):
    (handle, self.temp_pathname) = tempfile.mkstemp()
    fout = os.fdopen(handle, 'w')
    fp = open(obfuscated_file, 'r')
    unused_line = fp.readline()
    content = fp.read()
    fp.close()
    for byte in content:
      byte = chr(ord(byte) - 1)
      fout.write(byte)
    fout.close()
    return self.temp_pathname

  def cleanup(self):
    os.unlink(self.temp_pathname)
    self.temp_pathname = None

  def make_obfuscated(self, cleartext_file):
    fout = sys.stdout
    fp = open(cleartext_file, 'r')
    content = fp.read()
    fp.close()
    for byte in content:
      byte = chr(ord(byte) + 1)
      fout.write(byte)
