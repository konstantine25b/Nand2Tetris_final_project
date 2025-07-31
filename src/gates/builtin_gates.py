"""
Built-in Gates Module

This module provides improved implementations of built-in gates using
strategy pattern and better decomposition for extensibility.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from ..models.chip_models import BuiltinChipEvaluator, ChipDefinition, ChipType


class GateLogic(ABC):
    """Abstract base class for gate logic implementations."""
    
    @abstractmethod
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute gate outputs given inputs."""
        pass
    
    @abstractmethod
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get the complete truth table for this gate."""
        pass


class NandGateLogic(GateLogic):
    """NAND gate logic implementation."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute NAND gate: out = NOT (a AND b)"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 0 if (a == 1 and b == 1) else 1
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get NAND gate truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 1},
            {'a': 0, 'b': 1, 'out': 1},
            {'a': 1, 'b': 0, 'out': 1},
            {'a': 1, 'b': 1, 'out': 0}
        ]


class NotGateLogic(GateLogic):
    """NOT gate logic implementation."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute NOT gate: out = NOT in"""
        input_val = inputs.get('in', 0)
        result = 0 if input_val == 1 else 1
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get NOT gate truth table."""
        return [
            {'in': 0, 'out': 1},
            {'in': 1, 'out': 0}
        ]


class AndGateLogic(GateLogic):
    """AND gate logic implementation."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute AND gate: out = a AND b"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 1 if (a == 1 and b == 1) else 0
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get AND gate truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 0},
            {'a': 0, 'b': 1, 'out': 0},
            {'a': 1, 'b': 0, 'out': 0},
            {'a': 1, 'b': 1, 'out': 1}
        ]


class OrGateLogic(GateLogic):
    """OR gate logic implementation."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute OR gate: out = a OR b"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 1 if (a == 1 or b == 1) else 0
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get OR gate truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 0},
            {'a': 0, 'b': 1, 'out': 1},
            {'a': 1, 'b': 0, 'out': 1},
            {'a': 1, 'b': 1, 'out': 1}
        ]


class BuiltinGate(BuiltinChipEvaluator):
    """Enhanced built-in gate implementation using strategy pattern."""
    
    def __init__(self, name: str, inputs: List[str], outputs: List[str], 
                 logic: GateLogic, description: Optional[str] = None):
        super().__init__(name, inputs, outputs)
        self.logic = logic
        self.description = description
    
    def evaluate(self, input_values: Dict[str, int]) -> Dict[str, int]:
        """Evaluate the gate using its logic strategy."""
        # Validate inputs
        self._validate_inputs(input_values)
        
        # Compute outputs using the logic strategy
        outputs = self.logic.compute(input_values)
        
        # Validate outputs
        self._validate_outputs(outputs)
        
        return outputs
    
    def _validate_inputs(self, input_values: Dict[str, int]):
        """Validate input values."""
        # Check that all required inputs are provided
        for required_input in self.inputs:
            if required_input not in input_values:
                raise ValueError(f"Missing required input: {required_input}")
        
        # Check that input values are valid
        for pin_name, value in input_values.items():
            if pin_name in self.inputs and value not in (0, 1):
                raise ValueError(f"Invalid input value for {pin_name}: {value}")
    
    def _validate_outputs(self, outputs: Dict[str, int]):
        """Validate output values."""
        # Check that all required outputs are provided
        for required_output in self.outputs:
            if required_output not in outputs:
                raise ValueError(f"Gate logic failed to provide output: {required_output}")
        
        # Check that output values are valid
        for pin_name, value in outputs.items():
            if value not in (0, 1):
                raise ValueError(f"Invalid output value for {pin_name}: {value}")
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Get the truth table for this gate."""
        return self.logic.get_truth_table()
    
    def test_all_combinations(self) -> bool:
        """Test all input combinations against the truth table."""
        truth_table = self.get_truth_table()
        
        for row in truth_table:
            # Extract inputs and expected outputs from truth table row
            inputs = {pin: row[pin] for pin in self.inputs if pin in row}
            expected_outputs = {pin: row[pin] for pin in self.outputs if pin in row}
            
            # Compute actual outputs
            actual_outputs = self.evaluate(inputs)
            
            # Compare with expected
            if actual_outputs != expected_outputs:
                return False
        
        return True


class GateFactory:
    """Factory for creating built-in gates."""
    
    _gate_definitions = {
        'Nand': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': NandGateLogic,
            'description': 'Logical NAND gate: out = NOT (a AND b)'
        },
        'Not': {
            'inputs': ['in'],
            'outputs': ['out'],
            'logic_class': NotGateLogic,
            'description': 'Logical NOT gate: out = NOT in'
        },
        'And': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': AndGateLogic,
            'description': 'Logical AND gate: out = a AND b'
        },
        'Or': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': OrGateLogic,
            'description': 'Logical OR gate: out = a OR b'
        }
    }
    
    @classmethod
    def create_gate(cls, gate_name: str) -> BuiltinGate:
        """Create a built-in gate by name."""
        if gate_name not in cls._gate_definitions:
            raise ValueError(f"Unknown built-in gate: {gate_name}")
        
        definition = cls._gate_definitions[gate_name]
        logic = definition['logic_class']()
        
        return BuiltinGate(
            name=gate_name,
            inputs=definition['inputs'],
            outputs=definition['outputs'],
            logic=logic,
            description=definition['description']
        )
    
    @classmethod
    def create_all_gates(cls) -> Dict[str, BuiltinGate]:
        """Create all built-in gates."""
        gates = {}
        for gate_name in cls._gate_definitions:
            gates[gate_name] = cls.create_gate(gate_name)
        return gates
    
    @classmethod
    def get_available_gates(cls) -> List[str]:
        """Get list of available built-in gate names."""
        return list(cls._gate_definitions.keys())
    
    @classmethod
    def is_builtin_gate(cls, gate_name: str) -> bool:
        """Check if a gate name is a built-in gate."""
        return gate_name in cls._gate_definitions
    
    @classmethod
    def get_gate_info(cls, gate_name: str) -> Dict[str, Any]:
        """Get information about a built-in gate."""
        if gate_name not in cls._gate_definitions:
            raise ValueError(f"Unknown built-in gate: {gate_name}")
        
        definition = cls._gate_definitions[gate_name]
        gate = cls.create_gate(gate_name)
        
        return {
            'name': gate_name,
            'inputs': definition['inputs'],
            'outputs': definition['outputs'],
            'description': definition['description'],
            'truth_table': gate.get_truth_table()
        }


class GateRegistry:
    """Registry for managing built-in gates."""
    
    def __init__(self):
        self._gates = {}
        self._initialize_builtin_gates()
    
    def _initialize_builtin_gates(self):
        """Initialize all built-in gates."""
        self._gates = GateFactory.create_all_gates()
    
    def get_gate(self, gate_name: str) -> BuiltinGate:
        """Get a built-in gate by name."""
        if gate_name not in self._gates:
            raise ValueError(f"Gate not found: {gate_name}")
        return self._gates[gate_name]
    
    def has_gate(self, gate_name: str) -> bool:
        """Check if a gate is available."""
        return gate_name in self._gates
    
    def get_all_gates(self) -> Dict[str, BuiltinGate]:
        """Get all available gates."""
        return self._gates.copy()
    
    def get_gate_names(self) -> List[str]:
        """Get list of all gate names."""
        return list(self._gates.keys())
    
    def register_custom_gate(self, gate: BuiltinGate):
        """Register a custom gate."""
        self._gates[gate.name] = gate
    
    def validate_all_gates(self) -> Dict[str, bool]:
        """Validate all gates against their truth tables."""
        results = {}
        for gate_name, gate in self._gates.items():
            try:
                results[gate_name] = gate.test_all_combinations()
            except Exception as e:
                results[gate_name] = False
        return results


# Create a global gate registry instance
gate_registry = GateRegistry()


# Convenience functions for backward compatibility
def get_builtin_gate(gate_name: str) -> BuiltinGate:
    """Get a built-in gate (convenience function)."""
    return gate_registry.get_gate(gate_name)


def is_builtin_gate(gate_name: str) -> bool:
    """Check if a gate is built-in (convenience function)."""
    return gate_registry.has_gate(gate_name)


def get_all_builtin_gates() -> Dict[str, BuiltinGate]:
    """Get all built-in gates (convenience function)."""
    return gate_registry.get_all_gates()


# Legacy compatibility functions (for old code)
class BuiltInGates:
    """Legacy compatibility class."""
    
    @staticmethod
    def nand(a: int, b: int) -> int:
        gate = get_builtin_gate('Nand')
        result = gate.evaluate({'a': a, 'b': b})
        return result['out']
    
    @staticmethod
    def not_gate(input_val: int) -> int:
        gate = get_builtin_gate('Not')
        result = gate.evaluate({'in': input_val})
        return result['out']
    
    @staticmethod
    def and_gate(a: int, b: int) -> int:
        gate = get_builtin_gate('And')
        result = gate.evaluate({'a': a, 'b': b})
        return result['out']
    
    @staticmethod
    def or_gate(a: int, b: int) -> int:
        gate = get_builtin_gate('Or')
        result = gate.evaluate({'a': a, 'b': b})
        return result['out'] 