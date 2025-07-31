"""
Built-in Gates - implements the 4 basic gates using strategy pattern

Better organized gate implementations that I can extend easily.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from ..models.chip_models import BuiltinChipEvaluator, ChipDefinition, ChipType


class GateLogic(ABC):
    """Base class for different gate logic implementations."""
    
    @abstractmethod
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Figure out outputs given inputs."""
        pass
    
    @abstractmethod
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """Return the full truth table for this gate."""
        pass


class NandGateLogic(GateLogic):
    """NAND gate - output is 0 only when both inputs are 1."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute NAND: out = NOT (a AND b)"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 0 if (a == 1 and b == 1) else 1
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """NAND truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 1},
            {'a': 0, 'b': 1, 'out': 1},
            {'a': 1, 'b': 0, 'out': 1},
            {'a': 1, 'b': 1, 'out': 0}
        ]


class NotGateLogic(GateLogic):
    """NOT gate - just flip the input."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute NOT: out = NOT in"""
        input_val = inputs.get('in', 0)
        result = 1 if input_val == 0 else 0
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """NOT truth table."""
        return [
            {'in': 0, 'out': 1},
            {'in': 1, 'out': 0}
        ]


class AndGateLogic(GateLogic):
    """AND gate - output is 1 only when both inputs are 1."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute AND: out = a AND b"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 1 if (a == 1 and b == 1) else 0
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """AND truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 0},
            {'a': 0, 'b': 1, 'out': 0},
            {'a': 1, 'b': 0, 'out': 0},
            {'a': 1, 'b': 1, 'out': 1}
        ]


class OrGateLogic(GateLogic):
    """OR gate - output is 1 when at least one input is 1."""
    
    def compute(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Compute OR: out = a OR b"""
        a = inputs.get('a', 0)
        b = inputs.get('b', 0)
        result = 1 if (a == 1 or b == 1) else 0
        return {'out': result}
    
    def get_truth_table(self) -> List[Dict[str, Any]]:
        """OR truth table."""
        return [
            {'a': 0, 'b': 0, 'out': 0},
            {'a': 0, 'b': 1, 'out': 1},
            {'a': 1, 'b': 0, 'out': 1},
            {'a': 1, 'b': 1, 'out': 1}
        ]


class BuiltinGate(BuiltinChipEvaluator):
    """
    Wrapper for built-in gates that handles validation and execution.
    Uses strategy pattern so I can swap out different logic implementations.
    """
    
    def __init__(self, name: str, inputs: List[str], outputs: List[str], 
                 logic: GateLogic, description: str = ""):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.logic = logic
        self.description = description
    
    def evaluate(self, input_values: Dict[str, int]) -> Dict[str, int]:
        """Run the gate with given inputs and return outputs."""
        # Check that we have all required inputs
        for pin in self.inputs:
            if pin not in input_values:
                raise ValueError(f"Missing input pin '{pin}' for gate {self.name}")
        
        # Check input values are valid (0 or 1)
        for pin, value in input_values.items():
            if pin in self.inputs and value not in (0, 1):
                raise ValueError(f"Invalid value {value} for pin '{pin}' (must be 0 or 1)")
        
        # Run the logic
        result = self.logic.compute(input_values)
        
        # Make sure we got all expected outputs
        for pin in self.outputs:
            if pin not in result:
                raise ValueError(f"Gate {self.name} didn't produce output pin '{pin}'")
        
        return result
    
    def get_chip_definition(self) -> ChipDefinition:
        """Return a chip definition for this gate."""
        from ..models.chip_models import Pin, PinType, create_chip_definition
        
        input_pins = [Pin(name=pin, pin_type=PinType.INPUT) for pin in self.inputs]
        output_pins = [Pin(name=pin, pin_type=PinType.OUTPUT) for pin in self.outputs]
        
        return create_chip_definition(
            name=self.name,
            pins=input_pins + output_pins,
            parts=[],
            chip_type=ChipType.BUILTIN,
            description=self.description
        )
    
    def test_all_combinations(self) -> bool:
        """Test this gate against its truth table to make sure it works."""
        truth_table = self.logic.get_truth_table()
        
        for row in truth_table:
            # Separate inputs from expected outputs
            inputs = {k: v for k, v in row.items() if k in self.inputs}
            expected_outputs = {k: v for k, v in row.items() if k in self.outputs}
            
            # Run the gate
            actual_outputs = self.evaluate(inputs)
            
            # Check if outputs match
            for pin, expected in expected_outputs.items():
                if actual_outputs.get(pin) != expected:
                    return False
        
        return True


class GateFactory:
    """Factory to create the 4 built-in gates we need."""
    
    # Define all our gates here
    _gate_definitions = {
        'Nand': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': NandGateLogic,
            'description': 'NAND gate: out = NOT (a AND b)'
        },
        'Not': {
            'inputs': ['in'],
            'outputs': ['out'],
            'logic_class': NotGateLogic,
            'description': 'NOT gate: out = NOT in'
        },
        'And': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': AndGateLogic,
            'description': 'AND gate: out = a AND b'
        },
        'Or': {
            'inputs': ['a', 'b'],
            'outputs': ['out'],
            'logic_class': OrGateLogic,
            'description': 'OR gate: out = a OR b'
        }
    }
    
    @classmethod
    def create_gate(cls, gate_name: str) -> BuiltinGate:
        """Create a gate by name."""
        if gate_name not in cls._gate_definitions:
            raise ValueError(f"Don't know how to make gate: {gate_name}")
        
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
        """Get list of gate names we can create."""
        return list(cls._gate_definitions.keys())
    
    @classmethod
    def is_builtin_gate(cls, gate_name: str) -> bool:
        """Check if we can make this gate."""
        return gate_name in cls._gate_definitions


class GateRegistry:
    """Keeps track of all our built-in gates."""
    
    def __init__(self):
        self._gates = GateFactory.create_all_gates()
    
    def get_gate(self, gate_name: str) -> BuiltinGate:
        """Get a gate by name."""
        if gate_name not in self._gates:
            raise ValueError(f"Unknown gate: {gate_name}")
        return self._gates[gate_name]
    
    def get_all_gates(self) -> Dict[str, BuiltinGate]:
        """Get all gates."""
        return self._gates.copy()
    
    def is_builtin(self, gate_name: str) -> bool:
        """Check if this is a built-in gate."""
        return gate_name in self._gates
    
    def validate_all_gates(self) -> bool:
        """Test all gates to make sure they work correctly."""
        for gate_name, gate in self._gates.items():
            if not gate.test_all_combinations():
                print(f"Gate {gate_name} failed validation!")
                return False
        return True


# Global registry that everyone can use
gate_registry = GateRegistry()


# Helper functions for easy access
def get_builtin_gate(gate_name: str) -> BuiltinGate:
    """Get a built-in gate by name."""
    return gate_registry.get_gate(gate_name)


def is_builtin_gate(gate_name: str) -> bool:
    """Check if this is a built-in gate."""
    return gate_registry.is_builtin(gate_name)


def validate_all_builtin_gates() -> bool:
    """Test all built-in gates."""
    return gate_registry.validate_all_gates()


def get_all_builtin_gates() -> Dict[str, BuiltinGate]:
    """Get all built-in gates."""
    return gate_registry.get_all_gates()


# Legacy compatibility for old code
class BuiltInGates:
    """Old-style interface for backwards compatibility."""
    
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