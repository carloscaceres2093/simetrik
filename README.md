# SIMETRIK Parser Assessment

This project is a flexible, extensible framework for running data transformation jobs using pluggable parser classes. It supports both local and S3-hosted parser modules, YAML-based logging, and job definitions in JSON format.

## Features
- **Dynamic parser loading**: Use local or S3-hosted Python parser classes.
- **Job definition**: Describe transformations in a JSON file.
- **YAML logging**: Configurable logging to console and file.
- **Kwargs support**: Download parser code and data from S3.

---

## Requirements

### Python Version
- Python 3.12

### Dependencies
```
boto3>=10.26
PyYAML>=6.0
```

### Installation
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install boto3 pyyaml
```

### AWS Credentials Setup

To use S3 download functionality, you need to configure your AWS credentials. Choose one of the following methods:

#### Method 1: AWS CLI Configuration (Recommended)
```bash
aws configure
```
This will prompt you for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., `us-east-1`)
- Default output format (e.g., `json`)

#### Method 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

#### Method 3: Credentials File
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key_here
aws_secret_access_key = your_secret_key_here
```

And `~/.aws/config`:
```ini
[default]
region = us-east-1
```

## Project Structure

```
simetrik/
├── job.runner.py           # Main job runner script
├── job_definition.json     # Example job definition
├── parsers/                # Local parser modules
│   ├── base_parser.py      # Abstract base class for all parsers
│   ├── zip_file_parser.py  # Example: ZIP file parser
│   └── xml_to_csv_parser.py# Example: XML to CSV parser
├── s3/                     # Local mirror of S3 data (for testing)
│   └── ...
├── utils/
│   ├── file_manager.py     # S3/local file utilities and dynamic loader
│   ├── logger.py           # Logging setup and log() function
│   └── logging.yaml        # Logging configuration
└── README.md               # This file
```

---

## How It Works

1. **Job Definition**
   - You define a list of transformations in `job_definition.json`.
   - Each transformation specifies:
     - `origin`: Input file (S3 or local path)
     - `destiny`: Output directory (S3 or local path)
     - `parser`: Method to call on the parser (e.g., `unzip`, `xml_to_csv`)
     - `classname`: Parser class to use (e.g., `ZipFileParser`)
     - `kwargs`: (Optional) Extra arguments to import scripts from s3

2. **Parser Loading**
   - If `scripts_bucket` and `scripts_path` are provided, the runner will download the parser (and its `base_parser.py`) from S3.
   - Otherwise, it loads the parser from the local `parsers/` directory.

3. **Transformation Execution**
   - The runner instantiates the parser class with the input/output paths and kwargs.
   - It calls the specified method (e.g., `unzip`, `xml_to_csv`).
   - Logging is handled via the YAML config in `utils/logging.yaml`.

4. **Logging**
   - All logs go to both the console and `logs.log` file.
   - Noisy logs from AWS libraries are filtered out in `utils/logging.yaml` definition.

---

## How to Run

### 1. Install Dependencies

```bash
pip install boto3 pyyaml
```

### 2. Prepare Your Job Definition

Edit `job_definition.json` to describe your transformations. Example:

```json
{
  "transformations": [
    {
      "object": {
        "origin": "s3://alejo-parsers/workspace1/sources/rutafuente1/miarchivo1.zip",
        "destiny": "s3://alejo-parsers/workspace1/sources/rutafuente2/",
        "parser": "unzip",
        "classname": "ZipFileParser"
      },
      "kwargs": {
        "scripts_path": "scripts/",
        "scripts_bucket": "alejo-scripts"
      }
    },
    {
      "object": {
        "origin": "s3://alejo-parsers/workspace1/sources/rutafuente1/miarchivo2.xml",
        "destiny": "s3://alejo-parsers/workspace1/sources/rutafuente2/",
        "parser": "xml_to_csv",
        "classname": "XmlToCsvParser"
      },
      "kwargs": {
        "delimiter": ";",
        "output_filename": "output.csv"
      }
    }
  ]
}
```

### 3. Run the Job Runner

```bash
python job.runner.py
```

- Logs will appear in the console and in `utils/logs.log`.
- Output files will be written to the specified `destiny` paths.

---

## Adding New Parsers

1. **Local**: Place your parser in `parsers/` and inherit from `BaseParser`.
2. **S3**: Upload your parser and `base_parser.py` to your S3 bucket and set `scripts_bucket`/`scripts_path` in your job definition.
3. **Implement**: Your parser must implement `process()` and `get_available_operations()`.

---

## Example: Writing a Parser

```python
# parsers/my_custom_parser.py
from parsers.base_parser import BaseParser

class MyCustomParser(BaseParser):
    def get_available_operations(self):
        return ['process', 'custom_method']

    def process(self):
        # Default operation
        pass

    def custom_method(self, **kwargs):
        # Your custom logic
        pass
```

---

## Troubleshooting
- **S3 credentials**: Make sure your AWS credentials are set up (e.g., via `aws configure`).
- **Logging issues**: Check `utils/logging.yaml` and `logs.log` for errors.
- **Parser import errors**: Ensure `base_parser.py` is available both locally and in S3 for S3-based parsers.
- **Noisy logs**: AWS and S3 logs are filtered in `logging.yaml`.

---

## Error Handling

The framework includes comprehensive error handling for various scenarios. Here are the common errors and when they occur:

### Parser Loading Errors

#### `ModuleNotFoundError`
**When it happens**: 
- Parser class name doesn't match the module name
- Parser file is missing from local `parsers/` directory
- S3 download failed for remote parsers
**Solution**: 
- Check that class names follow CamelCase convention (e.g., `ZipFileParser`)
- Ensure parser files exist in the correct location
- Verify S3 paths for remote parsers

#### `ImportError`
**When it happens**: 
- Parser class cannot be imported due to syntax errors
- Missing dependencies in the parser module
- `base_parser.py` is not available for S3 parsers
**Solution**: 
- Check parser code for syntax errors
- Ensure all required dependencies are installed
- Verify `base_parser.py` is uploaded to S3 for remote parsers

#### `AttributeError: 'ParserClass' object has no attribute 'method_name'`
**When it happens**: The specified parser method doesn't exist in the parser class.
**Solution**: 
- Check that the method exists in the parser class
- Verify the method name in the job definition matches the actual method name
- Ensure the parser inherits from `BaseParser`


### Job Definition Errors

#### `KeyError`
**When it happens**: Required fields are missing from the job definition.
**Solution**: Ensure all required fields (`origin`, `destiny`, `parser`, `classname`) are present in the job definition.

#### `JSONDecodeError`
**When it happens**: Job definition JSON file is malformed.
**Solution**: Validate JSON syntax using a JSON validator or IDE.

### Recovery Strategies

1. **Check logs first**: Always review `utils/logs.log` for detailed error messages.
2. **Verify credentials**: Ensure AWS credentials are properly configured if you want to get the parsers from s3.
3. **Test file access**: Verify input files exist and are accessible.
4. **Validate job definition**: Use JSON validators to check job definition syntax.
5. **Test parsers individually**: Run parser classes directly to isolate issues.
6. **Check permissions**: Verify file and S3 bucket permissions.

---

