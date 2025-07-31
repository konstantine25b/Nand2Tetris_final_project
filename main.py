#!/usr/bin/env python3
"""
HDL Parser and Chip Testing Framework - Main Entry Point

This is the main entry point for the HDL parser and testing framework.
It provides a command-line interface for testing HDL chips.

Usage:
    python main.py <hdl_file> <test_file> [<hdl_file> <test_file> ...]
    python main.py -h/--help

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

import sys
import argparse
import os
import unittest
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tester import ChipTester
from src.chip_simulator import ChipSimulator
from src.hdl_parser import parse_hdl_file


def run_all_tests():
    """
    Run all unit tests and integration tests for the HDL framework.
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("HDL Parser and Chip Testing Framework - Test Suite")
    print("=" * 60)
    print()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(':', 1)[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} tests failed")
    
    return success


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='HDL Parser and Chip Testing Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s examples/And.hdl examples/And.tst
  %(prog)s examples/And.hdl examples/And.tst examples/Or.hdl examples/Or.tst
  %(prog)s -v examples/Xor.hdl examples/Xor.tst
  %(prog)s --run-all-tests
        """
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='HDL and test file pairs (hdl_file test_file ...)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (default: summary only)'
    )
    
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Show only summary (default behavior)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Base directory for HDL files (default: current directory)'
    )
    
    parser.add_argument(
        '--run-all-tests',
        action='store_true',
        help='Run all unit tests and integration tests'
    )
    
    return parser.parse_args()


def validate_file_pairs(files):
    """
    Validate that files are provided in pairs and exist.
    
    Args:
        files: List of file paths
        
    Returns:
        List of (hdl_file, test_file) tuples
        
    Raises:
        ValueError: If validation fails
    """
    if len(files) % 2 != 0:
        raise ValueError("Files must be provided in pairs: <hdl_file> <test_file>")
    
    file_pairs = []
    for i in range(0, len(files), 2):
        hdl_file = files[i]
        test_file = files[i + 1]
        
        # Check if files exist
        if not os.path.exists(hdl_file):
            raise ValueError(f"HDL file not found: {hdl_file}")
        
        if not os.path.exists(test_file):
            raise ValueError(f"Test file not found: {test_file}")
        
        # Validate file extensions
        if not hdl_file.endswith('.hdl'):
            raise ValueError(f"HDL file must have .hdl extension: {hdl_file}")
        
        if not test_file.endswith('.tst'):
            raise ValueError(f"Test file must have .tst extension: {test_file}")
        
        file_pairs.append((hdl_file, test_file))
    
    return file_pairs


def validate_hdl_file(hdl_file, base_directory):
    """
    Validate that an HDL file can be parsed correctly.
    
    Args:
        hdl_file: Path to HDL file
        base_directory: Base directory for chip resolution
        
    Returns:
        ChipDefinition object
        
    Raises:
        Exception: If parsing fails
    """
    try:
        chip_def = parse_hdl_file(hdl_file)
        print(f"✓ Successfully parsed {hdl_file} (chip: {chip_def.name})")
        return chip_def
    except Exception as e:
        print(f"✗ Failed to parse {hdl_file}: {e}")
        raise


def run_tests(file_pairs, base_directory, verbose=True):
    """
    Run tests for all file pairs.
    
    Args:
        file_pairs: List of (hdl_file, test_file) tuples
        base_directory: Base directory for chip resolution
        verbose: Whether to show verbose output
        
    Returns:
        Overall success status (bool)
    """
    # Determine the directory where HDL files are located
    # Use the directory of the first HDL file as the base directory for chip resolution
    if file_pairs:
        first_hdl_file = file_pairs[0][0]
        hdl_directory = os.path.dirname(os.path.abspath(first_hdl_file))
        if not hdl_directory:
            hdl_directory = base_directory
    else:
        hdl_directory = base_directory
    
    tester = ChipTester(hdl_directory)
    
    print("HDL Parser and Chip Testing Framework")
    print("=" * 50)
    
    # Validate all HDL files first
    print("\nValidating HDL files...")
    for hdl_file, _ in file_pairs:
        validate_hdl_file(hdl_file, hdl_directory)
    
    # Run tests
    test_files = [test_file for _, test_file in file_pairs]
    all_results = tester.run_multiple_tests(test_files, verbose)
    
    # Calculate overall success
    overall_success = True
    for _, (_, stats) in all_results.items():
        if stats['failed'] > 0:
            overall_success = False
            break
    
    return overall_success


def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        
        # Handle running all tests
        if args.run_all_tests:
            success = run_all_tests()
            return 0 if success else 1
        
        # Show help if no files provided
        if not args.files:
            print("HDL Parser and Chip Testing Framework")
            print("=" * 50)
            print("Usage: python main.py <hdl_file> <test_file> [<hdl_file> <test_file> ...]")
            print("\nFor help: python main.py --help")
            print("\nExample:")
            print("  python main.py examples/And.hdl examples/And.tst")
            print("\nTo run all tests:")
            print("  python main.py --run-all-tests")
            return 0
        
        # Validate file pairs
        file_pairs = validate_file_pairs(args.files)
        
        # Determine verbosity
        verbose = args.verbose or not args.summary
        
        # Resolve base directory
        base_directory = os.path.abspath(args.directory)
        if not os.path.exists(base_directory):
            print(f"Error: Base directory does not exist: {base_directory}")
            return 1
        
        # Run tests
        success = run_tests(file_pairs, base_directory, verbose)
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 