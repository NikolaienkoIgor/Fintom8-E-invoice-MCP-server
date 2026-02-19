# PyPI Release Instructions

## ✅ Single Source of Truth

**The source code is now in `src/fintom8_mcp/server.py`** - there's only ONE copy!

- **Development**: Edit `src/fintom8_mcp/server.py` (or use root `server.py` wrapper for convenience)
- **PyPI Build**: Builds from `src/fintom8_mcp/server.py` automatically
- **No more sync needed!** 🎉

## Prerequisites
Make sure you have `build` and `twine` installed:
```bash
pip install --upgrade build twine
```

## Step 1: Update Version
Edit `pyproject.toml` and update the version:
```toml
version = "0.1.X"
```

## Step 2: Build the Package
Build from the **root directory**:
```bash
python3 -m build
```

This will create in `dist/`:
- `e_invoice_mcp-<version>.tar.gz` (source distribution)
- `e_invoice_mcp-<version>-py3-none-any.whl` (wheel distribution)

## Step 3: Test the Build (Recommended)
Install the built wheel in a clean venv and verify it works:

```bash
python3 -m venv .venv-test
source .venv-test/bin/activate   # on Windows: .venv-test\Scripts\activate
pip install dist/e_invoice_mcp-*.whl
e-invoice-mcp --help
deactivate
rm -rf .venv-test
```

If `e-invoice-mcp --help` runs without errors, the package is correct.

## Step 4: Check the Build (Optional)
Verify the build files before uploading:
```bash
twine check dist/*
```

## Step 5: Upload to PyPI

### Test PyPI (Recommended first)
Upload to Test PyPI to verify everything works:
```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
You'll need Test PyPI credentials (create account at https://test.pypi.org if needed).

### Production PyPI
Once verified on Test PyPI, upload to production:
```bash
twine upload dist/*
```

You'll be prompted for your PyPI credentials:
- Username: Your PyPI username
- Password: Your PyPI password or API token (recommended)

**Note:** If you're using API tokens, use `__token__` as the username and your token as the password.

## Step 6: Verify the Release
After uploading, verify the release at:
https://pypi.org/project/e-invoice-mcp/

## Summary
1. Update version in `pyproject.toml`
2. Build: `python3 -m build` (from root)
3. Test: install wheel in venv and run `e-invoice-mcp --help`
4. Upload: `twine upload dist/*`

## Note about `pypi_dist/`
The `pypi_dist/` directory is now **deprecated**. The package builds from the root `src/` directory. You can safely ignore or remove `pypi_dist/` if you want.
