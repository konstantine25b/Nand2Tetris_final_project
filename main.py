#!/usr/bin/env python3
"""
Main entry point for HDL Parser and Testing Framework

Run this to test your HDL chips against test vectors.
"""

import argparse
import os
import sys
import unittest
from typing import List, Tuple
from src.hdl_parser import HDLParser
from src.tester import ChipTester


def validate_file_pairs(files: List[str]) -> List[Tuple[str, str]]:
    """
    Make sure we have pairs of HDL and test files.
    Returns list of (hdl_file, test_file) tuples.
    """
    if len(files) % 2 != 0:
        raise ValueError("Files must be provided in pairs: HDL file followed by test file")
    
    pairs = []
    for i in range(0, len(files), 2):
        hdl_file = files[i]
        test_file = files[i + 1]
        
        # Check files exist
        if not os.path.exists(hdl_file):
            raise FileNotFoundError(f"HDL file not found: {hdl_file}")
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        # Check file extensions
        if not hdl_file.endswith('.hdl'):
            raise ValueError(f"Expected HDL file (.hdl), got: {hdl_file}")
        if not test_file.endswith('.tst'):
            raise ValueError(f"Expected test file (.tst), got: {test_file}")
        
        pairs.append((hdl_file, test_file))
    
    return pairs


def validate_hdl_files(hdl_files: List[str]) -> None:
    """Parse HDL files to make sure they're valid before testing."""
    parser = HDLParser()
    
    print("Validating HDL files...")
    for hdl_file in hdl_files:
        try:
            chip_def = parser.parse_file(hdl_file)
            print(f"✓ Successfully parsed {hdl_file} (chip: {chip_def.name})")
        except Exception as e:
            print(f"✗ Failed to parse {hdl_file}: {e}")
            sys.exit(1)


def run_tests(file_pairs: List[Tuple[str, str]], verbose: bool = True) -> bool:
    """Run tests for all chip pairs and return True if all passed."""
    # Figure out base directory from the first HDL file
    # This is important so the simulator can find referenced chips
    if file_pairs:
        first_hdl_file = file_pairs[0][0]
        hdl_directory = os.path.dirname(os.path.abspath(first_hdl_file))
    else:
        hdl_directory = "."
    
    # Validate HDL files first
    hdl_files = [pair[0] for pair in file_pairs]
    validate_hdl_files(hdl_files)
    
    # Set up tester
    tester = ChipTester(hdl_directory)
    
    # Run tests
    if len(file_pairs) == 1:
        # Single chip test
        hdl_file, test_file = file_pairs[0]
        results, stats = tester.run_test_file(test_file, verbose)
        return stats['passed'] == stats['total']
    else:
        # Multiple chips
        all_results = tester.run_multiple_tests(file_pairs, verbose)
        
        # Check if all tests passed
        total_passed = sum(stats['passed'] for stats in all_results.values())
        total_tests = sum(stats['total'] for stats in all_results.values())
        
        return total_passed == total_tests


def run_all_tests():
    """Run all unit tests in the tests/ directory."""
    print("Running all unit and integration tests...\n")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        success_rate = 100.0
        print(f"Success rate: {success_rate:.1f}%")
        print("\n🎉 ALL TESTS PASSED!")
    else:
        failed = len(result.failures) + len(result.errors)
        success_rate = ((result.testsRun - failed) / result.testsRun * 100) if result.testsRun > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        print(f"\n❌ {failed} test(s) failed")
    
    return result.wasSuccessful()


def main():
    """Main function - parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="HDL Parser and Chip Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py examples/And.hdl examples/And.tst
  python main.py examples/And.hdl examples/And.tst examples/Or.hdl examples/Or.tst
  python main.py --run-all-tests
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
        default=True,
        help='Show detailed test output (default)'
    )
    
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Show only summary output'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Base directory for HDL files (default: current directory)'
    )
    
    parser.add_argument(
        '--run-all-tests',
        action='store_true',
        help='Run all unit and integration tests'
    )
    
    args = parser.parse_args()
    
    # Handle --run-all-tests option
    if args.run_all_tests:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    # Need file arguments if not running all tests
    if not args.files:
        parser.error("Provide HDL and test file pairs, or use --run-all-tests")
    
    try:
        # Print header
        print("HDL Parser and Chip Testing Framework")
        print("=" * 50)
        
        # Validate and process file pairs
        file_pairs = validate_file_pairs(args.files)
        
        # Run tests (verbose unless --summary specified)
        verbose = not args.summary
        success = run_tests(file_pairs, verbose)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 