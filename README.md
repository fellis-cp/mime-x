# 🚀 Mime-X

**Mime-X** is a GUI application designed to simplify the management of XDG MIME type associations. Built with PySide6.

## 📦 Installation

### Prerequisites

- Python 3.8+
- PySide6
- xdg-mime

### Quick Install

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mime-x.git
   cd mime-x
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the installer to add Mime-X to your application menu:
   ```bash
   ./scripts/install.sh
   ```

## 🚀 Usage

You can launch Mime-X from your application menu or directly from the terminal (with venv active):

```bash
python src/mime_x/main.py
```

### Dashboard
The Dashboard gives you a bird's eye view of your most important applications. Click on any category to manage its supporting apps.

### Explorer
Use the Explorer to dive deep into specific MIME types. Search by extension (e.g., `.txt`) or type (e.g., `text/html`) to find exactly what you need.

### Audit
The Audit page shows only the associations you have manually changed, allowing you to reset them back to system defaults with a single click.

## 🛠️ Development

### Directory Structure
```text
mime-x/
├── src/
│   └── mime_x/        # Core package
├── scripts/           # Deployment scripts
├── data/              # Desktop files and assets
└── tests/             # (Future) Unit tests
```

### Packaging
This project uses `pyproject.toml` for modern Python packaging. To install in editable mode:
```bash
pip install -e .
```

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

*Made with ❤️ for the Linux Community.*
