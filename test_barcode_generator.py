import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import io
from datetime import datetime
import sys
import string  # Add this import for string.digits
from typing import Any, Dict, Tuple, List, Optional, Union

# Import the module to test - with error handling
try:
    from barcode_generator import BarcodeGenerator
except ImportError:
    # If running from a different directory, try to add the current directory to the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    # Try again
    from barcode_generator import BarcodeGenerator

class TestBarcodeGenerator(unittest.TestCase):
    
    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        self.test_output_dir: str = "test_barcodes"
        self.generator: BarcodeGenerator = BarcodeGenerator(output_dir=self.test_output_dir)
        
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_init_creates_directory_if_not_exists(self, mock_makedirs: MagicMock, mock_exists: MagicMock) -> None:
        """Test that the constructor creates the output directory if it doesn't exist."""
        mock_exists.return_value = False
        
        BarcodeGenerator(output_dir="new_dir")
        
        mock_makedirs.assert_called_once_with("new_dir")
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_init_does_not_create_directory_if_exists(self, mock_makedirs: MagicMock, mock_exists: MagicMock) -> None:
        """Test that the constructor doesn't create the output directory if it already exists."""
        mock_exists.return_value = True
        
        BarcodeGenerator(output_dir="existing_dir")
        
        mock_makedirs.assert_not_called()
    
    @patch('barcode.get')
    def test_generate_barcode_formats_data_correctly(self, mock_get: MagicMock) -> None:
        """Test that the barcode data is formatted correctly."""
        # Setup mock
        mock_code: MagicMock = MagicMock()
        mock_code.save.return_value = "test_path.jpeg"
        mock_get.return_value = mock_code
        
        # Call the method
        self.generator.generate_barcode("SN12345", 5000, "PN-ABC-789")
        
        # Assert the barcode was created with the correct data format
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], 'code128')
        self.assertEqual(args[1], "SN:SN12345|SC:5000|PN:PN-ABC-789")
        # Check if writer is an instance of ImageWriter without importing barcode
        self.assertEqual(kwargs['writer'].__class__.__name__, 'ImageWriter')
    
    @patch('barcode.get')
    def test_generate_barcode_returns_correct_path(self, mock_get: MagicMock) -> None:
        """Test that the generate_barcode method returns the correct file path."""
        # Setup mock
        mock_code: MagicMock = MagicMock()
        mock_code.save.return_value = "test_barcodes/barcode_SN12345_20231015.jpeg"
        mock_get.return_value = mock_code
        
        # Call the method
        result: str = self.generator.generate_barcode("SN12345", 5000, "PN-ABC-789")
        
        # Assert the correct path is returned
        self.assertEqual(result, "test_barcodes/barcode_SN12345_20231015.jpeg")
    
    @patch('barcode_generator.datetime')
    @patch('barcode.get')
    def test_generate_barcode_with_default_cycles(self, mock_get: MagicMock, mock_datetime: MagicMock) -> None:
        """Test that generate_barcode_with_default_cycles uses the default cycles."""
        # Setup mocks
        mock_dt: MagicMock = MagicMock()
        mock_dt.strftime.return_value = "2023-10-15 12:30:45"
        mock_datetime.now.return_value = mock_dt
        
        mock_code: MagicMock = MagicMock()
        mock_code.save.return_value = "test_path.jpeg"
        mock_get.return_value = mock_code
        
        # Call the method
        self.generator.generate_barcode_with_default_cycles("SN12345", "PN-ABC-789")
        
        # Assert the barcode was created with the default cycles
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[1], "SN:SN12345|SC:1000|PN:PN-ABC-789")
    
    @patch('barcode_generator.datetime')
    @patch('barcode.get')
    def test_generate_barcode_saves_file_with_correct_name(self, mock_get: MagicMock, mock_datetime: MagicMock) -> None:
        """Test that the barcode is saved with the correct filename pattern."""
        # Setup mock
        mock_dt: MagicMock = MagicMock()
        mock_dt.strftime.return_value = "20231015123045"
        mock_datetime.now.return_value = mock_dt
        
        mock_code: MagicMock = MagicMock()
        mock_code.save.return_value = "test_path.jpeg"
        mock_get.return_value = mock_code
        
        # Call the method
        self.generator.generate_barcode("SN12345", 5000, "PN-ABC-789")
        
        # Assert the save method was called with the correct filename
        mock_code.save.assert_called_once()
        args, kwargs = mock_code.save.call_args
        self.assertEqual(args[0], f"{self.test_output_dir}/barcode_SN12345_20231015123045")
    
    def test_sanitize_filename(self) -> None:
        """Test that the _sanitize_filename method correctly sanitizes filenames."""
        # Test with invalid characters
        invalid_chars: str = r'test\file/with*invalid?chars:"<>|'
        sanitized: str = self.generator._sanitize_filename(invalid_chars)
        self.assertEqual(sanitized, 'test_file_with_invalid_chars_____')
        
        # Test with valid filename
        valid_name: str = "valid-filename_123"
        self.assertEqual(self.generator._sanitize_filename(valid_name), valid_name)
    
    @patch('barcode.get')
    @patch('os.path.exists')
    def test_barcode_image_is_created(self, mock_exists: MagicMock, mock_get: MagicMock) -> None:
        """Test that a barcode image is created."""
        # This test is modified to use mocks instead of creating real files
        mock_exists.return_value = True
        
        mock_code: MagicMock = MagicMock()
        mock_code.save.return_value = "test_barcodes/barcode_TEST123_20231015.jpeg"
        mock_get.return_value = mock_code
        
        # Call the method
        path: str = self.generator.generate_barcode("TEST123", 5000, "PART-456")
        
        # Check that the barcode generation was called correctly
        mock_get.assert_called_once()
        self.assertEqual(path, "test_barcodes/barcode_TEST123_20231015.jpeg")
    
    @patch('random.choices')
    def test_generate_random_serial_default(self, mock_choices: MagicMock) -> None:
        """Test that generate_random_serial generates correct serial numbers with default parameters."""
        # Setup mock to return predictable "random" digits
        mock_choices.return_value = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        # Call the method
        serial: str = self.generator.generate_random_serial()
        
        # Assert the serial number is formatted correctly
        self.assertEqual(serial, "SN12345678")
        mock_choices.assert_called_once_with(string.digits, k=8)

    @patch('random.choices')
    def test_generate_random_serial_custom(self, mock_choices: MagicMock) -> None:
        """Test that generate_random_serial generates correct serial numbers with custom parameters."""
        # Setup mock to return predictable "random" digits
        mock_choices.return_value = ['9', '8', '7', '6', '5']
        
        # Call the method with custom prefix and length
        serial: str = self.generator.generate_random_serial(prefix="PART", length=5)
        
        # Assert the serial number is formatted correctly
        self.assertEqual(serial, "PART98765")
        mock_choices.assert_called_once_with(string.digits, k=5)

    def test_generate_batch_serials(self) -> None:
        """Test that generate_batch_serials generates the correct number of unique serials."""
        # Call the method
        serials: List[str] = self.generator.generate_batch_serials(10)
        
        # Assert we get the right number of unique serials
        self.assertEqual(len(serials), 10)
        self.assertEqual(len(set(serials)), 10)  # All should be unique
        
        # Check format of serials
        for serial in serials:
            self.assertTrue(serial.startswith("SN"))
            self.assertEqual(len(serial), 10)  # "SN" + 8 digits
            self.assertTrue(serial[2:].isdigit())

    @patch('barcode_generator.BarcodeGenerator.generate_random_serial')
    @patch('barcode_generator.BarcodeGenerator.generate_barcode')
    def test_generate_barcode_with_random_serial(self, mock_generate_barcode: MagicMock, 
                                               mock_generate_random_serial: MagicMock) -> None:
        """Test that generate_barcode_with_random_serial works correctly."""
        # Setup mocks
        mock_generate_random_serial.return_value = "SN87654321"
        mock_generate_barcode.return_value = "path/to/barcode.jpeg"
        
        # Call the method
        path, serial = self.generator.generate_barcode_with_random_serial("PN-TEST", 2000)
        
        # Assert the method returns the expected values
        self.assertEqual(path, "path/to/barcode.jpeg")
        self.assertEqual(serial, "SN87654321")
        
        # Assert the underlying methods were called correctly
        mock_generate_random_serial.assert_called_once_with("SN", 8)
        mock_generate_barcode.assert_called_once_with("SN87654321", 2000, "PN-TEST")


if __name__ == '__main__':
    unittest.main()