import subprocess
import os
import re
from typing import List, Dict, Optional, Set

class AppInfo:
    def __init__(self, desktop_id: str, name: str, icon: str, exec_cmd: str, mimetypes: List[str]):
        self.desktop_id = desktop_id
        self.name = name
        self.icon = icon
        self.exec_cmd = exec_cmd
        self.mimetypes = mimetypes

    def __repr__(self):
        return f"AppInfo({self.name}, {self.desktop_id})"

class MimeManager:
    ESSENTIALS = {
        "Web Browser": ["text/html", "application/xhtml+xml", "x-scheme-handler/http", "x-scheme-handler/https"],
        "PDF Reader": ["application/pdf"],
        "Video Player": ["video/mp4", "video/x-matroska", "video/webm", "video/quicktime"],
        "Music Player": ["audio/mpeg", "audio/ogg", "audio/flac", "audio/wav"],
        "Image Viewer": ["image/jpeg", "image/png", "image/gif", "image/svg+xml"],
        "Text Editor": ["text/plain", "text/markdown", "application/x-shellscript"],
        "Terminals": ["x-scheme-handler/terminal"]
    }

    def __init__(self):
        self.apps: Dict[str, AppInfo] = {}  # desktop_id -> AppInfo
        self.mime_to_apps: Dict[str, List[str]] = {}  # mime -> [desktop_id]
        self.mime_list: List[str] = []
        self.mime_to_ext: Dict[str, List[str]] = {} # mime -> [*.txt, *.docx]
        self.load_system_info()

    def load_system_info(self):
        # 1. Load all MIME types
        mime_types_path = "/usr/share/mime/types"
        if os.path.exists(mime_types_path):
            try:
                with open(mime_types_path, "r") as f:
                    self.mime_list = sorted(list(set([line.strip() for line in f if line.strip() and not line.startswith("#")])))
            except Exception as e:
                print(f"Error loading mime types: {e}")
        
        # fallback if mime_list is empty
        if not self.mime_list:
            self.mime_list = ["text/plain", "text/html", "application/pdf"] # Basic defaults

        # 2. Load extension globs
        self._load_extensions()

        # 3. Load all desktop files
        desktop_dirs = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        for ddir in desktop_dirs:
            if not os.path.exists(ddir):
                continue
            try:
                for filename in sorted(os.listdir(ddir)):
                    if filename.endswith(".desktop"):
                        self._parse_desktop_file(os.path.join(ddir, filename), filename)
            except Exception as e:
                print(f"Error reading directory {ddir}: {e}")

    def _load_extensions(self):
        glob_files = ["/usr/share/mime/globs", "/usr/share/mime/globs2"]
        for gpath in glob_files:
            if not os.path.exists(gpath): continue
            try:
                with open(gpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        
                        parts = line.split(":")
                        if len(parts) >= 2:
                            mimetype = parts[-2]
                            glob = parts[-1]
                            if mimetype not in self.mime_to_ext:
                                self.mime_to_ext[mimetype] = []
                            if glob not in self.mime_to_ext[mimetype]:
                                self.mime_to_ext[mimetype].append(glob)
            except Exception as e:
                print(f"Error loading extensions from {gpath}: {e}")

    def _parse_desktop_file(self, path: str, desktop_id: str):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            if "[Desktop Entry]" not in content:
                return

            # Simple Ini parsing logic
            lines = content.splitlines()
            in_entry = False
            item_data = {}
            for line in lines:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_entry = True
                    continue
                elif line.startswith("["):
                    in_entry = False
                
                if in_entry and "=" in line:
                    key, val = line.split("=", 1)
                    item_data[key.strip()] = val.strip()

            if item_data.get("NoDisplay") == "true":
                return

            name = item_data.get("Name", desktop_id)
            icon = item_data.get("Icon", "application-x-executable")
            exec_cmd = item_data.get("Exec", "")
            mime_str = item_data.get("MimeType", "")
            mimetypes = [m.strip() for m in mime_str.split(";") if m.strip()]

            if desktop_id not in self.apps:
                app = AppInfo(desktop_id, name, icon, exec_cmd, mimetypes)
                self.apps[desktop_id] = app
                for mime in mimetypes:
                    if mime not in self.mime_to_apps:
                        self.mime_to_apps[mime] = []
                    self.mime_to_apps[mime].append(desktop_id)
        except Exception:
            pass 

    def get_supporting_apps(self, mimetype: str) -> List[AppInfo]:
        app_ids = self.mime_to_apps.get(mimetype, [])
        seen = set()
        result = []
        for aid in app_ids:
            if aid in self.apps and aid not in seen:
                result.append(self.apps[aid])
                seen.add(aid)
        return sorted(result, key=lambda x: x.name)

    def get_default_app_id(self, mimetype: str) -> Optional[str]:
        try:
            result = subprocess.run(["xdg-mime", "query", "default", mimetype], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return None

    def set_default_app(self, mimetype: str, desktop_id: str) -> bool:
        try:
            subprocess.run(["xdg-mime", "default", desktop_id, mimetype], check=True)
            return True
        except Exception as e:
            print(f"Error setting default for {mimetype}: {e}")
            return False

    def unset_default(self, mimetype: str):
        mimeapps_path = os.path.expanduser("~/.config/mimeapps.list")
        if not os.path.exists(mimeapps_path):
            return
        
        try:
            with open(mimeapps_path, "r") as f:
                lines = f.readlines()
            
            with open(mimeapps_path, "w") as f:
                for line in lines:
                    if line.startswith(f"{mimetype}="):
                        continue
                    f.write(line)
            # Notify system
            subprocess.run(["update-desktop-database", os.path.expanduser("~/.local/share/applications")], 
                          capture_output=True)
        except Exception as e:
            print(f"Error unsetting {mimetype}: {e}")

    def get_user_overrides(self) -> List[Dict[str, str]]:
        mimeapps_path = os.path.expanduser("~/.config/mimeapps.list")
        if not os.path.exists(mimeapps_path):
            return []
        
        overrides = []
        try:
            in_default_apps = False
            with open(mimeapps_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line == "[Default Applications]":
                        in_default_apps = True
                        continue
                    elif line.startswith("[") and in_default_apps:
                        in_default_apps = False
                        break
                        
                    if in_default_apps and "=" in line:
                        mime, app_id = line.split("=", 1)
                        if mime and app_id:
                            overrides.append({"mimetype": mime, "app_id": app_id.strip()})
        except Exception as e:
            print(f"Error reading user overrides: {e}")
        return overrides

if __name__ == "__main__":
    manager = MimeManager()
    print(f"Loaded {len(manager.mime_list)} MIME types and {len(manager.apps)} applications.")
    test_mime = "text/plain"
    print(f"Default for {test_mime}: {manager.get_default_app_id(test_mime)}")
    apps = manager.get_supporting_apps(test_mime)
    print(f"Apps supporting {test_mime}: {[app.name for app in apps]}")
