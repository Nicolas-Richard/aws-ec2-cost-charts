# AWS EC2 Cost Charts Generator

Generate AWS EC2 cost charts similar to Cost Explorer, showing daily costs by purchase type (Spot, On Demand, Savings Plans).

## Features

- 📊 **Interactive Charts**: Both matplotlib (static) and Plotly (interactive) visualizations
- 🎯 **Purchase Type Breakdown**: Groups costs by Spot, On Demand, Savings Plans, and Reserved instances
- 📈 **Daily Granularity**: Shows cost trends over time with daily data points
- ⚙️ **Flexible Configuration**: Supports custom date ranges, AWS profiles, and service filters
- 🎨 **AWS-like UI**: Charts styled to match AWS Cost Explorer appearance

## Prerequisites

### AWS Setup

1. **AWS Credentials**: Configure your AWS credentials:
   ```bash
   aws configure
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

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script to analyze the last 12 months of EC2 costs:

```bash
python aws_cost_charts.py
```

This will:
- Fetch daily cost data for the past 12 months
- Create two chart files:
  - `aws_costs_matplotlib.png` (static chart)
  - `aws_costs_plotly.html` (interactive chart) 