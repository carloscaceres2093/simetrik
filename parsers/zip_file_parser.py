import zipfile
import os
from parsers.base_parser import BaseParser
from utils.logger import log

class ZipFileParser(BaseParser):
    """
    Parser for handling ZIP files.
    """
    
    def get_available_operations(self):
        """Return all available ZIP operations."""
        return ['unzip']

    def process(self):
        """Default operation - extract the ZIP file."""
        return self.unzip()

    def unzip(self, password=None):
        """
        Extract all files from the ZIP archive.
        
        Args:
            password (str, optional): Password for encrypted ZIP files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(self.output_directory, exist_ok=True)
            
            with zipfile.ZipFile(self.source_file, 'r') as zip_file:
                if password:
                    zip_file.extractall(self.output_directory, pwd=password.encode())
                else:
                    zip_file.extractall(self.output_directory)
            
            log(f"Successfully extracted ZIP file: {self.source_file} -> {self.output_directory}")
            return True
            
        except zipfile.BadZipFile:
            log(f"Error: {self.source_file} is not a valid ZIP file", error=True)
            return False
        except Exception as e:
            log(f"Error extracting ZIP file {self.source_file}: {e}", error=True)
            return False

