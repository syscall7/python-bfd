import unittest
from odb.odb_file import OdbFile
from odb.ops.add_operation import AddOperation
from odb.structures import comment
from odb.structures.comment import Comment

__author__ = 'davis'

class TestAddFunction(unittest.TestCase):
    def test_add(self):

        odb_file = OdbFile()

        item = odb_file.create_item('Comment', {
            'comment': 'This is a comment',
            'offset': 0
        })

        odb_file.execute(comment.generate_operation(AddOperation, item))

        self.assertEquals(1, len(odb_file.get_structure_list(Comment)))

