from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from mcp_risk_calculator import MCPRiskCalculator
import io
import csv
import json
import numpy as np
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize calculator with the CSV file path - use os.path for cross-platform compatibility
csv_path = os.path.join(os.path.dirname(__file__), 'abstract_risks_with_overall_risk_score.csv')
calculator = MCPRiskCalculator(csv_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_risk():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save the uploaded file to a temporary buffer
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            suppliers = []
            csv_reader = csv.reader(stream)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                if len(row) >= 2:
                    # Strip whitespace from both supplier name and country while preserving internal spaces
                    supplier_name = row[0].strip()
                    country = row[1].strip()
                    if supplier_name and country:  # Ensure neither field is empty
                        suppliers.append((supplier_name, country))
        else:
            # Handle direct text input
            data = request.form.get('data', '')
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            suppliers = []
            lines = data.strip().split('\n')
            # Skip the first line if it contains headers
            start_index = 1 if len(lines) > 0 and any(header.lower() in lines[0].lower() for header in ['supplier name', 'country']) else 0
            
            for line in lines[start_index:]:
                try:
                    # Split only on the first comma to preserve any commas in names
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        supplier_name = parts[0].strip()
                        country = parts[1].strip()
                        if supplier_name and country:  # Ensure neither field is empty
                            suppliers.append((supplier_name, country))
                except Exception as e:
                    logger.warning(f"Skipping invalid line: {line}. Error: {str(e)}")
                    continue

        if not suppliers:
            return jsonify({'error': 'No valid supplier data provided'}), 400

        logger.debug(f"Processed suppliers: {suppliers}")

        # Convert suppliers list to DataFrame for processing
        supplier_df = pd.DataFrame(suppliers, columns=['Supplier Name', 'Country'])
        
        # Process the supplier data
        results = calculator.process_supplier_list(suppliers)
        df = calculator.format_risk_table(results)
        
        # Convert risk scores to numeric type
        risk_columns = [col for col in df.columns if col not in ['Supplier Name', 'Country']]
        for col in risk_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert DataFrame to HTML table with Bootstrap classes
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)

        # Prepare CSV output
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Convert DataFrame to list of dictionaries for JSON serialization
        json_data = json.loads(df.to_json(orient='records'))

        return jsonify({
            'table': table_html,
            'csv': csv_data,
            'data': json_data
        })

    except Exception as e:
        logger.error(f"Error in calculate_risk: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Vercel requires the app to be named 'app'
app = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 