# Markdown Server

A lightweight Python HTTP server for viewing and editing Markdown files in your browser with live preview.

## Features

- 📝 **View** markdown files with GitHub-style rendering
- ✏️ **Edit** markdown files with live preview
- 🔄 **Auto-refresh** preview as you type
- 📁 **Recursive folder support** - finds all `.md` files in subdirectories
- 🚫 **Ignores hidden folders** (`.git`, `.vscode`, etc.)
- 💾 **Save directly** from the browser
- 🎨 **Clean, modern UI** with GitHub-inspired styling

## Requirements

- Python 3.7 or higher
- `markdown` library

## Installation

### 1. Clone or download this project

```bash
cd /path/to/your/markdown/files
```

### 2. Set up a virtual environment (recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install markdown
```

**Alternative**: If you get "externally-managed-environment" error without venv:

```bash
pip3 install --break-system-packages markdown
```

## Usage

### Starting the Server

1. **With virtual environment** (recommended):
```bash
source .venv/bin/activate
python3 md_server.py
```

2. **Without virtual environment**:
```bash
python3 md_server.py
```

The server will start at http://localhost:8000

### Viewing and Editing

1. Open your browser to http://localhost:8000
2. You'll see a list of all markdown files
3. Click any filename to **view** the rendered markdown
4. Click **[edit]** to **edit** the file with live preview
5. Click **Save** button to save your changes
6. Click "View rendered" to see the full styled version

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:

```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Then restart the server
python3 md_server.py
```

### Change Port

To use a different port, edit `md_server.py` and change:

```python
PORT = 8000  # Change to any port you like
```

### Missing Markdown Library

If the auto-install fails:

```bash
# With venv activated
pip install markdown

# Or without venv
pip3 install --break-system-packages markdown
```

## File Structure

```
your-project/
├── md_server.py          # The server script
├── README.md             # This file
├── *.md                  # Your markdown files
└── subdirectory/
    └── *.md              # Markdown files in subfolders (also served)
```

## Features in Detail

### Viewing
- GitHub-style markdown rendering
- Proper handling of newlines (single newline = line break)
- Support for headers, bold, italic, code, links, lists, tables
- Syntax highlighting for code blocks

### Editing
- Split-screen editor with live preview
- Save changes with one click
- Security checks to prevent directory traversal
- Real-time preview as you type

## Configuration

Edit the following in `md_server.py`:

- `PORT = 8000` - Change server port
- Extensions: Modify the `markdown.markdown()` call to add/remove extensions

## License

Free to use and modify as needed.

## Tips

- Keep the virtual environment activated while using the server
- The server serves files from the directory where `md_server.py` is located
- Hidden files and folders (starting with `.`) are automatically excluded
- All markdown files in subdirectories are accessible

## Deactivating Virtual Environment

When done, deactivate the virtual environment:

```bash
deactivate
```
