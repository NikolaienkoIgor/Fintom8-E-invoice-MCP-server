# PyPI Release Instructions for Version 0.1.16

## Prerequisites
Make sure you have `build` and `twine` installed:
```bash
pip install --upgrade build twine
```

## Step 1: Build the Package
Navigate to the `pypi_dist` directory and build the distribution files:
```bash
cd pypi_dist
python3 -m build
```

This will create:
- `dist/e_invoice_mcp-0.1.16.tar.gz` (source distribution)
- `dist/e_invoice_mcp-0.1.16-py3-none-any.whl` (wheel distribution)

## Step 2: Check the Build (Optional but Recommended)
Verify the build files before uploading:
```bash
twine check dist/*
```

## Step 3: Upload to PyPI

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

## Step 4: Verify the Release
After uploading, verify the release at:
https://pypi.org/project/e-invoice-mcp/

## Summary
The version has been updated to **0.1.16** in `pypi_dist/pyproject.toml`. 
All you need to do is:
1. Install build tools: `pip install --upgrade build twine`
2. Build: `cd pypi_dist && python3 -m build`
3. Upload: `twine upload dist/*`
