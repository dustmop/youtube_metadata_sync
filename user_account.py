#!/usr/bin/env python

"""Wraps the Youtube API to make it trivial to use."""

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

import data_util
import secret_obfuscator
import video_element


AUTHENTICATION_FILE = 'auth.json'
CLIENT_SECRETS_FILE = 'client_secrets.obf'
VIDEO_LENGTH_REQUEST_SIZE = 20
YOUTUBE_READONLY_SCOPE = 'https://www.googleapis.com/auth/youtube.readonly'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


class OauthFlags(object):
  def __init__(self):
    self.auth_host_name = 'localhost'
    self.auth_port_port = [8080, 8090]
    self.logging_level = 'ERROR'
    self.noauth_local_webserver = True


class UserAccount(object):
  def __init__(self):
    self.credentials = None
    self.service = None
    self.auth_storage = Storage(AUTHENTICATION_FILE)
    obfuscator = secret_obfuscator.SecretObfuscator()
    secret_cleartext = obfuscator.make_cleartext(CLIENT_SECRETS_FILE)
    self.connect_flow = flow_from_clientsecrets(secret_cleartext,
                                                scope=YOUTUBE_READONLY_SCOPE)
    obfuscator.cleanup()

  def authenticate(self):
    """Run the command-line authentication flow and save credentials."""
    self.credentials = run_flow(self.connect_flow, self.auth_storage,
                                OauthFlags())

  def connect(self):
    """Load credentials and create the Youtube API wrapper."""
    self.credentials = self.auth_storage.get()
    if self.credentials is None or self.credentials.invalid:
      raise RuntimeError('Not authenticated!')
    http_credentials = self.credentials.authorize(httplib2.Http())
    self.youtube_service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                 http=http_credentials)

  def get_all_playlists(self):
    """Get information about all playlists the user has.

    Return playlists in an arbitrary order. Each playlist is represented by
    a dictionary with keys 'title', 'directory', 'playlist_id'.
    """
    playlists = []
    response = self.youtube_service.channels().list(
      mine=True, part='contentDetails').execute()
    favorites_id = (response['items'][0]['contentDetails']
                    ['relatedPlaylists']['favorites'])
    playlists.append({'title': u'Favorites',
                      'directory': u'favorites',
                      'playlist_id': favorites_id})
    page_token = None
    while True:
      response = self.youtube_service.playlists().list(
        part='id,snippet', mine='true', pageToken=page_token).execute()
      for item in response['items']:
        title = item['snippet']['title']
        playlists.append({'title': title,
                          'directory': data_util.normalize_name(title),
                          'playlist_id': item['id']})
      if 'nextPageToken' in response:
        page_token = response['nextPageToken']
      else:
        break
    return playlists

  def get_playlist_videos(self, playlist_id, min_timestamp=None,
                          etag_cache=None):
    """Get information about all videos in the playlist.

    Return videos in order by timestamp, with newer (larger timestamp) videos
    first. If min_timestamp is set, only return videos with larger timestamps.
    If playlist has the same etag as in the etag_cache, return None. Each video
    is represented by a VideoElement object.
    """
    videos = []
    # Youtube API's playlist ids begin with 'FL' for favorites list, and 'PL'
    # for other playlists. Favorites are ordered with newest videos first,
    # while other playlists are ordered with newest videos last. Version 2 of
    # the API had a parameter for reversing the order (orderBy=reversedOrder)
    # whereas version 3 does not, so for non-favorites playlists we need to get
    # all videos then reverse the order.
    reverse_order = False
    if playlist_id[0:2] == 'PL':
      reverse_order = True
    elif playlist_id[0:2] == 'FL':
      pass
    else:
      raise RuntimeError('Cannot parse playlist id: %s' % (playlist_id,))
    last_timestamp = None
    # Call Youtube API to get videos in the playlist.
    page_token = None
    while True:
      response = self.youtube_service.playlistItems().list(
        part='snippet,contentDetails',
        maxResults=10,
        playlistId=playlist_id,
        pageToken=page_token
      ).execute()
      # Check etag for only the first page, and abort if it matches the cache.
      if not etag_cache is None and page_token is None:
        if etag_cache.get(playlist_id) == response['etag']:
          return None
        etag_cache[playlist_id] = response['etag']
      for item in response['items']:
        element = video_element.VideoElement()
        element.title = item['snippet']['title']
        element.description = item['snippet']['description']
        element.published = item['snippet']['publishedAt']
        element.timestamp = data_util.create_timestamp(element.published)
        element.video_id = item['contentDetails']['videoId']
        element.safename = (data_util.normalize_name(element.title) + '-' +
                            element.video_id)
        element.url = 'http://youtube.com/watch?v=%s' % element.video_id
        # Filter by timestamp if necessary.
        last_timestamp = element.timestamp
        if not min_timestamp or last_timestamp > min_timestamp:
          videos.append(element)
      # Pagination. We want all pages if the order needs to be reversed, or
      # there is no minimum timestamp. Otherwise, continue as long as the
      # last timestamp is larger than the minimum timestamp and a next page
      # exists.
      if ((reverse_order or not min_timestamp or
           (min_timestamp and last_timestamp > min_timestamp)) and
          'nextPageToken' in response):
        page_token = response['nextPageToken']
      else:
        break
    # Reverse the order after getting all videos.
    if reverse_order:
      videos.reverse()
    # Get video lengths.
    lengths = self.get_video_length([element.video_id for element in videos])
    for element in videos:
      if element.video_id in lengths:
        element.length = lengths[element.video_id]
    return videos

  def get_video_length(self, video_ids):
    """Get a dictionary mapping video_id to length of video in seconds."""
    lengths = {}
    if not isinstance(video_ids, list):
      video_ids = [video_ids]
    offset = 0
    while offset < len(video_ids):
      request_ids = video_ids[offset:offset + VIDEO_LENGTH_REQUEST_SIZE]
      response = self.youtube_service.videos().list(
        part='contentDetails',
        id=','.join(request_ids)).execute()
      for item in response['items']:
        duration = item['contentDetails']['duration']
        length = data_util.convert_youtube_time_to_sec(duration)
        lengths[item['id']] = length
      offset += VIDEO_LENGTH_REQUEST_SIZE
    return lengths
