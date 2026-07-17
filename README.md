# Isiro — Personal Finance Management & Statement Intelligence Platform

![Isiro Logo](#)

Isiro is a smart personal finance management platform designed to help individuals and small businesses track expenses, manage budgets, import bank statements, and gain insights into their financial habits.

The system combines manual transaction tracking with intelligent document processing to automatically extract transactions from PDF and CSV bank statements, reducing the effort required to maintain accurate financial records.

Built as a final-year project, Isiro demonstrates the integration of web development, financial data processing, OCR technology, and data visualization.

---

## 🚀 Features

### Manual Expense & Income Tracking

Record financial transactions manually with:

- Amount tracking
- Transaction dates
- Categories
- Descriptions
- Payment methods
- Income and expense classification

---

### 📄 PDF Bank Statement Import

Upload bank statements in PDF format and allow Isiro to automatically:

- Extract transaction tables
- Detect statement headers
- Identify transaction dates
- Extract descriptions
- Detect income and expenses
- Store transactions automatically

Supports different bank statement formats through intelligent column mapping.

---

### 📊 CSV Import

Import transaction data from CSV files with:

- Automatic column detection
- Flexible header matching
- Transaction validation
- Duplicate prevention

---

### 🔍 OCR Document Extraction

For scanned statements, Isiro uses OCR technology to extract readable text from documents.

Features:

- Image-based PDF support
- Text extraction using Tesseract OCR
- Transaction recovery from scanned files

---

### 📈 Financial Analytics Dashboard

Understand financial behaviour through:

- Expense summaries
- Income tracking
- Spending breakdowns
- Category analysis
- Monthly trends
- Savings rate calculations

---

### 💰 Budget Management

Create and monitor budgets by category.

Users can:

- Set monthly limits
- Track spending progress
- Compare actual spending against targets

---

### 📑 Reports Export

Generate financial reports in:

- PDF format
- CSV format

Useful for:

- Personal records
- Financial reviews
- Business reporting

---

### 🔐 Security & Privacy

Isiro ensures:

- User authentication
- Private financial records
- User-specific data access
- Protected uploads

Your financial information belongs only to you.

---

# How It Works

## 1. Upload Statement

Users upload:

- PDF bank statements
- CSV transaction files

---

## 2. Transaction Extraction

Isiro processes the document using:

- PDF table extraction
- OCR extraction
- Intelligent header detection
- Column mapping

---

## 3. Review & Categorise

Users can:

- Review imported transactions
- Edit categories
- Correct transaction types
- Remove unwanted records

---

## 4. Financial Insights

The system generates:

- Spending summaries
- Budget progress
- Financial reports
- Dashboard insights

---

# Technology Stack

## Backend

- Python
- Django
- Django Authentication
- Django ORM

## Frontend

- HTML5
- CSS3
- JavaScript
- Django Templates

## Data Processing

- PDF parsing
- CSV processing
- OCR extraction
- Intelligent column mapping

## Database

- SQLite (development)
- PostgreSQL (production recommended)

## Document Processing

- pdfplumber
- Tesseract OCR

---

# Project Architecture
