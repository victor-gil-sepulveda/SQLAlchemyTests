import unittest
from sqlalchemytests.tools.sql_files import parse_sql_file, get_transaction_set

class TestSQLFileParsing(unittest.TestCase):
    def setUp(self):
        self.file1 = """
-- Name: test
-- A test
Lorem ipsum dolor sit amet,
consequat, tortor
quis tristique imperdiet,
-- Some comments
ligula mauris cursus ipsum,

-- Name: second_test
diam risus in mi.
Aliquam interdum nibh;

vitae metus tristique, eget
condimentum mattis nisi;


""".split("\n")
        self.expected_parsed = {
            'test': [
                ['-- Name: test',
                 '-- A test',
                 'Lorem ipsum dolor sit amet,',
                 'consequat, tortor',
                 'quis tristique imperdiet,',
                 '-- Some comments',
                 'ligula mauris cursus ipsum,']
            ],
            'second_test': [
                ['-- Name: second_test',
                 'diam risus in mi.',
                 'Aliquam interdum nibh;'
                 ],
                ['vitae metus tristique, eget',
                 'condimentum mattis nisi;'
                 ], []
            ]
        }

        self.expected_code = [
            """-- Name: second_test
diam risus in mi.
Aliquam interdum nibh;""",
            """vitae metus tristique, eget
condimentum mattis nisi;"""]

    def test_parsing(self):
        self.assertDictEqual(parse_sql_file(self.file1),
                             self.expected_parsed)

    def test_get_transactions(self):
        self.assertItemsEqual(get_transaction_set("second_test", self.expected_parsed),
                              self.expected_code)

if __name__ == '__main__':
    unittest.main()
