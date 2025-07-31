"""
Test Models Module

This module contains models for representing test cases, test suites,
and test results with improved validation and reporting capabilities.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class TestStatus(Enum):
    """Enumeration of test statuses."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestFormat(Enum):
    """Enumeration of supported test file formats."""
    CSV = "csv"
    TST = "tst"
    JSON = "json"


@dataclass(frozen=True)
class TestVector:
    """Represents a single test case with inputs and expected outputs."""
    test_id: str
    inputs: Dict[str, int]
    expected_outputs: Dict[str, int]
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate test vector after initialization."""
        if not self.test_id or not self.test_id.strip():
            raise ValueError("Test ID cannot be empty")
        
        if not self.inputs:
            raise ValueError("Test vector must have at least one input")
        
        if not self.expected_outputs:
            raise ValueError("Test vector must have at least one expected output")
        
        # Validate input values
        for pin_name, value in self.inputs.items():
            if not pin_name or not pin_name.strip():
                raise ValueError("Input pin name cannot be empty")
            if value not in (0, 1):
                raise ValueError(f"Input value must be 0 or 1, got {value} for pin {pin_name}")
        
        # Validate expected output values
        for pin_name, value in self.expected_outputs.items():
            if not pin_name or not pin_name.strip():
                raise ValueError("Output pin name cannot be empty")
            if value not in (0, 1):
                raise ValueError(f"Expected output value must be 0 or 1, got {value} for pin {pin_name}")
    
    @property
    def input_pins(self) -> List[str]:
        """Get list of input pin names."""
        return list(self.inputs.keys())
    
    @property
    def output_pins(self) -> List[str]:
        """Get list of expected output pin names."""
        return list(self.expected_outputs.keys())
    
    def format_inputs(self) -> str:
        """Format inputs as a readable string."""
        return ", ".join(f"{pin}={value}" for pin, value in self.inputs.items())
    
    def format_expected_outputs(self) -> str:
        """Format expected outputs as a readable string."""
        return ", ".join(f"{pin}={value}" for pin, value in self.expected_outputs.items())


@dataclass
class TestResult:
    """Represents the result of executing a single test case."""
    test_vector: TestVector
    actual_outputs: Dict[str, int] = field(default_factory=dict)
    status: TestStatus = TestStatus.PENDING
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def passed(self) -> bool:
        """Check if the test passed."""
        return self.status == TestStatus.PASSED
    
    @property
    def failed(self) -> bool:
        """Check if the test failed."""
        return self.status == TestStatus.FAILED
    
    @property
    def has_error(self) -> bool:
        """Check if the test encountered an error."""
        return self.status == TestStatus.ERROR
    
    def mark_passed(self):
        """Mark the test as passed."""
        self.status = TestStatus.PASSED
        self.error_message = None
    
    def mark_failed(self, reason: str):
        """Mark the test as failed with a reason."""
        self.status = TestStatus.FAILED
        self.error_message = reason
    
    def mark_error(self, error: str):
        """Mark the test as having an error."""
        self.status = TestStatus.ERROR
        self.error_message = error
    
    def get_differences(self) -> Dict[str, Dict[str, int]]:
        """Get differences between expected and actual outputs."""
        differences = {}
        
        for pin_name, expected_value in self.test_vector.expected_outputs.items():
            actual_value = self.actual_outputs.get(pin_name)
            if actual_value != expected_value:
                differences[pin_name] = {
                    'expected': expected_value,
                    'actual': actual_value if actual_value is not None else -1
                }
        
        return differences
    
    def format_actual_outputs(self) -> str:
        """Format actual outputs as a readable string."""
        if not self.actual_outputs:
            return ""
        return ", ".join(f"{pin}={value}" for pin, value in self.actual_outputs.items())
    
    def get_status_symbol(self) -> str:
        """Get a visual symbol for the test status."""
        status_symbols = {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.SKIPPED: "⊝",
            TestStatus.PENDING: "○",
            TestStatus.RUNNING: "⟳"
        }
        return status_symbols.get(self.status, "?")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary for serialization."""
        return {
            'test_id': self.test_vector.test_id,
            'inputs': self.test_vector.inputs,
            'expected_outputs': self.test_vector.expected_outputs,
            'actual_outputs': self.actual_outputs,
            'status': self.status.value,
            'error_message': self.error_message,
            'execution_time_ms': self.execution_time_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'differences': self.get_differences()
        }


@dataclass
class TestSuite:
    """Represents a complete test suite for a chip."""
    chip_name: str
    test_vectors: List[TestVector]
    input_pins: List[str] = field(default_factory=list)
    output_pins: List[str] = field(default_factory=list)
    description: Optional[str] = None
    source_file: Optional[str] = None
    format_type: TestFormat = TestFormat.CSV
    
    def __post_init__(self):
        """Validate and initialize test suite."""
        if not self.chip_name or not self.chip_name.strip():
            raise ValueError("Chip name cannot be empty")
        
        if not self.test_vectors:
            raise ValueError("Test suite must have at least one test vector")
        
        # Auto-detect pins if not provided
        if not self.input_pins or not self.output_pins:
            self._detect_pins()
        
        # Validate consistency
        self._validate_consistency()
    
    def _detect_pins(self):
        """Automatically detect input and output pins from test vectors."""
        if self.test_vectors:
            first_vector = self.test_vectors[0]
            if not self.input_pins:
                self.input_pins = first_vector.input_pins
            if not self.output_pins:
                self.output_pins = first_vector.output_pins
    
    def _validate_consistency(self):
        """Validate that all test vectors have consistent pins."""
        expected_inputs = set(self.input_pins)
        expected_outputs = set(self.output_pins)
        
        for i, vector in enumerate(self.test_vectors):
            vector_inputs = set(vector.input_pins)
            vector_outputs = set(vector.output_pins)
            
            if vector_inputs != expected_inputs:
                raise ValueError(f"Test vector {i} has inconsistent input pins: "
                               f"expected {expected_inputs}, got {vector_inputs}")
            
            if vector_outputs != expected_outputs:
                raise ValueError(f"Test vector {i} has inconsistent output pins: "
                               f"expected {expected_outputs}, got {vector_outputs}")
    
    @property
    def test_count(self) -> int:
        """Get the number of test vectors."""
        return len(self.test_vectors)
    
    @property
    def all_pins(self) -> List[str]:
        """Get all pin names (inputs + outputs)."""
        return self.input_pins + self.output_pins
    
    def get_test_by_id(self, test_id: str) -> Optional[TestVector]:
        """Get a test vector by its ID."""
        for vector in self.test_vectors:
            if vector.test_id == test_id:
                return vector
        return None
    
    def filter_tests(self, predicate) -> 'TestSuite':
        """Create a new test suite with filtered test vectors."""
        filtered_vectors = [v for v in self.test_vectors if predicate(v)]
        return TestSuite(
            chip_name=self.chip_name,
            test_vectors=filtered_vectors,
            input_pins=self.input_pins.copy(),
            output_pins=self.output_pins.copy(),
            description=self.description,
            source_file=self.source_file,
            format_type=self.format_type
        )


@dataclass
class TestReport:
    """Represents a complete test execution report."""
    chip_name: str
    test_suite: TestSuite
    test_results: List[TestResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_execution_time_ms: Optional[float] = None
    
    def __post_init__(self):
        """Initialize report with default start time."""
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def add_result(self, result: TestResult):
        """Add a test result to the report."""
        self.test_results.append(result)
    
    def finish(self):
        """Mark the report as finished and calculate total time."""
        self.end_time = datetime.now()
        if self.start_time:
            delta = self.end_time - self.start_time
            self.total_execution_time_ms = delta.total_seconds() * 1000
    
    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return len(self.test_results)
    
    @property
    def passed_tests(self) -> int:
        """Get number of passed tests."""
        return sum(1 for result in self.test_results if result.passed)
    
    @property
    def failed_tests(self) -> int:
        """Get number of failed tests."""
        return sum(1 for result in self.test_results if result.failed)
    
    @property
    def error_tests(self) -> int:
        """Get number of tests with errors."""
        return sum(1 for result in self.test_results if result.has_error)
    
    @property
    def pass_rate(self) -> float:
        """Get pass rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return self.passed_tests == self.total_tests and self.total_tests > 0
    
    def get_failed_results(self) -> List[TestResult]:
        """Get all failed test results."""
        return [result for result in self.test_results if result.failed]
    
    def get_error_results(self) -> List[TestResult]:
        """Get all test results with errors."""
        return [result for result in self.test_results if result.has_error]
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert report to summary dictionary."""
        return {
            'chip_name': self.chip_name,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'error_tests': self.error_tests,
            'pass_rate': self.pass_rate,
            'all_passed': self.all_passed,
            'execution_time_ms': self.total_execution_time_ms,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def to_detailed_dict(self) -> Dict[str, Any]:
        """Convert report to detailed dictionary including all results."""
        summary = self.to_summary_dict()
        summary['test_results'] = [result.to_dict() for result in self.test_results]
        summary['test_suite'] = {
            'input_pins': self.test_suite.input_pins,
            'output_pins': self.test_suite.output_pins,
            'test_count': self.test_suite.test_count,
            'source_file': self.test_suite.source_file,
            'format_type': self.test_suite.format_type.value
        }
        return summary


# Factory functions for creating test objects

def create_test_vector(test_id: str, inputs: Dict[str, int], 
                      expected_outputs: Dict[str, int],
                      description: Optional[str] = None) -> TestVector:
    """Factory function to create test vectors with validation."""
    return TestVector(
        test_id=test_id,
        inputs=inputs,
        expected_outputs=expected_outputs,
        description=description
    )


def create_test_suite(chip_name: str, test_vectors: List[TestVector],
                     source_file: Optional[str] = None,
                     description: Optional[str] = None) -> TestSuite:
    """Factory function to create test suites."""
    return TestSuite(
        chip_name=chip_name,
        test_vectors=test_vectors,
        source_file=source_file,
        description=description
    ) 