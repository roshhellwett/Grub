### 1. Add New Themes
The easiest way to contribute is to add your own GRUB theme to the `themes/` folder.

#### Theme Requirements
- Theme folder structure: `themes/<theme-name>/<resolution>/`
- Required: `theme.txt` file
- Recommended: `metadata.json` file
- Optional: Preview images

#### Steps to Add a Theme
1. Create a folder for your theme: `themes/your-theme-name/`
2. Create resolution subfolders: `1080p/`, `2k/`, `4k/`
3. Add theme files to each resolution folder
4. Create a `metadata.json` with theme info
5. Submit a pull request

#### Example Structure
```
themes/my-awesome-theme/
├── 1080p/
│   ├── theme.txt
│   ├── background.png
│   ├── select_c.png
│   ├── select_e.png
│   └── select_w.png
├── 2k/
│   └── ...
├── 4k/
│   └── ...
└── metadata.json
```

#### metadata.json Format
```json
{
  "name": "My Awesome Theme",
  "author": "Your Name",
  "description": "Description of your theme",
  "version": "1.0.0",
  "license": "MIT"
}
```

### 2. Report Issues
Found a bug or have a feature request? Please open an issue on GitHub with:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (distro, Python version, etc.)

### 3. Improve Documentation
- Fix typos or unclear explanations
- Add examples
- Translate to other languages
- Improve troubleshooting guides

### 4. Code Contributions
For code contributions:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/zenithopensourceprojects/projectgrub.git
cd projectgrub

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run the application
python -m projectgrub start
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for public functions
- Keep functions focused and small

## Testing

Write tests for new features:
- Unit tests in `tests/test_*.py`
- Test both success and failure cases
- Mock external dependencies

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/projectgrub

# Run specific test file
pytest tests/test_validators.py -v
```

Thank you for contributing to ProjectGRUB! 🎉
