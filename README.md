# UTF-8 Text File Converter – Integration Project

## Overview
This project is a Python application designed to convert text files (`.txt`) to UTF-8 encoding. It implements asynchronous file conversion with progress tracking, detailed logging, and supports containerization and automation using Docker and a Makefile. The application only processes text files, as required by the assignment.

## Features
- **Text File Conversion:** Converts files with the `.txt` extension to UTF-8 encoding.
- **Asynchronous Processing:** Utilizes Python’s `asyncio` to concurrently process multiple files.
- **Progress Monitoring:** Uses `tqdm` to display a progress bar during the conversion process.
- **Logging:** Provides detailed logging (`INFO`, `WARNING`, and `ERROR`) for monitoring conversion progress and error handling.
- **Containerization & Automation:** Includes a Dockerfile and Makefile for easy building, running, and cleaning of the Docker container.

## Requirements
- Python 3.9 or higher
- Docker (if using containerization)
- Dependencies listed in `requirements.txt` (e.g., `tqdm`, `python-dotenv`)
- A `.env` file configured with the following environment variables:
  - `INPUT_DIR` – Absolute path to the input directory containing `.txt` files.
  - `OUTPUT_DIR` – Absolute path to the output directory where converted files will be saved.

## Setup

1. **Clone the repository:**
```bash
  git clone https://github.com/witoldkrzyk/integration-project
  cd integration-project
```

2. **Create and configure the .env file.**

In the project root, create a file named `.env` with the following content:
    
```env
  INPUT_DIR=/absolute/path/to/input/directory
  OUTPUT_DIR=/absolute/path/to/output/directory
```

Ensure that both directories exist before running the app.

### Run project using Docker
Run the application in Docker container step by step:

**Build the image:**
```bash
  make build
```

**Run the container:**
```bash
  make run
```

**Clean up the image (optional):**
```bash
  make clean
```

### Install dependencies (for local execution).

If you wish to run the application locally (without Docker), create a virtual environment and install dependencies:

```bash
  python -m venv venv
  . venv/bin/activate
  pip install -r requirements.txt
```

**Run the main script with:**
```bash
  python main.py
```

## Logging
The application logs events to the console using Python's `logging` module:
 * `INFO`: Start and end of processes, successful conversions.
 * `WARNING`: Fallbacks from UTF-8 to `latin-1`.
 * `ERROR`: Critical issues like missing files, invalid extensions, or crashes.

## License 

This project is released under the **MIT License**.

## Final Notes

You're ready to go! Just add your `.txt` files to the input folder and run the application.
All converted files will be saved in the output folder.
Unsupported file types will be moved to an error folder for review.