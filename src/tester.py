"""
Testing Framework - reads test files and runs chip tests

Parses CSV test files and compares expected vs actual outputs.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import csv
import io
from .chip_simulator import ChipSimulator


@dataclass
class TestCase:
    """Single test case with inputs and expected outputs."""
    inputs: Dict[str, int]
    expected_outputs: Dict[str, int]


@dataclass
class TestResult:
    """Result of running one test case."""
    test_case: TestCase
    actual_outputs: Dict[str, int]
    passed: bool
    message: str


@dataclass
class TestSuite:
    """Collection of test cases for one chip."""
    chip_name: str
    input_pins: List[str]
    output_pins: List[str]
    test_cases: List[TestCase]


class TestVectorParser:
    """Parses CSV-style test files."""
    
    def parse_file(self, filepath: str) -> TestSuite:
        """Parse a test file and return all test cases."""
        with open(filepath, 'r') as file:
            content = file.read()
        
        return self.parse_text(content, filepath)
    
    def parse_text(self, text: str, source_name: str = "test") -> TestSuite:
        """Parse test content from string."""
        lines = text.strip().split('\n')
        if not lines:
            raise ValueError("Empty test file")
        
        # First line is header: "a,b;out"
        header = lines[0].strip()
        input_pins, output_pins = self._parse_header(header)
        
        # Rest are test cases
        test_cases = []
        for i, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if line:  # Skip empty lines
                test_case = self._parse_test_case(line, input_pins, output_pins, i)
                test_cases.append(test_case)
        
        # Figure out chip name from filename
        chip_name = self._extract_chip_name(source_name)
        
        return TestSuite(
            chip_name=chip_name,
            input_pins=input_pins,
            output_pins=output_pins,
            test_cases=test_cases
        )
    
    def _parse_header(self, header: str) -> Tuple[List[str], List[str]]:
        """
        Parse header line like "a,b;out" or "in,sel;a,b".
        Returns (input_pins, output_pins).
        """
        if ';' not in header:
            raise ValueError(f"Invalid header format: {header}. Expected 'inputs;outputs'")
        
        inputs_part, outputs_part = header.split(';', 1)
        
        # Parse input pins
        input_pins = [pin.strip() for pin in inputs_part.split(',') if pin.strip()]
        if not input_pins:
            raise ValueError("No input pins found in header")
        
        # Parse output pins
        output_pins = [pin.strip() for pin in outputs_part.split(',') if pin.strip()]
        if not output_pins:
            raise ValueError("No output pins found in header")
        
        return input_pins, output_pins
    
    def _parse_test_case(self, line: str, input_pins: List[str], 
                        output_pins: List[str], line_number: int) -> TestCase:
        """Parse one test case line like "0,1;1"."""
        if ';' not in line:
            raise ValueError(f"Line {line_number}: Expected ';' to separate inputs from outputs")
        
        inputs_part, outputs_part = line.split(';', 1)
        
        # Parse input values
        input_values = [val.strip() for val in inputs_part.split(',')]
        if len(input_values) != len(input_pins):
            raise ValueError(f"Line {line_number}: Expected {len(input_pins)} input values, got {len(input_values)}")
        
        # Parse output values
        output_values = [val.strip() for val in outputs_part.split(',')]
        if len(output_values) != len(output_pins):
            raise ValueError(f"Line {line_number}: Expected {len(output_pins)} output values, got {len(output_values)}")
        
        # Convert to integers and build dictionaries
        try:
            inputs = {}
            for i, pin_name in enumerate(input_pins):
                inputs[pin_name] = int(input_values[i])
            
            expected_outputs = {}
            for i, pin_name in enumerate(output_pins):
                expected_outputs[pin_name] = int(output_values[i])
                
        except ValueError as e:
            raise ValueError(f"Line {line_number}: Invalid number format: {e}")
        
        return TestCase(inputs=inputs, expected_outputs=expected_outputs)
    
    def _extract_chip_name(self, source_name: str) -> str:
        """Get chip name from file path like 'examples/And.tst' -> 'And'."""
        import os
        base_name = os.path.basename(source_name)
        # Remove .tst extension
        if base_name.endswith('.tst'):
            return base_name[:-4]
        return base_name


class ChipTester:
    """Main class for running tests on chips."""
    
    def __init__(self, base_directory: str = "."):
        self.simulator = ChipSimulator(base_directory)
        self.parser = TestVectorParser()
    
    def run_test_file(self, test_filepath: str, 
                     verbose: bool = True) -> Tuple[List[TestResult], Dict[str, int]]:
        """
        Run all tests from a file and return results.
        """
        # Parse the test file
        test_suite = self.parser.parse_file(test_filepath)
        
        if verbose:
            print(f"\nTesting chip: {test_suite.chip_name}")
            print("-" * 50)
        
        # Run each test case
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
        """Run one test case and return the result."""
        try:
            # Run the simulation
            actual_outputs = self.simulator.simulate_chip(chip_name, test_case.inputs)
            
            # Check if outputs match what we expected
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
        """Print the result of one test case."""
        # Format input values
        inputs_str = ", ".join(f"{pin}={val}" for pin, val in result.test_case.inputs.items())
        
        # Format expected outputs
        expected_str = ", ".join(f"{pin}={val}" for pin, val in result.test_case.expected_outputs.items())
        
        # Format actual outputs
        actual_str = ", ".join(f"{pin}={val}" for pin, val in result.actual_outputs.items())
        
        # Print with pass/fail indicator
        status_symbol = "✓" if result.passed else "✗"
        print(f"Test case {test_number}: {inputs_str} → Expected: {expected_str}, Got: {actual_str} {status_symbol} {result.message}")
    
    def run_multiple_tests(self, test_files: List[Tuple[str, str]], 
                          verbose: bool = True) -> Dict[str, Dict[str, int]]:
        """
        Run tests for multiple chips.
        test_files is list of (hdl_file, test_file) pairs.
        """
        all_results = {}
        total_passed = 0
        total_tests = 0
        
        for hdl_file, test_file in test_files:
            # Extract chip name from HDL file
            import os
            chip_name = os.path.basename(hdl_file).replace('.hdl', '')
            
            # Run tests for this chip
            results, stats = self.run_test_file(test_file, verbose)
            all_results[chip_name] = stats
            
            total_passed += stats['passed']
            total_tests += stats['total']
        
        # Print overall summary if multiple chips
        if len(test_files) > 1 and verbose:
            print("\n" + "=" * 60)
            print("OVERALL SUMMARY")
            print("=" * 60)
            
            for chip_name, stats in all_results.items():
                pass_rate = stats['pass_rate']
                print(f"{chip_name:<15} : {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%)")
            
            print("-" * 60)
            overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            print(f"{'TOTAL':<15} : {total_passed}/{total_tests} passed ({overall_rate:.1f}%)")
        
        return all_results 