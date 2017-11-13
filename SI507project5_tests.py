import unittest
from SI507project5_code import *

class CodeTests(unittest.TestCase):
	def setUp(self):
		self.photo_dict = tumblr_photo_result
		self.p_id = photo_id_list
		self.p_timestamp = photo_timestamp_list
		self.p_tags = photo_tags_list
		self.p_url = photo_url_list
		self.p_dims = photo_dimensions_list
		self.p_note = photo_note_count

		self.text_dict = tumblr_text_result
		self.t_id = text_id_list
		self.t_date = text_date_list
		self.t_timestamp = text_timestamp_list
		self.t_title = text_title_list
		self.t_content = text_content_list
		self.t_tags = text_tags_list
		self.t_note = text_note_count

	def test1(self):
		self.assertEqual(type(self.photo_dict),dict, "Testing that tumblr photo method successfully returns a dictionary")

	def test2(self):
		self.assertEqual(type(self.text_dict),dict,"Testing that tumblr text method successfully returns a dictionary")

	def test3(self):
		for i in self.t_content:
			self.assertEqual(type(i),str,"Testing that the content returned for text results are strings")

	def test4(self):
		for i in self.p_tags:
			self.assertEqual(type(i),list,"Testing that the tags returned for the photo search are lists")
			for j in i:
				self.assertEqual(type(j),str,"Testing that the tags in the lists are strings")

	def test5(self):
		self.assertLessEqual(len(self.photo_dict['response']['posts']),20,"Testing that the tumblr photo method return no more than 20 results")
		self.assertLessEqual(len(self.text_dict['response']['posts']),20,"Testing that the tumblr photo method return no more than 20 results")

	def tearDown(self):
		pass

if __name__ == "__main__":
    unittest.main(verbosity=2)
