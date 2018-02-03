import math
import statistics
from decimal import Decimal
from fractions import Fraction
import numpy as np
from scipy import stats

def parse_file_to_data_dict(file_path, separator=','):
    data_dict = dict()
    column_number_to_variable_name_mapping = dict()
    try:
        wrapped_in_double_quotes = True
        with open(file_path, 'r') as file:
            for line in file.readlines():
                for value in line.strip().split(separator):
                    if not (value.startswith('"') and value.endswith('"')):
                        wrapped_in_double_quotes = False
                        break

        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file.readlines()):
                split_line = line.strip().split(separator)
                if line_number == 0:
                    number_of_columns_in_header_line = len(split_line)
                    for column_number, variable_name in enumerate(split_line):
                        if wrapped_in_double_quotes:
                            variable_name = variable_name[1:-1]
                        column_number_to_variable_name_mapping[column_number] = variable_name
                        data_dict[variable_name] = list()
                else:
                    number_of_columns_in_this_line = len(split_line)
                    if number_of_columns_in_this_line != number_of_columns_in_header_line:
                        raise ValueError(
                            'The number of columns in this line is different from the number of columsn in the header line: line number - {}, number of columns in this line - {}, number of columns in the header line - {}'.format(
                                line_number, number_of_columns_in_this_line, number_of_columns_in_header_line
                            )
                        )
                    for column_number, value in enumerate(split_line):
                        if wrapped_in_double_quotes:
                            value = value[1:-1]
                        data_dict[column_number_to_variable_name_mapping[column_number]].append(value)
    except FileNotFoundError:
        raise ValueError('The given file path does not exist: file_path - {}'.format(file_path))
    return data_dict

def bucketize(numbers, buckets, variable_name='x'):
    if not buckets:
        return ['-inf<{}<inf'.format(variable_name)] * len(numbers)

    bucketized_numbers = list()
    buckets.sort()
    left_boundary = buckets[0]
    right_boundary = buckets[-1]
    for number in numbers:
        if number < left_boundary:
            bucketized_numbers.append('{}<{}'.format(variable_name, left_boundary))
        elif number >= right_boundary:
            bucketized_numbers.append('{}<={}'.format(right_boundary, variable_name))
        else:
            for boundary_index, boundary in enumerate(buckets):
                if number < buckets[boundary_index+1]:
                    bucketized_numbers.append('{}<={}<{}'.format(boundary, variable_name, buckets[boundary_index+1]))
                    break
    return bucketized_numbers

def _get_storage_types(values):
    storage_types = set()
    for value in values:
        value_type  = type(value)
        if value is None:
            storage_types.add('null')
        elif value_type in [bool]:
            storage_types.add('boolean')
        elif value_type in [str]:
            storage_types.add('string')
        elif value_type in [int, float, Decimal, Fraction]:
            storage_types.add('number')
    return sorted(list(storage_types))

def _all_values_booleans(values):
    all_values_boolean = True
    for value in values:
        value_type = type(value)
        if value is None:
            pass
        elif value_type in [bool]:
            pass
        elif value_type in [str]:
            if value.lower() in ['t', 'f', 'true', 'false', '0', '1']:
                pass
            else:
                all_values_boolean = False
                break
        elif value_type in [int, float, Decimal, Fraction]:
            if value in [0, 1, 0.0, 1.0, Decimal(0), Decimal(1), Fraction(0), Fraction(1)]:
                pass
            else:
                all_values_boolean = False
                break
        else:
            all_values_boolean = False
            break
    return all_values_boolean

def _all_values_numbers(values):
    all_values_numbers = True
    values_as_numbers = list()
    for value in values:
        value_type = type(value)
        if value is None:
            pass
        elif value_type in [bool, int, float, Decimal, Fraction]:
            if value_type == bool:
                values_as_numbers.append(int(value))
            else:
                values_as_numbers.append(value)
        else:
            try:
                value_as_number = int(value)
            except ValueError:
                try:
                    value_as_number = float(value)
                except ValueError:
                    all_values_numbers = False
                    break
                else:
                    values_as_numbers.append(value_as_number)
            else:
                values_as_numbers.append(value_as_number)
    return all_values_numbers, values_as_numbers

def get_metadata_from_data_dict(data_dict, num_buckets=10, max_num_unique_values=10):
    """
    if all values can be expressed as 0 or 1
        return binary
    else:
        if the number of unique values is less than 10 * log10(number of rows):
            categorical
        else:
            if all values can be expressed as number:
                numeric
            else
                textual

    information to return across all types: meaning_type, storage_types, nullable
    information to return when binary, categorical and textual: unique_values
    information to return when numeric: buckets, min, median and max
    """

    metadata = dict()
    for key in data_dict.keys():
        values = data_dict[key]
        if not values:
            metadata[key] = {'meaning_type': 'empty'}
        else:
            unique_values = list(set(values))
            nullable = True if '' in unique_values or None in unique_values else False
            num_values = len(values)
            num_unique_values = len(unique_values)
            if num_unique_values > max_num_unique_values:
                unique_values = unique_values[:max_num_unique_values] + ['TRUNCATED']
            storage_types = _get_storage_types(values)

            if _all_values_booleans(values):
                metadata[key] = {
                    'meaning_type': 'binary'
                    , 'storage_types': storage_types
                    , 'unique_values': unique_values
                    , 'number_of_unique_values': num_unique_values
                    , 'nullable': nullable
                }
            else:
                if num_unique_values <= 10 * max(math.log10(num_values), 1):
                    metadata[key] = {
                        'meaning_type': 'categorical'
                        , 'storage_types': storage_types
                        , 'unique_values': unique_values
                        , 'number_of_unique_values': num_unique_values
                        , 'nullable': nullable
                    }
                else:
                    all_values_numbers, values_as_numbers = _all_values_numbers(values)
                    if all_values_numbers:
                        metadata[key] = {
                            'meaning_type': 'numeric'
                            , 'buckets': np.round(stats.mstats.mquantiles(values_as_numbers, np.arange(0.0, 1.0+1.0/num_buckets, 1.0/num_buckets)), 2).tolist()
                            , 'min': min(values_as_numbers)
                            , 'median': statistics.median(values_as_numbers)
                            , 'max': max(values_as_numbers)
                            , 'nullable': nullable
                        }
                    else:
                        metadata[key] = {
                            'meaning_type': 'textual'
                            , 'storage_types': storage_types
                            , 'unique_values': unique_values
                            , 'number_of_unique_values': num_unique_values
                            , 'nullable': nullable
                        }
    return metadata
            
def get_metadata_from_file(file_path, separator=',', num_buckets=10):
    return get_metadata_from_data_dict(parse_file_to_data_dict(file_path, separator), num_buckets)

def process_data_dict_by_metadata(data_dict, metadata):
    processed_data_dict = dict()
    for key in data_dict.keys():
        processed_data_dict[key] = list()
        if metadata[key]['meaning_type'] in ['categorical', 'textual']:
            for value in data_dict[key]:
                if isinstance(value, str):
                    processed_data_dict[key].append('\"{}\"'.format(value))
                else:
                    processed_data_dict[key].append(value)
        elif metadata[key]['meaning_type'] == 'binary':
            for value in data_dict[key]:
                if isinstance(value, bool):
                    processed_data_dict[key].append(value)
                elif type(value) in [int, float, Decimal, Fraction]:
                    if value == 0:
                        processed_data_dict[key].append(False)
                    else:
                        processed_data_dict[key].append(True)
                else:
                    try:
                        lowered_value = value.lower()
                    except AttributeError:
                        if value:
                            processed_data_dict[key].append(True)
                        else:
                            processed_data_dict[key].append(False)
                    else:
                        if lowered_value in ['f', 'false', '0']:
                            processed_data_dict[key].append(False)
                        else:
                            processed_data_dict[key].append(True)
        elif metadata[key]['meaning_type'] == 'numeric':
            for value in data_dict[key]:
                if not value:
                    processed_data_dict[key].append(value)
                else:
                    if not type(value) in [int, float, Decimal, Fraction]:
                            try:
                                number = int(value)
                            except ValueError:
                                try:
                                    number = float(value)
                                except ValueError:
                                    raise ValueError('Metadata says a variable is a number but some values of it are not numbers: variable name - {}, value - {}'.format(key, value))
                    else:
                        number = value

                    if metadata[key]['buckets']:
                        if number < metadata[key]['buckets'][0]:
                            processed_data_dict[key].append('{}<{}'.format(key, metadata[key]['buckets'][0]))
                        elif number >= metadata[key]['buckets'][-1]:
                            processed_data_dict[key].append('{}<={}'.format(metadata[key]['buckets'][-1], key))
                        else:
                            for boundary_index, boundary in enumerate(metadata[key]['buckets']):
                                if number >= boundary and number < metadata[key]['buckets'][boundary_index+1]:
                                    processed_data_dict[key].append('{}<={}<{}'.format(boundary, key, metadata[key]['buckets'][boundary_index+1]))
                                    break
                    else:
                        processed_data_dict[key].append('-inf<{}<inf'.format(key))
        return processed_data_dict