import pandas as pd
import numpy as np

class MCPRiskCalculator:
    def __init__(self, risk_data_file):
        """Initialize the calculator with risk data from CSV file."""
        try:
            self.risk_data = pd.read_csv(risk_data_file)
            # Set Country as index for faster lookups
            self.risk_data.set_index('Country', inplace=True)
            # Remove the existing Overall Risk Score column if it exists
            if 'Overall Risk Score' in self.risk_data.columns:
                self.risk_data = self.risk_data.drop('Overall Risk Score', axis=1)
        except Exception as e:
            raise Exception(f"Error loading risk data: {str(e)}")

    def calculate_overall_risk(self, row):
        """
        Calculate overall risk score using weighted average of risk categories.
        Weights are assigned based on severity and impact of each risk factor.
        """
        # Define weights for each risk category
        weights = {
            'Forced_Labor': 0.15,           # Highest weight due to human rights severity
            'Child_Labor': 0.15,            # Equally severe human rights issue
            'Gender_Based_Violence': 0.12,   # Significant human rights concern
            'Health_and_Safety': 0.10,       # Direct impact on human life
            'Wages': 0.10,                   # Critical for worker livelihood
            'Hazardous_Chemicals': 0.08,     # Environmental and health impact
            'Bribery_and_Corruption': 0.08,  # Business ethics and compliance
            'Water': 0.06,                   # Environmental resource
            'GHG_Emissions': 0.06,           # Environmental impact
            'Working_Time': 0.05,            # Labor conditions
            'Trade_Unions': 0.03,            # Worker rights
            'Biodiversity': 0.02             # Environmental impact
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for factor, weight in weights.items():
            if factor in row and pd.notnull(row[factor]):
                weighted_sum += float(row[factor]) * weight
                total_weight += weight
        
        # If no valid risk scores, return None
        if total_weight == 0:
            return None
            
        # Calculate weighted average and round to 2 decimal places
        overall_risk = round(weighted_sum / total_weight, 2)
        
        return overall_risk

    def process_supplier_list(self, suppliers):
        """Process a list of suppliers and return their risk scores."""
        results = []
        for supplier_name, country in suppliers:
            try:
                # Get risk scores for the country
                if country in self.risk_data.index:
                    risk_scores = self.risk_data.loc[country].to_dict()
                    # Calculate overall risk score
                    overall_risk = self.calculate_overall_risk(risk_scores)
                    results.append({
                        'Supplier Name': supplier_name,
                        'Country': country,
                        'Overall Risk Score': overall_risk,
                        **risk_scores
                    })
                else:
                    # If country not found, add with None values
                    risk_scores = {col: None for col in self.risk_data.columns}
                    results.append({
                        'Supplier Name': supplier_name,
                        'Country': country,
                        'Overall Risk Score': None,
                        **risk_scores
                    })
            except Exception as e:
                print(f"Error processing supplier {supplier_name}: {str(e)}")
                continue
        return results

    def format_risk_table(self, results):
        """Format the results into a pandas DataFrame."""
        if not results:
            return pd.DataFrame(columns=['Supplier Name', 'Country', 'Overall Risk Score'])
        
        df = pd.DataFrame(results)
        # Ensure consistent column order and exclude ISO2 and ISO3
        columns = ['Supplier Name', 'Country', 'Overall Risk Score']
        risk_columns = [col for col in df.columns if col not in columns + ['ISO2', 'ISO3']]
        
        return df[columns + sorted(risk_columns)] 