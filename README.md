# Dynaman - Dynamic Schema PoC

[日本語で読む](README.ja.md)

**Dynaman** is a Proof of Concept (PoC) project designed to demonstrate the architecture and implementation of **unfixed, dynamic schemas**—a core pattern found in modern **NoCode/LowCode platforms**.

Unlike traditional applications with hard-coded database models, Dynaman allows users to define data structures (Entities/Schemas) at runtime. The system dynamically generates validation logic and API endpoints to support these user-defined structures without requiring code changes or deployments.

## 🎯 Core Concept

The primary goal is to showcase how to handle **User-Defined Requirements** where the data shape is not known at compile time. This is achieved through:

1.  **Metadata-Driven Architecture**: Storing schema definitions (Metadata) separately from the actual data (Execution Data).
2.  **Dynamic Pydantic Models**: Constructing Python classes and validation rules on-the-fly based on stored metadata.
3.  **Schemaless Storage**: Utilizing MongoDB's flexibility to store variable content while enforcing strict application-level validation.

## 🛠 Tech Stack

### Backend (`/engine`)
*   **Language**: Python 3.13+
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Async web framework)
*   **Database Driver**: [Motor](https://motor.readthedocs.io/) (Async MongoDB driver)
*   **Validation**: [Pydantic](https://docs.pydantic.dev/) (Dynamic model creation)
*   **Architecture**: Clean Architecture / Domain-Driven Design (DDD) principles separating Metadata and Execution contexts.

### Frontend (`/dynaman-ui`)
*   **Framework**: [React](https://react.dev/) (with Vite)
*   **Language**: TypeScript
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **UI Components**: [shadcn/ui](https://ui.shadcn.com/)
*   **State/Data**: React Hooks, Axios

## ✨ Key Features

*   **Schema Editor**: specific UI to define new Entities (e.g., "Product", "Employee") with custom fields.
*   **Supported Field Types**:
    *   String, Number, Boolean
    *   **Date** (with validation)
    *   **Reference** (Link to other dynamic entities)
*   **Dynamic CRUD API**: Automatically generated REST endpoints for every defined entity.
*   **Data Explorer**: Generic data grid to view, search, edit, and delete records for any entity.
*   **Runtime Validation**: Robust data integrity checks based on user-defined rules (Required fields, Data types).

## 📂 Project Structure

```
dynaman/
├── engine/                 # Python Backend
│   ├── api/                # FastAPI Routers
│   ├── building_blocks/    # Shared kernel/utils
│   ├── execution_context/  # Handling runtime Data Records
│   ├── metadata_context/   # Handling Schema definitions
│   └── main.py             # Entry point
│
└── dynaman-ui/             # React Frontend
    ├── src/
    │   ├── components/     # UI Components (Forms, Layouts)
    │   ├── pages/          # Application Views (Schema Editor, Explorer)
    │   └── lib/            # Utilities (API client)
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.13+
*   Node.js 18+
*   MongoDB (Running locally or via Docker)

### Backend Setup
1.  Navigate to `engine`:
    ```bash
    cd engine
    ```
2.  Create and activate virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server:
    ```bash
    fastapi dev main.py
    ```
    API will be available at `http://localhost:8000`.

### Frontend Setup
1.  Navigate to `dynaman-ui`:
    ```bash
    cd dynaman-ui
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start development server:
    ```bash
    npm run dev
    ```
    UI will be available at `http://localhost:5173`.

---

*This project is for educational and demonstration purposes.*

## 🤖 AI Development

This project was totally developed by **GCA** (Gemini Code Assist).

