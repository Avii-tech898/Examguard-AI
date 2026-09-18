# EXAMGUARD-AI

> AI-Powered Examination Document Security, Similarity & Risk Assessment Platform

EXAMGUARD-AI is a research-oriented AI/ML platform designed to analyze examination-related documents, extract and process textual content, compare documents for similarity, assess document-level security risk, generate alerts, and provide analytical insights through a web-based dashboard.

The system combines a **FastAPI backend**, **React/Vite frontend**, **Python-based AI/ML processing**, **MySQL database**, and **Docker-based backend deployment** into a modular architecture.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Core Features](#core-features)
5. [System Architecture](#system-architecture)
6. [Technology Stack](#technology-stack)
7. [Project Structure](#project-structure)
8. [Document Processing Workflow](#document-processing-workflow)
9. [NLP Analysis](#nlp-analysis)
10. [Document Similarity](#document-similarity)
11. [Risk Engine](#risk-engine)
12. [Alert Management](#alert-management)
13. [Analytics](#analytics)
14. [Verified API Endpoints](#verified-api-endpoints)
15. [Database Architecture](#database-architecture)
16. [Environment Configuration](#environment-configuration)
17. [Local Backend Setup](#local-backend-setup)
18. [React Frontend Setup](#react-frontend-setup)
19. [Docker Deployment](#docker-deployment)
20. [Persistent Document Storage](#persistent-document-storage)
21. [Swagger / OpenAPI](#swagger--openapi)
22. [Testing and Validation](#testing-and-validation)
23. [Research Experiments](#research-experiments)
24. [Security Considerations](#security-considerations)
25. [Current Validation Status](#current-validation-status)
26. [Future Development](#future-development)
27. [Repository](#repository)
28. [Project Status](#project-status)

---

# Project Overview

EXAMGUARD-AI provides an automated analytical pipeline for examination documents.

The platform is designed around the following workflow:

```text
Document Upload
      ↓
Document Storage
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
      ↓
Web Dashboard
