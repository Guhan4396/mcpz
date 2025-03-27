# Model Context Protocol (MCP) Risk Calculator

This tool implements a Model Context Protocol for calculating supplier risks based on 12 static country-level risk factors.

## Features

- Calculate risk scores (1-5 scale) for suppliers based on their country location
- Process individual suppliers or bulk supplier lists
- Support for country identification via name, ISO2, or ISO3 codes
- Input via file or direct text
- Detailed risk breakdown including all 12 risk factors
- CSV output support

## Risk Factors

The system evaluates the following 12 static risks:
1. GHG Emissions
2. Trade Unions
3. Wages
4. Working Time
5. Gender-Based Violence
6. Hazardous Chemicals
7. Bribery and Corruption
8. Water
9. Health and Safety
10. Forced Labor
11. Child Labor
12. Biodiversity

Each risk is scored on a scale of 1-5, where:
- 1 = Lowest risk
- 5 = Highest risk

## Requirements

```bash
pip install pandas numpy
```

## Usage

### Command Line Interface

1. Process suppliers from a file:
```bash
python mcp_cli.py --file suppliers.csv
```

2. Process suppliers from direct text input:
```bash
python mcp_cli.py --text "Supplier A,USA
Supplier B,CHN
Supplier C,GBR"
```

3. Save results to a CSV file:
```bash
python mcp_cli.py --file suppliers.csv --output results.csv
```

### Input Format

The supplier data should be in CSV format with two columns:
```
supplier_name,country
```

The country can be specified using:
- Full country name
- ISO2 code (2 letters)
- ISO3 code (3 letters)

Example:
```
Acme Corp,United States of America
Tech Ltd,GB
Supplier C,USA
```

### Python API

```python
from mcp_risk_calculator import MCPRiskCalculator

# Initialize calculator
calculator = MCPRiskCalculator('risk_data.csv')

# Calculate risk for a single supplier
risk = calculator.calculate_supplier_risk('Supplier A', 'USA')

# Process multiple suppliers
suppliers = [
    ('Supplier A', 'USA'),
    ('Supplier B', 'CHN'),
    ('Supplier C', 'GBR')
]
results = calculator.process_supplier_list(suppliers)

# Format results as a table
df = calculator.format_risk_table(results)
print(df)
```

## Output Format

The tool outputs a table with the following columns:
- Supplier Name
- Country
- Country Code
- Overall Risk (1-5)
- Individual scores for all 12 risk factors 