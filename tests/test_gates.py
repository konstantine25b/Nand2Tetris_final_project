#!/usr/bin/env python3
"""
Tests for HDL Parser Framework Gates

This module contains comprehensive tests for the improved gate implementations
including gate logic, factory pattern, and registry functionality.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.gates.builtin_gates import (
    GateLogic, NandGateLogic, NotGateLogic, AndGateLogic, OrGateLogic,
    BuiltinGate, GateFactory, GateRegistry, gate_registry,
    get_builtin_gate, is_builtin_gate, get_all_builtin_gates, BuiltInGates
)


class TestGateLogic(unittest.TestCase):
    """Test individual gate logic implementations."""
    
    def test_nand_gate_logic(self):
        """Test NAND gate logic implementation."""
        logic = NandGateLogic()
        
        # Test all combinations
        self.assertEqual(logic.compute({'a': 0, 'b': 0}), {'out': 1})
        self.assertEqual(logic.compute({'a': 0, 'b': 1}), {'out': 1})
        self.assertEqual(logic.compute({'a': 1, 'b': 0}), {'out': 1})
        self.assertEqual(logic.compute({'a': 1, 'b': 1}), {'out': 0})
        
        # Test truth table
        truth_table = logic.get_truth_table()
        self.assertEqual(len(truth_table), 4)
        self.assertIn({'a': 0, 'b': 0, 'out': 1}, truth_table)
        self.assertIn({'a': 1, 'b': 1, 'out': 0}, truth_table)
    
    def test_not_gate_logic(self):
        """Test NOT gate logic implementation."""
        logic = NotGateLogic()
        
        # Test all combinations
        self.assertEqual(logic.compute({'in': 0}), {'out': 1})
        self.assertEqual(logic.compute({'in': 1}), {'out': 0})
        
        # Test truth table
        truth_table = logic.get_truth_table()
        self.assertEqual(len(truth_table), 2)
        self.assertIn({'in': 0, 'out': 1}, truth_table)
        self.assertIn({'in': 1, 'out': 0}, truth_table)
    
    def test_and_gate_logic(self):
        """Test AND gate logic implementation."""
        logic = AndGateLogic()
        
        # Test all combinations
        self.assertEqual(logic.compute({'a': 0, 'b': 0}), {'out': 0})
        self.assertEqual(logic.compute({'a': 0, 'b': 1}), {'out': 0})
        self.assertEqual(logic.compute({'a': 1, 'b': 0}), {'out': 0})
        self.assertEqual(logic.compute({'a': 1, 'b': 1}), {'out': 1})
        
        # Test truth table
        truth_table = logic.get_truth_table()
        self.assertEqual(len(truth_table), 4)
        self.assertIn({'a': 0, 'b': 0, 'out': 0}, truth_table)
        self.assertIn({'a': 1, 'b': 1, 'out': 1}, truth_table)
    
    def test_or_gate_logic(self):
        """Test OR gate logic implementation."""
        logic = OrGateLogic()
        
        # Test all combinations
        self.assertEqual(logic.compute({'a': 0, 'b': 0}), {'out': 0})
        self.assertEqual(logic.compute({'a': 0, 'b': 1}), {'out': 1})
        self.assertEqual(logic.compute({'a': 1, 'b': 0}), {'out': 1})
        self.assertEqual(logic.compute({'a': 1, 'b': 1}), {'out': 1})
        
        # Test truth table
        truth_table = logic.get_truth_table()
        self.assertEqual(len(truth_table), 4)
        self.assertIn({'a': 0, 'b': 0, 'out': 0}, truth_table)
        self.assertIn({'a': 1, 'b': 0, 'out': 1}, truth_table)


class TestBuiltinGate(unittest.TestCase):
    """Test the BuiltinGate class."""
    
    def test_nand_gate_creation(self):
        """Test NAND gate creation and evaluation."""
        logic = NandGateLogic()
        gate = BuiltinGate("Nand", ["a", "b"], ["out"], logic)
        
        self.assertEqual(gate.name, "Nand")
        self.assertEqual(gate.get_input_pins(), ["a", "b"])
        self.assertEqual(gate.get_output_pins(), ["out"])
        
        # Test evaluation
        result = gate.evaluate({"a": 1, "b": 1})
        self.assertEqual(result, {"out": 0})
    
    def test_gate_validation(self):
        """Test gate input/output validation."""
        logic = NandGateLogic()
        gate = BuiltinGate("Nand", ["a", "b"], ["out"], logic)
        
        # Test missing input
        with self.assertRaises(ValueError):
            gate.evaluate({"a": 1})  # Missing 'b'
        
        # Test invalid input value
        with self.assertRaises(ValueError):
            gate.evaluate({"a": 2, "b": 1})  # Invalid value '2'
    
    def test_truth_table_testing(self):
        """Test automatic truth table validation."""
        logic = NandGateLogic()
        gate = BuiltinGate("Nand", ["a", "b"], ["out"], logic)
        
        # Should pass truth table test
        self.assertTrue(gate.test_all_combinations())
        
        # Test with broken logic
        class BrokenLogic(GateLogic):
            def compute(self, inputs):
                return {"out": 1}  # Always returns 1 (incorrect)
            
            def get_truth_table(self):
                return NandGateLogic().get_truth_table()  # Correct truth table
        
        broken_gate = BuiltinGate("Broken", ["a", "b"], ["out"], BrokenLogic())
        self.assertFalse(broken_gate.test_all_combinations())


class TestGateFactory(unittest.TestCase):
    """Test the GateFactory class."""
    
    def test_create_individual_gates(self):
        """Test creating individual gates."""
        # Test NAND gate
        nand_gate = GateFactory.create_gate("Nand")
        self.assertEqual(nand_gate.name, "Nand")
        self.assertEqual(nand_gate.get_input_pins(), ["a", "b"])
        self.assertEqual(nand_gate.get_output_pins(), ["out"])
        
        # Test NOT gate
        not_gate = GateFactory.create_gate("Not")
        self.assertEqual(not_gate.name, "Not")
        self.assertEqual(not_gate.get_input_pins(), ["in"])
        self.assertEqual(not_gate.get_output_pins(), ["out"])
        
        # Test AND gate
        and_gate = GateFactory.create_gate("And")
        self.assertEqual(and_gate.name, "And")
        
        # Test OR gate
        or_gate = GateFactory.create_gate("Or")
        self.assertEqual(or_gate.name, "Or")
    
    def test_create_unknown_gate(self):
        """Test creating unknown gate throws error."""
        with self.assertRaises(ValueError):
            GateFactory.create_gate("UnknownGate")
    
    def test_create_all_gates(self):
        """Test creating all gates at once."""
        all_gates = GateFactory.create_all_gates()
        
        self.assertIn("Nand", all_gates)
        self.assertIn("Not", all_gates)
        self.assertIn("And", all_gates)
        self.assertIn("Or", all_gates)
        
        self.assertEqual(len(all_gates), 4)
    
    def test_gate_info(self):
        """Test getting gate information."""
        info = GateFactory.get_gate_info("Nand")
        
        self.assertEqual(info["name"], "Nand")
        self.assertEqual(info["inputs"], ["a", "b"])
        self.assertEqual(info["outputs"], ["out"])
        self.assertIn("description", info)
        self.assertIn("truth_table", info)
        self.assertEqual(len(info["truth_table"]), 4)
    
    def test_available_gates(self):
        """Test getting available gate names."""
        available = GateFactory.get_available_gates()
        
        self.assertIn("Nand", available)
        self.assertIn("Not", available)
        self.assertIn("And", available)
        self.assertIn("Or", available)
        self.assertEqual(len(available), 4)
    
    def test_is_builtin_gate(self):
        """Test checking if gate is built-in."""
        self.assertTrue(GateFactory.is_builtin_gate("Nand"))
        self.assertTrue(GateFactory.is_builtin_gate("Not"))
        self.assertTrue(GateFactory.is_builtin_gate("And"))
        self.assertTrue(GateFactory.is_builtin_gate("Or"))
        self.assertFalse(GateFactory.is_builtin_gate("CustomGate"))


class TestGateRegistry(unittest.TestCase):
    """Test the GateRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry is properly initialized."""
        registry = GateRegistry()
        
        self.assertTrue(registry.has_gate("Nand"))
        self.assertTrue(registry.has_gate("Not"))
        self.assertTrue(registry.has_gate("And"))
        self.assertTrue(registry.has_gate("Or"))
        
        gate_names = registry.get_gate_names()
        self.assertEqual(len(gate_names), 4)
    
    def test_get_gate(self):
        """Test getting gates from registry."""
        registry = GateRegistry()
        
        nand_gate = registry.get_gate("Nand")
        self.assertEqual(nand_gate.name, "Nand")
        
        # Test unknown gate
        with self.assertRaises(ValueError):
            registry.get_gate("UnknownGate")
    
    def test_custom_gate_registration(self):
        """Test registering custom gates."""
        registry = GateRegistry()
        
        # Create a custom gate
        logic = NandGateLogic()  # Reuse NAND logic for simplicity
        custom_gate = BuiltinGate("CustomGate", ["x", "y"], ["z"], logic)
        
        # Register it
        registry.register_custom_gate(custom_gate)
        
        # Verify it's available
        self.assertTrue(registry.has_gate("CustomGate"))
        retrieved_gate = registry.get_gate("CustomGate")
        self.assertEqual(retrieved_gate.name, "CustomGate")
    
    def test_validate_all_gates(self):
        """Test validating all gates."""
        registry = GateRegistry()
        results = registry.validate_all_gates()
        
        # All built-in gates should pass validation
        for gate_name, passed in results.items():
            self.assertTrue(passed, f"Gate {gate_name} failed validation")


class TestGlobalRegistry(unittest.TestCase):
    """Test the global gate registry and convenience functions."""
    
    def test_global_registry_functions(self):
        """Test global registry convenience functions."""
        # Test get_builtin_gate
        nand_gate = get_builtin_gate("Nand")
        self.assertEqual(nand_gate.name, "Nand")
        
        # Test is_builtin_gate
        self.assertTrue(is_builtin_gate("Nand"))
        self.assertFalse(is_builtin_gate("NonExistent"))
        
        # Test get_all_builtin_gates
        all_gates = get_all_builtin_gates()
        self.assertEqual(len(all_gates), 4)
        self.assertIn("Nand", all_gates)


class TestLegacyCompatibility(unittest.TestCase):
    """Test legacy compatibility functions."""
    
    def test_legacy_builtin_gates_class(self):
        """Test legacy BuiltInGates class still works."""
        # Test NAND
        self.assertEqual(BuiltInGates.nand(0, 0), 1)
        self.assertEqual(BuiltInGates.nand(0, 1), 1)
        self.assertEqual(BuiltInGates.nand(1, 0), 1)
        self.assertEqual(BuiltInGates.nand(1, 1), 0)
        
        # Test NOT
        self.assertEqual(BuiltInGates.not_gate(0), 1)
        self.assertEqual(BuiltInGates.not_gate(1), 0)
        
        # Test AND
        self.assertEqual(BuiltInGates.and_gate(0, 0), 0)
        self.assertEqual(BuiltInGates.and_gate(0, 1), 0)
        self.assertEqual(BuiltInGates.and_gate(1, 0), 0)
        self.assertEqual(BuiltInGates.and_gate(1, 1), 1)
        
        # Test OR
        self.assertEqual(BuiltInGates.or_gate(0, 0), 0)
        self.assertEqual(BuiltInGates.or_gate(0, 1), 1)
        self.assertEqual(BuiltInGates.or_gate(1, 0), 1)
        self.assertEqual(BuiltInGates.or_gate(1, 1), 1)


class TestGateIntegration(unittest.TestCase):
    """Integration tests for gate functionality."""
    
    def test_all_gates_truth_tables(self):
        """Test that all gates implement correct truth tables."""
        all_gates = get_all_builtin_gates()
        
        for gate_name, gate in all_gates.items():
            with self.subTest(gate=gate_name):
                self.assertTrue(gate.test_all_combinations(),
                              f"Gate {gate_name} failed truth table validation")
    
    def test_gate_composition(self):
        """Test using gates in composition (AND = NAND + NOT)."""
        nand_gate = get_builtin_gate("Nand")
        not_gate = get_builtin_gate("Not")
        and_gate = get_builtin_gate("And")
        
        # Test all input combinations
        for a in [0, 1]:
            for b in [0, 1]:
                # Compute AND using NAND + NOT
                nand_result = nand_gate.evaluate({"a": a, "b": b})
                composed_result = not_gate.evaluate({"in": nand_result["out"]})
                
                # Compare with direct AND
                direct_result = and_gate.evaluate({"a": a, "b": b})
                
                self.assertEqual(composed_result["out"], direct_result["out"],
                               f"Composition failed for inputs a={a}, b={b}")


if __name__ == "__main__":
    unittest.main() 