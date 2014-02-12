#!/usr/bin/env python

"""Execute plugins using the local metadata."""

import os
import shutil
import subprocess
import tempfile

import json

import file_util


PLUGINS_DIRECTORY = 'plugins'


class ExecutePlugins(object):
  def __init__(self):
    self.plugin_list = None
    self.plugin_script = None
    self.current_directory = os.getcwd()
    fp = open('plugin_config.cfg', 'r')
    content = fp.read()
    fp.close()
    self.plugin_list = json.loads(content).get(PLUGINS_DIRECTORY)
    file_util.mkdir_p(PLUGINS_DIRECTORY)
    for script in os.listdir(PLUGINS_DIRECTORY):
      if os.access(os.path.join(PLUGINS_DIRECTORY, script), os.X_OK):
        self.plugin_script = os.path.abspath(
          os.path.join(PLUGINS_DIRECTORY, script))
      else:
        sys.stderr.write(('Plugin script found at "%s", ' +
                          'but it is not executable\n') % script)
      break

  def execute(self, metadata):
    """Execute matching plugins for all local metadata."""
    output_directory = metadata.output_directory
    feeds = metadata.get_metadata_feeds()
    for filename in feeds:
      self._process_metadata_file(filename, metadata, output_directory)

  def _process_metadata_file(self, filename, metadata, output_directory):
    """Execute plugins for the given file or metadata."""
    data = metadata.deserialize_feed(filename)
    for i,meta in enumerate(data):
      if 'status' in meta:
        continue
      retval = self._run_plugin(meta, output_directory)
      if retval:
        data[i]['status'] = retval
        metadata.serialize_feed(filename, data)

  def _run_plugin(self, meta, output_directory):
    """Run the configured plugins for the given metadata object."""
    retval = None
    if (not self.plugin_list or not isinstance(self.plugin_list, list) or
        not self.plugin_script):
      return False
    for plugin in self.plugin_list:
      # Plugin API still in development.
      if (plugin.get('script') != '*' or
          plugin.get('condition') != 'executable' or
          plugin.get('save_as') != '${safename}' or
          plugin.get('defaults') != True):
        continue
      # Create the command to run.
      command = plugin.get('command')
      command = command.replace('${script}', self.plugin_script)
      command = command.replace('${url}', meta['url'])
      # Make temporary directory, execute script within it.
      temp_directory = tempfile.mkdtemp()
      os.chdir(temp_directory)
      outcode = subprocess.call(command, shell=True)
      # Find output the script may have created.
      script_output = None
      for output_file in os.listdir('.'):
        script_output = os.path.abspath(output_file)
        break
      # Command completed.
      os.chdir(self.current_directory)
      if outcode != 0:
        retval = 'failed'
      elif script_output:
        # Rename output and move it to the files directory.
        ext = os.path.splitext(script_output)[1]
        target = os.path.join(output_directory, 'files', meta['safename'] + ext)
        file_util.mkdir_p(os.path.dirname(target))
        shutil.move(script_output, target)
        retval = 'success'
      # Cleanup temporary directory.
      shutil.rmtree(temp_directory)
    return retval

