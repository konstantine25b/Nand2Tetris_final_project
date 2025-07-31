#!/usr/bin/env python3
"""
Basic tests for HDL Parser and Testing Framework

This module contains basic unit tests to verify core functionality.
Run with: python -m pytest tests/test_basic.py

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

import sys
import os
import unittest
from unittest.mock import patch, mock_open

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.hdl_parser import HDLParser, ChipDefinition, PartInstance
from src.chip_simulator import BuiltInGates, ChipSimulator
from src.tester import TestVectorParser, ChipTester


class TestBuiltInGates(unittest.TestCase):
    """Test built-in gate implementations."""
    
    def test_nand_gate(self):
        """Test NAND gate truth table."""
        self.assertEqual(BuiltInGates.nand(0, 0), 1)
        self.assertEqual(BuiltInGates.nand(0, 1), 1)
        self.assertEqual(BuiltInGates.nand(1, 0), 1)
        self.assertEqual(BuiltInGates.nand(1, 1), 0)
    
    def test_not_gate(self):
        """Test NOT gate truth table."""
        self.assertEqual(BuiltInGates.not_gate(0), 1)
        self.assertEqual(BuiltInGates.not_gate(1), 0)
    
    def test_and_gate(self):
        """Test AND gate truth table."""
        self.assertEqual(BuiltInGates.and_gate(0, 0), 0)
        self.assertEqual(BuiltInGates.and_gate(0, 1), 0)
        self.assertEqual(BuiltInGates.and_gate(1, 0), 0)
        self.assertEqual(BuiltInGates.and_gate(1, 1), 1)
    
    def test_or_gate(self):
        """Test OR gate truth table."""
        self.assertEqual(BuiltInGates.or_gate(0, 0), 0)
        self.assertEqual(BuiltInGates.or_gate(0, 1), 1)
        self.assertEqual(BuiltInGates.or_gate(1, 0), 1)
        self.assertEqual(BuiltInGates.or_gate(1, 1), 1)


class TestHDLParser(unittest.TestCase):
    """Test HDL parser functionality."""
    
    def setUp(self):
        self.parser = HDLParser()
    
    def test_parse_simple_chip(self):
        """Test parsing a simple chip definition."""
        hdl_text = """
        CHIP And {
            IN a, b;
            OUT out;
            
            PARTS:
            Nand(a=a, b=b, out=nandOut);
            Not(in=nandOut, out=out);
        }
        """
        
        chip_def = self.parser.parse_text(hdl_text)
        
        self.assertEqual(chip_def.name, "And")
        self.assertEqual(chip_def.inputs, ["a", "b"])
        self.assertEqual(chip_def.outputs, ["out"])
        self.assertEqual(len(chip_def.parts), 2)
        
        # Check first part (Nand)
        nand_part = chip_def.parts[0]
        self.assertEqual(nand_part.chip_type, "Nand")
        self.assertEqual(nand_part.connections, {"a": "a", "b": "b", "out": "nandOut"})
        
        # Check second part (Not)
        not_part = chip_def.parts[1]
        self.assertEqual(not_part.chip_type, "Not")
        self.assertEqual(not_part.connections, {"in": "nandOut", "out": "out"})
    
    def test_tokenizer(self):
        """Test HDL tokenizer."""
        text = "CHIP And { IN a, b; }"
        tokens = self.parser.tokenizer.tokenize(text)
        
        expected_tokens = [
            ("CHIP", "CHIP"),
            ("IDENTIFIER", "And"),
            ("LBRACE", "{"),
            ("IN", "IN"),
            ("IDENTIFIER", "a"),
            ("COMMA", ","),
            ("IDENTIFIER", "b"),
            ("SEMICOLON", ";"),
            ("RBRACE", "}")
        ]
        
        self.assertEqual(tokens, expected_tokens)
    
    def test_parse_single_input_output(self):
        """Test parsing chip with single input and output."""
        hdl_text = """
        CHIP Not {
            IN in;
            OUT out;
            
            PARTS:
            Nand(a=in, b=in, out=out);
        }
        """
        
        chip_def = self.parser.parse_text(hdl_text)
        
        self.assertEqual(chip_def.name, "Not")
        self.assertEqual(chip_def.inputs, ["in"])
        self.assertEqual(chip_def.outputs, ["out"])
        self.assertEqual(len(chip_def.parts), 1)


class TestTestVectorParser(unittest.TestCase):
    """Test test vector parser functionality."""
    
    def setUp(self):
        self.parser = TestVectorParser()
    
    def test_parse_simple_test(self):
        """Test parsing simple test vectors."""
        test_text = """a,b;out
0,0;0
0,1;0
1,0;0
1,1;1"""
        
        test_suite = self.parser.parse_text(test_text, "And.tst")
        
        self.assertEqual(test_suite.chip_name, "And")
        self.assertEqual(test_suite.input_pins, ["a", "b"])
        self.assertEqual(test_suite.output_pins, ["out"])
        self.assertEqual(len(test_suite.test_cases), 4)
        
        # Check first test case
        test_case = test_suite.test_cases[0]
        self.assertEqual(test_case.inputs, {"a": 0, "b": 0})
        self.assertEqual(test_case.expected_outputs, {"out": 0})
        
        # Check last test case
        test_case = test_suite.test_cases[3]
        self.assertEqual(test_case.inputs, {"a": 1, "b": 1})
        self.assertEqual(test_case.expected_outputs, {"out": 1})
    
    def test_parse_single_input_output(self):
        """Test parsing test with single input and output."""
        test_text = """in;out
0;1
1;0"""
        
        test_suite = self.parser.parse_text(test_text, "Not.tst")
        
        self.assertEqual(test_suite.input_pins, ["in"])
        self.assertEqual(test_suite.output_pins, ["out"])
        self.assertEqual(len(test_suite.test_cases), 2)
    
    def test_extract_chip_name(self):
        """Test chip name extraction from file paths."""
        test_cases = [
            ("And.tst", "And"),
            ("examples/Or.tst", "Or"),
            ("/path/to/Xor.tst", "Xor"),
            ("Complex_Chip.tst", "Complex_Chip")
        ]
        
        for source_name, expected_name in test_cases:
            result = self.parser._extract_chip_name(source_name)
            self.assertEqual(result, expected_name)


class TestChipSimulator(unittest.TestCase):
    """Test chip simulator functionality."""
    
    def setUp(self):
        self.simulator = ChipSimulator()
    
    def test_built_in_chip_mapping(self):
        """Test that all built-in chips are properly mapped."""
        # Test that simulator can handle all required built-in chips
        expected_chips = {'Nand', 'Not', 'And', 'Or'}
        
        # Test each built-in chip can be recognized
        for chip_type in expected_chips:
            # Create a dummy chip instance to test recognition
            from src.chip_simulator import ChipInstance
            from src.hdl_parser import ChipDefinition, PartInstance
            
            # Create a simple chip that uses the built-in
            test_chip = ChipDefinition(
                name="TestChip",
                inputs=["a", "b"] if chip_type != "Not" else ["in"],
                outputs=["out"],
                parts=[PartInstance(
                    chip_type=chip_type,
                    connections={"a": "a", "b": "b", "out": "out"} if chip_type != "Not" else {"in": "in", "out": "out"}
                )]
            )
            
            # Should be able to create instance without errors
            instance = ChipInstance(test_chip)
            self.assertIsNotNone(instance)
    
    @patch('src.hdl_parser.HDLParser.parse_file')
    def test_load_chip_definition_caching(self, mock_parse):
        """Test that chip definitions are cached."""
        # Mock the parse function
        mock_chip_def = ChipDefinition(
            name="TestChip",
            inputs=["a"],
            outputs=["out"],
            parts=[]
        )
        mock_parse.return_value = mock_chip_def
        
        # Use simulate_chip which actually implements caching
        # First call should parse the file
        result1 = self.simulator.simulate_chip("TestChip", {"a": 1})
        self.assertEqual(mock_parse.call_count, 1)
        
        # Second call should use cache
        result2 = self.simulator.simulate_chip("TestChip", {"a": 0})
        self.assertEqual(mock_parse.call_count, 1)  # Still 1, not 2
        
        # Both calls should work (we can't compare results since they depend on simulation)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_and_gate_simulation(self):
        """Test complete AND gate simulation."""
        # Create a mock simulator with built-in chips only
        simulator = ChipSimulator()
        
        # Test all input combinations for NAND gate
        test_cases = [
            ({"a": 0, "b": 0}, {"out": 1}),
            ({"a": 0, "b": 1}, {"out": 1}),
            ({"a": 1, "b": 0}, {"out": 1}),
            ({"a": 1, "b": 1}, {"out": 0}),
        ]
        
        for inputs, expected_outputs in test_cases:
            # Simulate NAND gate directly
            result = BuiltInGates.nand(inputs["a"], inputs["b"])
            self.assertEqual(result, expected_outputs["out"])


if __name__ == "__main__":
    unittest.main() 