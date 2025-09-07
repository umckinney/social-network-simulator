# Architecture Documentation

## System Overview

This project implements a modular social networking platform with command-line and REST API interfaces. It supports CRUD operations for users and statuses, and partial support for pictures (read and reconcile only). It allows for reconciliation between the database and file system using tag-based organization. The architecture is layered to enforce separation of concerns, with explicit validation and structured logging throughout.

---

## Layered Architecture

1. **menu.py** (User Interface Layer)
   - Presents a command-line interface to the user
   - Maps input commands to appropriate controller functions
   - Validates user input before passing it downstream

2. **main.py** (Controller Layer)
   - Orchestrates the main flow of control
   - Delegates work to the domain logic layer
   - Handles loading/saving of data and batch operations

3. **domain_logic_layer.py** (Domain Logic Layer)
   - Enforces business rules (e.g., cascading deletes)
   - Normalizes tags and prepares picture metadata
   - Validates operations before passing them to the database

4. **data_access_layer.py** (Data Access Layer)
   - Provides generic CRUD functions (`add_object`, `get_object`, etc.)
   - Abstracts direct interactions with the Dataset database

5. **socialnetwork_model.py** (Database Schema Layer)
   - Initializes and configures tables using the `dataset` library
   - Applies primary keys, foreign keys, and unique constraints

6. **api.py** (API Layer)
   - Exposes the application via a RESTful web API using Flask
   - Provides routes for reading users, statuses, pictures, and reconciled differences
   - Uses SQLAlchemy models and Flask-RESTful `Resource` classes to organize endpoints

**Supporting Modules:**
- `validators.py`: Validates fields, formats, and file types across layers
- `file_structure_manager.py`: Builds directory structure and pointer files from tags
- `logging_decorator.py`: Adds structured logging to function calls using the `@log` decorator

---

## Module Summaries

- **menu.py**  
  Handles command-line user interaction. Maps options to controller functions, collects and validates user input.

- **main.py**  
  Orchestrates program logic. Bridges UI and domain layers, handles data reconciliation, pointer file creation, and batch file operations.

- **domain_logic_layer.py**  
  Applies business rules (e.g., cascading delete, tag normalization). Wraps core CRUD logic and ensures valid data is passed to the DB layer.

- **data_access_layer.py**  
  Implements generic CRUD operations over Dataset tables using a functional approach.

- **socialnetwork_model.py**  
  Defines and initializes the schema using the `dataset` library. Ensures tables exist and constraints are applied.

- **validators.py**  
  Validates fields like `user_id`, `email`, and `tags`. Also includes normalization helpers for tags and filenames.

- **file_structure_manager.py**  
  Creates user- and tag-specific directories and pointer files for picture metadata.

- **logging_decorator.py**  
  Provides a reusable `@log` decorator that logs function calls and arguments using the `loguru` library.

- **api.py**  
  Exposes the application’s data via a RESTful interface using Flask and Flask-RESTful. Defines routes for retrieving user, status, and picture records individually or in bulk, and for initiating reconciliation between the database and file system. Each route is encapsulated in a `Resource` class, promoting modular, readable API logic.

---

## Data Model Overview

- **UserTable**
  - `id` (integer, auto-incremented)
  - `user_id` (string, **primary key**)
  - `email`
  - `user_name`
  - `user_last_name`

- **StatusTable**
  - `id` (integer, auto-incremented)
  - `status_id` (string, **primary key**)
  - `user_id` (FK → UserTable.user_id)
  - `status_text`

- **PictureTable**
  - `id` (integer, auto-incremented)
  - `picture_id` (string, **primary key**)
  - `user_id` (FK → UserTable.user_id)
  - `file_name` (string, original file name for the picture)
  - `tags` (stringified list)

Constraints:
- Picture and Status entries are tied to a User
- Deleting a User cascades deletion of their Pictures

---

## Persistence Strategy

The system uses [Dataset](https://dataset.readthedocs.io/) to manage an SQLite database with simplified access to tables. It avoids raw SQL by exposing tables as Python objects.

Data is also exported/imported via JSON and CSV, with custom logic in `main.py` for handling edge cases and validation.

Pointer files are created during reconciliation in user/tag-nested folders to simulate file system presence of pictures.

---

## Logging Strategy

All key functions are decorated with `@log`, which captures inputs and key execution points using `loguru`. Log levels are:

| **Level** | **Use Case** |
|-----------|--------------|
| `DEBUG`   | Function calls, validation details, internal state |
| `INFO`    | Successful high-level operations |
| `WARNING` | Recoverable input/data errors |
| `ERROR`   | Unexpected crashes or fatal issues |

Logs are structured and can be filtered based on severity in different environments.

---

## Validation Strategy

Validation happens early—typically at the menu and domain layers—to prevent invalid data from reaching the database. Common validators include:

- `valid_name_format`: Ensures valid string formats
- `user_email_validator`: Uses `email_validator` lib
- `tag_normalizer`, `safe_parse_tags`: Normalize and safely decode tag lists
- Attribute length and file extension checks

Logging is integrated to distinguish between expected (debug/info) and unexpected (warning) validation outcomes.

---

## Testing Strategy

The application is tested using `unittest` with >85% coverage. The test suite includes:

- Unit tests for each layer (e.g., `test_main.py`, `test_menu.py`)
- Mocked tests for Flask routes (`test_api.py`)
- Integration-style tests for file and validation logic
- Use of `unittest.mock.patch` to isolate logic and simulate errors

Edge cases, cascading deletes, tag normalization, and pointer file creation are all tested directly.

---

## API Endpoints

- `GET /`  
  Returns an HTML index page with links and instructions for available endpoints

### User Endpoints
- `GET /users`  
  Returns a list of all user records  
  **Example Response:**
  ```json
  [
    {
      "id": 1,
      "user_id": "abc123",
      "email": "user@example.com",
      "user_name": "First",
      "user_last_name": "Last"
    }
  ]
  ```

- `GET /users/<user_id>`  
  Returns a single user record matching the given `user_id`  
  **Example Response:**
  ```json
  {
    "id": 1,
    "user_id": "abc123",
    "email": "user@example.com",
    "user_name": "First",
    "user_last_name": "Last"
  }
  ```

### Status Endpoints
- `GET /statuses`  
  Returns a list of all status records  
  **Example Response:**
  ```json
  [
    {
      "id": 1,
      "status_id": "status001",
      "user_id": "abc123",
      "status_text": "Hello World"
    }
  ]
  ```

- `GET /statuses/<status_id>`  
  Returns a single status record matching the given `status_id`  
  **Example Response:**
  ```json
  {
    "id": 1,
    "status_id": "status001",
    "user_id": "abc123",
    "status_text": "Hello World"
  }
  ```

### Picture Endpoints
- `GET /images`  
  Returns a list of all picture records  
  **Example Response:**
  ```json
  [
    {
      "id": 1,
      "picture_id": "img001",
      "user_id": "abc123",
      "file_name": "beach.png",
      "tags": "['#vacation', '#beach']"
    }
  ]
  ```

- `GET /images/<picture_id>`  
  Returns a single picture record matching the given `picture_id`  
  **Example Response:**
  ```json
  {
    "id": 1,
    "picture_id": "img001",
    "user_id": "abc123",
    "file_name": "beach.png",
    "tags": "['#vacation', '#beach']"
  }
  ```

### Reconciliation Endpoint
- `GET /differences`  
  Compares picture records between the database and file system

  - No query parameter → reconciles all users
  - With `?user_id=...` → reconciles a specific user's pictures

  **Example Response:**
  ```json
  {
    "abc123": {
      "missing_in_db": ["vacation.png"],
      "missing_in_fs": ["beach.jpg"]
    }
  }
  ```
