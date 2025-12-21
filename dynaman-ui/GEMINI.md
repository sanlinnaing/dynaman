# Dyna Management Tool - UI

## Introduction
The Dyna Management Tool UI is a modern Single Page Application (SPA) built to interact with the Dynamic Engine. It provides a visual interface for managing schemas and viewing data.

## Technologies Used
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router (inferred)
- **HTTP Client**: Fetch API / Axios (check `src/lib/api.ts`)

## Project Structure
- **src/components**: Reusable UI components.
- **src/pages**: Main view components (DataExplorer, SchemaEditor, Home).
- **src/lib**: Utility functions and API clients.
- **public**: Static assets.

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn

### Installation
1. Navigate to the `dynaman-ui` directory.
2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Development Server
```bash
npm run dev
```
The application will typically start at `http://localhost:5173`.

### Building for Production
```bash
npm run build
```
The output will be generated in the `dist` directory.

### Linting
```bash
npm run lint
```
