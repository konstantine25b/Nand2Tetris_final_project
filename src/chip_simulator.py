"""
Chip Simulator - actually runs the chips with given inputs

Handles built-in gates and loads/simulates custom chips from HDL files.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os
from .hdl_parser import HDLParser, ChipDefinition, PartInstance


@dataclass
class Signal:
    """Represents a signal wire with a value."""
    name: str
    value: Optional[int] = None


class BuiltInGates:
    """Logic for the 4 basic gates we need to support."""
    
    @staticmethod
    def nand(a: int, b: int) -> int:
        """NAND gate: output is 0 only when both inputs are 1."""
        return 0 if (a == 1 and b == 1) else 1
    
    @staticmethod
    def not_gate(input_val: int) -> int:
        """NOT gate: flip the input."""
        return 1 if input_val == 0 else 0
    
    @staticmethod
    def and_gate(a: int, b: int) -> int:
        """AND gate: output is 1 only when both inputs are 1."""
        return 1 if (a == 1 and b == 1) else 0
    
    @staticmethod
    def or_gate(a: int, b: int) -> int:
        """OR gate: output is 1 when at least one input is 1."""
        return 1 if (a == 1 or b == 1) else 0


class ChipInstance:
    """Represents a chip that we're simulating."""
    
    def __init__(self, definition: ChipDefinition, base_directory: str = "."):
        self.definition = definition
        self.base_directory = base_directory
        self.signals = {}  # All signals in this chip
        self.sub_chips = []  # Child chips used by this one
        
        # Set up input/output signals
        for pin_name in definition.inputs:
            self.signals[pin_name] = Signal(pin_name)
        for pin_name in definition.outputs:
            self.signals[pin_name] = Signal(pin_name)
        
        # Create instances of all sub-chips
        self._create_sub_chips()
    
    def _create_sub_chips(self):
        """Create instances for all chips used in PARTS section."""
        for part in self.definition.parts:
            if self._is_builtin_gate(part.chip_type):
                # Built-in gates don't need chip definitions
                self.sub_chips.append({
                    'type': part.chip_type,
                    'connections': part.connections,
                    'instance': None
                })
            else:
                # Load the HDL file for this chip type
                chip_def = self._load_chip_definition(part.chip_type)
                sub_instance = ChipInstance(chip_def, self.base_directory)
                self.sub_chips.append({
                    'type': part.chip_type,
                    'connections': part.connections,
                    'instance': sub_instance
                })
    
    def _is_builtin_gate(self, chip_type: str) -> bool:
        """Check if this is one of our 4 built-in gates."""
        return chip_type in ['Nand', 'Not', 'And', 'Or']
    
    def _load_chip_definition(self, chip_type: str) -> ChipDefinition:
        """Load and parse the HDL file for a chip type."""
        hdl_path = os.path.join(self.base_directory, f"{chip_type}.hdl")
        parser = HDLParser()
        return parser.parse_file(hdl_path)
    
    def set_inputs(self, input_values: Dict[str, int]):
        """Set the input pin values for this chip."""
        for pin_name, value in input_values.items():
            if pin_name in self.signals:
                self.signals[pin_name].value = value
    
    def get_outputs(self) -> Dict[str, int]:
        """Get the current output pin values."""
        outputs = {}
        for pin_name in self.definition.outputs:
            if pin_name in self.signals and self.signals[pin_name].value is not None:
                outputs[pin_name] = self.signals[pin_name].value
        return outputs
    
    def simulate(self):
        """Run the simulation - propagate signals through all sub-chips."""
        # Process each sub-chip
        for sub_chip_info in self.sub_chips:
            chip_type = sub_chip_info['type']
            connections = sub_chip_info['connections']
            instance = sub_chip_info['instance']
            
            if self._is_builtin_gate(chip_type):
                # Handle built-in gates directly
                self._simulate_builtin_gate(chip_type, connections)
            else:
                # Handle custom chips recursively
                self._simulate_custom_chip(instance, connections)
    
    def _simulate_builtin_gate(self, gate_type: str, connections: Dict[str, str]):
        """Simulate one of the built-in gates."""
        # Get input values from our signals
        if gate_type == 'Nand':
            a = self.signals[connections['a']].value
            b = self.signals[connections['b']].value
            result = BuiltInGates.nand(a, b)
            self._set_signal(connections['out'], result)
            
        elif gate_type == 'Not':
            input_val = self.signals[connections['in']].value
            result = BuiltInGates.not_gate(input_val)
            self._set_signal(connections['out'], result)
            
        elif gate_type == 'And':
            a = self.signals[connections['a']].value
            b = self.signals[connections['b']].value
            result = BuiltInGates.and_gate(a, b)
            self._set_signal(connections['out'], result)
            
        elif gate_type == 'Or':
            a = self.signals[connections['a']].value
            b = self.signals[connections['b']].value
            result = BuiltInGates.or_gate(a, b)
            self._set_signal(connections['out'], result)
    
    def _simulate_custom_chip(self, instance: 'ChipInstance', connections: Dict[str, str]):
        """Simulate a custom chip (loaded from HDL file)."""
        # Prepare input values for the sub-chip
        sub_inputs = {}
        for pin_name in instance.definition.inputs:
            if pin_name in connections:
                signal_name = connections[pin_name]
                sub_inputs[pin_name] = self.signals[signal_name].value
        
        # Set inputs and run simulation
        instance.set_inputs(sub_inputs)
        instance.simulate()
        
        # Get outputs and update our signals
        sub_outputs = instance.get_outputs()
        for pin_name in instance.definition.outputs:
            if pin_name in connections:
                signal_name = connections[pin_name]
                if pin_name in sub_outputs:
                    self._set_signal(signal_name, sub_outputs[pin_name])
    
    def _set_signal(self, signal_name: str, value: int):
        """Set the value of a signal, creating it if needed."""
        if signal_name not in self.signals:
            self.signals[signal_name] = Signal(signal_name)
        self.signals[signal_name].value = value


class ChipSimulator:
    """Main simulator that loads chips and runs tests."""
    
    def __init__(self, base_directory: str = "."):
        self.base_directory = base_directory
        self.parser = HDLParser()
        self.loaded_chips = {}  # Cache for loaded chip definitions
    
    def simulate_chip(self, chip_name: str, inputs: Dict[str, int]) -> Dict[str, int]:
        """
        Load a chip, set its inputs, run simulation, return outputs.
        This is the main function called by the tester.
        """
        # Load chip definition if not cached
        if chip_name not in self.loaded_chips:
            self.loaded_chips[chip_name] = self.load_chip_definition(chip_name)
        
        chip_def = self.loaded_chips[chip_name]
        
        # Create chip instance and simulate
        instance = ChipInstance(chip_def, self.base_directory)
        instance.set_inputs(inputs)
        instance.simulate()
        
        return instance.get_outputs()
    
    def load_chip_definition(self, chip_name: str) -> ChipDefinition:
        """Load and parse HDL file for a chip."""
        hdl_path = os.path.join(self.base_directory, f"{chip_name}.hdl")
        return self.parser.parse_file(hdl_path) 