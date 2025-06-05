# AWS EC2 Cost Charts Generator

A Python script that pulls cost data from the AWS Cost Explorer API and generates interactive charts similar to the AWS Cost Explorer interface. The script creates visualizations showing daily costs grouped by purchase option (Spot, On Demand, Savings Plans, Reserved).

## Features

- 📊 **Interactive Charts**: Both matplotlib (static) and Plotly (interactive) visualizations
- 🎯 **Purchase Type Breakdown**: Groups costs by Spot, On Demand, Savings Plans, and Reserved instances
- 📈 **Daily Granularity**: Shows cost trends over time with daily data points
- 📋 **Summary Reports**: Provides detailed cost breakdowns and statistics
- ⚙️ **Flexible Configuration**: Supports custom date ranges, AWS profiles, and service filters
- 🎨 **AWS-like UI**: Charts styled to match AWS Cost Explorer appearance

## Prerequisites

### AWS Setup

1. **AWS Credentials**: Configure your AWS credentials using one of these methods:
   ```bash
   # Method 1: AWS CLI
   aws configure
   
   # Method 2: Environment variables
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   
   # Method 3: AWS credentials file
   # Create ~/.aws/credentials with your keys
   ```

2. **IAM Permissions**: Your AWS user/role needs the following permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "ce:GetCostAndUsage",
                   "ce:GetUsageReport",
                   "ce:DescribeCostCategoryDefinition"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

3. **Cost Explorer**: Enable Cost Explorer in your AWS account:
   - Go to AWS Console → Billing → Cost Explorer
   - Click "Enable Cost Explorer" if not already enabled
   - Note: There may be a small charge for Cost Explorer API usage

## Installation

1. **Clone or download the files**:
   ```bash
   # If you have git
   git clone <repository-url>
   cd aws-ec2-cost-charts
   
   # Or just ensure you have these files:
   # - aws_cost_charts.py
   # - example_usage.py
   # - requirements.txt
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main script to analyze the last 12 months of EC2 costs:

```bash
python aws_cost_charts.py
```

This will:
- Fetch daily cost data for the past 12 months
- Generate a summary report in the terminal
- Create two chart files:
  - `aws_costs_matplotlib.png` (static chart)
  - `aws_costs_plotly.html` (interactive chart)

### Advanced Usage

#### Custom Date Range

```python
from aws_cost_charts import AWSCostAnalyzer

analyzer = AWSCostAnalyzer()

# Analyze specific date range
raw_data = analyzer.get_daily_costs('2024-01-01', '2024-03-31')
df = analyzer.process_cost_data(raw_data)

analyzer.generate_summary_report(df)
analyzer.create_matplotlib_chart(df, 'Q1_2024_costs.png')
analyzer.create_plotly_chart(df, 'Q1_2024_costs.html')
```

#### Using AWS Profile

```python
# Use a specific AWS profile
analyzer = AWSCostAnalyzer(profile_name='production')
```

#### Different AWS Services

```python
# Analyze other AWS services
raw_data = analyzer.get_daily_costs(
    '2024-01-01', 
    '2024-12-31',
    service_filter='Amazon Simple Storage Service'  # S3 costs
)
```

### Example Scripts

Run the example script for guided usage:

```bash
python example_usage.py
```

Choose from:
1. Last 30 days analysis
2. Custom date range (Q1 2024)
3. Using AWS profile
4. All AWS services analysis

## Output Files

### Summary Report
Console output showing:
- Date range analyzed
- Total cost and average daily cost
- Breakdown by purchase type with percentages
- Highest cost day

### Charts Generated

1. **Static Chart** (`aws_costs_matplotlib.png`):
   - High-resolution PNG file
   - Stacked bar chart showing daily costs
   - Summary statistics overlay
   - Professional styling

2. **Interactive Chart** (`aws_costs_plotly.html`):
   - Interactive HTML file
   - Hover tooltips with detailed information
   - Zoom and pan capabilities
   - Responsive design

## Configuration Options

### AWSCostAnalyzer Parameters

```python
analyzer = AWSCostAnalyzer(
    profile_name='your-profile',  # AWS profile (optional)
    region='us-east-1'           # AWS region for Cost Explorer
)
```

### get_daily_costs Parameters

```python
raw_data = analyzer.get_daily_costs(
    start_date='2024-01-01',     # Start date (YYYY-MM-DD)
    end_date='2024-12-31',       # End date (YYYY-MM-DD)
    service_filter='Amazon Elastic Compute Cloud - Compute'  # AWS service
)
```

### Chart Customization

```python
# Matplotlib chart
analyzer.create_matplotlib_chart(
    df, 
    save_path='custom_chart.png'
)

# Plotly chart
analyzer.create_plotly_chart(
    df, 
    save_path='custom_interactive.html'
)
```

## Troubleshooting

### Common Issues

1. **"NoCredentialsError"**:
   - Ensure AWS credentials are properly configured
   - Check `aws configure list` output

2. **"AccessDenied"**:
   - Verify IAM permissions for Cost Explorer
   - Ensure Cost Explorer is enabled in your account

3. **"InvalidNextTokenException"**:
   - Try reducing the date range
   - Cost Explorer has limits on data retrieval

4. **No data returned**:
   - Check if you have costs in the specified date range
   - Verify the service filter is correct
   - Some purchase types may not be present in your account

### Getting Help

- Check AWS Cost Explorer documentation
- Verify your account has billing data for the requested period
- Ensure you're using the correct AWS region for Cost Explorer (us-east-1 recommended)

## API Limits

- AWS Cost Explorer API has usage limits
- Each API call may incur small charges
- Be mindful of large date ranges that require many API calls

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational and practical use. 