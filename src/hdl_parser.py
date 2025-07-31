"""
HDL Parser - parses HDL files into internal chip representations

My implementation for parsing HDL syntax and building chip definitions.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class ChipDefinition:
    """Basic chip definition with inputs, outputs, and parts."""
    name: str
    inputs: List[str]
    outputs: List[str]
    parts: List['PartInstance']


@dataclass
class PartInstance:
    """A single chip instance used inside another chip."""
    chip_type: str
    connections: Dict[str, str]


class HDLTokenizer:
    """Breaks HDL text into tokens for parsing."""
    
    # All the different token types we need to recognize
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
        # Build one big regex from all patterns
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' 
                                   for name, pattern in self.TOKEN_PATTERNS)
        self.regex = re.compile(self.token_regex)
    
    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        Break HDL text into tokens.
        Returns list of (token_type, token_value) pairs.
        """
        tokens = []
        for match in self.regex.finditer(text):
            token_type = match.lastgroup
            token_value = match.group()
            
            # Skip whitespace and comments - we don't need them
            if token_type not in ('WHITESPACE', 'COMMENT', 'NEWLINE'):
                tokens.append((token_type, token_value))
        
        return tokens


class HDLParser:
    """
    Main parser that turns tokens into chip definitions.
    Handles the CHIP { IN ...; OUT ...; PARTS: ... } structure.
    """
    
    def __init__(self):
        self.tokenizer = HDLTokenizer()
        self.tokens = []
        self.position = 0
    
    def parse_file(self, filepath: str) -> ChipDefinition:
        """Parse an HDL file and return the chip definition."""
        with open(filepath, 'r') as file:
            content = file.read()
        
        return self.parse_text(content)
    
    def parse_text(self, text: str) -> ChipDefinition:
        """Parse HDL text and return the chip definition."""
        self.tokens = self.tokenizer.tokenize(text)
        self.position = 0
        
        return self._parse_chip()
    
    def _current_token(self) -> Optional[Tuple[str, str]]:
        """Get current token without moving forward."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _advance(self) -> Optional[Tuple[str, str]]:
        """Get current token and move to next one."""
        token = self._current_token()
        self.position += 1
        return token
    
    def _expect_token(self, expected_type: str) -> str:
        """
        Make sure next token is what we expect, return its value.
        Throws error if wrong token type.
        """
        token = self._advance()
        if not token or token[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token}")
        return token[1]
    
    def _parse_chip(self) -> ChipDefinition:
        """Parse the whole CHIP { ... } block."""
        # CHIP keyword
        self._expect_token('CHIP')
        
        # Chip name
        chip_name = self._expect_token('IDENTIFIER')
        
        # Opening {
        self._expect_token('LBRACE')
        
        # IN section
        inputs = self._parse_in_section()
        
        # OUT section
        outputs = self._parse_out_section()
        
        # PARTS section
        parts = self._parse_parts_section()
        
        # Closing }
        self._expect_token('RBRACE')
        
        return ChipDefinition(
            name=chip_name,
            inputs=inputs,
            outputs=outputs,
            parts=parts
        )
    
    def _parse_in_section(self) -> List[str]:
        """Parse IN pin1, pin2, ...; section."""
        self._expect_token('IN')
        
        inputs = []
        
        # First input pin
        inputs.append(self._expect_token('IDENTIFIER'))
        
        # Additional pins separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # eat comma
            inputs.append(self._expect_token('IDENTIFIER'))
        
        # Semicolon at end
        self._expect_token('SEMICOLON')
        
        return inputs
    
    def _parse_out_section(self) -> List[str]:
        """Parse OUT pin1, pin2, ...; section."""
        self._expect_token('OUT')
        
        outputs = []
        
        # First output pin
        outputs.append(self._expect_token('IDENTIFIER'))
        
        # Additional pins separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # eat comma
            outputs.append(self._expect_token('IDENTIFIER'))
        
        # Semicolon at end
        self._expect_token('SEMICOLON')
        
        return outputs
    
    def _parse_parts_section(self) -> List[PartInstance]:
        """Parse PARTS: section with chip instantiations."""
        self._expect_token('PARTS')
        self._expect_token('COLON')
        
        parts = []
        
        # Keep parsing part instances until we hit closing }
        while (self._current_token() and 
               self._current_token()[0] != 'RBRACE'):
            parts.append(self._parse_part_instance())
        
        return parts
    
    def _parse_part_instance(self) -> PartInstance:
        """Parse single chip instance like: And(a=x, b=y, out=z);"""
        # Chip type name
        chip_type = self._expect_token('IDENTIFIER')
        
        # Opening (
        self._expect_token('LPAREN')
        
        # Parse pin connections
        connections = {}
        
        # First connection
        pin_name = self._expect_token('IDENTIFIER')
        self._expect_token('EQUALS')
        signal_name = self._expect_token('IDENTIFIER')
        connections[pin_name] = signal_name
        
        # Additional connections separated by commas
        while (self._current_token() and 
               self._current_token()[0] == 'COMMA'):
            self._advance()  # eat comma
            pin_name = self._expect_token('IDENTIFIER')
            self._expect_token('EQUALS')
            signal_name = self._expect_token('IDENTIFIER')
            connections[pin_name] = signal_name
        
        # Closing )
        self._expect_token('RPAREN')
        
        # Semicolon at end
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