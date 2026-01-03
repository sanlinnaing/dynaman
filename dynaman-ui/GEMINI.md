# Dyna Management Tool - UI

## Introduction
The Dyna Management Tool UI is a modern Single Page Application (SPA) built to interact with the Dynamic Engine. It provides a visual interface for managing schemas and viewing data.

## Technologies Used
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **HTTP Client**: Axios (configured in `src/lib/api.ts`)
- **State Management**: React Context (Auth) + Local State
- **Internationalization**: Custom `i18n` hook (English/Japanese)

## Project Structure
- **src/components**: Reusable UI components.
  - `ui/`: Shadcn/UI-like base components.
  - `Layout.tsx`: Main dashboard shell.
  - `RequireAuth.tsx`: Route protection wrapper.
- **src/context**: React Context providers (e.g., `AuthContext`).
- **src/pages**: Main view components (Login, DataExplorer, SchemaEditor, Home).
- **src/lib**: Utility functions, API clients, and i18n.

## Authentication Implementation (Added Jan 2026)

### 1. API Client (`src/lib/api.ts`)
- **Interceptor**: Automatically injects the `Authorization: Bearer <token>` header into every request.
- **Error Handling**: Intercepts 401 Unauthorized responses to redirect users to `/login`.

### 2. State Management (`src/context/AuthContext.tsx`)
- **AuthContext**: Manages `isAuthenticated` state and provides `login()` and `logout()` methods.
- **Persistence**: Stores the JWT in `localStorage` to persist sessions across page reloads.

### 3. Routing (`src/App.tsx`)
- **`/login`**: Public route for authentication.
- **Protected Routes**: All dashboard routes (`/`, `/schemas`, `/data`) are wrapped in `<RequireAuth>`.
- **Admin Routes**: `/admin/users` is wrapped in `<RequireSystemAdmin>` (or appropriate role check) to restrict access to user management.

## Features

### User Management
- **User List**: View all registered users, their roles, and status.
- **Create User**: System Admins and User Admins can create new users with specific roles (User, User Admin, System Admin).
- **Delete User**: System Admins can delete users (except themselves).
- **Role-Based Access**: The UI adapts to the logged-in user's role.
    - **System Admin**: Full access, including Schema Management and User Management.
    - **User Admin**: Access to User Management and Data Explorer. Schema Management is hidden.
    - **User**: Access to Data Explorer only. Schema Management and User Management are hidden.

## Permissions & Roles
- **System Admin**:
  - Can create/edit schemas.
  - Can create, edit, and delete data records.
  - Can manage all users (create, delete).
- **User Admin**:
  - Can manage users (except System Admins).
  - Can create, edit, and delete data records.
  - Read-only access to schemas.
- **User**:
  - Can create, edit, and delete data records.
  - Read-only access to schemas.

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- npm

### Installation
```bash
npm install
```

### Running the Development Server
```bash
npm run dev
```
The application starts at `http://localhost:3000` (proxied to backend services via Docker/Nginx in production setups).

### Building for Production
```bash
npm run build
```