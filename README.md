# HDL Parser and Chip Testing Framework

My final project for Nand2Tetris 2025 Spring course.

## What This Project Does

I built a complete HDL parser and testing framework that can:

- Parse HDL files and understand chip definitions
- Simulate how chips work with different inputs
- Run automated tests to make sure everything works correctly
- Handle both simple gates (And, Or) and complex chips (like FullAdder)

Basically, you give it an HDL file and a test file, and it tells you if your chip implementation is correct or not.

## Project Structure

```
HDL_Konstantine_Bakhutashvili/
├── README.md                     # This file
├── requirements.txt              # Python stuff (but we only use standard library)
├── main.py                      # Run this to test your chips
├── venv/                        # Virtual environment
├── src/                         # All my code
│   ├── hdl_parser.py            # Parses HDL files
│   ├── chip_simulator.py        # Simulates chips
│   ├── tester.py                # Runs tests
│   ├── models/                  # Data structures I made
│   └── gates/                   # Built-in gate logic
├── examples/                    # Test chips I created
│   ├── And.hdl & And.tst       # Simple AND gate
│   ├── Or.hdl & Or.tst         # Simple OR gate
│   ├── Xor.hdl & Xor.tst       # XOR gate (more complex)
│   ├── DMux.hdl & DMux.tst     # Demultiplexer
│   ├── Mux.hdl & Mux.tst       # Multiplexer
│   ├── HalfAdder.hdl & HalfAdder.tst  # Half adder
│   └── FullAdder.hdl & FullAdder.tst  # Full adder (uses HalfAdder!)
└── tests/                       # Unit tests (53 tests total)
```

## How to Run It

### Setup (First Time Only)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# That's it! No external dependencies needed
```

### Testing Your Chips

```bash
# Always activate venv first
source venv/bin/activate

# Test a single chip
python main.py examples/And.hdl examples/And.tst

# Test multiple chips at once
python main.py examples/And.hdl examples/And.tst examples/Or.hdl examples/Or.tst

# Test all my examples (7 chips, 36 test cases)
python main.py examples/And.hdl examples/And.tst examples/Or.hdl examples/Or.tst examples/Xor.hdl examples/Xor.tst examples/DMux.hdl examples/DMux.tst examples/Mux.hdl examples/Mux.tst examples/HalfAdder.hdl examples/HalfAdder.tst examples/FullAdder.hdl examples/FullAdder.tst

# Run all unit tests
python main.py --run-all-tests
```

### What You'll See

When you run a test, you get output like this:

```
HDL Parser and Chip Testing Framework
==================================================

Validating HDL files...
✓ Successfully parsed examples/And.hdl (chip: And)

Testing chip: And
--------------------------------------------------
Test case 1: a=0, b=0 → Expected: out=0, Got: out=0 ✓ PASS
Test case 2: a=0, b=1 → Expected: out=0, Got: out=0 ✓ PASS
Test case 3: a=1, b=0 → Expected: out=0, Got: out=0 ✓ PASS
Test case 4: a=1, b=1 → Expected: out=1, Got: out=1 ✓ PASS
--------------------------------------------------
Summary: 4/4 tests passed (100.0%)
✅ All tests PASSED!
```

## File Formats

### HDL Files

Standard HDL format like we learned in class:

```hdl
CHIP And {
    IN a, b;
    OUT out;

    PARTS:
    Nand(a=a, b=b, out=nandOut);
    Not(in=nandOut, out=out);
}
```

### Test Files

CSV-style format as specified in the assignment:

```csv
a,b;out
0,0;0
0,1;0
1,0;0
1,1;1
```

The semicolon separates inputs from outputs, commas separate multiple pins.

## Built-in Gates

My simulator knows about these 4 primitive gates (as required):

| Gate | Inputs | Outputs | What it does  |
| ---- | ------ | ------- | ------------- |
| Nand | 2      | 1       | NOT (a AND b) |
| Not  | 1      | 1       | NOT in        |
| And  | 2      | 1       | a AND b       |
| Or   | 2      | 1       | a OR b        |

Everything else gets parsed from HDL files.

## Examples I Made

I created 7 different chips to test the framework:

| Chip      | Complexity | Test Cases | Notes                    |
| --------- | ---------- | ---------- | ------------------------ |
| And       | Basic      | 4          | Uses Nand + Not          |
| Or        | Basic      | 4          | Uses Nand + Not          |
| Xor       | Medium     | 4          | Uses 5 sub-chips!        |
| DMux      | Medium     | 4          | 1-to-2 demux             |
| Mux       | Medium     | 8          | 2-to-1 mux with selector |
| HalfAdder | Medium     | 4          | 1-bit addition           |
| FullAdder | Complex    | 8          | Uses 2 HalfAdders + Or   |

The FullAdder is especially cool because it shows recursive composition - it uses HalfAdders, which use Xor, which uses And/Or/Not, which use Nand. So it goes 4 levels deep!

## How It Works

1. **Parser** (`src/hdl_parser.py`): Reads HDL files and builds internal representation
2. **Simulator** (`src/chip_simulator.py`): Actually runs the chips with given inputs
3. **Tester** (`src/tester.py`): Reads test files and compares expected vs actual outputs
4. **Main** (`main.py`): Ties everything together with command-line interface

The cool part is handling non-built-in chips. When my simulator sees something like `HalfAdder(...)`, it automatically finds and parses `HalfAdder.hdl`, then simulates that chip recursively.

## Assignment Requirements ✓

I made sure to implement everything exactly as specified:

- ✓ Parse HDL files (CHIP, IN, OUT, PARTS sections)
- ✓ All 4 required built-in gates (Nand, Not, And, Or)
- ✓ Handle chip instantiations and recursive parsing
- ✓ Read CSV-style test vectors
- ✓ Compare actual vs expected outputs
- ✓ Print detailed test results + summary
- ✓ Documentation and examples

## Bonus Features

I went a bit beyond the requirements because I got excited:

- **Better architecture**: Used design patterns to make code more organized
- **More tests**: 53 unit tests to make sure everything works
- **Better error messages**: Helpful validation and error reporting
- **More examples**: 7 different chips instead of just basic gates
- **Built-in test runner**: `--run-all-tests` option

## Troubleshooting

**"No such file or directory"**  
→ Make sure you're in the right directory and activate venv first

**Import errors**  
→ Run `source venv/bin/activate` first

**Tests failing**  
→ Check that your HDL file is in the same directory as the test file

## Development Notes

The hardest part was getting the recursive parsing right. Making sure that when FullAdder instantiates HalfAdder, and HalfAdder instantiates Xor, everything gets loaded and simulated correctly took a lot of debugging.

I also spent time making the test output look nice and informative. The assignment just asked for pass/fail, but I added colors, progress indicators, and detailed error messages.

The code structure uses some fancy patterns I learned in other CS classes:

- Strategy pattern for gate logic
- Factory pattern for creating gates
- Data classes for type safety

But the core algorithm is straightforward: parse HDL → build internal model → simulate with inputs → compare outputs.

---

_Final project for Nand2Tetris 2025 Spring_  
_Free University of Tbilisi_
