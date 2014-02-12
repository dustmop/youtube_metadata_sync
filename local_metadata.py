#!/usr/bin/env python

"""Represents local metadata synchronized from the user's Youtube account.

Files on disk will live in the following directory structure:

output_directory/
  data/
    favorites/
      feed.json
    playlist_1/
      feed.json
    playlist_2/
      feed.json
  ...

Where each feed.json file will have the following structure:

[
  {
    "description": "The description.",
    "title": "Video Title as Displayed",
    "url": "http://youtube.com/watch?v=XXXXXXXXXXX",
    "timestamp": 1234567890,
    "video_id": "XXXXXXXXXXX",
    "safename": "video-title-as-displayed-XXXXXXXXXXX",
    "published": "2009-02-13T18:31:30.000Z",
    "length": 123
  },
  ...
]
"""

import errno
import os
import sys

import json

import file_util


class LocalMetadata(object):
  def __init__(self, output_directory, verbose=None):
    self.output_directory = output_directory
    self.verbose = verbose
    self.account = None
    self.feed_name = None
    self.target = None
    self.current_metadata = None

  def create_init(self, account):
    """Create initial local metadata. If it already exists, warn and delete."""
    self.account = account
    if os.path.isdir(self.output_directory):
      if not self._warning_accepted():
        return
    unused_num_added = self._sync_metadata(quiet=False, initialize=True)

  def synchronize(self, account, quiet=False):
    """Update existing local metadata, and return number of new items."""
    self.account = account
    if not self.verbose is None:
      quiet = self.verbose
    return self._sync_metadata(quiet, initialize=False)

  def get_metadata_feeds(self):
    """Return list of paths to local metadata json files."""
    feeds = []
    feed_directories = os.listdir(os.path.join(self.output_directory, 'data'))
    for item in feed_directories:
      directory = os.path.join(self.output_directory, 'data', item)
      if not os.path.isdir(directory):
        continue
      feeds.append(os.path.join(directory, 'feed.json'))
    feeds.sort()
    return feeds

  def serialize_feed(self, filename, data):
    """Serialize the metadata to the given filename."""
    fp = open(filename, 'w')
    fp.write(json.dumps(data, indent=2, separators=(',', ': ')))
    fp.close()

  def deserialize_feed(self, filename):
    """Deserialize the metadata from the given filename."""
    try:
      fp = open(filename, 'r')
    except IOError:
      e = sys.exc_info()[1]
      if e.errno == errno.ENOENT:
        return []
      else:
        raise
    content = fp.read()
    fp.close()
    return json.loads(content)

  def _sync_metadata(self, quiet, initialize):
    num_added = 0
    etag_cache = self._load_etag_cache()
    for playlist in self.account.get_all_playlists():
      self._set_current_metadata(playlist['title'], playlist['directory'],
                                 initialize)
      timestamp = self._most_recent_timestamp()
      if not quiet:
        sys.stderr.write('Getting playlist "%s"\n' % playlist['title'])
      videos = self.account.get_playlist_videos(playlist['playlist_id'],
                                                min_timestamp=timestamp,
                                                etag_cache=etag_cache)
      self._save_etag_cache(etag_cache)
      if videos is None:
        if not quiet:
          sys.stderr.write('No changes to "%s"\n' % playlist['title'])
        continue
      num_added += self._add_to_current_metadata(videos, quiet)
    return num_added

  def _save_etag_cache(self, etag_cache):
    path = os.path.join(self.output_directory, 'data', 'etags.json')
    fp = open(path, 'w')
    fp.write(json.dumps(etag_cache, indent=2, separators=(',', ': ')))
    fp.close()

  def _load_etag_cache(self):
    path = os.path.join(self.output_directory, 'data', 'etags.json')
    try:
      fp = open(path, 'r')
    except IOError:
      e = sys.exc_info()[1]
      if e.errno == errno.ENOENT:
        return {}
      else:
        raise
    content = fp.read()
    fp.close()
    return json.loads(content)

  def _set_current_metadata(self, title, feed_directory, initialize):
    self.feed_name = title
    self.target = os.path.join(self.output_directory, 'data', feed_directory,
                               'feed.json')
    file_util.mkdir_p(os.path.dirname(self.target))
    if initialize:
      self.current_metadata = []
    else:
      self.current_metadata = self.deserialize_feed(self.target)

  def _add_to_current_metadata(self, videos, quiet):
    if len(videos) == 0:
      if not quiet:
        sys.stderr.write('No new elements for "%s", has %d elements\n' % (
            self.feed_name, len(self.current_metadata)))
      return 0
    if not quiet:
      sys.stderr.write('Adding %d elements to "%s", had %d elements\n' % (
          len(videos), self.feed_name, len(self.current_metadata)))
    self.current_metadata = ([v.to_json() for v in videos] +
                             self.current_metadata)
    self.serialize_feed(self.target, self.current_metadata)
    return len(videos)

  def _most_recent_timestamp(self):
    if len(self.current_metadata) > 0:
      return self.current_metadata[0]['timestamp']

  def _warning_accepted(self):
    message = """Output directory '%s' already found. Running init will
clear existing metadata and download it again. Modifications that have been
made to the metadata, such as by plugins, will be lost. Are you sure you
want to do this? [Y/n] """ % self.output_directory
    sys.stdout.write(message)
    try:
      answer = raw_input()
    except NameError:
      answer = input()
    if answer == 'Y':
      return True
    return False
