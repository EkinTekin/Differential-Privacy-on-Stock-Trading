# Differential-Privacy-on-Stock-Trading
This project implements Differential Privacy mechanisms (Laplace &amp; Gaussian) with statistical clipping to enable the secure analysis of financial trading data while mathematically guaranteeing individual investor privacy against re-identification attacks



## 📌 Project Overview

This project implements **Differential Privacy (DP)** mechanisms to enable the secure sharing of sensitive financial trading data. The goal is to allow analysts to compute aggregate statistics (such as Total Trading Volume, Sectoral Distribution, and Average Trade Value) without compromising the privacy of individual investors.

Using a high-fidelity **synthetic dataset of 50,000 stock trades**, this project explores the **Privacy-Utility Trade-off** by comparing the **Laplace** and **Gaussian** mechanisms under various privacy budgets ($\epsilon$).

### 🚀 Key Features
* **Synthetic Data Generation:** Realistic stock trading data simulation (including "Whale" investors).
* **DP Mechanisms:** Implementation of **Laplace ($\epsilon$-DP)** and **Gaussian ($\epsilon, \delta$-DP)** noise injection.
* **Outlier Management:** Implementation of a statistical **Clipping Mechanism** to bound Global Sensitivity ($\Delta f$) and handle high-net-worth individuals.
* **Utility Analysis:** Comparative analysis of Mean Absolute Error (MAE) and RMSE across different privacy budgets.

---

## ❓ The Problem & The Solution

**The Problem:** Financial institutions need to share data for macroeconomic analysis. However, sharing raw data exposes investors to **Linkage Attacks** and **Differencing Attacks**, where adversaries can re-identify individuals and uncover their financial secrets.

**The Solution:** Instead of simple anonymization (which fails), we use **Differential Privacy**. We add mathematically calibrated noise to query results, guaranteeing that the output remains virtually the same whether any single individual is present in the dataset or not.

---

## 🛠️ Methodology

### 1. Sensitivity & Clipping
Financial data has unbounded sensitivity (a trade can range from $1 to $1M). To prevent infinite noise, I implemented a **Clipping Threshold ($C=20,000$)**.
* Any trade $> 20,000$ is clipped to $20,000$.
* This bounds Global Sensitivity ($\Delta f$) and stabilizes the noise.

### 2. Mechanisms
* **Laplace Mechanism:** Used for scalar queries (Sum/Count). Adds noise drawn from $Lap(\Delta f / \epsilon)$.
* **Gaussian Mechanism:** Used for comparison. Adds noise drawn from $N(0, \sigma^2)$.

---

## 📊 Results

The system was tested using **Monte Carlo Simulations (1,000 runs)**.

| Mechanism | Epsilon ($\epsilon$) | Avg Error (MAE) | Relative Error | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Laplace** | 0.5 (High Privacy) | ~38,945 | 0.84% | Usable for trends |
| **Laplace** | **2.0 (Low Privacy)** | **~9,978** | **0.21%** | **Optimal for Analytics** |
| Gaussian | 2.0 | ~38,248 | 0.82% | Higher error for scalar data |

**Key Finding:** The Laplace Mechanism outperformed Gaussian for one-dimensional financial aggregation, achieving **>99.7% accuracy** at $\epsilon=2.0$.

---

## 📷 Visualizations

*(You can upload your screenshots here)*

* **Privacy-Utility Trade-off:** A bar chart showing how error decreases as Epsilon increases.
* **Sectoral Histogram:** A comparison showing that DP-protected counts (Technology, Finance, etc.) are nearly identical to the ground truth.

---

## 💻 How to Run

1.  Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/differential-privacy-finance.git](https://github.com/yourusername/differential-privacy-finance.git)
    ```
2.  Install dependencies:
    ```bash
    pip install pandas numpy matplotlib
    ```
3.  Run the main script:
    ```bash
    python main.py
    ```

---

## 📂 Project Structure

* `main.py`: The core script containing data generation, DP algorithms, and simulation logic.
* `synthetic_stock_trades.csv`: The dataset used for analysis.
* `README.md`: Project documentation.

---

