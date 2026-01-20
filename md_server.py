#!/usr/bin/env python3
"""Simple HTTP server to view and edit markdown files in browser"""

import http.server
import socketserver
import os
import urllib.parse
import json
from pathlib import Path

try:
    import markdown
except ImportError:
    print("markdown library not found. Installing...")
    import subprocess
    import sys

    try:
        # Try with --break-system-packages (for Homebrew Python on macOS)
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--break-system-packages",
                "markdown",
            ]
        )
    except subprocess.CalledProcessError:
        print("\n❌ Could not auto-install markdown library.")
        print("Please install it manually:")
        print(f"  {sys.executable} -m pip install --break-system-packages markdown")
        print("  OR")
        print("  pip3 install --break-system-packages markdown")
        sys.exit(1)

    import markdown

PORT = 8000
SCRIPT_DIR = Path(__file__).parent


class MarkdownHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed_path.path)

        if path == "/" or path == "":
            self.serve_index()
        elif path.startswith("/edit/") and path.endswith(".md"):
            filename = path.replace("/edit/", "", 1)
            self.serve_editor(filename)
        elif path.endswith(".md"):
            self.serve_markdown(path.lstrip("/"))
        else:
            super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed_path.path)

        if path.startswith("/save/") and path.endswith(".md"):
            filename = path.replace("/save/", "", 1)
            self.save_markdown(filename)

    def serve_index(self):
        """Serve index page with list of markdown files"""
        # Find all markdown files recursively, excluding hidden folders
        md_files = []
        for root, dirs, files in os.walk(SCRIPT_DIR):
            # Remove hidden directories from the list (modifies in-place to skip them)
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.endswith(".md") and not file.startswith("."):
                    rel_path = os.path.relpath(os.path.join(root, file), SCRIPT_DIR)
                    md_files.append(rel_path)
        md_files.sort()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown Files</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 0 20px;
                    background: #fff;
                }}
                h1 {{
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 10px;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    margin: 10px 0;
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                    font-size: 16px;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .file-icon {{
                    margin-right: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>📝 Markdown Files</h1>
            <ul>
                {"".join([f'<li><span class="file-icon">📄</span><a href="/{f}">{f}</a> <a href="/edit/{f}" style="margin-left:10px;font-size:14px;">[edit]</a></li>' for f in md_files])}
            </ul>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_markdown(self, filename):
        """Serve markdown file as HTML"""
        filepath = SCRIPT_DIR / filename

        if not filepath.exists():
            self.send_error(404, f"File not found: {filename}")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            html_content = markdown.markdown(
                content,
                extensions=["extra", "codehilite", "tables", "fenced_code", "nl2br"],
            )

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{filename}</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                        max-width: 900px;
                        margin: 40px auto;
                        padding: 0 20px;
                        line-height: 1.6;
                        color: #24292e;
                        background: #fff;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    code {{
                        background-color: rgba(27,31,35,0.05);
                        border-radius: 3px;
                        padding: 0.2em 0.4em;
                        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                        font-size: 85%;
                    }}
                    pre {{
                        background-color: #f6f8fa;
                        border-radius: 3px;
                        padding: 16px;
                        overflow: auto;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                    }}
                    table th, table td {{
                        padding: 6px 13px;
                        border: 1px solid #dfe2e5;
                    }}
                    table th {{
                        font-weight: 600;
                        background-color: #f6f8fa;
                    }}
                    table tr:nth-child(2n) {{
                        background-color: #f6f8fa;
                    }}
                    blockquote {{
                        margin: 0;
                        padding: 0 1em;
                        color: #6a737d;
                        border-left: 0.25em solid #dfe2e5;
                    }}
                    ul, ol {{
                        padding-left: 2em;
                    }}
                    a {{
                        color: #0366d6;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    .back-link {{
                        display: inline-block;
                        margin-bottom: 20px;
                        color: #586069;
                    }}
                    .filename {{
                        color: #586069;
                        font-size: 14px;
                        margin-bottom: 8px;
                    }}
                </style>
            </head>
            <body>
                <a href="/" class="back-link">← Back to file list</a>
                <div class="filename">{filename} <a href="/edit/{filename}" style="margin-left:10px;">[edit]</a></div>
                {html_content}
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

    def serve_editor(self, filename):
        """Serve markdown editor"""
        filepath = SCRIPT_DIR / filename

        if not filepath.exists():
            self.send_error(404, f"File not found: {filename}")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Escape content for JavaScript
            content_escaped = (
                content.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            )

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Edit: {filename}</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: #f6f8fa;
                    }}
                    .header {{
                        max-width: 1200px;
                        margin: 0 auto 20px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    .back-link {{
                        color: #586069;
                        text-decoration: none;
                    }}
                    .filename {{
                        font-weight: 600;
                        color: #24292e;
                    }}
                    .editor-container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        height: calc(100vh - 120px);
                    }}
                    .panel {{
                        background: #fff;
                        border: 1px solid #d1d5da;
                        border-radius: 6px;
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                    }}
                    .panel-header {{
                        background: #f6f8fa;
                        padding: 10px 15px;
                        border-bottom: 1px solid #d1d5da;
                        font-weight: 600;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    textarea {{
                        flex: 1;
                        border: none;
                        padding: 15px;
                        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                        font-size: 14px;
                        resize: none;
                        outline: none;
                    }}
                    .preview {{
                        flex: 1;
                        padding: 15px;
                        overflow-y: auto;
                        line-height: 1.6;
                    }}
                    .btn {{
                        background: #2ea44f;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 600;
                    }}
                    .btn:hover {{
                        background: #2c974b;
                    }}
                    .btn:disabled {{
                        background: #94d3a2;
                        cursor: not-allowed;
                    }}
                    .message {{
                        margin-left: 10px;
                        color: #28a745;
                        font-size: 14px;
                    }}
                    /* Preview styles */
                    .preview h1, .preview h2, .preview h3 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; }}
                    .preview h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    .preview h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    .preview code {{
                        background-color: rgba(27,31,35,0.05);
                        border-radius: 3px;
                        padding: 0.2em 0.4em;
                        font-family: "SFMono-Regular", Consolas, monospace;
                        font-size: 85%;
                    }}
                    .preview pre {{
                        background-color: #f6f8fa;
                        border-radius: 3px;
                        padding: 16px;
                        overflow: auto;
                    }}
                    .preview pre code {{ background-color: transparent; padding: 0; }}
                    .preview ul, .preview ol {{ padding-left: 2em; }}
                    .preview a {{ color: #0366d6; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <a href="/" class="back-link">← Back to file list</a>
                    <div class="filename">Editing: {filename}</div>
                    <a href="/{filename}" class="back-link">View rendered</a>
                </div>
                <div class="editor-container">
                    <div class="panel">
                        <div class="panel-header">
                            Editor
                            <div>
                                <button class="btn" onclick="saveFile()">Save</button>
                                <span class="message" id="message"></span>
                            </div>
                        </div>
                        <textarea id="editor">{content_escaped}</textarea>
                    </div>
                    <div class="panel">
                        <div class="panel-header">Preview</div>
                        <div class="preview" id="preview"></div>
                    </div>
                </div>
                <script>
                    const editor = document.getElementById('editor');
                    const preview = document.getElementById('preview');
                    const message = document.getElementById('message');
                    
                    // Simple markdown to HTML converter (basic support)
                    function markdownToHtml(md) {{
                        let html = md;
                        
                        // Headers
                        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
                        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
                        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
                        
                        // Bold
                        html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                        
                        // Italic
                        html = html.replace(/\\*(.*?)\\*/g, '<em>$1</em>');
                        
                        // Code inline
                        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
                        
                        // Links
                        html = html.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2">$1</a>');
                        
                        // Paragraph breaks (double newline)
                        html = html.replace(/\\n\\n/g, '</p><p>');
                        
                        // Single newlines to <br>
                        html = html.replace(/\\n/g, '<br>');
                        
                        html = '<p>' + html + '</p>';
                        
                        // Lists
                        html = html.replace(/<p>- (.*?)<\\/p>/g, '<ul><li>$1</li></ul>');
                        html = html.replace(/<\\/ul><ul>/g, '');
                        
                        return html;
                    }}
                    
                    function updatePreview() {{
                        preview.innerHTML = markdownToHtml(editor.value);
                    }}
                    
                    async function saveFile() {{
                        const btn = event.target;
                        btn.disabled = true;
                        message.textContent = 'Saving...';
                        
                        try {{
                            const response = await fetch('/save/{filename}', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'text/plain; charset=utf-8' }},
                                body: editor.value
                            }});
                            
                            if (response.ok) {{
                                message.textContent = '✓ Saved!';
                                setTimeout(() => {{ message.textContent = ''; }}, 2000);
                            }} else {{
                                message.textContent = '✗ Error saving';
                                message.style.color = '#d73a49';
                            }}
                        }} catch (err) {{
                            message.textContent = '✗ Error: ' + err.message;
                            message.style.color = '#d73a49';
                        }} finally {{
                            btn.disabled = false;
                        }}
                    }}
                    
                    editor.addEventListener('input', updatePreview);
                    updatePreview();
                </script>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

    def save_markdown(self, filename):
        """Save edited markdown content"""
        filepath = SCRIPT_DIR / filename

        # Security check - ensure file is within SCRIPT_DIR (including subdirectories)
        try:
            filepath.resolve().relative_to(SCRIPT_DIR.resolve())
        except ValueError:
            self.send_error(403, "Access denied")
            return

        try:
            content_length = int(self.headers["Content-Length"])
            content = self.rfile.read(content_length).decode("utf-8")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())


if __name__ == "__main__":
    os.chdir(SCRIPT_DIR)

    with socketserver.TCPServer(("127.0.0.1", PORT), MarkdownHandler) as httpd:
        print(f"✓ Server started at http://localhost:{PORT}")
        print(f"✓ Serving markdown files from: {SCRIPT_DIR}")
        print(f"✓ Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")
