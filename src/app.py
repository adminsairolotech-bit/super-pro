#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import signal
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


# -------------------------------
# Synthesized architecture notes:
# - awesome-claude-code: strong governance/validation, repo-health checks, multi-output views
# - ui-ux-pro-max-skill: data-driven design-system + brand/token synchronization
# - everything-claude-code: skill-centric agent OS with per-agent runtime config
# - cloude-ai-agiant-superpowers: cross-tool plugin metadata + CLI integration posture
# -------------------------------


APP_NAME = "super-pro"
APP_VERSION = "1.0.0"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080


@dataclass
class AppConfig:
    root_dir: Path
    log_level: str = "INFO"
    data_dir: Path = field(default_factory=lambda: Path("data"))
    skills_dir: Path = field(default_factory=lambda: Path(".agents/skills"))
    plugins_dir: Path = field(default_factory=lambda: Path(".agents/plugins"))
    output_dir: Path = field(default_factory=lambda: Path("build"))
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    strict_validation: bool = False

    @staticmethod
    def from_sources(root_dir: Path, config_path: Optional[Path] = None) -> "AppConfig":
        env = os.environ
        cfg: Dict[str, Any] = {}

        if config_path and config_path.exists():
            loaded = load_config_file(config_path)
            if isinstance(loaded, dict):
                cfg = loaded

        def get(name: str, default: Any) -> Any:
            return env.get(name, cfg.get(name, default))

        data_dir = root_dir / str(get("SUPER_PRO_DATA_DIR", "data"))
        skills_dir = root_dir / str(get("SUPER_PRO_SKILLS_DIR", ".agents/skills"))
        plugins_dir = root_dir / str(get("SUPER_PRO_PLUGINS_DIR", ".agents/plugins"))
        output_dir = root_dir / str(get("SUPER_PRO_OUTPUT_DIR", "build"))
        origins_raw = get("SUPER_PRO_ALLOWED_ORIGINS", "*")
        origins = [o.strip() for o in str(origins_raw).split(",") if o.strip()]
        strict = str(get("SUPER_PRO_STRICT_VALIDATION", "false")).lower() in {"1", "true", "yes"}

        return AppConfig(
            root_dir=root_dir,
            log_level=str(get("SUPER_PRO_LOG_LEVEL", "INFO")).upper(),
            data_dir=data_dir,
            skills_dir=skills_dir,
            plugins_dir=plugins_dir,
            output_dir=output_dir,
            allowed_origins=origins or ["*"],
            strict_validation=strict,
        )


@dataclass
class SkillAgentConfig:
    provider: str
    model: Optional[str]
    raw: Dict[str, Any]


@dataclass
class Skill:
    name: str
    path: Path
    description: str
    tags: List[str]
    agents: List[SkillAgentConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginManifest:
    source: str
    name: str
    version: str
    description: str
    commands: List[Dict[str, Any]]
    raw: Dict[str, Any]


@dataclass
class ValidationIssue:
    level: str
    code: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


class RepoRegistry:
    def __init__(self, config: AppConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.skills: Dict[str, Skill] = {}
        self.plugins: List[PluginManifest] = []
        self.design_data: Dict[str, List[Dict[str, str]]] = {}
        self.issues: List[ValidationIssue] = []

    def load_all(self) -> None:
        self._load_skills()
        self._load_plugins()
        self._load_design_data()
        self._validate_registry()

    # From everything-claude-code: scalable skill discovery with per-agent config
    def _load_skills(self) -> None:
        skills_dir = self.config.skills_dir
        if not skills_dir.exists():
            self.issues.append(
                ValidationIssue(
                    level="warning",
                    code="skills_dir_missing",
                    message=f"Skills directory not found: {skills_dir}",
                )
            )
            return

        for child in sorted(skills_dir.iterdir()):
            if not child.is_dir():
                continue
            skill_name = child.name
            skill_md = child / "SKILL.md"
            description, tags = parse_skill_markdown(skill_md)

            agents: List[SkillAgentConfig] = []
            agents_dir = child / "agents"
            if agents_dir.exists():
                for agent_file in sorted(agents_dir.glob("*.yaml")) + sorted(agents_dir.glob("*.yml")):
                    data = load_config_file(agent_file) or {}
                    provider = agent_file.stem
                    model = None
                    if isinstance(data, dict):
                        model = str(data.get("model")) if data.get("model") else None
                    agents.append(SkillAgentConfig(provider=provider, model=model, raw=data if isinstance(data, dict) else {}))

            self.skills[skill_name] = Skill(
                name=skill_name,
                path=child,
                description=description,
                tags=tags,
                agents=agents,
                metadata={
                    "has_skill_doc": skill_md.exists(),
                    "agent_count": len(agents),
                },
            )

    # From cloude-ai-agiant-superpowers + ui-ux-pro-max-skill: plugin marketplace metadata ingestion
    def _load_plugins(self) -> None:
        candidate_paths = [
            self.config.root_dir / ".agents/plugins/marketplace.json",
            self.config.root_dir / ".claude-plugin/plugin.json",
            self.config.root_dir / ".claude-plugin/marketplace.json",
            self.config.root_dir / ".cursor-plugin/plugin.json",
            self.config.plugins_dir / "marketplace.json",
        ]
        seen = set()
        for path in candidate_paths:
            if path in seen or not path.exists():
                continue
            seen.add(path)
            data = load_json(path)
            if not isinstance(data, dict):
                continue

            if "plugins" in data and isinstance(data["plugins"], list):
                for item in data["plugins"]:
                    manifest = normalize_plugin_manifest(item, source=str(path))
                    if manifest:
                        self.plugins.append(manifest)
            else:
                manifest = normalize_plugin_manifest(data, source=str(path))
                if manifest:
                    self.plugins.append(manifest)

    # From ui-ux-pro-max-skill: data-driven design system CSV assets
    def _load_design_data(self) -> None:
        data_candidates = [
            self.config.root_dir / ".claude/skills/design-system/data",
            self.config.data_dir,
        ]
        for d in data_candidates:
            if not d.exists() or not d.is_dir():
                continue
            for csv_file in sorted(d.glob("*.csv")):
                rows = load_csv(csv_file)
                self.design_data[csv_file.stem] = rows

    # From awesome-claude-code: governance/validation checks
    def _validate_registry(self) -> None:
        if not self.skills:
            self.issues.append(
                ValidationIssue(level="warning", code="no_skills", message="No skills discovered.")
            )

        for name, skill in self.skills.items():
            if not skill.metadata.get("has_skill_doc"):
                self.issues.append(
                    ValidationIssue(
                        level="warning",
                        code="missing_skill_doc",
                        message=f"Skill '{name}' missing SKILL.md",
                        context={"skill": name},
                    )
                )
            if not skill.agents:
                self.issues.append(
                    ValidationIssue(
                        level="info",
                        code="missing_agent_config",
                        message=f"Skill '{name}' has no agent config files.",
                        context={"skill": name},
                    )
                )

        if not self.plugins:
            self.issues.append(
                ValidationIssue(level="info", code="no_plugins", message="No plugin manifests found.")
            )

    def repo_health(self) -> Dict[str, Any]:
        error_count = sum(1 for i in self.issues if i.level == "error")
        warning_count = sum(1 for i in self.issues if i.level == "warning")
        return {
            "ok": error_count == 0,
            "errors": error_count,
            "warnings": warning_count,
            "skills": len(self.skills),
            "plugins": len(self.plugins),
            "design_datasets": len(self.design_data),
            "timestamp": now_iso(),
        }

    # From awesome-claude-code alternative outputs: generate sorted indices
    def generate_indexes(self) -> Dict[str, Path]:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        outputs: Dict[str, Path] = {}

        skills_sorted_az = sorted(self.skills.values(), key=lambda s: s.name.lower())
        path_az = self.config.output_dir / "skills_az.json"
        write_json(path_az, [skill_to_public_dict(s) for s in skills_sorted_az])
        outputs["skills_az"] = path_az

        skills_by_agents = sorted(self.skills.values(), key=lambda s: len(s.agents), reverse=True)
        path_agents = self.config.output_dir / "skills_by_agent_count.json"
        write_json(path_agents, [skill_to_public_dict(s) for s in skills_by_agents])
        outputs["skills_by_agent_count"] = path_agents

        path_health = self.config.output_dir / "repo_health.json"
        write_json(path_health, self.repo_health())
        outputs["repo_health"] = path_health

        return outputs


def skill_to_public_dict(skill: Skill) -> Dict[str, Any]:
    return {
        "name": skill.name,
        "description": skill.description,
        "tags": skill.tags,
        "agents": [{"provider": a.provider, "model": a.model} for a in skill.agents],
        "metadata": skill.metadata,
    }


def normalize_plugin_manifest(data: Dict[str, Any], source: str) -> Optional[PluginManifest]:
    name = str(data.get("name") or data.get("id") or "").strip()
    if not name:
        return None
    version = str(data.get("version") or "0.0.0")
    description = str(data.get("description") or "")
    commands = data.get("commands") if isinstance(data.get("commands"), list) else []
    return PluginManifest(
        source=source,
        name=name,
        version=version,
        description=description,
        commands=commands,
        raw=data,
    )


def parse_skill_markdown(path: Path) -> Tuple[str, List[str]]:
    if not path.exists():
        return "", []
    text = path.read_text(encoding="utf-8", errors="ignore")
    first_para = ""
    for block in re.split(r"\n\s*\n", text):
        cleaned = block.strip()
        if cleaned and not cleaned.startswith("#"):
            first_para = re.sub(r"\s+", " ", cleaned)[:300]
            break
    tags = sorted(set(re.findall(r"#([a-zA-Z0-9_-]+)", text)))
    return first_para, tags


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({str(k): str(v) for k, v in row.items()})
    except Exception:
        return []
    return rows


def load_config_file(path: Path) -> Any:
    if path.suffix.lower() in {".json"}:
        return load_json(path)
    if path.suffix.lower() in {".yml", ".yaml"}:
        if yaml is None:
            return None
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def setup_logging(level: str) -> logging.Logger:
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def create_app(config: AppConfig, registry: RepoRegistry, logger: logging.Logger) -> Flask:
    app = Flask(APP_NAME)

    # Basic middleware: request timing + CORS
    @app.before_request
    def before_request() -> None:
        request._start_time = time.perf_counter()  # type: ignore[attr-defined]

    @app.after_request
    def after_request(response):
        elapsed_ms = None
        if hasattr(request, "_start_time"):
            elapsed_ms = round((time.perf_counter() - request._start_time) * 1000, 2)  # type: ignore[attr-defined]
            response.headers["X-Response-Time-Ms"] = str(elapsed_ms)

        origin = request.headers.get("Origin", "*")
        if "*" in config.allowed_origins or origin in config.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*" if "*" in config.allowed_origins else origin
            response.headers["Vary"] = "Origin"
        response.headers["X-App-Name"] = APP_NAME
        response.headers["X-App-Version"] = APP_VERSION
        return response

    @app.errorhandler(Exception)
    def handle_error(err: Exception):
        code = 500
        if isinstance(err, HTTPException):
            code = err.code or 500
        logger.exception("Unhandled error: %s", err)
        return jsonify({
            "error": type(err).__name__,
            "message": str(err),
            "status": code,
            "timestamp": now_iso(),
        }), code

    @app.get("/healthz")
    def healthz():
        return jsonify(registry.repo_health())

    @app.get("/skills")
    def list_skills():
        provider = request.args.get("provider")
        items = []
        for skill in registry.skills.values():
            if provider:
                if not any(a.provider == provider for a in skill.agents):
                    continue
            items.append(skill_to_public_dict(skill))
        return jsonify({"count": len(items), "items": sorted(items, key=lambda x: x["name"].lower())})

    @app.get("/skills/<name>")
    def get_skill(name: str):
        skill = registry.skills.get(name)
        if not skill:
            return jsonify({"error": "not_found", "message": f"Skill '{name}' not found"}), 404
        return jsonify(skill_to_public_dict(skill))

    @app.get("/plugins")
    def list_plugins():
        items = [asdict(p) for p in registry.plugins]
        return jsonify({"count": len(items), "items": items})

    @app.get("/design-data")
    def list_design_data():
        return jsonify({
            "datasets": sorted(registry.design_data.keys()),
            "count": len(registry.design_data),
        })

    @app.get("/design-data/<dataset>")
    def get_design_dataset(dataset: str):
        rows = registry.design_data.get(dataset)
        if rows is None:
            return jsonify({"error": "not_found", "message": f"Dataset '{dataset}' not found"}), 404
        return jsonify({"dataset": dataset, "count": len(rows), "rows": rows})

    @app.post("/validate")
    def validate():
        registry.issues.clear()
        registry._validate_registry()
        return jsonify({
            "health": registry.repo_health(),
            "issues": [asdict(i) for i in registry.issues],
        })

    return app


def run_cli(args: argparse.Namespace, config: AppConfig, registry: RepoRegistry, logger: logging.Logger) -> int:
    if args.command == "scan":
        registry.load_all()
        print(json.dumps({
            "health": registry.repo_health(),
            "issues": [asdict(i) for i in registry.issues],
        }, indent=2))
        return 0

    if args.command == "build-index":
        registry.load_all()
        outputs = registry.generate_indexes()
        print(json.dumps({k: str(v) for k, v in outputs.items()}, indent=2))
        return 0

    if args.command == "serve":
        registry.load_all()
        app = create_app(config, registry, logger)

        stop = {"requested": False}

        def _signal_handler(signum, frame):
            stop["requested"] = True
            logger.info("Received signal %s, shutdown requested.", signum)

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        logger.info("Starting server on %s:%s", args.host, args.port)
        app.run(host=args.host, port=args.port, debug=args.debug)
        return 0

    return 1


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=APP_NAME, description="Super-Pro unified agent skill registry and runtime.")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--config", default="", help="Path to JSON/YAML config file")
    parser.add_argument("--log-level", default="", help="Override log level")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan", help="Scan skills/plugins/design data and print health report")
    sub.add_parser("build-index", help="Generate alternative index outputs into build dir")

    p_serve = sub.add_parser("serve", help="Run HTTP API server")
    p_serve.add_argument("--host", default=DEFAULT_HOST)
    p_serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    p_serve.add_argument("--debug", action="store_true")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    config_path = Path(args.config).resolve() if args.config else None
    config = AppConfig.from_sources(root_dir=root, config_path=config_path)

    if args.log_level:
        config.log_level = args.log_level.upper()

    logger = setup_logging(config.log_level)
    logger.info("%s v%s starting", APP_NAME, APP_VERSION)

    registry = RepoRegistry(config=config, logger=logger)
    return run_cli(args, config, registry, logger)


if __name__ == "__main__":
    raise SystemExit(main())