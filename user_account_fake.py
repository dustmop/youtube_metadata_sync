import video_element


class UserAccountFake(object):
  def get_all_playlists(self):
    return [{'title': 'Apple', 'directory': 'apple', 'playlist_id': 'PLA'},
            {'title': 'Banana', 'directory': 'banana', 'playlist_id': 'PLB'},
            {'title': 'Carrot', 'directory': 'carrot', 'playlist_id': 'PLC'}]

  def get_playlist_videos(self, playlist_id, min_timestamp=None,
                          etag_cache=None):
    videos = []
    if playlist_id == 'PLA':
      element = video_element.VideoElement()
      element.title = 'Apple Video'
      element.description = 'an apple'
      element.published = '123'
      element.timestamp = 123
      element.video_id = 'vA_'
      element.safename = 'apple-video'
      element.url = 'http://youtube.com/watch?v=vA_'
      element.length = 0
      videos.append(element)
      etag_cache['PLA'] = 'Aetag1'
    elif playlist_id == 'PLB':
      element = video_element.VideoElement()
      element.title = 'Banana Video'
      element.description = 'a banana'
      element.published = '456'
      element.timestamp = 456
      element.video_id = 'vB_'
      element.safename = 'banana-video'
      element.url = 'http://youtube.com/watch?v=vB_'
      element.length = 0
      videos.append(element)
      etag_cache['PLB'] = 'Betag1'
    elif playlist_id == 'PLC':
      element = video_element.VideoElement()
      element.title = 'Carrot Video'
      element.description = 'a carrot'
      element.published = '789'
      element.timestamp = 789
      element.video_id = 'vC_'
      element.safename = 'carrot-video'
      element.url = 'http://youtube.com/watch?v=vC_'
      element.length = 0
      videos.append(element)
      etag_cache['PLC'] = 'Cetag1'
    return videos
