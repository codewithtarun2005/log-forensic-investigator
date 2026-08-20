# 🔐 Log Forensic Investigator

A cybersecurity forensic investigation system that combines **log analysis, AI-powered threat detection, digital evidence integrity verification, SHA-256 hashing, blockchain registration, and chain of custody management**.

## 📌 Project Overview

Log Forensic Investigator is designed to help investigators analyze suspicious activities in server logs and maintain the integrity of digital evidence.

The system provides two major capabilities:

1. **AI-Powered Log Forensic Analysis**
   - Searches and analyzes uploaded/server logs
   - Retrieves relevant log events
   - Identifies suspicious IP addresses and attack patterns
   - Generates a cybersecurity incident report using AI

2. **Digital Evidence Integrity Verification**
   - Registers digital evidence
   - Generates a SHA-256 hash
   - Stores the evidence hash on blockchain
   - Verifies whether evidence has been modified
   - Maintains a chain-of-custody record

## ✨ Key Features

- 🔍 Log searching and analysis
- 🤖 AI-powered cybersecurity incident reports
- 🌐 Suspicious IP detection
- 🚨 Brute-force and lateral-movement detection
- 🔐 SHA-256 digital evidence hashing
- ⛓️ Blockchain-based evidence registration
- 🛡️ Evidence integrity verification
- 🚨 Tampering detection
- 🔗 Chain-of-custody tracking
- 📊 Streamlit-based user interface
- 🔄 AI fallback analysis when the external AI API is unavailable

## 🏗️ System Architecture

```text
                    LOG FORENSIC ANALYSIS
                            
Server Logs
     ↓
Log Parser
     ↓
Text Chunking
     ↓
Embeddings
     ↓
ChromaDB
     ↓
Relevant Log Retrieval
     ↓
AI Threat Analysis
     ↓
Incident Report


                  DIGITAL EVIDENCE MANAGEMENT

Digital Evidence
     ↓
SHA-256 Hash
     ↓
Evidence Registration
     ↓
Blockchain
     ↓
Integrity Verification
     ↓
VERIFIED / TAMPERED
     ↓
Chain of Custody