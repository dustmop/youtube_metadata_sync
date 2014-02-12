#!/usr/bin/env python

"""Frontend for Youtube Metadata Sync."""


import sys

import execute_plugins
import local_metadata
import user_account


def usage():
  print("""Usage: python youtube_metadata_sync.py [command] [-o [output]] [-v] [-a]
  Commands:
      init     Initialize your metadata repository.
      update   Sync and execute any plugins.
      sync     Synchronize new metadata since the last run.
      execute  Run plugins for any items with no status attribute.
  Options:
   -o output   Output directory.
   -v          Verbose logging.
   -a          Skip authentication flow, just use existing auth.json.
""")
  sys.exit(1)


class CommandLine(object):
  def __init__(self):
    self.output = None
    self.command = None
    self.verbose = None
    self.authenticated = False


def get_command_line(args):
  cmdline = CommandLine()
  i = 0
  while i < len(args):
    if args[i] == '-o':
      i += 1
      cmdline.output = args[i]
    elif args[i] == '-v':
      cmdline.verbose = True
    elif args[i] == '-a':
      cmdline.authenticated = True
    else:
      cmdline.command = args[i]
    i += 1
  if not cmdline.output or not cmdline.command:
    usage()
  return cmdline


def run():
  cmdline = get_command_line(sys.argv[1:])
  account = user_account.UserAccount()
  if cmdline.command == 'init':
    if not cmdline.authenticated:
      account.authenticate()
    account.connect()
    metadata = local_metadata.LocalMetadata(cmdline.output, cmdline.verbose)
    metadata.create_init(account)
  elif cmdline.command == 'update':
    account.connect()
    metadata = local_metadata.LocalMetadata(cmdline.output, cmdline.verbose)
    num_added = metadata.synchronize(account, quiet=True)
    if num_added > 0:
      print('Sync found %d new videos.' % (num_added,))
    executor = execute_plugins.ExecutePlugins()
    executor.execute(metadata)
  elif cmdline.command == 'sync':
    account.connect()
    metadata = local_metadata.LocalMetadata(cmdline.output, cmdline.verbose)
    num_added = metadata.synchronize(account, quiet=False)
    if num_added > 0:
      print('Sync found %d new videos.' % (num_added,))
  elif cmdline.command == 'execute':
    metadata = local_metadata.LocalMetadata(cmdline.output, cmdline.verbose)
    executor = execute_plugins.ExecutePlugins()
    executor.execute(metadata)
  else:
    raise RuntimeError('Uknown command %s' % args[0])


if __name__ == '__main__':
  run()
