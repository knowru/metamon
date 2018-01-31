# parse_file_to_data_dict(file_path, separator=','); returns data dict
# get_metadata_from_data_dict(data_dict, num_buckets=10); returns metadata dict
# get_metadata_from_file(file_path, separator=',', num_buckets=10); returns metadata dict

import unittest
from tempfile import NamedTemporaryFile
from metamon import parse_file_to_data_dict

class ParseFileToDataDictTestCase(unittest.TestCase):
    def test_empty_file(self):
        with NamedTemporaryFile(mode='w') as ntf:
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, dict())

    def test_header_only_file(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': []})

        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1,variable2')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': [], 'variable2': []})

    def test_two_line_file(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1\nvalue1')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': ['value1']})

        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1,variable2\nvalue1,value2')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': ['value1'], 'variable2': ['value2']})

    def test_multiple_lines(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1\nvalue1a\nvalue1b')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b']})

        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1,variable2\nvalue1a,value2a\nvalue1b,value2b')
            data_dict = parse_file_to_data_dict(ntf.name)
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b'], 'variable2': ['value2a', 'value2b']})

    def test_separator_other_than_comma(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1\nvalue1a\nvalue1b')
            data_dict = parse_file_to_data_dict(ntf.name, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b']})

        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1;variable2\nvalue1a;value2a\nvalue1b;value2b')
            data_dict = parse_file_to_data_dict(ntf.name, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b'], 'variable2': ['value2a', 'value2b']})

    def test_file_with_empty_value(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1;variable2\nvalue1a;\n;value2b')
            data_dict = parse_file_to_data_dict(ntf.name, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', ''], 'variable2': ['', 'value2b']})

    def test_non_existing_file(self):
        try:
            data_dict = parse_file_to_data_dict('non-existing-file.txt')
        except ValueError as ve:
            pass
        except Exception as e:
            self.fail('Expected ValueError but received: {}'.format(type(e).__name__))
        else:
            self.fail('Expected ValueError but no exception happened')

    def test_binary_file(self):
        with NamedTemporaryFile() as ntf:
            ntf.write(b"""330d 0d0a 0e0b 4559 c022 0000 e300 0000
0000 0000 0000 0000 0005 0000 0040 0000
0073 7600 0000 6400 5a00 6401 6402 6c01
6d02 5a02 0100 6403 6404 8400 5a03 4700
6405 6406 8400 6406 6504 8303 5a05 4700
6407 6408 8400 6408 6506 8303 5a07 4700
6409 640a 8400 640a 6508 8303 5a09 4700
640b 640c 8400 640c 650a 8303 5a0b 4700
640d 640e 8400 640e 650b 640f 8d03 5a0c""")
            try:
                data_dict = parse_file_to_data_dict(ntf.name)
            except ValueError as ve:
                pass
            except Exception as e:
                self.fail('Expected ValueError but received: {}'.format(type(e).__name__))
            else:
                self.fail('Expected ValueError but no exception happened')

    def test_improperly_formatted_file(self):
        with NamedTemporaryFile(mode='w') as ntf:
            ntf.write('variable1;variable2\nvalue1,value2')
            try:
                data_dict = parse_file_to_data_dict(ntf.name)
            except ValueError as ve:
                pass
            except Exception as e:
                self.fail('Expected ValueError but received: {}'.format(type(e).__name__))
            else:
                self.fail('Expected ValueError but no exception happened')

'''


binary
categorical
textual
    meaning_type
    unique_values
    
numeric
    meaning_type
    storage_types

    buckets
    min
    median
    max

class GetMetadataFromDataDictTestCase(TestCase):
    def test_booleans(self):
        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 0.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'boolean', 'string', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 0.0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 12)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 2.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'boolean', 'string', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 2.0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 12)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, None]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'boolean', 'string', 'float', 'null'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, None])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 12)
        self.assertEqual(metadata['variable']['nullable'], True)

    def test_numbers(self):
        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, None, 0, 1]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, None])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], True)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 2)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, 1.0, 0.0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 4)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [1, 0, 1.0, 0.0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 4)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0, 2]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'float'])
        self.assertEqual(metadata['variable']['unique_values'], [0, 1, 0.0, 1.0, 2])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 4)
        self.assertEqual(metadata['variable']['nullable'], False)
        
        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0, 2, None]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['integer', 'float', 'null'])
        self.assertEqual(metadata['variable']['unique_values'], [0, 1, 0.0, 1.0, 2, None])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 5)
        self.assertEqual(metadata['variable']['nullable'], True)

        metadata = get_metadata_from_data_dict({'variable': [-3, -2, -1, 0, 1, 2, 3, 4, 5]})
        self.assertEqual(metadata['variable']['meaning_type'], 'numeric')
        self.assertEqual(metadata['variable']['storage_types'], ['integer'])
        self.assertEqual(metadata['variable']['storage_types'], ['integer'])
        
        self.assertEqual(metadata['variable']['number_of_unique_values'], 5)
        self.assertEqual(metadata['variable']['nullable'], True)

    def test_strings(self):
        metadata = get_metadata_from_data_dict({'variable': ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(metadata['variable']['unique_values'], ['a', 'b', 'c'])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f']})
        self.assertEqual(metadata['variable']['meaning_type'], 'textual')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(metadata['variable']['unique_values'], ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 6)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 2, 3, 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f']})
        self.assertEqual(metadata['variable']['meaning_type'], 'textual')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(metadata['variable']['unique_values'], ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 6)
        self.assertEqual(metadata['variable']['nullable'], False)
        

    def test_combinations(self):
        pass

class GetMetadataFromFileTestCase(TestCase):
    pass

class ParseFileToDataDictTestCase(TestCase):
    pass

from tempfile import NamedTemporaryFile
from sniffer.utils import SnifferError
from sniffer.metamon import get_data, transform_target_variable_column

class GetDataTestCase(TestCase):
    def test_double_quote_wrapped_data(self):
        with NamedTemporaryFile() as f:
            f.write('"var1","var2","var3"\n"a","b","c"\n"1","2","3"')
            f.flush()

            data = get_data(f.name)
        self.assertEqual(data, [['var1','var2','var3'], ['a','b','c'], ['1','2','3']])

    def test_not_double_quote_wrapped_data(self):
        with NamedTemporaryFile() as f:
            f.write('var1,var2,var3\na,b,c\n1,2,3')
            f.flush()

            data = get_data(f.name)
        self.assertEqual(data, [['var1','var2','var3'], ['a','b','c'], ['1','2','3']])

class TransformTargetVariableColumn(TestCase):
    def test_target_variable_is_utf_and_not_boolean(self):
        data=[["a", "b", "c"], [1,2,u"安녕"]]
        try:
            transform_target_variable_column(data, "c", ",")
        except SnifferError as se:
            if not se.message == u"The target variable contains a non-boolean value (all values of the target variable column in their lower case should be t, true, 1, f, false, or 0): line - {}, target variable - {}, value - {}".format(1, 'c', u'安녕'):
                self.fail(u'SnifferError was correctly raised but with a different message: {}'.format(se.message))
        except Exception as e:
            traceback.print_exc()
            self.fail(u'Expected SnifferError but {} exception was raised'.format(type(e).__name__))
        else:
            self.fail(u'Expected SnifferError but no exception was raised.')

    def test_target_variable_name_is_utf_and_missing(self):
        data=[["a", "b", "c"], [1,2,u"安녕"]]
        try:
            transform_target_variable_column(data, u"安녕", ",")
        except SnifferError as se:
            if not se.message == u"The target variable is not found in header: target variable - 安녕, header - a,b,c":
                self.fail(u'SnifferError was correctly raised but with a different message: {}'.format(se.message))
        except Exception as e:
            self.fail(u'Expected SnifferError but {} exception was raised'.format(type(e).__name__))
        else:
            self.fail(u'Expected SnifferError but no exception was raised.')
'''

if __name__ == '__main__':
    unittest.main()