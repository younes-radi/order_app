# Custom Instructions for GitHub Copilot

This repository contains a **Software Requirements Specification (SRS)** for a standalone application designed to process **customer orders** and **payments** for small to medium-sized businesses. Please use the following custom instructions to guide implementation:

## Functional Priorities
1. Implement **User Management** with secure login and role-based access control (Admin, Cashier).
2. Develop **Customer Management** to handle CRUD operations for customer profiles.
3. Build a **Product Catalog** to manage inventory with attributes like SKU, price, and stock quantity.
4. Create an **Order Processing** system to handle product selection, quantity input, and cost calculations (including taxes and discounts).
5. Add **Payment Processing** supporting cash, credit/debit cards, and store credit, with receipt generation.
6. Include **Reporting** for sales data (daily, weekly, monthly) exportable in PDF and CSV formats.
7. Provide **Data Backup & Restore** functionality for database safety.

## Non-Functional Priorities
1. Ensure **Performance**: 
   - Dashboard loads within 2 seconds.
   - Order processing completes in under 1 second.
2. Focus on **Usability**: 
   - Intuitive UI requiring minimal training (<1 hour).
3. Guarantee **Reliability**: 
   - 99.9% uptime and crash recovery for unsaved states.
4. Prioritize **Security**: 
   - Encrypt user credentials and enforce session timeouts (15 minutes).
5. Ensure **Portability**: 
   - Application must run on Windows, macOS, and Linux, and work offline.
6. Maintain **Maintainability**: 
   - Modular, well-documented codebase with separated configuration files.

## Technical Choices
- Use **Python** as the primary programming language.
- Leverage frameworks like **Flask** or **Django** for backend development.
- Use **SQLite** for offline-capable database storage.
- Follow **PEP 8** coding standards for consistency and readability.

## Performance and Maintainability
- Optimize database queries for fast response times.
- Write unit tests for critical functionalities (e.g., login, order processing, payment validation).
- Use a modular architecture to simplify future updates and patches.

## Additional Notes
- Refer to the **Entity-Relationship Diagram** in `assets/entity-relationship_diagram.png` for database design.
- Ensure the application is designed to operate offline without requiring internet connectivity.

These instructions aim to ensure that GitHub Copilot generates code aligned with the project's requirements and priorities.