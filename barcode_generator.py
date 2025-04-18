import barcode
from barcode.writer import ImageWriter
from datetime import datetime
import os
import re
import random
import string
from typing import Optional, Union, Any, List

class BarcodeGenerator:
    def __init__(self, output_dir: str = "barcodes") -> None:
        """
        Initialize the barcode generator with an output directory.
        
        Args:
            output_dir: Directory where barcodes will be saved
        """
        self.output_dir: str = output_dir
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize the filename to remove invalid characters.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            A sanitized filename
        """
        # Replace invalid filename characters with underscores
        return re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    def generate_random_serial(self, prefix: str = "SN", length: int = 8) -> str:
        """
        Generate a random serial number with the specified length.
        
        Args:
            prefix: Prefix for the serial number (default: "SN")
            length: Length of the numeric part of the serial number (default: 8)
            
        Returns:
            A random serial number string
        """
        # Generate random digits for the serial number
        digits: str = ''.join(random.choices(string.digits, k=length))
        
        # Return the serial number with prefix
        return f"{prefix}{digits}"
    
    def generate_batch_serials(self, count: int, prefix: str = "SN", length: int = 8) -> List[str]:
        """
        Generate a batch of unique random serial numbers.
        
        Args:
            count: Number of serial numbers to generate
            prefix: Prefix for the serial numbers (default: "SN")
            length: Length of the numeric part of the serial numbers (default: 8)
            
        Returns:
            List of unique random serial numbers
        """
        serials: set = set()
        
        # Generate unique serial numbers
        while len(serials) < count:
            serials.add(self.generate_random_serial(prefix, length))
            
        return list(serials)
    
    def generate_barcode(self, serial_number: str, service_cycles: int, part_number: str) -> str:
        """
        Generate a barcode with the specified information.
        
        Args:
            serial_number: The serial number of the part
            service_cycles: The number of machine use cycles before service is required
            part_number: The part number
            
        Returns:
            Path to the generated barcode image
        """
        # Format the data to be encoded in the barcode
        # Format: SN:{serial_number}|SC:{service_cycles}|PN:{part_number}
        # SC = Service Cycles (machine use cycles before service is required)
        barcode_data: str = f"SN:{serial_number}|SC:{service_cycles}|PN:{part_number}"
        print(f'barcode_data: {barcode_data}')
        
        # Generate a filename based on the data
        timestamp: str = datetime.now().strftime("%Y%m%d%H%M%S")
        # Sanitize the serial number for use in filename
        safe_serial: str = self._sanitize_filename(serial_number)
        filename: str = f"{self.output_dir}/barcode_{safe_serial}_{timestamp}"
        
        # Generate the barcode (Code128 is versatile for alphanumeric data)
        code128: Any = barcode.get('code128', barcode_data, writer=ImageWriter(format='JPEG'))
        
        # Save the barcode to a file
        full_path: str = code128.save(filename)
        
        return full_path
    
    def generate_barcode_with_default_cycles(self, serial_number: str, part_number: str, default_cycles: int = 1000) -> str:
        """
        Generate a barcode with default service cycles.
        
        Args:
            serial_number: The serial number of the part
            part_number: The part number
            default_cycles: Default number of machine use cycles before service (default: 1000)
            
        Returns:
            Path to the generated barcode image
        """
        return self.generate_barcode(serial_number, default_cycles, part_number)
    
    def generate_barcode_with_random_serial(self, part_number: str, service_cycles: int, 
                                           prefix: str = "SN", length: int = 8) -> tuple[str, str]:
        """
        Generate a barcode with a random serial number.
        
        Args:
            part_number: The part number
            service_cycles: The number of machine use cycles before service is required
            prefix: Prefix for the serial number (default: "SN")
            length: Length of the numeric part of the serial number (default: 8)
            
        Returns:
            Tuple containing (path to the generated barcode image, generated serial number)
        """
        # Generate a random serial number
        serial_number: str = self.generate_random_serial(prefix, length)
        
        # Generate the barcode
        barcode_path: str = self.generate_barcode(serial_number, service_cycles, part_number)
        
        return barcode_path, serial_number


# Example usage
if __name__ == "__main__":
    generator: BarcodeGenerator = BarcodeGenerator()
    
    # Generate barcode with random serial number
    for _ in range(1, 10):
        barcode_path, serial = generator.generate_barcode_with_random_serial(
            part_number="PN-DEF-456",
            service_cycles=3000
        )
        print(f"Barcode with random serial {serial} generated at: {barcode_path}")

    for _ in range(1, 10):
        barcode_path, serial = generator.generate_barcode_with_random_serial(
            part_number="PN-ABC-123",
            service_cycles=700
        )
        print(f"Barcode with random serial {serial} generated at: {barcode_path}")
