import os
import xml.etree.ElementTree as ET
import csv
from parsers.base_parser import BaseParser
from utils.logger import log


class XmlToCsvParser(BaseParser):
    """
    Parser for handling XML files.
    Supports converting XML to CSV.
    """
    
    def get_available_operations(self):
        """Return all available XML operations."""
        return ['xml_to_csv']

    def process(self):
        """Default operation - convert XML to CSV."""
        return self.xml_to_csv()

    def xml_to_csv(self):
        """
        Convert XML file to CSV format.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            tree = ET.parse(self.source_file)
            root = tree.getroot()
            
            os.makedirs(self.output_directory, exist_ok=True)
            
            output_filename = os.path.basename(self.source_file).replace('.xml', '.csv')
            output_path = os.path.join(self.output_directory, output_filename)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if len(root) > 0:
                    headers = [elem.tag for elem in root[0]]
                    writer.writerow(headers)
                    
                    for element in root:
                        row = [elem.text or '' for elem in element]
                        writer.writerow(row)
                else:
                    log(f"Warning: XML file {self.source_file} has no data elements", error=True)
                    return False
            
            log(f"Successfully converted XML to CSV: {self.source_file} -> {output_path}")
            return True
            
        except ET.ParseError as e:
            log(f"Error: {self.source_file} is not a valid XML file: {e}", error=True)
            return False
        except Exception as e:
            log(f"Error converting XML to CSV {self.source_file}: {e}", error=True)
            return False