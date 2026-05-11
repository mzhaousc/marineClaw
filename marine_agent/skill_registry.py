import re
from pathlib import Path
from typing import Optional

import yaml


class SkillRegistry:
    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, dict] = {}
        self._load_skills()

    def _find_main_md(self, skill_dir: Path) -> Optional[Path]:
        name = skill_dir.name
        for p in [skill_dir / f"{name}.md", skill_dir / f"{name}_primary.md"]:
            if p.exists():
                return p
        fallback = sorted([f for f in skill_dir.iterdir() if f.is_file() and f.suffix == ".md"])
        return fallback[0] if fallback else None

    def _load_skills(self) -> None:
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            md_path = self._find_main_md(skill_dir)
            if not md_path:
                continue
            text = md_path.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            if not isinstance(fm, dict):
                continue
            body = m.group(2).strip()
            scripts_dir = skill_dir / "scripts"
            scripts_list = sorted([p.name for p in scripts_dir.iterdir() if p.is_file()]) if scripts_dir.exists() else []
            skill_name = fm.get("name", skill_dir.name)
            self.skills[skill_name] = {
                "name": skill_name,
                "display_name": fm.get("display-name", skill_name),
                "category": fm.get("category", "marine-genomics"),
                "short_description": str(fm.get("short-description", "")).replace("\n", " ").strip(),
                "starting_prompt": str(fm.get("starting-prompt", "")).replace("\n", " ").strip(),
                "body": body,
                "skill_dir": str(skill_dir),
                "scripts_dir": str(scripts_dir) if scripts_dir.exists() else None,
                "scripts_list": scripts_list,
                "md_path": str(md_path),
            }

    def get_all_summaries(self) -> list[dict]:
        return [
            {
                "name": s["name"],
                "display_name": s["display_name"],
                "category": s["category"],
                "short_description": s["short_description"],
            }
            for s in self.skills.values()
        ]

    def get_skill(self, name: str) -> Optional[dict]:
        return self.skills.get(name)

    def get_skills_by_names(self, names: list[str]) -> list[dict]:
        return [self.skills[n] for n in names if n in self.skills]

    def __len__(self) -> int:
        return len(self.skills)
