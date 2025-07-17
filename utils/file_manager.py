import os
import boto3
import tempfile
import importlib.util
from botocore.exceptions import ClientError, NoCredentialsError
from utils.logger import log

def s3_to_local(s3_path):
    """
    Convert an S3 path to a local path.
    """
    return s3_path.replace("s3://", "s3/")


def download_from_s3(parser_file_name, kwargs):
    """
    Download a parser file from S3 to local storage.
    
    Args:
        parser_file_name (str): Name of the parser file to download
        kwargs (dict): Contains optional parameters for the parser
        
    Returns:
        str: Local path where file was saved
    """
    try:

        bucket_name = kwargs["scripts_bucket"]
        object_key = kwargs["scripts_path"] + parser_file_name + ".py"

        s3_client = boto3.client('s3')
        
        filename = os.path.basename(object_key)
        local_path = os.path.join(tempfile.gettempdir(), f"s3_download_{filename}")
        
        s3_client.download_file(bucket_name, object_key, local_path)
        
        return local_path
        
    except NoCredentialsError:
        raise Exception("AWS credentials not found. Please configure your AWS credentials.")
    except ClientError as e:
        raise Exception(f"Error downloading from S3: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error downloading from S3: {e}")

def load_parser_from_s3(parser_file_name, class_name, kwargs):
    """
    Load a parser class from an S3 file.
    
    Args:
        parser_file_name (str): Name of the parser file to load
        class_name (str): Name of the parser class to load
        kwargs (dict): Contains optional parameters for the parser
        
    Returns:
        class: The parser class
    """
    try:
        download_from_s3("base_parser",kwargs)
        local_file_path = download_from_s3(parser_file_name, kwargs)
        module_name = f"s3_parser_{os.path.basename(local_file_path).replace('.py', '')}"
        spec = importlib.util.spec_from_file_location(module_name, local_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, class_name):
            parser_class = getattr(module, class_name)
            log(f"S3 parser {parser_file_name} loaded")
            return parser_class
        else:
            log(f"Parser '{parser_file_name}' not found in {kwargs['scripts_path']}")
            return None
            
    except Exception as e:
        log(f"Could not load parser {parser_file_name} from S3")
        return None
