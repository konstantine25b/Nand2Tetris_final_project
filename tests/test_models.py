#!/usr/bin/env python3
"""
Tests for HDL Parser Framework Models

This module contains comprehensive tests for the improved model classes
including chip models, test models, and validation functionality.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

import sys
import os
import unittest
from datetime import datetime
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.chip_models import (
    ChipDefinition, PartInstance, Pin, Connection, SimulationState,
    ChipType, PinType, create_builtin_chip_definition, create_custom_chip_definition
)
from src.models.test_models import (
    TestVector, TestResult, TestSuite, TestReport, TestStatus, TestFormat,
    create_test_vector, create_test_suite
)


class TestChipModels(unittest.TestCase):
    """Test chip model classes."""
    
    def test_pin_validation(self):
        """Test pin validation."""
        # Valid pin
        pin = Pin("test", PinType.INPUT, 1)
        self.assertEqual(pin.name, "test")
        self.assertEqual(pin.pin_type, PinType.INPUT)
        self.assertEqual(pin.value, 1)
        
        # Invalid pin name
        with self.assertRaises(ValueError):
            Pin("", PinType.INPUT)
        
        # Invalid pin value
        with self.assertRaises(ValueError):
            Pin("test", PinType.INPUT, 2)
    
    def test_connection_validation(self):
        """Test connection validation."""
        # Valid connection
        conn = Connection("source", "target")
        self.assertEqual(conn.source_pin, "source")
        self.assertEqual(conn.target_pin, "target")
        
        # Invalid connections
        with self.assertRaises(ValueError):
            Connection("", "target")
        
        with self.assertRaises(ValueError):
            Connection("source", "")
    
    def test_part_instance_validation(self):
        """Test part instance validation."""
        # Valid part instance
        part = PartInstance("And", {"a": "input1", "b": "input2", "out": "output1"}, "and1")
        self.assertEqual(part.chip_type, "And")
        self.assertEqual(part.instance_name, "and1")
        self.assertEqual(len(part.connections), 3)
        
        # Valid part instance without explicit name
        part2 = PartInstance("Nand", {"a": "input1", "b": "input2", "out": "output1"})
        self.assertEqual(part2.chip_type, "Nand")
        self.assertEqual(part2.instance_name, "nand1")  # Auto-generated
        
        # Invalid part instances
        with self.assertRaises(ValueError):
            PartInstance("", {"a": "input1"})
        
        with self.assertRaises(ValueError):
            PartInstance("And", {})
    
    def test_chip_definition_validation(self):
        """Test chip definition validation."""
        # Valid chip definition
        chip = ChipDefinition("TestChip", ["a", "b"], ["out"])
        self.assertEqual(chip.name, "TestChip")
        self.assertEqual(chip.inputs, ["a", "b"])
        self.assertEqual(chip.outputs, ["out"])
        self.assertEqual(chip.chip_type, ChipType.CUSTOM)
        
        # Invalid chip definitions
        with self.assertRaises(ValueError):
            ChipDefinition("", ["a"], ["out"])  # Empty name
        
        with self.assertRaises(ValueError):
            ChipDefinition("TestChip", [], ["out"])  # No inputs
        
        with self.assertRaises(ValueError):
            ChipDefinition("TestChip", ["a"], [])  # No outputs
        
        with self.assertRaises(ValueError):
            ChipDefinition("TestChip", ["a", "a"], ["out"])  # Duplicate pins
    
    def test_chip_definition_properties(self):
        """Test chip definition properties."""
        parts = [PartInstance("Nand", {"a": "a", "b": "b", "out": "internal"}, "nand1")]
        chip = ChipDefinition("TestChip", ["a", "b"], ["out"], parts)
        
        self.assertEqual(chip.all_pins, ["a", "b", "out"])
        self.assertFalse(chip.is_builtin)
        self.assertTrue(chip.is_composite)
        
        internal_signals = chip.get_internal_signals()
        self.assertIn("internal", internal_signals)
    
    def test_simulation_state(self):
        """Test simulation state management."""
        state = SimulationState("TestChip")
        
        # Test input setting
        state.set_input("a", 1)
        self.assertEqual(state.input_values["a"], 1)
        
        # Test invalid input
        with self.assertRaises(ValueError):
            state.set_input("a", 2)
        
        # Test signal retrieval
        state.set_internal_signal("internal", 0)
        self.assertEqual(state.get_signal_value("a"), 1)
        self.assertEqual(state.get_signal_value("internal"), 0)
        self.assertIsNone(state.get_signal_value("nonexistent"))
    
    def test_factory_functions(self):
        """Test factory functions for creating chip definitions."""
        # Builtin chip
        builtin = create_builtin_chip_definition("Nand", ["a", "b"], ["out"])
        self.assertEqual(builtin.chip_type, ChipType.BUILTIN)
        self.assertTrue(builtin.is_builtin)
        
        # Custom chip
        parts = [PartInstance("Nand", {"a": "a", "b": "b", "out": "out"}, "nand1")]
        custom = create_custom_chip_definition("And", ["a", "b"], ["out"], parts)
        self.assertEqual(custom.chip_type, ChipType.CUSTOM)
        self.assertFalse(custom.is_builtin)


class TestTestModels(unittest.TestCase):
    """Test test model classes."""
    
    def test_test_vector_validation(self):
        """Test test vector validation."""
        # Valid test vector
        vector = TestVector("test1", {"a": 0, "b": 1}, {"out": 0})
        self.assertEqual(vector.test_id, "test1")
        self.assertEqual(len(vector.inputs), 2)
        self.assertEqual(len(vector.expected_outputs), 1)
        
        # Invalid test vectors
        with self.assertRaises(ValueError):
            TestVector("", {"a": 0}, {"out": 0})  # Empty ID
        
        with self.assertRaises(ValueError):
            TestVector("test1", {}, {"out": 0})  # No inputs
        
        with self.assertRaises(ValueError):
            TestVector("test1", {"a": 0}, {})  # No outputs
        
        with self.assertRaises(ValueError):
            TestVector("test1", {"a": 2}, {"out": 0})  # Invalid input value
    
    def test_test_vector_properties(self):
        """Test test vector properties."""
        vector = TestVector("test1", {"a": 0, "b": 1}, {"out": 0, "carry": 1})
        
        self.assertEqual(vector.input_pins, ["a", "b"])
        self.assertEqual(set(vector.output_pins), {"out", "carry"})
        self.assertEqual(vector.format_inputs(), "a=0, b=1")
        self.assertIn("out=0", vector.format_expected_outputs())
        self.assertIn("carry=1", vector.format_expected_outputs())
    
    def test_test_result(self):
        """Test test result functionality."""
        vector = TestVector("test1", {"a": 0, "b": 1}, {"out": 0})
        result = TestResult(vector)
        
        # Initial state
        self.assertEqual(result.status, TestStatus.PENDING)
        self.assertFalse(result.passed)
        self.assertFalse(result.failed)
        self.assertFalse(result.has_error)
        
        # Mark as passed
        result.actual_outputs = {"out": 0}
        result.mark_passed()
        self.assertTrue(result.passed)
        self.assertEqual(result.status, TestStatus.PASSED)
        
        # Mark as failed
        result.mark_failed("Output mismatch")
        self.assertTrue(result.failed)
        self.assertEqual(result.error_message, "Output mismatch")
        
        # Test differences
        result.actual_outputs = {"out": 1}
        differences = result.get_differences()
        self.assertIn("out", differences)
        self.assertEqual(differences["out"]["expected"], 0)
        self.assertEqual(differences["out"]["actual"], 1)
    
    def test_test_result_symbols(self):
        """Test test result status symbols."""
        vector = TestVector("test1", {"a": 0}, {"out": 0})
        result = TestResult(vector)
        
        result.status = TestStatus.PASSED
        self.assertEqual(result.get_status_symbol(), "✓")
        
        result.status = TestStatus.FAILED
        self.assertEqual(result.get_status_symbol(), "✗")
        
        result.status = TestStatus.ERROR
        self.assertEqual(result.get_status_symbol(), "⚠")
    
    def test_test_suite_validation(self):
        """Test test suite validation."""
        vectors = [
            TestVector("test1", {"a": 0, "b": 0}, {"out": 0}),
            TestVector("test2", {"a": 0, "b": 1}, {"out": 0}),
            TestVector("test3", {"a": 1, "b": 0}, {"out": 0}),
            TestVector("test4", {"a": 1, "b": 1}, {"out": 1})
        ]
        
        # Valid test suite
        suite = TestSuite("And", vectors)
        self.assertEqual(suite.chip_name, "And")
        self.assertEqual(suite.test_count, 4)
        self.assertEqual(suite.input_pins, ["a", "b"])
        self.assertEqual(suite.output_pins, ["out"])
        
        # Invalid test suites
        with self.assertRaises(ValueError):
            TestSuite("", vectors)  # Empty chip name
        
        with self.assertRaises(ValueError):
            TestSuite("And", [])  # No test vectors
    
    def test_test_suite_consistency(self):
        """Test test suite pin consistency validation."""
        vectors = [
            TestVector("test1", {"a": 0, "b": 0}, {"out": 0}),
            TestVector("test2", {"a": 0, "c": 1}, {"out": 0})  # Different input pin
        ]
        
        # Should raise error due to inconsistent input pins
        with self.assertRaises(ValueError):
            TestSuite("BadChip", vectors)
    
    def test_test_suite_filtering(self):
        """Test test suite filtering."""
        vectors = [
            TestVector("test1", {"a": 0, "b": 0}, {"out": 0}),
            TestVector("test2", {"a": 0, "b": 1}, {"out": 0}),
            TestVector("test3", {"a": 1, "b": 0}, {"out": 0}),
            TestVector("test4", {"a": 1, "b": 1}, {"out": 1})
        ]
        
        suite = TestSuite("And", vectors)
        
        # Filter for tests where a=1
        filtered = suite.filter_tests(lambda v: v.inputs.get("a") == 1)
        self.assertEqual(filtered.test_count, 2)
        
        # Find test by ID
        test = suite.get_test_by_id("test3")
        self.assertIsNotNone(test)
        self.assertEqual(test.inputs["a"], 1)
        self.assertEqual(test.inputs["b"], 0)
    
    def test_test_report(self):
        """Test test report functionality."""
        vectors = [TestVector("test1", {"a": 0}, {"out": 1})]
        suite = TestSuite("Not", vectors)
        report = TestReport("Not", suite)
        
        # Initial state
        self.assertEqual(report.total_tests, 0)
        self.assertEqual(report.passed_tests, 0)
        self.assertEqual(report.pass_rate, 0.0)
        self.assertFalse(report.all_passed)
        
        # Add passing result
        result = TestResult(vectors[0])
        result.actual_outputs = {"out": 1}
        result.mark_passed()
        report.add_result(result)
        
        self.assertEqual(report.total_tests, 1)
        self.assertEqual(report.passed_tests, 1)
        self.assertEqual(report.pass_rate, 100.0)
        self.assertTrue(report.all_passed)
        
        # Test report finishing
        report.finish()
        self.assertIsNotNone(report.end_time)
        self.assertIsNotNone(report.total_execution_time_ms)
    
    def test_report_serialization(self):
        """Test test report serialization."""
        vectors = [TestVector("test1", {"a": 0}, {"out": 1})]
        suite = TestSuite("Not", vectors)
        report = TestReport("Not", suite)
        
        result = TestResult(vectors[0])
        result.actual_outputs = {"out": 1}
        result.mark_passed()
        report.add_result(result)
        report.finish()
        
        # Test summary serialization
        summary = report.to_summary_dict()
        self.assertIn("chip_name", summary)
        self.assertIn("total_tests", summary)
        self.assertIn("pass_rate", summary)
        
        # Test detailed serialization
        detailed = report.to_detailed_dict()
        self.assertIn("test_results", detailed)
        self.assertIn("test_suite", detailed)
    
    def test_factory_functions(self):
        """Test factory functions for test objects."""
        # Test vector factory
        vector = create_test_vector("test1", {"a": 0}, {"out": 1})
        self.assertEqual(vector.test_id, "test1")
        
        # Test suite factory
        vectors = [vector]
        suite = create_test_suite("Not", vectors, "Not.tst")
        self.assertEqual(suite.chip_name, "Not")
        self.assertEqual(suite.source_file, "Not.tst")


class TestModelIntegration(unittest.TestCase):
    """Integration tests for model interactions."""
    
    def test_chip_and_test_integration(self):
        """Test integration between chip and test models."""
        # Create a chip definition
        parts = [PartInstance("Nand", {"a": "a", "b": "b", "out": "nandOut"}, "nand1"),
                PartInstance("Not", {"in": "nandOut", "out": "out"}, "not1")]
        chip = ChipDefinition("And", ["a", "b"], ["out"], parts)
        
        # Create test vectors
        vectors = [
            TestVector("test1", {"a": 0, "b": 0}, {"out": 0}),
            TestVector("test2", {"a": 1, "b": 1}, {"out": 1})
        ]
        suite = TestSuite("And", vectors)
        
        # Verify compatibility
        self.assertEqual(chip.name, suite.chip_name)
        self.assertEqual(set(chip.inputs), set(suite.input_pins))
        self.assertEqual(set(chip.outputs), set(suite.output_pins))
    
    def test_validation_scenarios(self):
        """Test various validation scenarios."""
        # Test connection validation
        parts = [PartInstance("Nand", {"a": "unknown_signal", "b": "b", "out": "out"}, "nand1")]
        chip = ChipDefinition("BadChip", ["a", "b"], ["out"], parts)
        
        issues = chip.validate_connections()
        self.assertTrue(len(issues) > 0)
        self.assertIn("unknown_signal", issues[0])


if __name__ == "__main__":
    unittest.main() 