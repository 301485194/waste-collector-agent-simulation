# 🗑️ Waste Collector Simulation
**Author:** Mohammed Safique Hossain  

A Python-based **AI agent simulation** that models urban waste collection using **AIMA-style agent–environment interaction** and **object-oriented programming (OOP)** principles.

---

## 🧠 Overview
This project simulates a smart waste collection system where an **autonomous agent** decides whether to collect or move based on the type of day — *Garbage* or *Recycle*.  
It detects contamination, issues fines, and provides a detailed step-by-step log of actions.

---

## ⚙️ Features
- 🧩 **Autonomous Agent Logic:** Perception-based decision-making using a reflex agent model.  
- 🗑️ **Day-Aware Behavior:**  
  - Garbage Day → collects garbage, checks contamination in garbage bins.  
  - Recycle Day → collects recyclables, checks contamination in recycle bins.  
- 💸 **Fine System:**  
  - `$100` → for uncollected scheduled waste.  
  - `$200` → for contamination (wrong waste type in bin).  
- 🎛️ **Interactive CLI:** Prompts the user for:
  - Day type: Garbage / Recycle  
  - Number of locations: e.g., 30  
- 🧱 **Clean OOP Design:** Classes for `Environment`, `Agent`, and `BinState`.

---

## 🚀 How to Run

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/301485194/waste-collector-agent-simulation.git
cd waste-collector-agent-simulation
