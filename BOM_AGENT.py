"""
BOM Analysis Agent - Intelligent querying and analysis of consolidated BOM data
"""

import openpyxl
import pandas as pd
from pathlib import Path
from collections import defaultdict
import json


class BOMAgent:
    """Intelligent agent for BOM analysis and queries"""

    def __init__(self, bom_file):
        """Initialize agent with consolidated BOM file"""
        self.bom_file = Path(bom_file)
        self.data = {}
        self.load_data()

    def load_data(self):
        """Load consolidated BOM data from Excel"""
        print(f"\n📂 Loading BOM data from: {self.bom_file.name}")

        # Read all three sheets
        self.data['summary_sections'] = pd.read_excel(self.bom_file, sheet_name='Summary per sections', header=0)
        self.data['summary_total'] = pd.read_excel(self.bom_file, sheet_name='Summary Total', header=0)
        self.data['summary_comparison'] = pd.read_excel(self.bom_file, sheet_name='Summary total comparison', header=0)

        print("✅ Data loaded successfully")
        print(f"\n📊 Dataset Summary:")
        print(f"   - Summary per sections: {len(self.data['summary_sections'])} rows")
        print(f"   - Summary total: {len(self.data['summary_total'])} rows")
        print(f"   - Summary comparison: {len(self.data['summary_comparison'])} rows")

    def get_summary_stats(self):
        """Get overall summary statistics"""
        df = self.data['summary_total']

        # Filter out metadata rows
        data_df = df[df['Model/PN'].notna()].copy()

        stats = {
            'total_unique_items': len(data_df),
            'total_quantity': data_df['Total Quantity'].sum() if 'Total Quantity' in data_df.columns else 0,
            'categories': data_df['Category'].nunique() if 'Category' in data_df.columns else 0,
            'by_category': {}
        }

        # Category breakdown
        if 'Category' in data_df.columns:
            for category in data_df['Category'].unique():
                if pd.notna(category):
                    cat_data = data_df[data_df['Category'] == category]
                    stats['by_category'][str(category)] = {
                        'items': len(cat_data),
                        'quantity': cat_data['Total Quantity'].sum() if 'Total Quantity' in cat_data.columns else 0
                    }

        return stats

    def get_category_analysis(self, category=None):
        """Get detailed analysis by category"""
        df = self.data['summary_total']
        data_df = df[df['Model/PN'].notna()].copy()

        if category:
            data_df = data_df[data_df['Category'] == category]
            return {
                'category': category,
                'items': data_df[['Model/PN', 'Description', 'Total Quantity']].to_dict('records'),
                'total_quantity': data_df['Total Quantity'].sum(),
                'item_count': len(data_df)
            }
        else:
            analysis = {}
            for cat in data_df['Category'].unique():
                if pd.notna(cat):
                    cat_df = data_df[data_df['Category'] == cat]
                    analysis[str(cat)] = {
                        'item_count': len(cat_df),
                        'total_quantity': cat_df['Total Quantity'].sum(),
                        'top_items': cat_df.nlargest(3, 'Total Quantity')[['Model/PN', 'Total Quantity']].to_dict('records')
                    }
            return analysis

    def find_item(self, item_name):
        """Find item by name or PN"""
        df = self.data['summary_total']

        search_term = str(item_name).lower()

        # Search in Model/PN and Description
        results = df[
            (df['Model/PN'].astype(str).str.lower().str.contains(search_term, na=False)) |
            (df['Description'].astype(str).str.lower().str.contains(search_term, na=False))
        ]

        if len(results) > 0:
            return {
                'found': True,
                'items': results[['Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category', 'Total Quantity']].to_dict('records')
            }
        else:
            return {'found': False, 'items': []}

    def get_top_items(self, limit=10, category=None):
        """Get top items by quantity"""
        df = self.data['summary_total']
        data_df = df[df['Model/PN'].notna()].copy()

        if category:
            data_df = data_df[data_df['Category'] == category]

        top = data_df.nlargest(limit, 'Total Quantity')
        return top[['Model/PN', 'Description', 'Category', 'Total Quantity']].to_dict('records')

    def get_customer_locations(self):
        """Get all customers and locations in the BOM"""
        df = self.data['summary_total']

        # Extract metadata from rows 2-4
        customers = {}

        # Get unique file columns
        file_cols = [col for col in df.columns if df[col].dtype == 'object' and col not in
                    ['Model/PN', 'Description', 'NVIDIA Generic Part number', 'Dell PN', 'Category']]

        # Parse metadata manually from the Excel file
        wb = openpyxl.load_workbook(self.bom_file)
        ws = wb['Summary Total']

        for col_idx in range(6, ws.max_column):
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            customer = ws[f'{col_letter}2'].value
            location = ws[f'{col_letter}3'].value

            if customer or location:
                customers[f'{customer}-{location}'] = {
                    'customer': customer,
                    'location': location,
                    'column': col_letter
                }

        return customers

    def get_file_summary(self):
        """Get summary by file/customer"""
        df = self.data['summary_total']
        data_df = df[df['Model/PN'].notna()].copy()

        # Parse metadata
        wb = openpyxl.load_workbook(self.bom_file)
        ws = wb['Summary Total']

        file_summary = {}

        for col_idx in range(6, ws.max_column - 1):  # Exclude Total Quantity column
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            customer = ws[f'{col_letter}2'].value
            location = ws[f'{col_letter}3'].value

            if customer or location:
                file_key = f"{customer} - {location}"

                # Sum quantities for this file
                if col_idx <= len(data_df.columns):
                    col_name = data_df.columns[col_idx - 1] if col_idx - 1 < len(data_df.columns) else None
                    if col_name:
                        total_qty = data_df[col_name].sum() if col_name in data_df.columns else 0
                        file_summary[file_key] = {
                            'customer': customer,
                            'location': location,
                            'quantity': int(total_qty) if not pd.isna(total_qty) else 0
                        }

        return file_summary

    def get_network_recommendations(self):
        """Get recommendations based on BOM analysis"""
        stats = self.get_summary_stats()

        recommendations = []

        # Recommendation 1: High-count items
        if stats['total_quantity'] > 1000000:
            recommendations.append({
                'type': 'SCALE',
                'message': f"Very large deployment detected ({stats['total_quantity']:,} items). Consider volume discounts and supply chain planning.",
                'severity': 'HIGH'
            })

        # Recommendation 2: Category balance
        cables_count = stats['by_category'].get('Cables', {}).get('quantity', 0)
        transceiver_count = stats['by_category'].get('Transceiver', {}).get('quantity', 0)

        if cables_count > transceiver_count * 8:
            recommendations.append({
                'type': 'OPTIMIZATION',
                'message': 'High cable-to-transceiver ratio detected. Verify fiber optic specifications.',
                'severity': 'MEDIUM'
            })

        # Recommendation 3: Network infrastructure
        rack_count = stats['by_category'].get('Rack', {}).get('items', 0)
        if rack_count > 0:
            recommendations.append({
                'type': 'INFRASTRUCTURE',
                'message': f"Rack infrastructure required for {rack_count} rack units. Ensure power and cooling capacity.",
                'severity': 'HIGH'
            })

        return recommendations

    def print_agent_info(self):
        """Print agent information and capabilities"""
        print("\n" + "="*80)
        print("BOM ANALYSIS AGENT - Ready for Queries")
        print("="*80)
        print("\n📊 Available Commands:")
        print("  - agent.get_summary_stats()          : Overall BOM statistics")
        print("  - agent.get_category_analysis()      : Analysis by category")
        print("  - agent.find_item('item_name')       : Search for items")
        print("  - agent.get_top_items(limit=10)      : Top items by quantity")
        print("  - agent.get_customer_locations()     : All customers and locations")
        print("  - agent.get_file_summary()           : Summary by file/customer")
        print("  - agent.get_network_recommendations(): Smart recommendations")
        print("\n" + "="*80)


# MAIN EXECUTION
if __name__ == "__main__":
    current_dir = Path.cwd()
    bom_file = current_dir / "BOM_CONSOLIDATED_FINAL.xlsx"

    if not bom_file.exists():
        print(f"❌ ERROR: {bom_file.name} not found")
        exit(1)

    # Initialize agent
    agent = BOMAgent(bom_file)
    agent.print_agent_info()

    # Run sample queries
    print("\n📈 SAMPLE ANALYSIS:")
    print("\n1. Overall Statistics:")
    stats = agent.get_summary_stats()
    print(f"   Total Unique Items: {stats['total_unique_items']}")
    print(f"   Total Quantity: {stats['total_quantity']:,}")
    print(f"   Categories: {stats['categories']}")

    print("\n2. Category Breakdown:")
    for category, data in sorted(stats['by_category'].items()):
        print(f"   {category:20} | Items: {data['items']:3} | Qty: {data['quantity']:,}")

    print("\n3. Top 5 Items by Quantity:")
    top_items = agent.get_top_items(limit=5)
    for i, item in enumerate(top_items, 1):
        print(f"   {i}. {item['Model/PN']:30} | Qty: {item['Total Quantity']:>8,}")

    print("\n4. Recommendations:")
    recommendations = agent.get_network_recommendations()
    for rec in recommendations:
        print(f"   [{rec['severity']}] {rec['message']}")

    print("\n✅ Agent initialized and ready for use!")
