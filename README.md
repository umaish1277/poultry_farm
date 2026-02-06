# Poultry Farm Management System

A comprehensive Frappe application integrated with ERPNext to manage and operate multi-branch poultry farms. Optimized for both Broiler (Meat) and Layer (Egg) operations.

## Key Features

### 🏢 Multi-Company Isolation (Advanced)
- **Centralized Setup**: Dedicated `Poultry Farm Settings` to lock the app to a specific `Company`.
- **Global Tagging**: Automatic company assignment for all master data and transactions.
- **Strict Data Security**: Role-based permission queries ensure users only access data belonging to their designated company.
- **Group Filtering**: Dynamically filters Items and Customers based on poultry-specific groups defined in settings.

### 🚜 Operational Management
- **Infrastructure Hierarchy**: Manage Farms and Sheds with capacity tracking and warehouse linking.
- **Batch Tracking**: Holistic flock lifecycle management from chick placement to harvest.
- **Daily Flock Entries**: Streamlined daily recording of:
  - **Mortality & Culls**: Automatic stock adjustment for flock size.
  - **Feed Consumption**: Automated `Stock Entry` (Material Issue) for feed items.
  - **Egg Collection**: Automated `Stock Entry` (Material Receipt) for egg inventory.

### 💰 Harvesting & Sales Integration
- **Weight-Based Valuation**: Harvest live birds based on total weight (kg) with precision `basic_rate` calculation for ERPNext Stock Entries.
- **Automated Invoicing**: submission of a harvest record automatically triggers a linked **Sales Invoice** for the customer.
- **Reverse Workflow**: Automated cancellation of linked stock and financial records when harvesting is revoked.

### 📊 Analytics Dashboard
- **Real-time Trends**: Interactive charts for Mortality, Egg Production, and Feed Consumption.
- **Harvesting Performance**: Visual trends for bird counts and yield weight across batches.
- **Operational Shortcuts**: Quick navigation hub for all masters, operations, and setup.

## Installation

Install the app via [bench](https://github.com/frappe/bench):

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/[your-repo]/poultry_farm.git
bench --site [your-site] install-app poultry_farm
bench --site [your-site] migrate
```

## Setup Guide

1. **Company Logic**: Initialize your company in ERPNext.
2. **Poultry Settings**: Navigate to **Poultry Farm Settings** on the dashboard.
   - Set the `Primary Company`.
   - Select your poultry-specific `Item Group` (e.g., "Poultry Feed & Birds").
3. **Infrastructure**: Create your first `Poultry Farm` and link it to a warehouse.
4. **Operations**: Start a new `Poultry Batch` and begin recording `Daily Flock Entries`.

## License

MIT
