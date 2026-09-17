# EXAMGUARD-AI

> An AI-powered examination document security and risk analysis platform for detecting suspicious documents, measuring document similarity, extracting document content, analyzing textual characteristics, and generating examination-security risk assessments.

---

## 📌 Project Overview

**EXAMGUARD-AI** is a research-oriented AI/ML platform designed to analyze examination-related documents and identify potential security risks.

The system combines:

- Document extraction
- Natural Language Processing
- Document similarity analysis
- Feature engineering
- Rule-based risk assessment
- Versioned risk analysis
- Alert generation
- Analytics
- REST APIs
- React-based frontend
- MySQL database
- Docker-based backend deployment

The platform is designed as a modular architecture so that additional AI/ML models and advanced risk-detection techniques can be integrated in future development phases.

---

# 🎯 Objectives

The main objectives of EXAMGUARD-AI are:

1. Analyze examination-related documents.
2. Extract machine-readable text from uploaded documents.
3. Perform NLP-based document analysis.
4. Compare documents using similarity analysis.
5. Generate examination-security risk scores.
6. Provide explainable risk factors.
7. Generate alerts based on detected risk.
8. Store analysis results for future investigation.
9. Provide analytics for document and risk monitoring.
10. Provide a scalable foundation for advanced AI/ML research.

---

# 🧠 Core Capabilities

## 1. Document Management

The platform supports:

- Document upload
- Document listing
- Document details
- Document metadata
- Document text extraction
- Persistent document storage

Uploaded documents are stored locally in:

```text
uploads/documents/
🏗️ System Architecture
                    ┌──────────────────────────┐
                    │       React Frontend     │
                    │      Vite Application    │
                    └────────────┬─────────────┘
                                 │
                                 │ HTTP / REST API
                                 ▼
                    ┌──────────────────────────┐
                    │       FastAPI Backend    │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       Document Layer       Analysis Layer     Risk Layer
              │                  │                  │
              │                  │                  │
              ▼                  ▼                  ▼
       Text Extraction          NLP           Risk Engine
              │                  │                  │
              └──────────────┬───┴──────────────┐   │
                             │                  │   │
                             ▼                  ▼   ▼
                       Similarity Engine   Alert Engine
                             │                  │
                             └────────┬─────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │     MySQL     │
                              │   Database    │
                              └───────────────┘

                         Document Storage
                                │
                                ▼
                        uploads/documents/
EXAMGUARD-AI/
│
├── backend/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── alerts.py
│   │   ├── analysis.py
│   │   ├── analytics.py
│   │   ├── document_text.py
│   │   ├── documents.py
│   │   ├── processing.py
│   │   ├── risk.py
│   │   └── similarity.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── analysis_result.py
│   │   ├── document.py
│   │   ├── document_text.py
│   │   ├── risk_score.py
│   │   └── similarity_result.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── analysis_result.py
│   │   ├── document.py
│   │   ├── document_text.py
│   │   ├── processing.py
│   │   ├── risk_score.py
│   │   └── similarity_result.py
│   │
│   ├── services/
│   │   ├── alert_engine.py
│   │   ├── document_extractor.py
│   │   ├── feature_engine.py
│   │   ├── nlp_analyzer.py
│   │   ├── processing_engine.py
│   │   ├── risk_engine.py
│   │   └── similarity_engine.py
│   │
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   └── documentsApi.js
│   │   │
│   │   ├── components/
│   │   │   └── DocumentCard.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── AlertManagement.jsx
│   │   │   └── DocumentDetails.jsx
│   │   │
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── tests/
│   ├── test_alert_engine.py
│   ├── test_api.py
│   ├── test_benchmark_reporting.py
│   ├── test_experiment_10_report.py
│   ├── test_experiment_13_reproducibility.py
│   ├── test_experiment_14_evidence_consolidation.py
│   ├── test_experiment_15_final_validation.py
│   ├── test_multi_document_evaluation.py
│   ├── test_performance_reliability.py
│   ├── test_real_document_evaluation.py
│   ├── test_risk_similarity.py
│   ├── test_risk_v1_vs_v2.py
│   ├── test_security_validation.py
│   ├── test_statistical_analysis.py
│   └── test_system_integration.py
│
├── uploads/
│   └── documents/
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Core Modules](#-core-modules)
- [Document Processing Workflow](#-document-processing-workflow)
- [Risk Assessment](#-risk-assessment)
- [Alert Management](#-alert-management)
- [Analytics](#-analytics)
- [API Endpoints](#-api-endpoints)
- [Database](#-database)
- [Environment Configuration](#-environment-configuration)
- [Local Installation](#-local-installation)
- [Backend Setup](#-backend-setup)
- [Frontend Setup](#-frontend-setup)
- [Docker Deployment](#-docker-deployment)
- [Persistent Storage](#-persistent-document-storage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Validation Status](#-validation-status)
- [Research Experiments](#-research-experiments)
- [Security Considerations](#-security-considerations)
- [Future Development](#-future-development)
- [Disclaimer](#-disclaimer)
- [Repository](#-repository)

---

# 🎯 Project Overview

Examination environments handle large numbers of documents such as:

- Question papers
- Examination reports
- Student documents
- Answer-related documents
- Supporting examination records
- Administrative examination documents

Manual inspection of these documents can become difficult when the number of documents increases.

EXAMGUARD-AI provides an automated analytical pipeline that can:

```text
Document
   ↓
Text Extraction
   ↓
NLP Analysis
   ↓
Feature Engineering
   ↓
Document Similarity
   ↓
Risk Assessment
   ↓
Alert Generation
   ↓
Analytics
