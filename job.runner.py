import json
import re
import importlib
from utils.file_manager import s3_to_local, load_parser_from_s3
from utils.logger import log

def run_job():
    """
    Execute all transformations defined in the job definition file.
    """
    try:
        with open("job_definition.json") as f:
            job = json.load(f)
        log("Starting job execution...")
        for transformation in job["transformations"]:
            obj = transformation["object"]
            options = transformation.get("kwargs", {})
            operation_name = obj["parser"]
            log(f"Processing transformation {operation_name}")
            success = execute_transformation(
                obj,
                operation_name,
                options
            )
            
            if success:
                log(f"  ✓ Transformation {operation_name} completed successfully")
            else:
                log(f"  ✗ Transformation {operation_name} failed", error=True)
        
        log("Job execution completed")
        
    except FileNotFoundError:
        log("Error: job_definition.json file not found", error=True)
    except json.JSONDecodeError as e:
        log(f"Error: Invalid JSON in job_definition.json: {e}", error=True)
    except Exception as e:
        log(f"Unexpected error during job execution: {e}", error=True)

def execute_transformation(obj, operation_name, options):
    """
    Execute a single transformation.
    
    Args:
        obj (dict): Object containing parser details
        operation_name (str): Name of the operation to perform
        options (dict): Additional options for scripts imports
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        parser = create_parser(obj, options)
        
        if parser is None:
            return False
        
        if hasattr(parser, 'run_operation'):
            result = parser.run_operation(operation_name)
            return result is not False
        else:
            if hasattr(parser, operation_name):
                method = getattr(parser, operation_name)
                method(**options)
                return True
            else:
                parser.process()
                return True
                
    except Exception as e:
        log(f"Error executing transformation: {e}", error=True)
        return False

def create_parser(obj, options):
    """
    Dynamically create a parser instance based on the class name.
    
    Args:
        obj (dict): Object containing parser details
        options (dict): Additional options
        
    Returns:
        BaseParser: Parser instance or None if creation failed
    """
    try:
        source_file = s3_to_local(obj["origin"])
        output_directory = s3_to_local(obj["destiny"])
        parser_class_name = obj["classname"]
    except Exception as e:
        log(f"Error: {e}", error=True)
        return False

    module_name = camel_to_snake(parser_class_name)
    parser_class = load_parser_from_s3(module_name, parser_class_name, options)

    if not parser_class:
        log(f"Local parser {module_name} loaded")
        try:
            
            module = importlib.import_module(f"parsers.{module_name}")
            
            parser_class = getattr(module, parser_class_name)
            
            return parser_class(source_file, output_directory, **options)
            
        except ImportError as e:
            log(f"Error: Could not import parser module for '{parser_class_name}': {e}", error=True)
            return None
        except AttributeError as e:
            log(f"Error: Class '{parser_class_name}' not found in module: {e}", error=True)
            return None
        except Exception as e:
            log(f"Error creating parser '{parser_class_name}': {e}", error=True)
            return None
    else:
        return parser_class(source_file, output_directory)

def camel_to_snake(name):
    """
    Convert a camel case string to a snake case string.
    Args:
        name (str): The camel case string to convert
    Returns:
        str: The snake case string
    """
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

if __name__ == "__main__":
    run_job()
