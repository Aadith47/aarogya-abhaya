# Arogya Abhaya

### AI-Powered Rural Healthcare Platform

Arogya Abhaya is an AI-powered digital healthcare platform designed to improve healthcare accessibility for rural and underserved communities. The platform focuses on **pregnant women, newborns/children, teenagers, and community healthcare workers** by combining healthcare management with Artificial Intelligence, Machine Learning, Deep Learning, Computer Vision, and conversational AI.

The system provides intelligent health monitoring, nutritional deficiency detection, pregnancy posture analysis, mental health chatbot support, vaccination tracking, supplement management, and role-based healthcare administration.

---

## Features

### AI-Powered Health Monitoring

* AI-based analysis of health-related data
* Early identification of potential nutritional deficiencies
* Health status classification and reporting
* Data-driven health insights for healthcare workers

### Pregnancy Posture Correction

* Real-time posture analysis using computer vision
* Pose estimation using MediaPipe
* Deep learning-based posture classification
* Exercise and workout guidance
* Real-time corrective feedback

### Mental Health Chatbot

* Conversational AI support for teenagers
* Natural Language Processing (NLP)
* Context-aware interaction
* Mental health and wellness guidance
* Support for escalation of critical cases

### Vaccination & Supplement Tracking

* Digital vaccination schedules
* Upcoming vaccination reminders
* Supplement distribution tracking
* Health activity notifications
* Historical health records

### Healthcare Worker Management

* ASHA worker beneficiary management
* Supervisor dashboards
* Beneficiary monitoring
* Health record management
* Role-Based Access Control (RBAC)
* Case tracking and follow-up

---

## System Architecture

The platform follows a modular architecture consisting of:

```text
                    AROGYA ABHAYA
                          |
          +---------------+---------------+
          |               |               |
     Pregnant         Newborns &       Teenagers
      Women            Children           |
          |               |               |
     Posture           Health &        AI Chatbot
     Analysis        Deficiency        NLP Support
          |             Detection
          |               |
          +---------------+---------------+
                          |
                  Healthcare Workers
                    ASHA / JPHA / LHA
                          |
                    Central Database
```

---

## Technology Stack

### Programming Languages

* Python
* JavaScript
* HTML5
* CSS3

### Frontend

* React.js
* HTML5
* CSS3
* JavaScript

### Backend

* Node.js
* Express.js
* Flask
* REST APIs

### Artificial Intelligence & Machine Learning

* TensorFlow
* Keras
* Scikit-learn
* CNN
* LSTM
* MobileNetV2
* Machine Learning
* Deep Learning

### Computer Vision

* OpenCV
* MediaPipe
* Pose Estimation
* Image Classification

### Data & Database

* PostgreSQL
* Supabase
* NumPy
* Pandas

### Development Tools

* Git
* GitHub
* Visual Studio Code
* Postman
* Streamlit

---

## AI Modules

### 1. Newborn & Child Health Monitoring

The health monitoring module uses Deep Learning techniques to analyze health-related inputs and generate health status information.

**Technologies:**

* Python
* TensorFlow
* Keras
* CNN
* Scikit-learn

---

### 2. Pregnancy Posture Correction

The posture correction module analyzes body movement and posture through camera input.

**Technologies:**

* Python
* OpenCV
* MediaPipe
* CNN
* LSTM
* Computer Vision

The system extracts body landmarks, analyzes movement patterns, and provides feedback regarding posture and exercise performance.

---

### 3. AI Mental Health Chatbot

The chatbot module provides conversational support for teenagers using Natural Language Processing techniques.

**Capabilities:**

* Conversational interaction
* Mental health guidance
* Context-based responses
* Sentiment/emotional analysis
* Critical-case escalation

---

## User Roles

The platform supports multiple user categories:

| Role           | Responsibilities                                     |
| -------------- | ---------------------------------------------------- |
| Beneficiary    | Access personalized healthcare services              |
| Pregnant Woman | Pregnancy monitoring, posture guidance and reminders |
| Caregiver      | Manage newborn/child health information              |
| Teenager       | Access mental health chatbot                         |
| ASHA Worker    | Manage and monitor beneficiaries                     |
| JPHA/LHA       | Supervise healthcare activities and view reports     |

---

## Security & Access Control

The system incorporates security-oriented design features including:

* Role-Based Access Control (RBAC)
* Secure authentication
* JWT-based authentication
* OTP-based verification
* HTTPS communication
* Data encryption
* Audit logging
* Data integrity validation

---

## Database Design

The platform uses a centralized database architecture for managing healthcare information.

Major entities include:

```text
User
 |
 +-- Supervisor
 |
 +-- ASHA Worker
       |
       +-- Beneficiary
              |
              +-- Health Record
              +-- Vaccine Schedule
              +-- Supplement Distribution
              +-- Deficiency Report
              +-- Notifications
              +-- Chatbot Interaction
```

---

## Project Architecture

```text
Frontend
   |
   | REST API
   v
Backend
   |
   +--------------------+
   |                    |
   v                    v
AI/ML Services       Database
   |                    |
   +--------+-----------+
            |
            v
      Healthcare Data
```

The architecture separates the presentation, application, AI/ML, and data layers to support maintainability and scalability.

---

## Development Workflow

```text
Requirement Analysis
        ↓
System Design
        ↓
Database Design
        ↓
Frontend Development
        ↓
Backend Development
        ↓
AI/ML Model Development
        ↓
API Integration
        ↓
Module Integration
        ↓
Testing & Evaluation
        ↓
Deployment
```

---

## Project Objectives

* Develop an AI-powered healthcare platform for rural communities
* Enable early identification of potential health risks
* Provide pregnancy posture correctio
