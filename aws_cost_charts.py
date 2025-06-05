
#!/usr/bin/env python3
"""
AWS EC2 Cost Charts Generator

This script pulls cost data from AWS Cost Explorer API and generates
charts similar to the AWS Cost Explorer interface, showing costs
grouped by purchase option (Spot, On Demand, Savings Plans).
"""

import boto3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import argparse
from typing import Dict, List, Optional


class AWSCostAnalyzer:
    """Class to analyze and visualize AWS costs using Cost Explorer API."""
    
    def __init__(self, profile_name: Optional[str] = None, region: str = 'us-east-1'):
        """
        Initialize the AWS Cost Analyzer.
        
        Args:
            profile_name: AWS profile name (optional, uses default if None)
            region: AWS region for the Cost Explorer client
        """
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
            self.cost_client = session.client('ce', region_name=region)
        else:
            self.cost_client = boto3.client('ce', region_name=region)
        
        self.cost_data = None
        
    def get_daily_costs(self, 
                       start_date: str, 
                       end_date: str,
                       service_filter: str = 'Amazon Elastic Compute Cloud - Compute') -> Dict:
        """
        Retrieve daily costs from AWS Cost Explorer API.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            service_filter: AWS service to filter (default: EC2)
            
        Returns:
            Dictionary containing cost data from AWS API
        """
        try:
            print(f"Fetching cost data from {start_date} to {end_date}...")
            
            response = self.cost_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'PURCHASE_TYPE'
                    }
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service_filter]
                    }
                }
            )
            
            print(f"Successfully retrieved {len(response['ResultsByTime'])} days of cost data")
            return response
            
        except Exception as e:
            print(f"Error fetching cost data: {str(e)}")
            raise
    
    def process_cost_data(self, raw_data: Dict) -> pd.DataFrame:
        """
        Process raw AWS cost data into a pandas DataFrame.
        
        Args:
            raw_data: Raw response from AWS Cost Explorer API
            
        Returns:
            Processed DataFrame with date, purchase_type, and cost columns
        """
        processed_data = []
        
        for result in raw_data['ResultsByTime']:
            date = result['TimePeriod']['Start']
            
            for group in result['Groups']:
                purchase_type = group['Keys'][0] if group['Keys'] else 'Unknown'
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                
                processed_data.append({
                    'date': pd.to_datetime(date),
                    'purchase_type': purchase_type,
                    'cost': cost
                })
        
        df = pd.DataFrame(processed_data)
        
        # Pivot to have purchase types as columns
        df_pivot = df.pivot(index='date', columns='purchase_type', values='cost').fillna(0)
        df_pivot = df_pivot.reset_index()
        
        # Calculate totals
        cost_columns = [col for col in df_pivot.columns if col != 'date']
        df_pivot['total_cost'] = df_pivot[cost_columns].sum(axis=1)
        
        return df_pivot
    
    def create_matplotlib_chart(self, df: pd.DataFrame, save_path: str = 'aws_costs_matplotlib.png', headless: bool = False) -> None:
        """
        Create a stacked bar chart using matplotlib.
        
        Args:
            df: Processed cost DataFrame
            save_path: Path to save the chart
            headless: If True, don't display the chart (just save)
        """
        # Set up the plot
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Get cost columns (excluding date and total)
        cost_columns = [col for col in df.columns if col not in ['date', 'total_cost']]
        
        # Define colors for different purchase types
        colors = {
            'Spot': '#3498db',  # Bright Blue
            'On Demand': '#e74c3c',  # Bright Red
            'Savings Plans': '#27ae60',  # Bright Green
            'Reserved': '#f39c12',  # Orange
            'Spot Instances': '#3498db',  # Bright Blue
            'On Demand Instances': '#e74c3c',  # Bright Red
        }
        
        # Create stacked bar chart
        bottom = pd.Series([0] * len(df))
        
        for purchase_type in cost_columns:
            if purchase_type in df.columns:
                color = colors.get(purchase_type, '#95a5a6')  # Default gray
                ax.bar(df['date'], df[purchase_type], bottom=bottom, 
                      label=purchase_type, color=color, alpha=0.8)
                bottom += df[purchase_type]
        
        # Customize the chart
        ax.set_title('AWS EC2 Daily Costs by Purchase Type', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cost ($)', fontsize=12)
        
        # Position legend with proper spacing to avoid text overlap
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fancybox=True, shadow=True, 
                 fontsize=10, labelspacing=0.8, handletextpad=0.5)
        
        # Format x-axis dates
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add summary statistics
        total_cost = df['total_cost'].sum()
        avg_daily_cost = df['total_cost'].mean()
        
        summary_text = f'Total Cost: ${total_cost:,.2f}\nAvg Daily Cost: ${avg_daily_cost:,.2f}'
        ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {save_path}")
        
        if not headless:
            plt.show()
        else:
            plt.close()  # Close the figure to free memory in headless mode
    
    def create_plotly_chart(self, df: pd.DataFrame, save_path: str = 'aws_costs_plotly.html', headless: bool = False) -> None:
        """
        Create an interactive stacked bar chart using Plotly.
        
        Args:
            df: Processed cost DataFrame
            save_path: Path to save the HTML chart
            headless: If True, don't open the chart in browser (just save)
        """
        # Get cost columns (excluding date and total)
        cost_columns = [col for col in df.columns if col not in ['date', 'total_cost']]
        
        # Define colors for different purchase types
        colors = {
            'Spot': '#3498db',  # Bright Blue
            'On Demand': '#e74c3c',  # Bright Red
            'Savings Plans': '#27ae60',  # Bright Green
            'Reserved': '#f39c12',  # Orange
            'Spot Instances': '#3498db',  # Bright Blue
            'On Demand Instances': '#e74c3c',  # Bright Red
        }
        
        fig = go.Figure()
        
        # Add traces for each purchase type
        for purchase_type in cost_columns:
            if purchase_type in df.columns:
                color = colors.get(purchase_type, '#95a5a6')
                fig.add_trace(go.Bar(
                    name=purchase_type,
                    x=df['date'],
                    y=df[purchase_type],
                    marker_color=color,
                    hovertemplate=f'<b>{purchase_type}</b><br>' +
                                 'Date: %{x}<br>' +
                                 'Cost: $%{y:,.2f}<br>' +
                                 '<extra></extra>'
                ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'AWS EC2 Daily Costs by Purchase Type',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Date',
            yaxis_title='Cost ($)',
            barmode='stack',
            hovermode='x unified',
            width=1200,
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add summary statistics as annotation
        total_cost = df['total_cost'].sum()
        avg_daily_cost = df['total_cost'].mean()
        
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            text=f"Total Cost: ${total_cost:,.2f}<br>Avg Daily Cost: ${avg_daily_cost:,.2f}",
            showarrow=False,
            font=dict(size=12),
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        )
        
        # Save and show
        fig.write_html(save_path)
        print(f"Interactive chart saved as {save_path}")
        
        if not headless:
            fig.show()
    
    def generate_summary_report(self, df: pd.DataFrame) -> None:
        """
        Generate a summary report of the cost data.
        
        Args:
            df: Processed cost DataFrame
        """
        print("\n" + "="*50)
        print("AWS COST SUMMARY REPORT")
        print("="*50)
        
        # Date range
        start_date = df['date'].min().strftime('%Y-%m-%d')
        end_date = df['date'].max().strftime('%Y-%m-%d')
        print(f"Date Range: {start_date} to {end_date}")
        
        # Total costs
        total_cost = df['total_cost'].sum()
        avg_daily_cost = df['total_cost'].mean()
        print(f"Total Cost: ${total_cost:,.2f}")
        print(f"Average Daily Cost: ${avg_daily_cost:,.2f}")
        
        # Breakdown by purchase type
        print(f"\nCost Breakdown by Purchase Type:")
        cost_columns = [col for col in df.columns if col not in ['date', 'total_cost']]
        
        for purchase_type in cost_columns:
            if purchase_type in df.columns:
                type_total = df[purchase_type].sum()
                percentage = (type_total / total_cost) * 100 if total_cost > 0 else 0
                print(f"  {purchase_type}: ${type_total:,.2f} ({percentage:.1f}%)")
        
        # Highest cost day
        max_cost_day = df.loc[df['total_cost'].idxmax()]
        print(f"\nHighest Cost Day: {max_cost_day['date'].strftime('%Y-%m-%d')} (${max_cost_day['total_cost']:.2f})")
        
        print("="*50)


def main():
    """Main function to run the AWS cost analysis."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate AWS EC2 cost charts using Cost Explorer API')
    parser.add_argument('--headless', action='store_true', 
                        help='Run in headless mode (save charts without displaying)')
    parser.add_argument('--profile', type=str, 
                        help='AWS profile to use (default: default profile)')
    parser.add_argument('--months', type=int, default=12,
                        help='Number of months to analyze (default: 12)')
    parser.add_argument('--output-prefix', type=str, default='aws_costs',
                        help='Prefix for output files (default: aws_costs)')
    
    args = parser.parse_args()
    
    # Initialize the analyzer
    analyzer = AWSCostAnalyzer(profile_name=args.profile)
    
    # Define date range
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=args.months)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # Fetch cost data
        raw_data = analyzer.get_daily_costs(start_date_str, end_date_str)
        
        # Process the data
        df = analyzer.process_cost_data(raw_data)
        
        # Generate summary report
        analyzer.generate_summary_report(df)
        
        # Create visualizations
        print("\nGenerating charts...")
        
        # Create output filenames
        png_file = f"{args.output_prefix}_matplotlib.png"
        html_file = f"{args.output_prefix}_plotly.html"
        
        analyzer.create_matplotlib_chart(df, png_file, headless=args.headless)
        analyzer.create_plotly_chart(df, html_file, headless=args.headless)
        
        if args.headless:
            print(f"\nHeadless mode: Charts saved to {png_file} and {html_file}")
        
        print("\nAnalysis complete!")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print("\nMake sure you have:")
        print("1. AWS credentials configured (aws configure)")
        print("2. Proper IAM permissions for Cost Explorer API")
        print("3. Cost Explorer enabled in your AWS account")


if __name__ == "__main__":
    main() 