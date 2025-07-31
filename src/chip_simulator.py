"""
Chip Simulator Module

This module provides functionality to simulate chip behavior, including
built-in primitive gates and custom chips composed of other chips.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import os
from .hdl_parser import ChipDefinition, PartInstance, parse_hdl_file


@dataclass
class Signal:
    """Represents a signal in the chip simulation."""
    name: str
    value: Optional[int] = None


class BuiltInGates:
    """Implementation of built-in primitive gates."""
    
    @staticmethod
    def nand(a: int, b: int) -> int:
        """
        NAND gate: output is 0 only when both inputs are 1.
        
        Args:
            a, b: Input values (0 or 1)
            
        Returns:
            Output value (0 or 1)
        """
        return 0 if (a == 1 and b == 1) else 1
    
    @staticmethod
    def not_gate(input_val: int) -> int:
        """
        NOT gate: output is opposite of input.
        
        Args:
            input_val: Input value (0 or 1)
            
        Returns:
            Output value (0 or 1)
        """
        return 0 if input_val == 1 else 1
    
    @staticmethod
    def and_gate(a: int, b: int) -> int:
        """
        AND gate: output is 1 only when both inputs are 1.
        
        Args:
            a, b: Input values (0 or 1)
            
        Returns:
            Output value (0 or 1)
        """
        return 1 if (a == 1 and b == 1) else 0
    
    @staticmethod
    def or_gate(a: int, b: int) -> int:
        """
        OR gate: output is 1 when at least one input is 1.
        
        Args:
            a, b: Input values (0 or 1)
            
        Returns:
            Output value (0 or 1)
        """
        return 1 if (a == 1 or b == 1) else 0


class ChipInstance:
    """Represents an instance of a chip in the simulation."""
    
    def __init__(self, chip_def: ChipDefinition, simulator: 'ChipSimulator'):
        self.chip_def = chip_def
        self.simulator = simulator
        self.signals = {}  # signal_name -> value
        self.sub_chips = []  # List of instantiated sub-chips
        
        # Initialize all signals to None
        for input_pin in chip_def.inputs:
            self.signals[input_pin] = None
        for output_pin in chip_def.outputs:
            self.signals[output_pin] = None
        
        # Create instances of all parts
        self._instantiate_parts()
    
    def _instantiate_parts(self):
        """Create instances of all parts defined in the chip."""
        for part in self.chip_def.parts:
            if part.chip_type in self.simulator.built_in_chips:
                # Built-in chip - store for later simulation
                self.sub_chips.append({
                    'type': 'builtin',
                    'chip_type': part.chip_type,
                    'connections': part.connections
                })
            else:
                # Custom chip - load and instantiate
                sub_chip_def = self.simulator.load_chip_definition(part.chip_type)
                sub_chip_instance = ChipInstance(sub_chip_def, self.simulator)
                self.sub_chips.append({
                    'type': 'custom',
                    'chip_type': part.chip_type,
                    'connections': part.connections,
                    'instance': sub_chip_instance
                })
    
    def set_inputs(self, input_values: Dict[str, int]):
        """
        Set input values for the chip.
        
        Args:
            input_values: Dictionary mapping input pin names to values
        """
        for pin_name, value in input_values.items():
            if pin_name in self.chip_def.inputs:
                self.signals[pin_name] = value
    
    def simulate(self) -> Dict[str, int]:
        """
        Simulate the chip and return output values.
        
        Returns:
            Dictionary mapping output pin names to values
        """
        # Clear internal signals (keep inputs)
        for signal_name in self.signals:
            if signal_name not in self.chip_def.inputs:
                self.signals[signal_name] = None
        
        # Simulate each sub-chip
        for sub_chip in self.sub_chips:
            if sub_chip['type'] == 'builtin':
                self._simulate_builtin_chip(sub_chip)
            else:
                self._simulate_custom_chip(sub_chip)
        
        # Return output values
        outputs = {}
        for output_pin in self.chip_def.outputs:
            outputs[output_pin] = self.signals[output_pin]
        
        return outputs
    
    def _simulate_builtin_chip(self, sub_chip: Dict[str, Any]):
        """Simulate a built-in chip."""
        chip_type = sub_chip['chip_type']
        connections = sub_chip['connections']
        
        # Get the gate function
        gate_func = self.simulator.built_in_chips[chip_type]
        
        if chip_type == 'Nand':
            a_val = self.signals[connections['a']]
            b_val = self.signals[connections['b']]
            if a_val is not None and b_val is not None:
                result = gate_func(a_val, b_val)
                self.signals[connections['out']] = result
        
        elif chip_type == 'Not':
            in_val = self.signals[connections['in']]
            if in_val is not None:
                result = gate_func(in_val)
                self.signals[connections['out']] = result
        
        elif chip_type == 'And':
            a_val = self.signals[connections['a']]
            b_val = self.signals[connections['b']]
            if a_val is not None and b_val is not None:
                result = gate_func(a_val, b_val)
                self.signals[connections['out']] = result
        
        elif chip_type == 'Or':
            a_val = self.signals[connections['a']]
            b_val = self.signals[connections['b']]
            if a_val is not None and b_val is not None:
                result = gate_func(a_val, b_val)
                self.signals[connections['out']] = result
    
    def _simulate_custom_chip(self, sub_chip: Dict[str, Any]):
        """Simulate a custom chip."""
        instance = sub_chip['instance']
        connections = sub_chip['connections']
        
        # Set inputs for the sub-chip
        sub_inputs = {}
        for pin_name, signal_name in connections.items():
            if pin_name in instance.chip_def.inputs:
                sub_inputs[pin_name] = self.signals[signal_name]
        
        instance.set_inputs(sub_inputs)
        
        # Simulate the sub-chip
        sub_outputs = instance.simulate()
        
        # Copy outputs back to our signals
        for pin_name, signal_name in connections.items():
            if pin_name in instance.chip_def.outputs:
                self.signals[signal_name] = sub_outputs[pin_name]


class ChipSimulator:
    """
    Main chip simulator class that manages chip definitions and simulations.
    """
    
    def __init__(self, base_directory: str = "."):
        self.base_directory = base_directory
        self.chip_cache = {}  # Cache loaded chip definitions
        
        # Built-in chips mapping
        self.built_in_chips = {
            'Nand': BuiltInGates.nand,
            'Not': BuiltInGates.not_gate,
            'And': BuiltInGates.and_gate,
            'Or': BuiltInGates.or_gate,
        }
    
    def load_chip_definition(self, chip_name: str) -> ChipDefinition:
        """
        Load a chip definition from an HDL file.
        
        Args:
            chip_name: Name of the chip to load
            
        Returns:
            ChipDefinition object
        """
        if chip_name in self.chip_cache:
            return self.chip_cache[chip_name]
        
        # Find the HDL file
        hdl_file = os.path.join(self.base_directory, f"{chip_name}.hdl")
        
        # Parse the chip definition
        chip_def = parse_hdl_file(hdl_file)
        
        # Cache the definition
        self.chip_cache[chip_name] = chip_def
        
        return chip_def
    
    def create_chip_instance(self, chip_name: str) -> ChipInstance:
        """
        Create an instance of a chip.
        
        Args:
            chip_name: Name of the chip to instantiate
            
        Returns:
            ChipInstance object ready for simulation
        """
        chip_def = self.load_chip_definition(chip_name)
        return ChipInstance(chip_def, self)
    
    def simulate_chip(self, chip_name: str, 
                     input_values: Dict[str, int]) -> Dict[str, int]:
        """
        Simulate a chip with given input values.
        
        Args:
            chip_name: Name of the chip to simulate
            input_values: Dictionary mapping input pin names to values
            
        Returns:
            Dictionary mapping output pin names to values
        """
        chip_instance = self.create_chip_instance(chip_name)
        chip_instance.set_inputs(input_values)
        return chip_instance.simulate()


# Example usage and testing
if __name__ == "__main__":
    # Test built-in gates
    gates = BuiltInGates()
    
    print("Testing built-in gates:")
    print(f"NAND(0,0) = {gates.nand(0, 0)}")  # Should be 1
    print(f"NAND(0,1) = {gates.nand(0, 1)}")  # Should be 1
    print(f"NAND(1,0) = {gates.nand(1, 0)}")  # Should be 1
    print(f"NAND(1,1) = {gates.nand(1, 1)}")  # Should be 0
    
    print(f"NOT(0) = {gates.not_gate(0)}")     # Should be 1
    print(f"NOT(1) = {gates.not_gate(1)}")     # Should be 0
    
    print(f"AND(0,0) = {gates.and_gate(0, 0)}")  # Should be 0
    print(f"AND(0,1) = {gates.and_gate(0, 1)}")  # Should be 0
    print(f"AND(1,0) = {gates.and_gate(1, 0)}")  # Should be 0
    print(f"AND(1,1) = {gates.and_gate(1, 1)}")  # Should be 1
    
    print(f"OR(0,0) = {gates.or_gate(0, 0)}")   # Should be 0
    print(f"OR(0,1) = {gates.or_gate(0, 1)}")   # Should be 1
    print(f"OR(1,0) = {gates.or_gate(1, 0)}")   # Should be 1
    print(f"OR(1,1) = {gates.or_gate(1, 1)}")   # Should be 1 