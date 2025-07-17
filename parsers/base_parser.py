from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    Base class for all parsers.
    Provides common functionality and enforces a standard interface.
    """
    
    def __init__(self, source_file, output_directory, **options):
        """
        Initialize parser with source file and output directory.
        
        Args:
            source_file (str): Path to the input file
            output_directory (str): Directory where output will be saved
        """
        self.source_file = source_file
        self.output_directory = output_directory

    @abstractmethod
    def process(self):
        """
        Main processing method that must be implemented by each parser.
        """
        pass

    def get_available_operations(self):
        """
        Return list of available operations for this parser.
        Override this method to specify custom operations.
        """
        return ['process']

    def run_operation(self, operation_name):
        """
        Execute a specific operation by name.
        
        Args:
            operation_name (str): Name of the parser to run
        Returns:
            bool: True if successful, False otherwise
        """
        if operation_name not in self.get_available_operations():
            raise ValueError(f"Parser '{operation_name}' not available. "
                           f"Parsers available: {self.get_available_operations()}")
        
        method = getattr(self, operation_name, None)
        if method and callable(method):
            return method()
        else:
            raise NotImplementedError(f"Parser '{operation_name}' not implemented")
