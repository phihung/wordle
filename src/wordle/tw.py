"""
Python script to install and run Tailwind CLI
To be used with fasthtml

Usage:
```python
app, rt = fast_app(hdrs=[
        Tailwind("public").run().get_link_tag()
    ],
    static_path="public"
)

# Add public/app.css to your .gitignore
```

Acknowledgement: This code is heavily inspired by the [pytailwindcss](https://github.com/timonweb/pytailwindcss) project.
"""

import os
import shlex
import subprocess
import tempfile
from pathlib import Path
import platform
import shutil
import stat

import httpx


DEFAULT_CONFIG = """
/** @type {import('tailwindcss').Config} */
module.exports = {
content: ["**/*.py"],
theme: {
    extend: {},
},
plugins: [],
}
"""

DEFAULT_SOURCE_CSS = """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""


class Tailwind:
    """Utility to download and run Tailwind CLI

    Usage: `app, rt = fast_app(hdrs=[Tailwind("public").run().get_link_tag()], static_path="public")`

    `public/app.css` should be in .gitignore
    """

    def __init__(self, static_path = None, filename="app.css", cfg: str = DEFAULT_CONFIG, css: str = DEFAULT_SOURCE_CSS):
        self.dir = tempfile.TemporaryDirectory()
        path = Path(self.dir.name)
        if static_path is None:
            self.output_css_path = path / filename
        else:
            self.output_css_path = Path(static_path) / filename
        self.filename = filename
        self.source_css_path = path / "src_app.css"
        self.cfg_path = path / "tailwind.config.js"
        self.cfg_path.write_text(cfg)
        self.source_css_path.write_text(css)

    def run(self):
        kwargs = {
            "cwd": os.getcwd(),
            "env": {},
            "capture_output": False,
            "check": False,
        }

        cli = cached_download_tailwind_cli()
        args = shlex.split(
            f"-c {self.cfg_path} -i {self.source_css_path} -o {self.output_css_path}"
        )
        subprocess.run([str(cli)] + args, **kwargs)
        return self
    
    def get_link_tag(self):
        from fasthtml.common import Link

        return Link(rel="stylesheet", href=self.filename, type="text/css")

    def get_style_tag(self):
        """Get Style object in script tags"""
        from fasthtml.common import StyleX

        return StyleX(self.output_css_path)

    def cleanup(self):
        self.dir.cleanup()


CACHE_DIR = Path.home() / ".cache/fasthtml"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cached_download_tailwind_cli(version="latest") -> Path:
    ext = ".exe" if platform.system().lower() == "win32" else ""
    path = CACHE_DIR / f"tailwindcss{ext}"
    if path.exists():
        return path
    url = get_download_url(version)
    download_file(url, path)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def get_download_url(version):
    os_name, arch = platform.system().lower(), platform.machine().lower()
    os_name = os_name.lower().replace("win32", "windows").replace("darwin", "macos")
    ext = ".exe" if os_name == "windows" else ""

    target = {
        "amd64": f"{os_name}-x64{ext}",
        "x86_64": f"{os_name}-x64{ext}",
        "arm64": f"{os_name}-arm64",
        "aarch64": f"{os_name}-arm64",
    }[arch.lower()]

    v = "download" if version == "latest" else version
    binary_name = f"tailwindcss-{target}"
    return f"https://github.com/tailwindlabs/tailwindcss/releases/latest/{v}/{binary_name}"


def download_file(url, path):
    with httpx.stream("GET", url, follow_redirects=True) as resp:
        print(f"Downloading Tailwind CLI from {url}")
        with open(f"{path}.tmp", "wb") as f:
            for chunk in resp.iter_bytes(65536):
                f.write(chunk)
    shutil.move(f"{path}.tmp", path)
    print(f"Tailwind CLI Binary saved to {path}")
