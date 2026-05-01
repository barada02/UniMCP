# How to Publish an Update to PyPI

Whenever you make improvements to the `unimcp` package and want to release a new version, follow these steps:

## 1. Update the Version Number
You need to bump the version number in two files:
- Open `pyproject.toml` and update the `version = "0.1.0"` field (e.g., to `"0.1.1"` or `"0.2.0"`).
- Open `src/unimcp/__init__.py` and update the `__version__ = "0.1.0"` string to match.

## 2. Clear Old Builds (Optional but Recommended)
To prevent accidentally re-uploading older versions, delete the contents of your `dist/` folder.
*In your terminal:*
```bash
# On Windows PowerShell
Remove-Item -Recurse -Force dist\*
# On Mac/Linux
rm -rf dist/*
```

## 3. Build the New Version
Compile your Python code into PyPI distribution formats (`.whl` and `.tar.gz`).
*In your terminal (with your virtual environment activated):*
```bash
python -m build
```

## 4. Upload to PyPI
Upload the newly built files to PyPI using `twine`. 
*In your terminal:*
```bash
twine upload dist/*
```

**Credentials reminder:**
- **Username:** `__token__`
- **Password:** *<Paste your PyPI API Token here>*
