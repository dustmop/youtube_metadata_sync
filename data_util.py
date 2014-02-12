#!/usr/bin/env python

"""Utilities for manipulating metadata."""

import datetime
import time
import re


def normalize_name(title):
  accum = ''
  for ch in title.lower():
    if ord(ch) > 127:
      accum += ('--x%x' % ord(ch))
    elif ch in ['/', ':', ' ']:
      accum += '-'
    elif ch in ['(', ')']:
      pass
    else:
      accum += ch
  if len(accum) > 200:
    accum = accum[0:200]
  return accum


def create_timestamp(text):
  dt = datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.000Z')
  return int(time.mktime(dt.timetuple()))


def convert_youtube_time_to_sec(duration):
  m = re.match(r'^PT((\d)H)?((\d\d?)M)?((\d\d?)S)?$', duration)
  if not m:
    return 0
  hour = int(m.group(2)) if m.group(2) else 0
  minute = int(m.group(4)) if m.group(4) else 0
  second = int(m.group(6)) if m.group(6) else 0
  length = second + 60 * (minute + 60 * hour)
  return length
