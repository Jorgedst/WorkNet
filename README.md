# WorkNet

WorkNet is a Professional Network Application built with Python and [Flet](https://flet.dev/). It allows users to connect with other professionals, manage company profiles, view a network graph of connections, discover jobs, and manage professional projects.

## Features

- **User Profiles & Authentication**: Register, log in, and manage your professional profile.
- **Interactive Network Graph**: Visualize connections between professionals and companies.
- **Company Management**: View company profiles, directories, and associated professionals.
- **Jobs & Projects**: Discover job opportunities and track professional projects.
- **Modern UI**: Clean and responsive user interface built entirely in Python using Flet.

## Prerequisites

- Python 3.8+

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/WorkNet.git
   cd WorkNet
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the application, run:

```bash
python main.py
```
*(Alternatively, you can run `flet run main.py` if flet is available in your PATH)*

## Project Structure

- `main.py` - Main entry point with routing and layout management.
- `views/` - Contains the UI pages (Login, Register, Dashboard, Network, etc.).
- `components/` - Reusable UI components like the sidebar and navigation.
- `services/` - Business logic and data management (e.g., `graph_service.py`).
- `models/` - Data models.
- `utils/` - Utility functions and design tokens (colors, theme).
- `assets/` - Static assets like fonts, icons, and images.

## License

This project is open-source and available under the [MIT License](LICENSE).
