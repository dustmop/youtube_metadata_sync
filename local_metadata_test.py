import os
import shutil
import sys
import tempfile
import unittest

import local_metadata
import user_account_fake


class LocalMetadataTest(unittest.TestCase):
  def setUp(self):
    self.temp_directory = tempfile.mkdtemp()
    self.output_directory = os.path.join(self.temp_directory, 'output')
    self.metadata = local_metadata.LocalMetadata(self.output_directory,
                                                 verbose=False)
    self.account = user_account_fake.UserAccountFake()

  def tearDown(self):
    shutil.rmtree(self.temp_directory)

  def read(self, relative_path):
    path = os.path.join(self.temp_directory, relative_path)
    fp = open(path, 'r')
    content = fp.read()
    fp.close()
    return content

  def test_create_and_get_feeds(self):
    # Bind stderr.
    preserve_stderr = sys.stderr
    fp = open(os.path.join(self.temp_directory, "stderr"), 'w')
    sys.stderr = fp
    # Metadata creation.
    retval = self.metadata.create_init(self.account)
    self.assertEqual(retval, None)
    # Restore stderr.
    sys.stderr = preserve_stderr
    fp.close()
    expect_apple = """[
  {
    "safename": "apple-video",
    "video_id": "vA_",
    "description": "an apple",
    "title": "Apple Video",
    "url": "http://youtube.com/watch?v=vA_",
    "timestamp": 123,
    "published": "123",
    "length": 0
  }
]"""
    expect_banana = """[
  {
    "safename": "banana-video",
    "video_id": "vB_",
    "description": "a banana",
    "title": "Banana Video",
    "url": "http://youtube.com/watch?v=vB_",
    "timestamp": 456,
    "published": "456",
    "length": 0
  }
]"""
    expect_carrot = """[
  {
    "safename": "carrot-video",
    "video_id": "vC_",
    "description": "a carrot",
    "title": "Carrot Video",
    "url": "http://youtube.com/watch?v=vC_",
    "timestamp": 789,
    "published": "789",
    "length": 0
  }
]"""
    expect_etags = """{
  "PLC": "Cetag1",
  "PLB": "Betag1",
  "PLA": "Aetag1"
}"""
    expect_stderr = """Getting playlist "Apple"
Adding 1 elements to "Apple", had 0 elements
Getting playlist "Banana"
Adding 1 elements to "Banana", had 0 elements
Getting playlist "Carrot"
Adding 1 elements to "Carrot", had 0 elements
"""
    self.assertEqual(expect_apple, self.read('output/data/apple/feed.json'))
    self.assertEqual(expect_banana, self.read('output/data/banana/feed.json'))
    self.assertEqual(expect_carrot, self.read('output/data/carrot/feed.json'))
    self.assertEqual(expect_etags, self.read('output/data/etags.json'))
    self.assertEqual(expect_stderr, self.read('stderr'))
    # Get metadata feeds.
    expect_feeds = [self.temp_directory + '/output/data/apple/feed.json',
                    self.temp_directory + '/output/data/banana/feed.json',
                    self.temp_directory + '/output/data/carrot/feed.json']
    feeds = self.metadata.get_metadata_feeds()
    self.assertEqual(expect_feeds, feeds)


if __name__ == '__main__':
  unittest.main()
