# Carbon-Aware Cloud Workload Scheduler
## Using Machine Learning for Sustainable Cloud Optimization

---

## Overview

Cloud computing has become the backbone of modern digital infrastructure, enabling scalable and high-performance applications through distributed data centers. However, the rapid growth of cloud workloads has also increased energy consumption and carbon emissions.

Traditional cloud workload scheduling mechanisms primarily optimize for performance and operational cost, while environmental impact is rarely considered. Since the carbon intensity of electricity varies across geographic regions and time depending on energy generation sources, workloads executed without environmental awareness can lead to unnecessary carbon emissions.

This project proposes a **Carbon-Aware Cloud Workload Scheduler**, a machine learning driven framework that predicts future workload demand and generates scheduling recommendations based on carbon intensity, cost considerations, and performance requirements. The objective is to demonstrate how intelligent scheduling decisions can reduce environmental impact while maintaining operational efficiency.

---

## Problem Statement

Existing cloud scheduling mechanisms:

- Optimize resource allocation based on performance and cost
- Do not consider carbon intensity variations across regions and time
- Execute workloads during high-emission periods even when cleaner alternatives exist

This results in avoidable carbon emissions and inefficient energy usage.

The project addresses this gap by integrating workload forecasting with carbon-aware decision making to support sustainable cloud operations.

---

## Objectives

- Predict future cloud workload demand using machine learning models
- Integrate carbon intensity data into scheduling decisions
- Perform multi-objective optimization across performance, cost, and sustainability
- Reduce estimated carbon footprint without compromising service quality
- Demonstrate a practical framework for sustainable cloud scheduling

---

## System Architecture

The system follows a data-driven pipeline:

1. **Data Collection**
   - Historical workload data
   - Carbon intensity data

2. **Data Preparation**
   - Timestamp alignment
   - Missing value handling
   - Outlier detection
   - Time-series feature preparation

3. **Workload Forecasting**
   - Time-series prediction using Prophet or LSTM models
   - Multi-horizon workload prediction

4. **Carbon-Aware Scheduling Engine**
   - Combines workload prediction, carbon intensity, and cost metrics
   - Generates optimized scheduling recommendations

5. **Backend API**
   - FastAPI or Flask-based service
   - REST endpoints for scheduling recommendations

6. **Visualization Dashboard**
   - Streamlit interface
   - Displays forecasts, carbon trends, and scheduling outputs

---

## Key Features

- Predictive workload scheduling instead of reactive allocation
- Integration of environmental sustainability metrics
- Multi-objective optimization framework
- Modular architecture suitable for cloud integration
- Decision-support system without modifying existing applications

---

## Machine Learning Approach

The project uses time-series forecasting models:

### Prophet
- Captures seasonal workload patterns
- Handles trend changes effectively

### LSTM Networks
- Captures complex temporal dependencies
- Suitable for non-linear workload behavior

Prediction quality is evaluated using **Mean Absolute Percentage Error (MAPE)** to ensure reliable scheduling decisions.

---

## Expected Outcomes

- Improved energy efficiency compared to traditional scheduling
- Reduced carbon emissions through intelligent execution timing
- Demonstration of sustainability-aware cloud optimization
- Deployable prototype integrating ML prediction and scheduling logic

---

## Future Scope

- Integration with real-time carbon intensity APIs
- Reinforcement learning-based adaptive scheduling
- Multi-cloud optimization across providers
- Fully automated execution instead of recommendation-based scheduling
- Enterprise-scale deployment and orchestration integration

---

## Technologies Used

- Python
- Prophet / LSTM (TensorFlow or PyTorch)
- FastAPI / Flask
- Streamlit
- Cloud Platforms (AWS EC2 or equivalent)
- Time-series data processing libraries

---

## Author

**Sarah Sohaib**  
B.Tech Computer Science and Engineering  
Cloud Specialization Track  
Registration No: 23FE10CSE00673
