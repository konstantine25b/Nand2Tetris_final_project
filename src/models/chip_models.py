"""
Chip Models Module

This module contains the core data models for representing chips,
their components, and related structures with improved validation
and decomposition.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


class ChipType(Enum):
    """Enumeration of chip types for better type safety."""
    BUILTIN = "builtin"
    CUSTOM = "custom"
    COMPOSITE = "composite"


class PinType(Enum):
    """Enumeration of pin types."""
    INPUT = "input"
    OUTPUT = "output"
    INTERNAL = "internal"


@dataclass(frozen=True)
class Pin:
    """Represents a pin (input, output, or internal signal)."""
    name: str
    pin_type: PinType
    value: Optional[int] = None
    
    def __post_init__(self):
        """Validate pin after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Pin name cannot be empty")
        if self.value is not None and self.value not in (0, 1):
            raise ValueError(f"Pin value must be 0 or 1, got {self.value}")


@dataclass(frozen=True)
class Connection:
    """Represents a connection between pins."""
    source_pin: str
    target_pin: str
    
    def __post_init__(self):
        """Validate connection after initialization."""
        if not self.source_pin or not self.target_pin:
            raise ValueError("Connection pins cannot be empty")


@dataclass(frozen=True)
class PartInstance:
    """Represents an instance of a part within a chip."""
    chip_type: str
    connections: Dict[str, str]
    instance_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate part instance after initialization."""
        if not self.chip_type or not self.chip_type.strip():
            raise ValueError("Chip type cannot be empty")
        if not self.connections:
            raise ValueError("Part must have at least one connection")
        
        # Set default instance name if not provided
        if self.instance_name is None:
            object.__setattr__(self, 'instance_name', f"{self.chip_type.lower()}1")
    
    @property
    def input_connections(self) -> Dict[str, str]:
        """Get connections that represent inputs to this part."""
        # This could be enhanced with metadata about which pins are inputs
        return self.connections
    
    @property
    def output_connections(self) -> Dict[str, str]:
        """Get connections that represent outputs from this part."""
        # This could be enhanced with metadata about which pins are outputs
        return self.connections


@dataclass
class ChipDefinition:
    """Represents a complete chip definition with validation."""
    name: str
    inputs: List[str]
    outputs: List[str]
    parts: List[PartInstance] = field(default_factory=list)
    chip_type: ChipType = ChipType.CUSTOM
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate chip definition after initialization."""
        self._validate_name()
        self._validate_pins()
        self._validate_parts()
    
    def _validate_name(self):
        """Validate chip name."""
        if not self.name or not self.name.strip():
            raise ValueError("Chip name cannot be empty")
        if not self.name.isidentifier():
            raise ValueError(f"Chip name '{self.name}' is not a valid identifier")
    
    def _validate_pins(self):
        """Validate input and output pins."""
        if not self.inputs:
            raise ValueError("Chip must have at least one input")
        if not self.outputs:
            raise ValueError("Chip must have at least one output")
        
        # Check for duplicate pin names
        all_pins = self.inputs + self.outputs
        if len(all_pins) != len(set(all_pins)):
            raise ValueError("Duplicate pin names found")
        
        # Validate pin names
        for pin_name in all_pins:
            if not pin_name or not pin_name.strip():
                raise ValueError("Pin name cannot be empty")
            if not pin_name.isidentifier():
                raise ValueError(f"Pin name '{pin_name}' is not a valid identifier")
    
    def _validate_parts(self):
        """Validate part instances."""
        instance_names = set()
        for part in self.parts:
            if part.instance_name in instance_names:
                raise ValueError(f"Duplicate instance name: {part.instance_name}")
            instance_names.add(part.instance_name)
    
    @property
    def all_pins(self) -> List[str]:
        """Get all pin names (inputs + outputs)."""
        return self.inputs + self.outputs
    
    @property
    def is_builtin(self) -> bool:
        """Check if this is a built-in chip."""
        return self.chip_type == ChipType.BUILTIN
    
    @property
    def is_composite(self) -> bool:
        """Check if this is a composite chip."""
        return len(self.parts) > 0
    
    def get_internal_signals(self) -> Set[str]:
        """Get all internal signal names used in connections."""
        internal_signals = set()
        
        for part in self.parts:
            for signal_name in part.connections.values():
                if signal_name not in self.all_pins:
                    internal_signals.add(signal_name)
        
        return internal_signals
    
    def validate_connections(self) -> List[str]:
        """Validate all connections and return list of any issues found."""
        issues = []
        all_pins = set(self.all_pins)
        
        # Get all signals used in connections
        used_signals = set()
        for part in self.parts:
            for signal_name in part.connections.values():
                used_signals.add(signal_name)
        
        # Get signals that are properly defined (either chip pins or internal signals)
        # Internal signals must be outputs of some part and inputs to other parts
        signal_sources = {}  # signal -> list of parts that output it
        signal_sinks = {}    # signal -> list of parts that input it
        
        # Analyze signal flow
        for part in self.parts:
            for pin_name, signal_name in part.connections.items():
                # For now, we'll assume connections ending with 'out' are outputs
                # This is a simplification - in real implementation we'd need chip metadata
                if pin_name.endswith('out') or pin_name == 'out':
                    if signal_name not in signal_sources:
                        signal_sources[signal_name] = []
                    signal_sources[signal_name].append(part.instance_name)
                else:
                    if signal_name not in signal_sinks:
                        signal_sinks[signal_name] = []
                    signal_sinks[signal_name].append(part.instance_name)
        
        # Validate each signal
        for signal_name in used_signals:
            if signal_name in all_pins:
                continue  # Chip pins are always valid
            
            # For internal signals, check if they have proper sources
            if signal_name not in signal_sources:
                # This signal is used but never produced
                issues.append(f"Signal '{signal_name}' is used but never produced by any part")
        
        return issues


@dataclass
class SimulationState:
    """Represents the state of a chip simulation."""
    chip_name: str
    input_values: Dict[str, int] = field(default_factory=dict)
    output_values: Dict[str, int] = field(default_factory=dict)
    internal_signals: Dict[str, int] = field(default_factory=dict)
    is_valid: bool = True
    error_message: Optional[str] = None
    
    def set_input(self, pin_name: str, value: int):
        """Set an input value with validation."""
        if value not in (0, 1):
            raise ValueError(f"Input value must be 0 or 1, got {value}")
        self.input_values[pin_name] = value
    
    def get_output(self, pin_name: str) -> Optional[int]:
        """Get an output value."""
        return self.output_values.get(pin_name)
    
    def set_internal_signal(self, signal_name: str, value: int):
        """Set an internal signal value."""
        if value not in (0, 1):
            raise ValueError(f"Signal value must be 0 or 1, got {value}")
        self.internal_signals[signal_name] = value
    
    def get_signal_value(self, signal_name: str) -> Optional[int]:
        """Get any signal value (input, output, or internal)."""
        if signal_name in self.input_values:
            return self.input_values[signal_name]
        elif signal_name in self.output_values:
            return self.output_values[signal_name]
        elif signal_name in self.internal_signals:
            return self.internal_signals[signal_name]
        return None
    
    def clear_outputs_and_internals(self):
        """Clear output and internal signal values (keep inputs)."""
        self.output_values.clear()
        self.internal_signals.clear()
        self.is_valid = True
        self.error_message = None


# Abstract base classes for different chip behaviors

class ChipEvaluator(ABC):
    """Abstract base class for chip evaluation strategies."""
    
    @abstractmethod
    def evaluate(self, inputs: Dict[str, int]) -> Dict[str, int]:
        """Evaluate the chip with given inputs and return outputs."""
        pass
    
    @abstractmethod
    def get_input_pins(self) -> List[str]:
        """Get list of input pin names."""
        pass
    
    @abstractmethod
    def get_output_pins(self) -> List[str]:
        """Get list of output pin names."""
        pass


class BuiltinChipEvaluator(ChipEvaluator):
    """Base class for built-in chip evaluators."""
    
    def __init__(self, name: str, inputs: List[str], outputs: List[str]):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
    
    def get_input_pins(self) -> List[str]:
        return self.inputs.copy()
    
    def get_output_pins(self) -> List[str]:
        return self.outputs.copy()


# Factory function for creating chip definitions

def create_builtin_chip_definition(name: str, inputs: List[str], outputs: List[str], 
                                 description: Optional[str] = None) -> ChipDefinition:
    """Factory function to create built-in chip definitions."""
    return ChipDefinition(
        name=name,
        inputs=inputs,
        outputs=outputs,
        parts=[],
        chip_type=ChipType.BUILTIN,
        description=description
    )


def create_custom_chip_definition(name: str, inputs: List[str], outputs: List[str],
                                parts: List[PartInstance], 
                                description: Optional[str] = None) -> ChipDefinition:
    """Factory function to create custom chip definitions."""
    return ChipDefinition(
        name=name,
        inputs=inputs,
        outputs=outputs,
        parts=parts,
        chip_type=ChipType.CUSTOM,
        description=description
    ) 