# Coding Platform

This project is a web-based coding platform designed for students and beginners to write, run, and manage code in Python and C#. The platform includes a code editor, console output display, and package management features.

## Features

- **Code Editor**: A user-friendly interface for writing code in Python and C#.
- **Execution Environment**: Run console applications securely and view output in real-time.
- **Package Management**: Install and manage packages for both Python and C# projects.
- **Download Executables**: Users can download their compiled executable files after execution.

## Project Structure

```
coding-platform
├── backend
│   ├── python-service
│   └── csharp-service
├── frontend
│   └── src
├── config
├── server.js
└── README.md
```

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.x
- .NET SDK for C#

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd coding-platform
   ```

2. Install backend dependencies:
   - For Python service:
     ```
     cd backend/python-service
     pip install -r requirements.txt
     ```
   - For C# service, use the .NET CLI to restore packages.

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

### Running the Application

1. Start the backend services:
   - For Python service:
     ```
     cd backend/python-service
     python app.py
     ```
   - For C# service, use the .NET CLI to run the application.

2. Start the frontend:
   ```
   cd frontend
   npm start
   ```

3. Access the application in your web browser at `http://localhost:3000`.

## Usage

- Navigate to the code editor to write your code.
- Use the console to view output and errors.
- Manage packages through the provided interface.
- Download your executable files after running your code.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.