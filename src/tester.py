"""
Testing Framework Module

This module provides functionality to parse test vector files and run
automated tests on chip simulations.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import csv
import io
from .chip_simulator import ChipSimulator


@dataclass
class TestCase:
    """Represents a single test case."""
    inputs: Dict[str, int]
    expected_outputs: Dict[str, int]


@dataclass
class TestResult:
    """Represents the result of a single test case."""
    test_case: TestCase
    actual_outputs: Dict[str, int]
    passed: bool
    message: str


@dataclass
class TestSuite:
    """Represents a complete test suite for a chip."""
    chip_name: str
    input_pins: List[str]
    output_pins: List[str]
    test_cases: List[TestCase]


class TestVectorParser:
    """Parses test vector files in CSV format."""
    
    def parse_file(self, filepath: str) -> TestSuite:
        """
        Parse a test vector file.
        
        Args:
            filepath: Path to the test file
            
        Returns:
            TestSuite object containing all test cases
        """
        with open(filepath, 'r') as file:
            content = file.read()
        
        return self.parse_text(content, filepath)
    
    def parse_text(self, text: str, source_name: str = "test") -> TestSuite:
        """
        Parse test vector text.
        
        Args:
            text: Test vector content as string
            source_name: Name/path of the source for identification
            
        Returns:
            TestSuite object containing all test cases
        """
        lines = text.strip().split('\n')
        if not lines:
            raise ValueError("Empty test file")
        
        # Parse header line
        header = lines[0].strip()
        input_pins, output_pins = self._parse_header(header)
        
        # Parse test cases
        test_cases = []
        for i, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if line:  # Skip empty lines
                test_case = self._parse_test_case(line, input_pins, output_pins, i)
                test_cases.append(test_case)
        
        # Extract chip name from source
        chip_name = self._extract_chip_name(source_name)
        
        return TestSuite(
            chip_name=chip_name,
            input_pins=input_pins,
            output_pins=output_pins,
            test_cases=test_cases
        )
    
    def _parse_header(self, header: str) -> Tuple[List[str], List[str]]:
        """
        Parse the header line to extract input and output pin names.
        
        Args:
            header: Header line (e.g., "a,b;out")
            
        Returns:
            Tuple of (input_pins, output_pins)
        """
        if ';' not in header:
            raise ValueError("Header must contain ';' to separate inputs from outputs")
        
        inputs_part, outputs_part = header.split(';', 1)
        
        input_pins = [pin.strip() for pin in inputs_part.split(',') if pin.strip()]
        output_pins = [pin.strip() for pin in outputs_part.split(',') if pin.strip()]
        
        if not input_pins:
            raise ValueError("No input pins specified in header")
        if not output_pins:
            raise ValueError("No output pins specified in header")
        
        return input_pins, output_pins
    
    def _parse_test_case(self, line: str, input_pins: List[str], 
                        output_pins: List[str], line_number: int) -> TestCase:
        """
        Parse a single test case line.
        
        Args:
            line: Test case line (e.g., "0,1;1")
            input_pins: List of input pin names
            output_pins: List of output pin names
            line_number: Line number for error reporting
            
        Returns:
            TestCase object
        """
        if ';' not in line:
            raise ValueError(f"Line {line_number}: Test case must contain ';' "
                           "to separate inputs from outputs")
        
        inputs_part, outputs_part = line.split(';', 1)
        
        # Parse input values
        input_values_str = [val.strip() for val in inputs_part.split(',')]
        if len(input_values_str) != len(input_pins):
            raise ValueError(f"Line {line_number}: Expected {len(input_pins)} "
                           f"input values, got {len(input_values_str)}")
        
        inputs = {}
        for pin, value_str in zip(input_pins, input_values_str):
            try:
                value = int(value_str)
                if value not in (0, 1):
                    raise ValueError(f"Line {line_number}: Input value must be 0 or 1, "
                                   f"got {value}")
                inputs[pin] = value
            except ValueError as e:
                if "Input value must be 0 or 1" in str(e):
                    raise e
                raise ValueError(f"Line {line_number}: Invalid input value '{value_str}' "
                               f"for pin '{pin}'")
        
        # Parse output values
        output_values_str = [val.strip() for val in outputs_part.split(',')]
        if len(output_values_str) != len(output_pins):
            raise ValueError(f"Line {line_number}: Expected {len(output_pins)} "
                           f"output values, got {len(output_values_str)}")
        
        expected_outputs = {}
        for pin, value_str in zip(output_pins, output_values_str):
            try:
                value = int(value_str)
                if value not in (0, 1):
                    raise ValueError(f"Line {line_number}: Output value must be 0 or 1, "
                                   f"got {value}")
                expected_outputs[pin] = value
            except ValueError as e:
                if "Output value must be 0 or 1" in str(e):
                    raise e
                raise ValueError(f"Line {line_number}: Invalid output value '{value_str}' "
                               f"for pin '{pin}'")
        
        return TestCase(inputs=inputs, expected_outputs=expected_outputs)
    
    def _extract_chip_name(self, source_name: str) -> str:
        """Extract chip name from source file name."""
        import os
        base_name = os.path.basename(source_name)
        if base_name.endswith('.tst'):
            return base_name[:-4]  # Remove .tst extension
        return base_name


class ChipTester:
    """Main testing framework for running chip tests."""
    
    def __init__(self, base_directory: str = "."):
        self.simulator = ChipSimulator(base_directory)
        self.parser = TestVectorParser()
    
    def run_test_file(self, test_filepath: str, 
                     verbose: bool = True) -> Tuple[List[TestResult], Dict[str, int]]:
        """
        Run all tests from a test file.
        
        Args:
            test_filepath: Path to the test file
            verbose: Whether to print detailed output
            
        Returns:
            Tuple of (test_results, summary_stats)
        """
        # Parse test file
        test_suite = self.parser.parse_file(test_filepath)
        
        if verbose:
            print(f"\nTesting chip: {test_suite.chip_name}")
            print("-" * 50)
        
        # Run all test cases
        test_results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_suite.test_cases, start=1):
            result = self._run_single_test(test_suite.chip_name, test_case, i)
            test_results.append(result)
            
            if result.passed:
                passed_count += 1
            
            if verbose:
                self._print_test_result(result, i)
        
        # Print summary
        total_tests = len(test_suite.test_cases)
        pass_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        if verbose:
            print("-" * 50)
            print(f"Summary: {passed_count}/{total_tests} tests passed ({pass_rate:.1f}%)")
            
            if passed_count == total_tests:
                print("✅ All tests PASSED!")
            else:
                failed_count = total_tests - passed_count
                print(f"❌ {failed_count} test(s) FAILED")
        
        summary_stats = {
            'total': total_tests,
            'passed': passed_count,
            'failed': total_tests - passed_count,
            'pass_rate': pass_rate
        }
        
        return test_results, summary_stats
    
    def _run_single_test(self, chip_name: str, test_case: TestCase, 
                        test_number: int) -> TestResult:
        """Run a single test case."""
        try:
            # Simulate the chip
            actual_outputs = self.simulator.simulate_chip(chip_name, test_case.inputs)
            
            # Check if outputs match expected values
            passed = True
            failed_pins = []
            
            for pin, expected_value in test_case.expected_outputs.items():
                actual_value = actual_outputs.get(pin)
                if actual_value != expected_value:
                    passed = False
                    failed_pins.append(f"{pin}: expected {expected_value}, got {actual_value}")
            
            if passed:
                message = "PASS"
            else:
                message = f"FAIL - {', '.join(failed_pins)}"
            
            return TestResult(
                test_case=test_case,
                actual_outputs=actual_outputs,
                passed=passed,
                message=message
            )
            
        except Exception as e:
            return TestResult(
                test_case=test_case,
                actual_outputs={},
                passed=False,
                message=f"ERROR - {str(e)}"
            )
    
    def _print_test_result(self, result: TestResult, test_number: int):
        """Print the result of a single test."""
        # Format inputs
        inputs_str = ", ".join(f"{pin}={value}" 
                              for pin, value in result.test_case.inputs.items())
        
        # Format expected outputs
        expected_str = ", ".join(f"{pin}={value}" 
                               for pin, value in result.test_case.expected_outputs.items())
        
        # Format actual outputs
        actual_str = ", ".join(f"{pin}={value}" 
                             for pin, value in result.actual_outputs.items())
        
        # Status symbol
        status_symbol = "✓" if result.passed else "✗"
        
        print(f"Test case {test_number}: {inputs_str} → "
              f"Expected: {expected_str}, Got: {actual_str} "
              f"{status_symbol} {result.message}")
    
    def run_multiple_tests(self, test_files: List[str], 
                          verbose: bool = True) -> Dict[str, Tuple[List[TestResult], Dict[str, int]]]:
        """
        Run multiple test files.
        
        Args:
            test_files: List of test file paths
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary mapping test file names to their results
        """
        all_results = {}
        overall_stats = {'total': 0, 'passed': 0, 'failed': 0}
        
        for test_file in test_files:
            results, stats = self.run_test_file(test_file, verbose)
            all_results[test_file] = (results, stats)
            
            overall_stats['total'] += stats['total']
            overall_stats['passed'] += stats['passed']
            overall_stats['failed'] += stats['failed']
        
        # Print overall summary
        if verbose and len(test_files) > 1:
            print("\n" + "=" * 60)
            print("OVERALL SUMMARY")
            print("=" * 60)
            
            for test_file, (_, stats) in all_results.items():
                chip_name = test_file.split('/')[-1].replace('.tst', '')
                print(f"{chip_name:20}: {stats['passed']}/{stats['total']} passed "
                      f"({stats['pass_rate']:.1f}%)")
            
            print("-" * 60)
            overall_pass_rate = (overall_stats['passed'] / overall_stats['total'] * 100 
                                if overall_stats['total'] > 0 else 0)
            print(f"{'TOTAL':20}: {overall_stats['passed']}/{overall_stats['total']} passed "
                  f"({overall_pass_rate:.1f}%)")
        
        return all_results


# Example usage and testing
if __name__ == "__main__":
    # Example test vector content
    example_test = """a,b;out
0,0;0
0,1;0
1,0;0
1,1;1"""
    
    parser = TestVectorParser()
    test_suite = parser.parse_text(example_test, "And.tst")
    
    print(f"Parsed test suite for: {test_suite.chip_name}")
    print(f"Input pins: {test_suite.input_pins}")
    print(f"Output pins: {test_suite.output_pins}")
    print(f"Number of test cases: {len(test_suite.test_cases)}")
    
    for i, test_case in enumerate(test_suite.test_cases, start=1):
        print(f"Test {i}: inputs={test_case.inputs}, expected={test_case.expected_outputs}") 