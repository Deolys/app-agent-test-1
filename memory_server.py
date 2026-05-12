from fastmcp import FastMCP
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

class MemoryServer:
    def __init__(self):
        self.mcp = FastMCP("Memory-Server")
        self.storage_path = Path("./memory_data.json")

    def _load_memory(self) -> dict:
        if not self.storage_path.exists():
            return {}
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_memory(self, data: dict):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @self.mcp.tool()
    def save(key: str, value: Any) -> bool:
        data = self._load_memory()
        data[key] = {"value": value, "timestamp": datetime.utcnow().isoformat()}
        self._save_memory(data)
        return True

    @self.mcp.tool()
    def get(key: str) -> Optional[dict]:
        data = self._load_memory()
        if key in data:
            d = data[key]
            return {"key": key, "value": d["value"], "timestamp": d["timestamp"]}
        return None

    @self.mcp.tool()
    def delete(key: str) -> bool:
        data = self._load_memory()
        if key in data:
            del data[key]
            self._save_memory(data)
            return True
        return False

    @self.mcp.tool()
    def list_keys(pattern: str = "*") -> list[str]:
        import fnmatch
        data = self._load_memory()
        return [k for k in data if fnmatch.fnmatch(k, pattern)]

    @self.mcp.tool()
    def save_with_namespace(key: str, value: Any, namespace: str = "default") -> bool:
        full_key = f"{namespace}:{key}"
        return self.save(full_key, value)

    @self.mcp.tool()
    def get_by_namespace(namespace: str = "default") -> list[dict]:
        data = self._load_memory()
        prefix = f"{namespace}:"
        return [
            {"key": k[len(prefix):], "value": d["value"], "timestamp": d["timestamp"]}
            for k, d in data.items() if k.startswith(prefix)
        ]

if __name__ == "__main__":
    server = MemoryServer()
    server.mcp.run(transport="stdio", show_banner=False, log_level='ERROR')
