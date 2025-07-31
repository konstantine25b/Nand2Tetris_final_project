"""
HDL Parser Module

This module provides functionality to parse HDL files and build an internal
representation of chips, their inputs, outputs, and parts.

Author: HDL Parser Framework
Course: Nand2Tetris 2025 Spring
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class ChipDefinition:
    """Represents a parsed chip definition."""
    name: str
    inputs: List[str]
    outputs: List[str]
    parts: List['PartInstance']


@dataclass
class PartInstance:
    """Represents an instance of a part within a chip."""
    chip_type: str
    connections: Dict[str, str]


class HDLTokenizer:
    """Tokenizes HDL files into manageable tokens."""
    
    TOKEN_PATTERNS = [
        ('CHIP', r'\bCHIP\b'),
        ('IN', r'\bIN\b'),
        ('OUT', r'\bOUT\b'),
        ('PARTS', r'\bPARTS\b'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('SEMICOLON', r';'),
        ('COMMA', r','),
        ('EQUALS', r'='),
        ('COLON', r':'),
        ('COMMENT', r'//.*'),
        ('WHITESPACE', r'\s+'),
        ('NEWLINE', r'\n'),
    ]
    
    def __init__(self):
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' 
                                   for name, pattern in self.TOKEN_PATTERNS)
        self.regex = re.compile(self.token_regex)
    
    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        Tokenize HDL text into a list of (token_type, token_value) tuples.
        
        Args:
            text: HDL source code as string
            
        Returns:
            List of token tuples, filtering out whitespace and comments
        """
        tokens = []
        for match in self.regex.finditer(text):
            token_type = match.lastgroup
            token_value = match.group()
            
            # Skip whitespace and comments
            if token_type not in ('WHITESPACE', 'COMMENT', 'NEWLINE'):
                tokens.append((token_type, token_value))
        
        return tokens


class HDLParser:
    """
    Parses tokenized HDL code and builds chip definitions.
    
    This parser handles the HDL grammar:
    - CHIP declarations
    - IN/OUT pin definitions
    - PARTS section with chip instantiations
    """
    
    def __init__(self):
        self.tokenizer = HDLTokenizer()
        self.tokens = []
        self.position = 0
    
    def parse_file(self, filepath: str) -> ChipDefinition:
        """
        Parse an HDL file and return a ChipDefinition.
        
        Args:
            filepath: Path to the HDL file
            
        Returns:
            ChipDefinition object representing the parsed chip
        """
        with open(filepath, 'r') as file:
            content = file.read()
        
        return self.parse_text(content)
    
    def parse_text(self, text: str) -> ChipDefinition:
        """
        Parse HDL text and return a ChipDefinition.
        
        Args:
            text: HDL source code as string
            
        Returns:
            ChipDefinition object representing the parsed chip
        """
        self.tokens = self.tokenizer.tokenize(text)
        self.position = 0
        
        return self._parse_chip()
    
    def _current_token(self) -> Optional[Tuple[str, str]]:
        """Get the current token without advancing."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _advance(self) -> Optional[Tuple[str, str]]:
        """Advance to the next token and return the current one."""
        token = self._current_token()
        self.position += 1
        return token
    
    def _expect_token(self, expected_type: str) -> str:
        """
        Expect a specific token type and return its value.
        
        Args:
            expected_type: The expected token type
            
        Returns:
            The token value
            
        Raises:
            ValueError: If the current token doesn't match expected type
        """
        token = self._advance()
        if not token or token[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token}")
        return token[1]
    
    def _parse_chip(self) -> ChipDefinition:
        """Parse a complete chip definition."""
        # Parse CHIP keyword
        self._expect_token('CHIP')
        
        # Parse chip name
        chip_name = self._expect_token('IDENTIFIER')
        
        # Parse opening brace
        self._expect_token('LBRACE')
        
        # Parse IN section
        inputs = self._parse_in_section()
        
        # Parse OUT section
        outputs = self._parse_out_section()
        
        # Parse PARTS section
        parts = self._parse_parts_section()
        
        # Parse closing brace
        self._expect_token('RBRACE')
        
        return ChipDefinition(
            name=chip_name,
            inputs=inputs,
            outputs=outputs,
            parts=parts
        )
    
    def _parse_in_section(self) -> List[str]:
        """Parse the IN section and return list of input pin names."""
        self._expect_token('IN')
        
        inputs = []
        
        # Parse first input
        inputs.append(self._expect_token('IDENTIFIER'))
        
        # Parse additional inputs separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # consume comma
            inputs.append(self._expect_token('IDENTIFIER'))
        
        # Parse semicolon
        self._expect_token('SEMICOLON')
        
        return inputs
    
    def _parse_out_section(self) -> List[str]:
        """Parse the OUT section and return list of output pin names."""
        self._expect_token('OUT')
        
        outputs = []
        
        # Parse first output
        outputs.append(self._expect_token('IDENTIFIER'))
        
        # Parse additional outputs separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # consume comma
            outputs.append(self._expect_token('IDENTIFIER'))
        
        # Parse semicolon
        self._expect_token('SEMICOLON')
        
        return outputs
    
    def _parse_parts_section(self) -> List[PartInstance]:
        """Parse the PARTS section and return list of part instances."""
        self._expect_token('PARTS')
        self._expect_token('COLON')
        
        parts = []
        
        # Parse part instances until we hit the closing brace
        while (self._current_token() and 
               self._current_token()[0] != 'RBRACE'):
            parts.append(self._parse_part_instance())
        
        return parts
    
    def _parse_part_instance(self) -> PartInstance:
        """Parse a single part instance."""
        # Parse chip type
        chip_type = self._expect_token('IDENTIFIER')
        
        # Parse opening parenthesis
        self._expect_token('LPAREN')
        
        # Parse connections
        connections = {}
        
        # Parse first connection
        pin_name = self._expect_token('IDENTIFIER')
        self._expect_token('EQUALS')
        signal_name = self._expect_token('IDENTIFIER')
        connections[pin_name] = signal_name
        
        # Parse additional connections separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # consume comma
            pin_name = self._expect_token('IDENTIFIER')
            self._expect_token('EQUALS')
            signal_name = self._expect_token('IDENTIFIER')
            connections[pin_name] = signal_name
        
        # Parse closing parenthesis
        self._expect_token('RPAREN')
        
        # Parse semicolon
        self._expect_token('SEMICOLON')
        
        return PartInstance(
            chip_type=chip_type,
            connections=connections
        )


def parse_hdl_file(filepath: str) -> ChipDefinition:
    """
    Convenience function to parse an HDL file.
    
    Args:
        filepath: Path to the HDL file
        
    Returns:
        ChipDefinition object representing the parsed chip
    """
    parser = HDLParser()
    return parser.parse_file(filepath)


# Example usage and testing
if __name__ == "__main__":
    # Example HDL content for testing
    example_hdl = """
    CHIP And {
        IN a, b;
        OUT out;
        
        PARTS:
        Nand(a=a, b=b, out=nandOut);
        Not(in=nandOut, out=out);
    }
    """
    
    parser = HDLParser()
    chip_def = parser.parse_text(example_hdl)
    
    print(f"Parsed chip: {chip_def.name}")
    print(f"Inputs: {chip_def.inputs}")
    print(f"Outputs: {chip_def.outputs}")
    print(f"Parts: {len(chip_def.parts)}")
    for i, part in enumerate(chip_def.parts):
        print(f"  Part {i+1}: {part.chip_type} - {part.connections}") 