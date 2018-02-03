Metamon
=======
Produces metadata for your data.

Why needed?
-----------
How values are stored do not necessarily translate to how the values should be treated when analyzing. For example, values like `1, 2, 3, 1, 2, 3` are saved as numbers but are better to be interpreted as categorical. Values like `"1.1","1.2","-0.1"` are saved as characters but better interpreted as numbers (Excel has an option to let users wrap values with double quotes).

`metamon` allows you to create metadata of your data and then process the data according to the created metadata so that subsequent analysis or machine learning algorithms can interpret data like how human beings would see.

How to use
----------

* parse_file_to_data_dict

```
# data.csv looks as follows:
# var1,var2,var3,var4
# var1,var2,var3,var4
# t,1,1.1,text1
# 0,2,2.1,text2
# f,3,3.2,text3
# true,1,4.2,text4
# false,2,5.3,text5
# 1,3,2.4,text6

>>> from metamon import parse_file_to_data_dict
>>> data_dict = parse_file_to_data_dict(data.csv)
# {
#     'var1': ['t', '0', 'f', 'true', 'false', '1']
#     , 'var2': ['1', '2', '3', '1', '2', '3']
#     , 'var3': ['1.1', '2.1', '3.2', '4.2', '5.3', '2.4']
#     , 'var4': ['text1', 'text2', 'text3', 'text4', 'text5', 'text6']
# }
```


* get_metadata_from_data_dict

```
>>> from metamon import get_metadata_from_data_dict
>>> get_metadata_from_data_dict({"var": ['t',1,0,'t','f',True,'false']})
# {'var': {'meaning_type': 'binary', 'storage_types': ['boolean', 'number', 'string'], 'unique_values': [0, 1, 'f', 'false', 't'], 'number_of_unique_values': 5, 'nullable': False}}

>>> get_metadata_from_data_dict({"var": [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]})
# {'var': {'meaning_type': 'categorical', 'storage_types': ['number'], 'unique_values': [1, 2, 3], 'number_of_unique_values': 3, 'nullable': False}}

>>> get_metadata_from_data_dict({"var": ["1.2", -0.2, "3.4", 2.4, "2.1", 5.6, 1.2, 2.3, 10.2, 11.3, 24.1]})
{'var': {'meaning_type': 'numeric', 'buckets': [-0.2, 0.53, 1.2, 1.88, 2.28, 2.4, 3.66, 6.7, 10.6, 17.44, 24.1], 'min': -0.2, 'median': 2.4, 'max': 24.1, 'nullable': False}}

>>> get_metadata_from_data_dict({"var": ["text1", "text2", "text3", "text4", 1, 2, 3, "text5", "text6", "text7", "text8", "text9"]})
{'var': {'meaning_type': 'textual', 'storage_types': ['number', 'string'], 'unique_values': [1, 2, 'text2', 'text4', 3, 'text9', 'text1', 'text3', 'text7', 'text6', 'TRUNCATED'], 'number_of_unique_values': 12, 'nullable': False}}
```

* get_metadata_from_file

Parses file using `parse_file_to_data_dict` and pass the result `data_dict` to `get_metadata_from_data_dict`.

* process_data_dict_by_metadata

```
>>> from metamon import process_data_dict_by_metadata
>>> data_dict = {"var": ['t',1,0,'t','f',True,'false']}
>>> process_data_dict_by_metadata(data_dict, get_metadata_from_data_dict(data_dict))
{'var': [True, True, False, True, False, True, False]}

>>> data_dict = {"var": [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]}
>>> process_data_dict_by_metadata(data_dict, get_metadata_from_data_dict(data_dict))
{'var': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]}

>>> process_data_dict_by_metadata(data_dict, get_metadata_from_data_dict(data_dict))
{'var': ['1.2<=var<1.88', '-0.2<=var<0.53', '2.4<=var<3.66', '2.4<=var<3.66', '1.88<=var<2.28', '3.66<=var<6.7', '1.2<=var<1.88', '2.28<=var<2.4', '6.7<=var<10.6', '10.6<=var<17.44', '24.1<=var']}

>>> data_dict = {"var": ["text1", "text2", "text3", "text4", 1, 2, 3, "text5", "text6", "text7", "text8", "text9"]}
>>> process_data_dict_by_metadata(data_dict, get_metadata_from_data_dict(data_dict))
{'var': ['"text1"', '"text2"', '"text3"', '"text4"', 1, 2, 3, '"text5"', '"text6"', '"text7"', '"text8"', '"text9"']}
```

How to install
--------------

```pip install metamon```

License
--------
MIT

Questions?
----------
Email to support@knowru.com please.