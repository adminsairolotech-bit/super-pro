from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, HttpUrl, field_validator

router = APIRouter(prefix="/api/v1", tags=["super-pro"])


# -----------------------------
# In-memory store (demo-ready)
# -----------------------------
DB: Dict[str, Dict[str, Dict[str, Any]]] = {
    "resources": {},
    "submissions": {},
    "brands": {},
    "design_tokens": {},
    "repo_health": {},
    "release_snapshots": {},
}


# -----------------------------
# Helpers / common response
# -----------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def response_ok(data: Any, message: str = "ok") -> Dict[str, Any]:
    return {"ok": True, "message": message, "data": data, "timestamp": now_iso()}


def parse_github_repo(url: str) -> Optional[str]:
    # supports: https://github.com/owner/repo, optional trailing slash/segments
    m = re.match(r"^https?://github\.com/([^/\s]+)/([^/\s]+)", url.strip(), re.IGNORECASE)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    repo = repo.replace(".git", "")
    return f"{owner}/{repo}"


def hex_color_valid(value: str) -> bool:
    return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value))


# -----------------------------
# Models
# -----------------------------
class ResourceStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class SubmissionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ResourceBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: str = Field(min_length=2, max_length=80)
    tags: List[str] = Field(default_factory=list, max_length=30)
    source_url: HttpUrl
    status: ResourceStatus = ResourceStatus.draft

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        clean = []
        seen = set()
        for t in value:
            x = t.strip().lower()
            if x and x not in seen:
                clean.append(x)
                seen.add(x)
        return clean

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return value.strip().lower()


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    tags: Optional[List[str]] = Field(default=None, max_length=30)
    source_url: Optional[HttpUrl] = None
    status: Optional[ResourceStatus] = None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return value
        clean = []
        seen = set()
        for t in value:
            x = t.strip().lower()
            if x and x not in seen:
                clean.append(x)
                seen.add(x)
        return clean

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().lower() if value else value


class SubmissionCreate(BaseModel):
    # Inspired by awesome-claude-code submission governance workflows
    title: str = Field(min_length=4, max_length=180)
    resource_url: HttpUrl
    rationale: str = Field(min_length=10, max_length=3000)
    submitted_by: str = Field(min_length=2, max_length=80)


class SubmissionReview(BaseModel):
    # Inspired by submission-enforcement and command-based moderation
    status: SubmissionStatus
    reviewer: str = Field(min_length=2, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=1000)


class BrandCreate(BaseModel):
    # Inspired by ui-ux-pro-max-skill brand scripts/tokens pipeline
    name: str = Field(min_length=2, max_length=100)
    primary_color: str
    secondary_color: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_colors(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not hex_color_valid(value):
            raise ValueError("must be valid hex color like #1A2B3C")
        return value.upper()


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_colors(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not hex_color_valid(value):
            raise ValueError("must be valid hex color like #1A2B3C")
        return value.upper()


class DesignTokenCreate(BaseModel):
    # Inspired by design-system data artifacts and sync-brand-to-tokens script
    brand_id: str
    key: str = Field(min_length=2, max_length=80)
    value: str = Field(min_length=1, max_length=200)
    token_type: str = Field(min_length=2, max_length=50)

    @field_validator("key", "token_type")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower()


class DesignTokenUpdate(BaseModel):
    value: Optional[str] = Field(default=None, min_length=1, max_length=200)
    token_type: Optional[str] = Field(default=None, min_length=2, max_length=50)

    @field_validator("token_type")
    @classmethod
    def normalize(cls, value: Optional[str]) -> Optional[str]:
        return value.strip().lower() if value else value


# -----------------------------
# Minimal auth dependency
# -----------------------------
def require_admin(request: Request) -> None:
    # simple header auth for demo; replace with OAuth/JWT in prod
    if request.headers.get("x-admin-token") != "super-pro-admin":
        raise HTTPException(status_code=403, detail="admin token required")


# -----------------------------
# Resource routes (CRUD)
# -----------------------------
@router.post("/resources", status_code=status.HTTP_201_CREATED)
def create_resource(payload: ResourceCreate):
    # Inspired by awesome-list curation + validation pipelines
    for r in DB["resources"].values():
        if str(r["source_url"]).lower() == str(payload.source_url).lower():
            raise HTTPException(status_code=409, detail="resource with same source_url already exists")

    resource_id = str(uuid.uuid4())
    repo_slug = parse_github_repo(str(payload.source_url))
    item = {
        "id": resource_id,
        **payload.model_dump(),
        "repo_slug": repo_slug,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    DB["resources"][resource_id] = item
    return response_ok(item, "resource created")


@router.get("/resources")
def list_resources(
    q: Optional[str] = Query(default=None, description="search in name/description/tags"),
    category: Optional[str] = Query(default=None),
    status_filter: Optional[ResourceStatus] = Query(default=None, alias="status"),
    sort: str = Query(default="updated_desc", pattern="^(created_asc|created_desc|updated_asc|updated_desc|name_asc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    items = list(DB["resources"].values())

    if q:
        ql = q.lower()
        items = [
            r
            for r in items
            if ql in r["name"].lower()
            or (r.get("description") and ql in r["description"].lower())
            or any(ql in t for t in r.get("tags", []))
        ]
    if category:
        items = [r for r in items if r["category"] == category.strip().lower()]
    if status_filter:
        items = [r for r in items if r["status"] == status_filter]

    if sort == "created_asc":
        items.sort(key=lambda x: x["created_at"])
    elif sort == "created_desc":
        items.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort == "updated_asc":
        items.sort(key=lambda x: x["updated_at"])
    elif sort == "updated_desc":
        items.sort(key=lambda x: x["updated_at"], reverse=True)
    elif sort == "name_asc":
        items.sort(key=lambda x: x["name"].lower())

    total = len(items)
    items = items[offset : offset + limit]
    return response_ok({"items": items, "total": total, "limit": limit, "offset": offset})


@router.get("/resources/{resource_id}")
def get_resource(resource_id: str):
    item = DB["resources"].get(resource_id)
    if not item:
        raise HTTPException(status_code=404, detail="resource not found")
    return response_ok(item)


@router.patch("/resources/{resource_id}")
def update_resource(resource_id: str, payload: ResourceUpdate):
    item = DB["resources"].get(resource_id)
    if not item:
        raise HTTPException(status_code=404, detail="resource not found")

    updates = payload.model_dump(exclude_unset=True)
    if "source_url" in updates:
        for rid, r in DB["resources"].items():
            if rid != resource_id and str(r["source_url"]).lower() == str(updates["source_url"]).lower():
                raise HTTPException(status_code=409, detail="resource with same source_url already exists")
        updates["repo_slug"] = parse_github_repo(str(updates["source_url"]))

    item.update(updates)
    item["updated_at"] = now_iso()
    DB["resources"][resource_id] = item
    return response_ok(item, "resource updated")


@router.delete("/resources/{resource_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
def delete_resource(resource_id: str):
    item = DB["resources"].pop(resource_id, None)
    if not item:
        raise HTTPException(status_code=404, detail="resource not found")
    return response_ok({"id": resource_id}, "resource deleted")


# -----------------------------
# Submission moderation routes
# -----------------------------
@router.post("/submissions", status_code=status.HTTP_201_CREATED)
def create_submission(payload: SubmissionCreate):
    # Inspired by awesome-claude-code new issue validation + submission workflows
    sub_id = str(uuid.uuid4())
    item = {
        "id": sub_id,
        **payload.model_dump(),
        "status": SubmissionStatus.pending,
        "reviewer": None,
        "review_notes": None,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    DB["submissions"][sub_id] = item
    return response_ok(item, "submission created")


@router.get("/submissions")
def list_submissions(status_filter: Optional[SubmissionStatus] = Query(default=None, alias="status")):
    items = list(DB["submissions"].values())
    if status_filter:
        items = [x for x in items if x["status"] == status_filter]
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return response_ok({"items": items, "total": len(items)})


@router.post("/submissions/{submission_id}/review", dependencies=[Depends(require_admin)])
def review_submission(submission_id: str, payload: SubmissionReview):
    item = DB["submissions"].get(submission_id)
    if not item:
        raise HTTPException(status_code=404, detail="submission not found")
    if item["status"] != SubmissionStatus.pending:
        raise HTTPException(status_code=409, detail="submission already reviewed")

    item["status"] = payload.status
    item["reviewer"] = payload.reviewer
    item["review_notes"] = payload.notes
    item["updated_at"] = now_iso()

    # If approved, auto-create a resource candidate
    if payload.status == SubmissionStatus.approved:
        url = str(item["resource_url"])
        exists = any(str(r["source_url"]).lower() == url.lower() for r in DB["resources"].values())
        if not exists:
            rid = str(uuid.uuid4())
            DB["resources"][rid] = {
                "id": rid,
                "name": item["title"],
                "description": item["rationale"][:500],
                "category": "community-submission",
                "tags": ["submission", "approved"],
                "source_url": url,
                "status": ResourceStatus.active,
                "repo_slug": parse_github_repo(url),
                "created_at": now_iso(),
                "updated_at": now_iso(),
            }

    return response_ok(item, "submission reviewed")


# -----------------------------
# Brand + design-system routes
# -----------------------------
@router.post("/brands", status_code=status.HTTP_201_CREATED)
def create_brand(payload: BrandCreate, _: None = Depends(require_admin)):
    brand_id = str(uuid.uuid4())
    item = {
        "id": brand_id,
        **payload.model_dump(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    DB["brands"][brand_id] = item
    return response_ok(item, "brand created")


@router.get("/brands")
def list_brands():
    items = sorted(DB["brands"].values(), key=lambda x: x["name"].lower())
    return response_ok({"items": items, "total": len(items)})


@router.patch("/brands/{brand_id}")
def update_brand(brand_id: str, payload: BrandUpdate, _: None = Depends(require_admin)):
    item = DB["brands"].get(brand_id)
    if not item:
        raise HTTPException(status_code=404, detail="brand not found")
    updates = payload.model_dump(exclude_unset=True)
    item.update(updates)
    item["updated_at"] = now_iso()
    DB["brands"][brand_id] = item
    return response_ok(item, "brand updated")


@router.post("/design-tokens", status_code=status.HTTP_201_CREATED)
def create_design_token(payload: DesignTokenCreate, _: None = Depends(require_admin)):
    if payload.brand_id not in DB["brands"]:
        raise HTTPException(status_code=404, detail="brand not found")

    # uniqueness within brand by (key, token_type)
    for token in DB["design_tokens"].values():
        if token["brand_id"] == payload.brand_id and token["key"] == payload.key and token["token_type"] == payload.token_type:
            raise HTTPException(status_code=409, detail="token already exists for brand/key/type")

    token_id = str(uuid.uuid4())
    item = {
        "id": token_id,
        **payload.model_dump(),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    DB["design_tokens"][token_id] = item
    return response_ok(item, "design token created")


@router.get("/brands/{brand_id}/design-tokens")
def list_brand_tokens(brand_id: str):
    if brand_id not in DB["brands"]:
        raise HTTPException(status_code=404, detail="brand not found")
    items = [t for t in DB["design_tokens"].values() if t["brand_id"] == brand_id]
    items.sort(key=lambda x: (x["token_type"], x["key"]))
    return response_ok({"items": items, "total": len(items)})


@router.patch("/design-tokens/{token_id}")
def update_design_token(token_id: str, payload: DesignTokenUpdate, _: None = Depends(require_admin)):
    item = DB["design_tokens"].get(token_id)
    if not item:
        raise HTTPException(status_code=404, detail="design token not found")
    updates = payload.model_dump(exclude_unset=True)
    item.update(updates)
    item["updated_at"] = now_iso()
    DB["design_tokens"][token_id] = item
    return response_ok(item, "design token updated")


@router.delete("/design-tokens/{token_id}", dependencies=[Depends(require_admin)])
def delete_design_token(token_id: str):
    item = DB["design_tokens"].pop(token_id, None)
    if not item:
        raise HTTPException(status_code=404, detail="design token not found")
    return response_ok({"id": token_id}, "design token deleted")


# -----------------------------
# Repo health / release routes
# -----------------------------
@router.post("/repo-health/refresh", dependencies=[Depends(require_admin)])
def refresh_repo_health(payload: Dict[str, List[str]] = Body(..., example={"resource_ids": []})):
    # Inspired by awesome-claude-code validate-links/check-repo-health automation
    resource_ids = payload.get("resource_ids") or list(DB["resources"].keys())
    report = []
    for rid in resource_ids:
        r = DB["resources"].get(rid)
        if not r:
            continue
        url = str(r["source_url"])
        repo_slug = r.get("repo_slug") or parse_github_repo(url)
        healthy = bool(repo_slug) and r["status"] != ResourceStatus.archived
        entry = {
            "resource_id": rid,
            "repo_slug": repo_slug,
            "url": url,
            "healthy": healthy,
            "checked_at": now_iso(),
            "reason": "ok" if healthy else "invalid repo url or archived",
        }
        DB["repo_health"][rid] = entry
        report.append(entry)
    return response_ok({"items": report, "total": len(report)}, "repo health refreshed")


@router.get("/repo-health")
def get_repo_health(resource_id: Optional[str] = Query(default=None)):
    if resource_id:
        item = DB["repo_health"].get(resource_id)
        if not item:
            raise HTTPException(status_code=404, detail="repo health not found for resource")
        return response_ok(item)
    items = list(DB["repo_health"].values())
    items.sort(key=lambda x: x["checked_at"], reverse=True)
    return response_ok({"items": items, "total": len(items)})


@router.post("/releases/snapshot", dependencies=[Depends(require_admin)])
def create_release_snapshot():
    # Inspired by update-github-release-data and ticker-style aggregate outputs
    active_resources = [r for r in DB["resources"].values() if r["status"] == ResourceStatus.active]
    by_category: Dict[str, int] = {}
    for r in active_resources:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1

    snapshot_id = str(uuid.uuid4())
    snap = {
        "id": snapshot_id,
        "active_resources": len(active_resources),
        "categories": by_category,
        "submissions_pending": sum(1 for s in DB["submissions"].values() if s["status"] == SubmissionStatus.pending),
        "generated_at": now_iso(),
    }
    DB["release_snapshots"][snapshot_id] = snap
    return response_ok(snap, "release snapshot created")


@router.get("/releases/snapshot/latest")
def get_latest_release_snapshot():
    if not DB["release_snapshots"]:
        raise HTTPException(status_code=404, detail="no release snapshots found")
    latest = sorted(DB["release_snapshots"].values(), key=lambda x: x["generated_at"], reverse=True)[0]
    return response_ok(latest)