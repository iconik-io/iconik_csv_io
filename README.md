# iconik CSV Import/Export

This script is used to export all metadata of a particular view for search results, saved search results, or all items in a collection.
It will allow you to either export data from iconik to a CSV file, or alternately use a CSV file to modify large amounts of metadata inside iconik across multiple assets.

## Prerequisites

	- An iconik account
	- Python 3.x
	- a few external libraries (see requirements.txt)

## Installing

Use `pip install -r requirements` first to install all prerequisites.   If you are unsure of which version of Python you are running, type `python --version` in your CLI.   I recommend using `virtualenv` to build your environment for Python 3.x and installing requirements.   

## Usage

There are two primary modes of use for this script, input and output.  Input mode requires you feed the script a CSV file that is properly formatted.  The format of this CSV has some basic requirements.

	- First row MUST be a header row.  
	- R1C1 MUST be simply `id`
	- R1C2 MUST be simply `title`
	- R1C3 -> R1Cn are the `name` attributes of the metadata fields in the view you want to manipulte
	- First column is ALWAYS the UUID of the asset
	- Second column is ALWAYS the title of the asset
	- Columns 3->n are the values of the metadata fields in R1
	- If a field can have multiple values, they must be comma separated in the appropriate cell.
	- If a field is a boolean, it must be either `TRUE` or `FALSE`

| id | title | field1_name | field2_name | bool_field_name |
| ------ | ------ | ------ | ------ | ------ |
| `UUID` | My asset title | Field 1 Value | Field 2 Value1, Field 2 Value2 | `TRUE` |
| `UUID` | Another asset title | Field 1 Value | Field 2 Value1, Field 2 Value2 | `FALSE` |


If all that seems to difficult, I'd recommend you first use the script to export a CSV as it will be properly formatted CSV file.

For input mode, there are a few required command line arguments

| short flag | long flag | description |
| ------ | ------ | ------ |
|  `-i <FILE_PATH>` | `--input-file <PATH>` | Path to properly formatted CSV file |
|  `-v <UUID>` | `--metadata_view <UUID>` | UUID of metadata view containing fields you want to update |

For output mode, you are required to use a few more flags

| short flag | long flag | description |
| ------ | ------ | ------ |
|  `-o <DIR_PATH>` | `--output_dir <DIR_PATH>` | Path to directory where you want to save your CSV |
|  `-v <UUID>` | `--metadata_view <UUID>` | UUID of metadata view containing fields you want to put into CSV |
|  `-m <MODE>` | `--mode <MODE>` | One of three modes, `search`, `saved_search`, `collection` |
|  `-s <STRING>` | `--search_term <STRING>` | If using `saved_search` or `collection`, this should be the UUID of the item.  For `search` this is simply the search string |

## Using a Config File

All CLI arguments can be placed into a config file named `config.ini` in the same directory as the script, or in any location and called out by `-c` as a command line argument.
This can be useful if you'd like to use an app-id and auth token instead of logging in each time you run the script, or if you always use the same metadata view or output directory.

See the example config file `config.ini.example` to see how to format the file.

## Example Syntax

Outputting a CSV file for all items in a collection (requires manual login)
```python iconik_csv_io.py -o ~/Desktop -m collection -s ceeb2b0a-bad2-11ea-a431-0a580a3f6003 -v f3904488-f6d9-11e7-acf1-0a580a3c0118```

Outputting a CSV file for the simple search "Mountains OR Cliffs", using config file for view (requires manual login)
```python iconik_csv_io.py -o ~/Desktop -m search -s "Mountains OR Cliffs"```

Updating assets from a properly formatted CSV using app-id and token
```python iconik_csv_io.py -i ~/Desktop/my_csv_file -v f3904488-f6d9-11e7-acf1-0a580a3c0118 -a afa2a98a-903d-11eb-8ebb-0a580a3d1a0f -t DnF1ZXJ5VGhlbkZldGNoaQAAAAAFg1RjFnVpbXhTVmJKU3FlbGJfY09vRk1FRXcAAAAABW9PZxZsaTMwV1B6UVJ1bTZYQWNhMTFCUTVRAAAAAAXf1g0WVTA5dEpjTTZUNEs4LVJQWlhEam95QQAAAAAFdCd3Fkt6UXJzQ1ZIUVZ1Z21EVW12T01zeVEAAAAABd_WDhZVMDl0SmNNNlQ0SzgtUlBaWERqb3lBAAAAAAXziqkWS3dUYWc5UW9SYXE5SG5DU0lyT0x0QQAAAAAFdCd1Fkt6UXJzQ1ZIUVZ1Z21EVW12T01zeVEAAAAABhCEsxZGYi1GWlR4UVFsS2JuN3pDeWduVC13AAAAAAYQhLIWRmItRlpUeFFRbEtibjd6Q3lnblQtdwAAAAAFvZHMFldwbnp2Q0txU0FhZU9iRWQxTG5XNmcAAAAABhCEsRZGYi1GWlR4UVFsS2JuN3pDeWduVC13AAAAAAV0J3oWS3pRcnNDVkhRVnVnbURVbXZPTXN5UQAAAAAFdCd2Fkt6UXJzQ1ZIUVZ1Z21EVW12T01zeVEAAAAABW9PaRZsaTMwV1B6UVJ1bTZYQWNhMTFCUTVRAAAAAAVvT2UWbGkzMFdQelFSdW02WEFjYTExQlE1UQAAAAAFb09kFmxpMzBXUHpRUnVtNlhBY2ExMUJRNVEAAAAABXQneRZLelFyc0NWSFFWdWdtRFVtdk9Nc3lRAAAAAAVvT2gWbGkzMFdQelFSdW02WEFjYTExQlE1UQAAAAAGEIS2FkZiLUZaVHhRUWxLYm43ekN5Z25ULXcAAAAABW9PahZsaTMwV1B6UVJ1bTZYQWNhMTFCUTVRAAAAAAVvT2YWbGkzMFdQelFSdW02WEFjYTExQlE1UQAAAAAFdCd4Fkt6UXJzQ1ZIUVZ1Z21EVW12T01zeVEAAAAABb2RzhZXcG56dkNLcVNBYWVPYkVkMUxuVzZnAAAAAAW9kc0WV3BuenZDS3FTQWFlT2JFZDFMblc2ZwAAAAAFb09sFmxpMzBXUHpRUnVtNlhBY2ExMUJRNVEAAAAABW9PaxZsaTMwV1B6UVJ```

## Full Help Output

`python iconik_csv_io.py --help`

```
Import/Export metadata using CSV Files

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Path to custom config file
  -m MODE, --mode MODE  Must be either 'collection' or 'saved_search' or 'search'
  -s SEARCH_TERMS, --search_terms SEARCH_TERMS
                        Search string
  -v METADATA_VIEW, --metadata_view METADATA_VIEW
                        UUID of metadata view you want to work with
  -a APP_ID, --app_id APP_ID
                        iconik App-ID
  -t AUTH_TOKEN, --auth_token AUTH_TOKEN
                        iconik Auth Token
  -i INPUT_FILE, --input_file INPUT_FILE
                        Properly formatted importable CSV file
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Destination for exported CSV directory

Args that start with '--' (eg. -m) can also be set in a config file (config.ini or specified via -c). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then
commandline values override config file values which override defaults.
```