import data_util
import unittest


class DataUtilTest(unittest.TestCase):
  def test_unicode(self):
    normal = data_util.normalize_name('\xe3\x81\x8a\xe3\x81\xad')
    expect = '--xe3--x81--x8a--xe3--x81--xad'
    self.assertEqual(normal, expect)

  def test_slashes_and_spaces(self):
    normal = data_util.normalize_name('cat and/or dog')
    expect = 'cat-and-or-dog'
    self.assertEqual(normal, expect)

  def test_capitlaliztion(self):
    normal = data_util.normalize_name('Awesome Movie')
    expect = 'awesome-movie'
    self.assertEqual(normal, expect)

  def test_remove_paren(self):
    normal = data_util.normalize_name('Video (something)')
    expect = 'video-something'
    self.assertEqual(normal, expect)

  def test_convert_hours_minutes_seconds(self):
    length = data_util.convert_youtube_time_to_sec('PT1H45M29S')
    self.assertEqual(length, 6329)

  def test_convert_minutes_seconds(self):
    length = data_util.convert_youtube_time_to_sec('PT3M17S')
    self.assertEqual(length, 197)

  def test_convert_seconds(self):
    length = data_util.convert_youtube_time_to_sec('PT20S')
    self.assertEqual(length, 20)

  def test_convert_minutes_only(self):
    length = data_util.convert_youtube_time_to_sec('PT4M')
    self.assertEqual(length, 240)


if __name__ == '__main__':
  unittest.main()
