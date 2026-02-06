# Poultry Farm Management System

A comprehensive Frappe application integrated with ERPNext to manage and operate multi-branch poultry farms. Optimized for both Broiler (Meat) and Layer (Egg) operations.

## 🌟 Key Features

### 🏢 Multi-Company Isolation (Advanced)
- **Centralized Setup**: Dedicated `Poultry Farm Settings` to lock the app to a specific `Company`.
- **Global Tagging**: Automatic company assignment for all master data and transactions.
- **Strict Data Security**: Role-based permission queries ensure users only access data belonging to their designated company.

### 🚜 Lifecycle Operations
- **Infrastructure**: Manage Farms and Sheds with capacity tracking and warehouse linking.
- **Batch Tracking**: Holistic flock lifecycle management from chick placement to harvest.
- **Daily Flock Entries**:
  - **Mortality**: Auto-calculates remaining bird count.
  - **Feed**: Auto-creates `Stock Entry` (Material Issue) for accurate consumption.
  - **Eggs**: Auto-creates `Stock Entry` (Material Receipt) for daily production.

### 📈 Financial Intelligence (P&L)
- **Batch Profitability Report**: Real-time P&L per batch.
  - **Revenue**: Aggregated from Bird Sales and Egg Sales.
  - **Costs**: Automatically tracks Chick Purchase, Feed Consumption, Medication, and Overheads.
- **ROI Dashboard**: Visual insights like **ROI by Breed** and **Profit per Batch**.

### 🚚 Logistics & Dispatch Portal
- **Harvest Projections**: Public web portal (`/harvest_projections`) for buyers to view upcoming availability.
- **Driver Verification**: Mobile-friendly confirmation link (`/driver_verification`) for truck drivers to digitally verify bird counts and weights at the farm gate.

### 🌐 IoT Environmental Monitoring
- **Universal Sensors**: Connect any device (Temp, Humidity, CO2) via the `Poultry Sensor` API.
- **Automated Alerts**: Set `Environmental Thresholds` to trigger Email/SMS alerts if parameters are breached.
- **Real-Time API**: Endpoint `log_sensor_reading` for high-frequency data ingestion.

### 💉 Smart Health
- **Vaccination Templates**: Define standard protocols per breed.
- **Auto-Scheduling**: System generates a full calendar of doses upon batch creation.
- **Compliance**: Daily alerts for due vaccinations and medication tracking.

## 🛠️ Installation

Install the app via [bench](https://github.com/frappe/bench):

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/[your-repo]/poultry_farm.git
bench --site [your-site] install-app poultry_farm
bench --site [your-site] migrate
```

## 🚀 Quick Start Guide

1.  **Setup**:
    -   Go to **Poultry Farm Settings** and set your Primary Company.
    -   Define **Poultry Breed Standards** (e.g., "Ross 308") with mortality/feed goals.
2.  **Infrastructure**:
    -   Create a **Poultry Farm** and **Shed**.
3.  **Operations**:
    -   Create a **Poultry Batch** to start a cycle.
    -   Log **Daily Flock Entries** for feed, eggs, and mortality.
4.  **Logistics**:
    -   Share the `/harvest_projections` link with buyers.
    -   When harvesting, use the "Copy Driver Link" button to verify loads.
5.  **IoT**:
    -   Register your **Poultry Sensors** and set **Environmental Thresholds**.
    -   Post sensor data to `/api/method/poultry_farm.poultry_farm.api.log_sensor_reading`.

## License

MIT
