# Custom Instructions for GitHub Copilot

This project involves implementing a standalone application for order and payment processing, tailored for small to medium-sized businesses. The application must meet the functional and non-functional requirements outlined in the specification. Please follow these custom instructions to guide the implementation in Python:

1. **Frameworks and Libraries**:
   - Use **Flask** for the backend to handle user management, order processing, and reporting.
   - Use **SQLAlchemy** for database interactions and ORM.
   - For the frontend, integrate with **Jinja2** templates or suggest lightweight alternatives.

2. **Database**:
   - Design the database schema based on the provided Entity-Relationship (ER) diagram.
   - Use **SQLite** for offline capability, ensuring easy portability.

3. **Authentication and Security**:
   - Implement user authentication with **Flask-Login**.
   - Encrypt user credentials using **bcrypt** or similar libraries.
   - Ensure session management includes a 15-minute timeout.

4. **Performance**:
   - Optimize order processing to meet the requirement of completing transactions in under 1 second.
   - Ensure the dashboard loads within 2 seconds by caching frequently accessed data.

5. **Reporting**:
   - Generate reports in **PDF** using libraries like **ReportLab** and **CSV** using Python's built-in `csv` module.

6. **Backup and Restore**:
   - Implement database backup and restore functionality using Python's **shutil** module.

7. **Testing**:
   - Write unit tests for all critical functionalities using **pytest**.
   - Include integration tests for user workflows like order creation and payment processing.

8. **Code Quality**:
   - Follow **PEP 8** guidelines for Python code style.
   - Ensure modularity and documentation for maintainability.

9. **Offline Capability**:
   - Ensure the application can function without an internet connection by avoiding external dependencies during runtime.

10. **Deployment**:
    - Provide instructions for deploying the application on Windows, macOS, and Linux.

These instructions should guide Copilot to generate Python code that aligns with the project's requirements and best practices.