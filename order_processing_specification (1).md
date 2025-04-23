# Software Requirements Specification (SRS)

## 1. Overview

This document outlines the **functional** and **non-functional** requirements for a **standalone application** designed to process **customer orders** and **payments**. The application is intended for use by small to medium-sized businesses that need a simple, offline-capable solution for handling transactions.

---

## 2. Functional Requirements

These are the core features and behaviors the application must provide:

### 2.1 User Management
- **FR1.1**: The application shall allow users to log in with a username and password.
- **FR1.2**: The application shall support user roles (e.g., Admin, Cashier).

### 2.2 Customer Management
- **FR2.1**: The application shall allow users to add, edit, and delete customer profiles.
- **FR2.2**: The application shall store customer information including name, contact number, email, and address.

### 2.3 Product Catalog
- **FR3.1**: The application shall allow users to create and manage a product inventory.
- **FR3.2**: Each product entry shall include a name, SKU, description, price, and stock quantity.

### 2.4 Order Processing
- **FR4.1**: The application shall allow users to create new orders by selecting products and entering quantities.
- **FR4.2**: The application shall calculate total cost including taxes and discounts.
- **FR4.3**: The application shall allow users to update or cancel orders before they are finalized.

### 2.5 Payment Processing
- **FR5.1**: The application shall support payment types: cash, credit/debit card, and store credit.
- **FR5.2**: The application shall validate and record payment details.
- **FR5.3**: The application shall generate receipts for completed transactions.

### 2.6 Reporting
- **FR6.1**: The application shall generate daily, weekly, and monthly sales reports.
- **FR6.2**: Reports shall be exportable in PDF and CSV formats.

### 2.7 Data Backup & Restore
- **FR7.1**: The application shall allow users to create a manual backup of the database.
- **FR7.2**: The application shall support restoring data from a backup file.

---

## 3. Non-Functional Requirements

These define how the system should perform or behave.

### 3.1 Performance
- **NFR1**: The application shall load the main dashboard within 2 seconds.
- **NFR2**: Order processing (including payment confirmation) shall complete in under 1 second.

### 3.2 Usability
- **NFR3**: The application shall have an intuitive and user-friendly graphical interface.
- **NFR4**: Minimal training (less than 1 hour) should be needed for new users.

### 3.3 Reliability
- **NFR5**: The application shall be available for use 99.9% of the time when the device is powered on.
- **NFR6**: In case of a crash, the application shall recover the last unsaved state where possible.

### 3.4 Security
- **NFR7**: All user credentials shall be stored securely using encryption.
- **NFR8**: User sessions shall timeout after 15 minutes of inactivity.

### 3.5 Portability
- **NFR9**: The application shall be installable on Windows, macOS, and Linux operating systems.
- **NFR10**: It shall operate without an internet connection once installed.

### 3.6 Maintainability
- **NFR11**: Codebase shall be modular and documented to support updates and patches.
- **NFR12**: Configuration files and settings shall be separated from core logic.

---

## 4. Diagrams

### 4.1 Entity-Relationship (ER) Diagram
![ER Diagram](assets/Entity-Relationship_(ER)_diagram.svg)
the diagram is in this path :
C:\Users\younes.radi\copilot\spec_usecase\assets\Entity-Relationship_(ER)_diagram.png
