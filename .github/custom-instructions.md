# Custom Instructions for GitHub Copilot

This project involves implementing a **standalone application** for **customer order and payment processing** using **Python** and **PyQT**. The application must adhere to the following requirements:

## Functional Priorities
1. **User Management**: Implement secure login with role-based access (Admin, Cashier).
2. **Customer Management**: Enable CRUD operations for customer profiles.
3. **Product Catalog**: Manage product inventory with details like SKU, price, and stock.
4. **Order Processing**: Support order creation, updates, cancellations, and cost calculations (including taxes/discounts).
5. **Payment Processing**: Handle multiple payment types (cash, card, store credit) and generate receipts.
6. **Reporting**: Generate and export sales reports in PDF/CSV formats.
7. **Data Backup & Restore**: Provide manual backup and restore functionality.

## Non-Functional Priorities
1. **Performance**: Ensure the main dashboard loads within 2 seconds and order processing completes in under 1 second.
2. **Usability**: Design an intuitive GUI requiring minimal training (<1 hour).
3. **Reliability**: Achieve 99.9% uptime and implement crash recovery for unsaved states.
4. **Security**: Encrypt user credentials and enforce session timeouts after 15 minutes of inactivity.
5. **Portability**: Ensure compatibility with Windows, macOS, and Linux, and offline functionality post-installation.
6. **Maintainability**: Use a modular, well-documented codebase with separated configuration files.

## Technical Choices
- Use **PyQT** for the graphical interface.
- Store data in a lightweight database (e.g., SQLite).
- Follow **MVC architecture** for maintainability.
- Ensure the codebase is scalable for future updates.

## Additional Notes
- Prioritize modularity and reusability in the code.
- Include unit tests for critical functionalities.
- Optimize for offline-first usage.

Please tailor suggestions and code snippets to align with these requirements and the chosen tech stack.