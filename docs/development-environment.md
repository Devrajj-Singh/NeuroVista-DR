# Development Environment

## Overview

This document records the development environment verified for the **NeuroVista-DR** project.

The environment is intended to support development of the MATLAB-based explainable AI pipeline, supporting Python services, web application, and Git/GitHub workflow for **SIH 2026 Problem Statement 26038 — Explainable AI for Diabetic Retinopathy Screening in Rural India**.

---

## System Environment

| Component | Verified Version / Status |
|---|---|
| Operating System | Windows |
| Git | 2.51.0.windows.1 |
| Python | 3.13.7 |
| pip | 25.2 |
| Node.js | v24.13.0 |
| npm | 11.15.0 |
| MATLAB | R2026a Update 5 |
| MATLAB License | Academic |

---

## Python Environment

A project-specific Python virtual environment has been created using:

```powershell
python -m venv .venv