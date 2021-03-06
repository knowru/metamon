# parse_file_to_data_dict(file_path, separator=','); returns data dict
# bucketize(numbers, buckets); returns bucketized values
# get_metadata_from_data_dict(data_dict, num_buckets=10); returns metadata dict
# get_metadata_from_file(file_path, separator=',', num_buckets=10); returns metadata dict
# process_data_dict_by_metadata(data_dict, metadata); returns data dict

import unittest
from unittest.mock import MagicMock, patch, call, ANY
import shutil
from tempfile import mkdtemp
import math
from decimal import Decimal
from fractions import Fraction
from metamon import (
    parse_file_to_data_dict, bucketize
    , get_metadata_from_data_dict, get_metadata_from_file
    , process_data_dict_by_metadata
)

class ParseFileToDataDictTestCase(unittest.TestCase):
    def setUp(self):
        # To support tests in Windows as well, use mkdtemp instead of NamedTemporaryFile
        # Whether the name can be used to open the file a second time,
        # while the named temporary file is still open, varies across platforms
        # (it can be so used on Unix; it cannot on Windows NT or later).
        # Source: https://docs.python.org/3/library/tempfile.html

        self.temp_dir = mkdtemp()
        self.file_path = '{}/data.csv'.format(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_empty_file(self):
        with open(self.file_path, 'w') as f:
            f.write('')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, dict())

    def test_header_only_file(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': []})

        with open(self.file_path, 'w') as f:
            f.write('variable1,variable2')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': [], 'variable2': []})

    def test_two_line_file(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1\nvalue1')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': ['value1']})

        with open(self.file_path, 'w') as f:
            f.write('variable1,variable2\nvalue1,value2')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': ['value1'], 'variable2': ['value2']})

    def test_multiple_lines(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1\nvalue1a\nvalue1b')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b']})

        with open(self.file_path, 'w') as f:
            f.write('variable1,variable2\nvalue1a,value2a\nvalue1b,value2b')
        data_dict = parse_file_to_data_dict(self.file_path)
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b'], 'variable2': ['value2a', 'value2b']})

    def test_separator_other_than_comma(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1\nvalue1a\nvalue1b')
        data_dict = parse_file_to_data_dict(self.file_path, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b']})

        with open(self.file_path, 'w') as f:
            f.write('variable1;variable2\nvalue1a;value2a\nvalue1b;value2b')
        data_dict = parse_file_to_data_dict(self.file_path, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', 'value1b'], 'variable2': ['value2a', 'value2b']})

    def test_file_with_empty_value(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1;variable2\nvalue1a;\n;value2b')
        data_dict = parse_file_to_data_dict(self.file_path, separator=';')
        self.assertEqual(data_dict, {'variable1': ['value1a', ''], 'variable2': ['', 'value2b']})

    def test_file_with_double_quote_wrapped(self):
        with open(self.file_path, 'w') as f:
            f.write('"variable1";"variable2"\n"value1a";""\n"";"value2b"')
        data_dict = parse_file_to_data_dict(self.file_path, separator=';')
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

    def test_improperly_formatted_file(self):
        with open(self.file_path, 'w') as f:
            f.write('variable1;variable2\nvalue1,value2')
        try:
            data_dict = parse_file_to_data_dict(self.file_path)
        except ValueError as ve:
            pass
        except Exception as e:
            self.fail('Expected ValueError but received: {}'.format(type(e).__name__))
        else:
            self.fail('Expected ValueError but no exception happened')

class BucketizeTestCase(unittest.TestCase):
    def test_empty_numbers(self):
        bucketized_values = bucketize([], [])
        self.assertEqual(bucketized_values, [])

        bucketized_values = bucketize([], [(0, 1)])
        self.assertEqual(bucketized_values, [])

    def test_empty_buckets(self):
        bucketized_values = bucketize([-1, 0, 1], [])
        self.assertEqual(bucketized_values, ['-inf<x<inf', '-inf<x<inf', '-inf<x<inf'])

    def test_single_boundary_buckets(self):
        bucketized_values = bucketize([-1, 0, 1], [0])
        self.assertEqual(bucketized_values, ['x<0', '0<=x', '0<=x'])

    def test_numbers_outside_of_buckets(self):
        bucketized_values = bucketize([-10, 10], [0, 3, 12])
        self.assertEqual(bucketized_values, ['x<0', '3<=x<12'])

        bucketized_values = bucketize([-10, 10], [-20, 3, 9])
        self.assertEqual(bucketized_values, ['-20<=x<3', '9<=x'])

        bucketized_values = bucketize([-10, 10], [1, 3, 5])
        self.assertEqual(bucketized_values, ['x<1', '5<=x'])

    def test_normal_cases(self):
        bucketized_values = bucketize(range(0, 5), [-2, 0, 1, 3, 4, 8])
        self.assertEqual(bucketized_values, ['0<=x<1', '1<=x<3', '1<=x<3', '3<=x<4', '4<=x<8'])

        bucketized_values = bucketize(range(0, 5), [-2, 0, 1, 3, 4, 8], variable_name='y')
        self.assertEqual(bucketized_values, ['0<=y<1', '1<=y<3', '1<=y<3', '3<=y<4', '4<=y<8'])
    
class GetMetadataFromDataDictTestCase(unittest.TestCase):
    def test_very_small_data_dict(self):
        metadata = get_metadata_from_data_dict({'variable': []})
        self.assertEqual(metadata['variable']['meaning_type'], 'empty')

        metadata = get_metadata_from_data_dict({'variable': [True]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['boolean'])
        self.assertEqual(metadata['variable']['unique_values'], [True])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 1)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['number'])
        self.assertEqual(metadata['variable']['unique_values'], [0])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 1)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [-1]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['number'])
        self.assertEqual(metadata['variable']['unique_values'], [-1])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 1)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1.1]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['number'])
        self.assertEqual(metadata['variable']['unique_values'], [1.1])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 1)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': ['a']})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(metadata['variable']['unique_values'], ['a'])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 1)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, -1.1, '2.0']})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['number', 'string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([1, -1.1, '2.0']))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], False)

    def test_binary(self):
        metadata = get_metadata_from_data_dict({'variable': [True, False, True, True, False, False]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['boolean'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([True, False]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 2)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0, Decimal(0), Fraction(1)]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['number'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([0, 1]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 2)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, None, 0, 1]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['null', 'number'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([0, 1, None]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], True)

        metadata = get_metadata_from_data_dict({'variable': ['t', 'f', 'trUe', 'faLse']})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set(['f', 'faLse', 't', 'trUe']))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 4)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 0.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'], ['boolean', 'number', 'string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 0.0]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 8)  # 1 == True == 1.0, 0 == False == 0.0
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 2.0]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['boolean', 'number', 'string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, 2.0]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 9)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, None]})
        self.assertEqual(metadata['variable']['meaning_type'], 'binary')
        self.assertEqual(metadata['variable']['storage_types'],  ['boolean', 'null', 'number', 'string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([1, 0, True, False, 't', 'f', 'true', 'false', 'TrUe', 'FaLsE', 1.0, None]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 9)
        self.assertEqual(metadata['variable']['nullable'], True)

    def test_categorical(self):
        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0, 2]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['number'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([0, 1, 0.0, 1.0, 2]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [0, 1, 0, 1, 0, 1, 0, 1.0, 0.0, 2, None]})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['null', 'number'])
        self.assertEqual(set(metadata['variable']['unique_values']), set([0, 1, 0.0, 1.0, 2, None]))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 4)
        self.assertEqual(metadata['variable']['nullable'], True)

        metadata = get_metadata_from_data_dict({'variable': ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set(['a', 'b', 'c']))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 3)
        self.assertEqual(metadata['variable']['nullable'], False)

    def test_textual(self):
        metadata = get_metadata_from_data_dict({'variable': ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f']})
        self.assertEqual(metadata['variable']['meaning_type'], 'categorical')
        self.assertEqual(metadata['variable']['storage_types'], ['string'])
        self.assertEqual(set(metadata['variable']['unique_values']), set(['a', 'b', 'c', 'd', 'e', 'f']))
        self.assertEqual(metadata['variable']['number_of_unique_values'], 6)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [1, 2, 3, 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'abc', 'def']})
        self.assertEqual(metadata['variable']['meaning_type'], 'textual')
        self.assertEqual(metadata['variable']['storage_types'], ['number', 'string'])
        self.assertIn('TRUNCATED', metadata['variable']['unique_values'])
        self.assertEqual(metadata['variable']['number_of_unique_values'], 14)
        self.assertEqual(metadata['variable']['nullable'], False)

    def test_numeric(self):
        metadata = get_metadata_from_data_dict({'variable': list(range(-20, 20))})
        self.assertEqual(metadata['variable']['meaning_type'], 'numeric')
        self.assertEqual(metadata['variable']['buckets'], [-20, -16.58, -12.56, -8.54, -4.52, -0.5, 3.52, 7.54, 11.56, 15.58, 19])
        self.assertEqual(metadata['variable']['min'], -20)
        self.assertEqual(metadata['variable']['median'], -0.5)
        self.assertEqual(metadata['variable']['max'], 19)
        self.assertEqual(metadata['variable']['nullable'], False)

        metadata = get_metadata_from_data_dict({'variable': [-3, -2, -1, 0, 1, 2, 3, 4, 5, None, '6', '7.0']})
        self.assertEqual(metadata['variable']['meaning_type'], 'numeric')
        self.assertEqual(metadata['variable']['buckets'], [-3.0, -2.48, -1.36, -0.24, 0.88, 2.0, 3.12, 4.24, 5.36, 6.48, 7.0])
        self.assertEqual(metadata['variable']['min'], -3)
        self.assertEqual(metadata['variable']['median'], 2)
        self.assertEqual(metadata['variable']['max'], 7)
        self.assertEqual(metadata['variable']['nullable'], True)

class GetMetadataFromFileTestCase(unittest.TestCase):
    def test_get_metadata_from_file_call_order(self):
        source_mock = MagicMock()
        with patch('metamon.functions.get_metadata_from_data_dict', source_mock.get_metadata_from_data_dict), \
            patch('metamon.functions.parse_file_to_data_dict', source_mock.parse_file_to_data_dict):
            source_mock.parse_file_to_data_dict.return_value = {'data': 'dict'}
            get_metadata_from_file('file_path.txt')
            expected_calls = [
                call.parse_file_to_data_dict('file_path.txt', ',')
                , call.get_metadata_from_data_dict({'data': 'dict'}, 10)
            ]
            self.assertEqual(source_mock.mock_calls, expected_calls)

class ProcessDataDictByMetadataTestCase(unittest.TestCase):
    def test_binary(self):
        processed_data_dict = process_data_dict_by_metadata(
            {'variable': ['t', 'f', '0', '1', 'tRuE', 'fAlSe', True, False, 0.0, 1.0]}
            , {'variable': {'meaning_type': 'binary'}}
        )
        self.assertEqual(processed_data_dict, {'variable': [True, False, False, True, True, False, True, False, False, True]})

    def test_categorical(self):
        processed_data_dict = process_data_dict_by_metadata(
            {'variable': ['t', 'f', '0', '1', 'tRuE', 'fAlSe', True, False, 0.0, 1.0, 'a', 'a', 'b', 'b', 'c', 'c', 1, 1, 1, 1.2]}
            , {'variable': {'meaning_type': 'categorical'}}
        )
        self.assertEqual(processed_data_dict, {'variable': ['"t"', '"f"', '"0"', '"1"', '"tRuE"', '"fAlSe"', True, False, 0, 1, '"a"', '"a"', '"b"', '"b"', '"c"', '"c"', 1, 1, 1, 1.2]})

    def test_textual(self):
        processed_data_dict = process_data_dict_by_metadata(
            {'variable': ['t', 'f', '0', '1', 'tRuE', 'fAlSe', True, False, 0.0, 1.0, 'a', 'a', 'b', 'b', 'c', 'c', 1, 1, 1, 1.2]}
            , {'variable': {'meaning_type': 'textual'}}
        )
        self.assertEqual(processed_data_dict, {'variable': ['"t"', '"f"', '"0"', '"1"', '"tRuE"', '"fAlSe"', True, False, 0, 1, '"a"', '"a"', '"b"', '"b"', '"c"', '"c"', 1, 1, 1, 1.2]})

    def test_numeric(self):
        processed_data_dict = process_data_dict_by_metadata(
            {'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
            , {'x': {'meaning_type': 'numeric', 'buckets': [1, 5, 10]}}
        )
        self.assertEqual(processed_data_dict, {'x': ['1<=x<5', '1<=x<5', '1<=x<5', '1<=x<5', '5<=x<10', '5<=x<10', '5<=x<10', '5<=x<10', '5<=x<10', '10<=x']})

if __name__ == '__main__':
    unittest.main()