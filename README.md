## Carbon-Aware Cloud Workload Scheduler

A simulation-based system that optimizes cloud workload execution by shifting tasks to time periods with lower carbon intensity, while balancing delay and cost constraints.

---

## Project Overview

This project implements a **carbon-aware scheduling engine** that evaluates when to execute workloads based on environmental impact. Instead of running jobs immediately, the system intelligently selects future time slots that minimize carbon emissions without introducing excessive delay.

---

## Phase 1 — Data Preparation ✅

This phase focuses on generating a realistic dataset to simulate cloud workloads and carbon intensity patterns.

### Dataset Features

* Hourly timestamps over a 90-day period
* Simulated workload demand with daily and weekly trends
* Carbon intensity variation (gCO₂/kWh)
* Time-series structure suitable for scheduling decisions

### Output

```
data/carbon_aware_workload_dataset.csv
```

---

## Core System (Final Implementation)

The project is built around three main components:

### 1. Scheduler Engine

* Naive Scheduler: Executes jobs immediately
* Carbon-Aware Scheduler: Selects optimal execution time within a 24-hour window
* Multi-objective scoring based on:

  * Carbon intensity
  * Execution delay
  * Cost (simplified)

### 2. Simulation Engine

* Runs both naive and smart scheduling strategies
* Computes:

  * Total carbon emissions
  * Carbon savings (kg)
  * Percentage reduction
  * Average delay per job

### 3. Interactive Dashboard

* Built using Streamlit
* Real-time tuning using sliders:

  * Carbon weight
  * Delay weight
  * Cost weight
* Visualizations:

  * Total carbon comparison
  * Carbon intensity over time
  * Per-job carbon comparison
  * Delay distribution

---

## Key Results

* Achieves measurable carbon reduction (~10–20%) under realistic constraints
* Maintains low average delay per job
* Demonstrates trade-offs between sustainability and performance

---

## How It Works

For each job:

1. Identify candidate execution times within the next 24 hours
2. Compute a score for each candidate:

   ```
   score = w_carbon * carbon + w_delay * delay + w_cost * cost
   ```
3. Select the time with the minimum score
4. Compare against naive scheduling

---

## Tech Stack

* Python
* Pandas
* Streamlit
* Plotly / Matplotlib

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run src/dashboard/app.py
```

---

## Future Improvements

* Integration with real-world carbon intensity APIs (Electricity Maps, WattTime)
* Job-specific deadlines and SLA constraints
* Multi-region scheduling
* Dynamic cost modeling
* Advanced optimization techniques

---

## Conclusion

This project demonstrates how intelligent scheduling can reduce carbon emissions in cloud systems by leveraging time-based optimization. It highlights the importance of balancing environmental impact with system performance in modern cloud computing.
