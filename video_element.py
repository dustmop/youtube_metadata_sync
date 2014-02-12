#!/usr/bin/env python

"""VideoElement plain old data."""


class VideoElement(object):
  def __init__(self):
    self.title = None
    self.description = None
    self.published = None
    self.timestamp = None
    self.video_id = None
    self.safename = None
    self.url = None
    self.length = None

  def to_json(self):
    return {'title':self.title,
            'description': self.description,
            'published': self.published,
            'timestamp': self.timestamp,
            'video_id': self.video_id,
            'safename': self.safename,
            'url': self.url,
            'length': self.length}

  def __str__(self):
    return str(self.to_json())
