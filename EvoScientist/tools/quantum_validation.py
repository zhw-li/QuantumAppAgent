"""Deterministic validation tool for quantum application delivery artifacts."""

from __future__ import annotations

import json
import re
import sys
import importlib.util
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

REQUIRED_REPORT_FIELDS = (
    "task",
    "data",
    "primary_metric",
    "higher_is_better",
    "value",
    "command",
    "artifact_paths",
)

REQUIRED_BASE_ARTIFACTS = (
    "application_manifest.json",
    "requirements.json",
    "baseline_report.json",
    "quantum_report.json",
    "verification_report.md",
)

REQUIRED_PACKAGING_ARTIFACTS = (
    "README.md",
    "INTEGRATE.md",
)

ALLOWED_QCCP_HEX_COLORS = {
    "#1664FF",
    "#4F9DF7",
    "#1F84FC",
    "#FB4214",
    "#00C7E7",
    "#020814",
    "#41464F",
    "#939AAB",
    "#F4F7FC",
    "#FFFFFF",
    "#F3F7FF",
    "#DCE0EB",
    "#BB79E1",
    "#A58DF8",
    "#4A86FF",
    "#ECF2FF",
    "#B5BFFF",
}

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

DELIVERY_PROFILES = {
    "algorithm_only",
    "local_fastapi_demo",
    "qccp_web_page",
    "full_delivery",
}

PROFILE_LAYERS = {
    "algorithm_only": ("algorithm",),
    "local_fastapi_demo": ("algorithm", "local_demo"),
    "qccp_web_page": ("algorithm", "qccp_web"),
    "full_delivery": ("algorithm", "local_demo", "qccp_web", "docs"),
}


def _workspace_root() -> Path:
    from EvoScientist import paths as _paths_mod

    return Path(_paths_mod.WORKSPACE_ROOT)


def _resolve_app_dir(app_dir: str) -> Path:
    raw = Path(app_dir).expanduser()
    if raw.is_absolute() and raw.exists():
        return raw
    if raw.is_absolute():
        return _workspace_root() / str(raw).lstrip("/")
    return _workspace_root() / raw


def _json_default(value: Any) -> str:
    return str(value)


def _add_blocker(blockers: list[str], layer: str, message: str) -> None:
    blockers.append(f"[{layer}] {message}")


def _read_json(path: Path, blockers: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        blockers.append(f"{path.name}: invalid JSON ({exc})")
        return None
    if not isinstance(data, dict):
        blockers.append(f"{path.name}: top-level JSON value must be an object")
        return None
    return data


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nested_get(data: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = data or {}
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _manifest_artifact_ref(manifest: dict[str, Any] | None, name: str) -> str | None:
    artifacts = _as_dict((manifest or {}).get("artifacts"))
    value = artifacts.get(name)
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("path"), str):
        return value["path"]
    return None


def _resolve_app_ref(app_path: Path, ref: Any) -> Path | None:
    if not isinstance(ref, str) or not ref.strip():
        return None
    raw = Path(ref).expanduser()
    if raw.is_absolute():
        return raw
    return app_path / raw


def _artifact_exists(app_path: Path, manifest: dict[str, Any] | None, name: str) -> bool:
    ref = _manifest_artifact_ref(manifest, name)
    if ref:
        resolved = _resolve_app_ref(app_path, ref)
        return bool(resolved and resolved.is_file())
    return (app_path / name).is_file()


def _artifact_path(app_path: Path, manifest: dict[str, Any] | None, name: str) -> Path:
    ref = _manifest_artifact_ref(manifest, name)
    resolved = _resolve_app_ref(app_path, ref) if ref else None
    return resolved or (app_path / name)


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _normalize_method(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_endpoint_path(path: str) -> str:
    path = path.strip()
    if not path.startswith("/"):
        path = "/" + path
    return re.sub(r"/+", "/", path)


def _iter_backend_endpoints(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    endpoint_groups = (
        _nested_get(manifest, "local_demo", "endpoints"),
        _nested_get(manifest, "qccp_web", "backend_endpoints"),
        _nested_get(manifest, "backend", "endpoints"),
    )
    out: list[dict[str, Any]] = []
    for endpoints in endpoint_groups:
        for endpoint in _as_list(endpoints):
            if isinstance(endpoint, dict):
                out.append(endpoint)
    return out


def _endpoint_set(manifest: dict[str, Any] | None) -> set[str]:
    paths: set[str] = set()
    for endpoint in _iter_backend_endpoints(manifest):
        raw_path = endpoint.get("path")
        if isinstance(raw_path, str) and raw_path.strip():
            paths.add(_normalize_endpoint_path(raw_path))
    return paths


def _route_declared_in_source(source: str, method: str, path: str) -> bool:
    method_l = method.lower()
    escaped = re.escape(path)
    pattern = rf"@\s*(?:app|router)\s*\.\s*{method_l}\s*\(\s*['\"]{escaped}['\"]"
    return re.search(pattern, source) is not None


def _openapi_declares(openapi: dict[str, Any] | None, method: str, path: str) -> bool:
    paths = _as_dict((openapi or {}).get("paths"))
    entry = _as_dict(paths.get(path))
    return method.lower() in {key.lower() for key in entry}


def _extract_api_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for match in re.finditer(r"['\"](/api/[A-Za-z0-9_./{}:-]+)['\"]", text):
        paths.add(_normalize_endpoint_path(match.group(1)))
    for match in re.finditer(r"(?<![\w])(/api/[A-Za-z0-9_./{}:-]+)", text):
        paths.add(_normalize_endpoint_path(match.group(1)))

    api_base_match = re.search(r"API_BASE\s*=\s*['\"](/api[^'\"]*)['\"]", text)
    if api_base_match:
        api_base = _normalize_endpoint_path(api_base_match.group(1))
        for match in re.finditer(r"API_BASE\s*\+\s*['\"](/[^'\"]+)['\"]", text):
            paths.add(_normalize_endpoint_path(api_base.rstrip("/") + match.group(1)))

    for match in re.finditer(r"\burl\s*:\s*['\"](/[^'\"]+)['\"]", text):
        raw = _normalize_endpoint_path(match.group(1))
        if raw.startswith("/api/"):
            paths.add(raw)
        else:
            paths.add(_normalize_endpoint_path("/api" + raw))
    return paths


def _extract_static_urls_from_html(text: str) -> set[str]:
    urls: set[str] = set()
    for match in re.finditer(r"(?:href|src)\s*=\s*['\"](/static/[^'\"]+)['\"]", text):
        urls.add(_normalize_endpoint_path(match.group(1)))
    return urls


def _extract_external_resource_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for match in re.finditer(r"(?:href|src)\s*=\s*['\"](https?://[^'\"]+)['\"]", text):
        urls.add(match.group(1))
    return urls


def _extract_local_urls(text: str) -> set[str]:
    urls = set()
    for match in re.finditer(r"(?<![\w])(/(?:api|static)/[A-Za-z0-9_./{}:-]+)", text):
        urls.add(_normalize_endpoint_path(match.group(1)))
    return urls


def _extract_hex_colors(text: str) -> set[str]:
    colors: set[str] = set()
    for color in re.findall(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b", text):
        if len(color) == 4:
            color = "#" + "".join(ch * 2 for ch in color[1:])
        colors.add(color.upper())
    return colors


def _contains_emoji(text: str) -> bool:
    return re.search(r"[\U0001F300-\U0001FAFF]", text) is not None


def _stable_equal(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, default=_json_default) == json.dumps(
        right,
        sort_keys=True,
        default=_json_default,
    )


def _requirements_flag(
    requirements: dict[str, Any] | None,
    names: tuple[str, ...],
    default: bool,
) -> bool:
    if not requirements:
        return default
    for name in names:
        value = requirements.get(name)
        if isinstance(value, bool):
            return value
    return default


def _validate_report_schema(
    report_name: str,
    report: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
    *,
    layer: str = "algorithm",
) -> bool:
    if report is None:
        return False
    missing = [field for field in REQUIRED_REPORT_FIELDS if not _is_present(report.get(field))]
    value = report.get("value")
    if not isinstance(value, int | float) or isinstance(value, bool):
        missing.append("value:numeric")
    if not isinstance(report.get("higher_is_better"), bool):
        missing.append("higher_is_better:bool")
    ok = not missing
    checks.append(
        {
            "name": f"{layer}.{report_name}_schema",
            "status": "passed" if ok else "blocked",
            "missing_or_invalid": missing,
        }
    )
    if missing:
        _add_blocker(blockers, layer, f"{report_name}: missing or invalid fields: {', '.join(missing)}")
    return ok


def _delivery_profile(
    manifest: dict[str, Any] | None,
    *,
    require_packaging: bool,
) -> str:
    if not require_packaging:
        return "algorithm_only"
    profile = (manifest or {}).get("delivery_profile")
    if isinstance(profile, str) and profile in DELIVERY_PROFILES:
        return profile
    return "full_delivery"


def _profile_layers(profile: str) -> tuple[str, ...]:
    return PROFILE_LAYERS.get(profile, PROFILE_LAYERS["full_delivery"])


def _validate_application_manifest(
    app_path: Path,
    manifest: dict[str, Any] | None,
    required_artifacts: list[str],
    profile: str,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    if manifest is None:
        checks.append(
            {
                "name": "application_manifest_schema",
                "status": "blocked",
                "missing_or_invalid": ["application_manifest.json"],
            }
        )
        _add_blocker(blockers, "manifest", "application_manifest.json is missing or invalid")
        return

    missing: list[str] = []
    if manifest.get("delivery_profile") not in DELIVERY_PROFILES:
        missing.append("delivery_profile")
    if not _is_present(manifest.get("artifacts")):
        missing.append("artifacts")
    if "algorithm" in _profile_layers(profile) and not _is_present(manifest.get("algorithm")):
        missing.append("algorithm")

    for artifact in required_artifacts:
        if artifact == "application_manifest.json":
            continue
        if not _manifest_artifact_ref(manifest, artifact):
            missing.append(f"artifacts.{artifact}")
        elif not _artifact_exists(app_path, manifest, artifact):
            missing.append(f"artifacts.{artifact}:file")

    layers = _profile_layers(profile)
    if "local_demo" in layers:
        if not _is_present(manifest.get("local_demo")):
            missing.append("local_demo")
        else:
            for field in ("backend_entrypoint", "entrypoint", "endpoints", "static_assets"):
                if not _is_present(_nested_get(manifest, "local_demo", field)):
                    missing.append(f"local_demo.{field}")
    if "qccp_web" in layers:
        if not _is_present(manifest.get("qccp_web")):
            missing.append("qccp_web")
        else:
            for field in ("pageKey", "route", "sfc", "verification_command"):
                if not _is_present(_nested_get(manifest, "qccp_web", field)):
                    missing.append(f"qccp_web.{field}")
    if "docs" in layers and not _is_present(manifest.get("docs")):
        missing.append("docs")
    if not _is_present(_nested_get(manifest, "verification", "commands")):
        missing.append("verification.commands")
    if not _is_present(manifest.get("limitations")):
        missing.append("limitations")

    checks.append(
        {
            "name": "application_manifest_schema",
            "status": "passed" if not missing else "blocked",
            "missing_or_invalid": missing,
        }
    )
    if missing:
        _add_blocker(
            blockers,
            "manifest",
            "application_manifest.json: missing or invalid fields: "
            + ", ".join(missing),
        )


def _validate_backend_contract(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
    *,
    layer: str = "local_demo",
) -> None:
    endpoints = _iter_backend_endpoints(manifest)
    invalid: list[str] = []
    source = ""
    openapi: dict[str, Any] | None = None

    entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "local_demo", "backend_entrypoint"))
    if not entrypoint:
        entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "backend", "entrypoint"))
    if entrypoint and entrypoint.is_file():
        source = _read_text(entrypoint)

    openapi_path = _resolve_app_ref(app_path, _nested_get(manifest, "backend", "openapi"))
    if openapi_path and openapi_path.is_file():
        openapi = _read_json(openapi_path, blockers)

    if not endpoints:
        invalid.append("backend.endpoints")

    for idx, endpoint in enumerate(endpoints):
        label = f"backend.endpoints[{idx}]"
        path = endpoint.get("path")
        method = _normalize_method(endpoint.get("method"))
        if not isinstance(path, str) or not path.strip():
            invalid.append(f"{label}.path")
            continue
        path = _normalize_endpoint_path(path)
        if method not in HTTP_METHODS:
            invalid.append(f"{label}.method")
        for field in ("request_schema", "response_schema", "errors"):
            if not _is_present(endpoint.get(field)):
                invalid.append(f"{label}.{field}")
        if (source or openapi) and not (
            _route_declared_in_source(source, method, path)
            or _openapi_declares(openapi, method, path)
        ):
            invalid.append(f"{label}.route:{method} {path}")

    checks.append(
        {
            "name": f"{layer}.backend_contract",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(
            blockers,
            layer,
            "backend contract is incomplete or not implemented: " + ", ".join(invalid),
        )


def _validate_static_assets(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
    *,
    layer: str = "local_demo",
) -> None:
    invalid: list[str] = []
    asset_urls: set[str] = set()
    static_assets = _nested_get(manifest, "local_demo", "static_assets")
    if not _is_present(static_assets):
        static_assets = _nested_get(manifest, "backend", "static_assets")
    for idx, asset in enumerate(_as_list(static_assets)):
        if not isinstance(asset, dict):
            invalid.append(f"{layer}.static_assets[{idx}]")
            continue
        url = asset.get("url")
        path = _resolve_app_ref(app_path, asset.get("path"))
        if not isinstance(url, str) or not url.startswith("/static/"):
            invalid.append(f"{layer}.static_assets[{idx}].url")
            continue
        asset_urls.add(_normalize_endpoint_path(url))
        if not path or not path.is_file():
            invalid.append(f"{layer}.static_assets[{idx}].path")

    entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "local_demo", "entrypoint"))
    if not entrypoint:
        entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "frontend", "local_demo", "entrypoint"))
    if entrypoint and entrypoint.is_file():
        html_urls = _extract_static_urls_from_html(_read_text(entrypoint))
        missing = sorted(html_urls - asset_urls)
        invalid.extend(f"{layer}.static_assets:{url}" for url in missing)

    checks.append(
        {
            "name": f"{layer}.static_assets",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(blockers, layer, "static asset contract is inconsistent: " + ", ".join(invalid))


def _local_demo_assets(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    assets = _nested_get(manifest, "local_demo", "static_assets")
    if not _is_present(assets):
        assets = _nested_get(manifest, "backend", "static_assets")
    return [asset for asset in _as_list(assets) if isinstance(asset, dict)]


def _local_demo_entrypoint(app_path: Path, manifest: dict[str, Any] | None) -> Path | None:
    entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "local_demo", "entrypoint"))
    if entrypoint:
        return entrypoint
    return _resolve_app_ref(app_path, _nested_get(manifest, "frontend", "local_demo", "entrypoint"))


def _local_demo_source_text(app_path: Path, manifest: dict[str, Any] | None) -> str:
    parts: list[str] = []
    entrypoint = _local_demo_entrypoint(app_path, manifest)
    if entrypoint and entrypoint.is_file():
        parts.append(_read_text(entrypoint))
    for asset in _local_demo_assets(manifest):
        asset_path = _resolve_app_ref(app_path, asset.get("path"))
        if asset_path and asset_path.is_file() and asset_path.suffix.lower() == ".js":
            parts.append(_read_text(asset_path))
    return "\n".join(parts)


def _load_fastapi_test_client(app_path: Path, manifest: dict[str, Any] | None) -> tuple[Any | None, str | None]:
    entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "local_demo", "backend_entrypoint"))
    if not entrypoint:
        entrypoint = _resolve_app_ref(app_path, _nested_get(manifest, "backend", "entrypoint"))
    if not entrypoint or not entrypoint.is_file():
        return None, "local_demo.backend_entrypoint:file"

    module_name = f"_evos_quantum_app_{abs(hash(str(entrypoint)))}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, entrypoint)
        if spec is None or spec.loader is None:
            return None, "local_demo.backend_entrypoint:import"
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(entrypoint.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            try:
                sys.path.remove(str(entrypoint.parent))
            except ValueError:
                pass
        app_symbol = _nested_get(manifest, "local_demo", "app_symbol") or "app"
        app = getattr(module, str(app_symbol), None)
        if app is None:
            return None, f"local_demo.app_symbol:{app_symbol}"
        from fastapi.testclient import TestClient

        return TestClient(app), None
    except Exception as exc:
        return None, f"local_demo.backend_entrypoint:import:{exc}"


def _validate_local_demo(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    layer = "local_demo"
    _validate_backend_contract(app_path, manifest, checks, blockers, layer=layer)
    _validate_static_assets(app_path, manifest, checks, blockers, layer=layer)

    invalid: list[str] = []
    text = _local_demo_source_text(app_path, manifest)
    entrypoint = _local_demo_entrypoint(app_path, manifest)
    if not entrypoint or not entrypoint.is_file():
        invalid.append("local_demo.entrypoint:file")
    else:
        external_urls = sorted(_extract_external_resource_urls(_read_text(entrypoint)))
        invalid.extend(f"local_demo.external_resource:{url}" for url in external_urls)

    endpoint_paths = _endpoint_set(manifest)
    frontend_api_paths = _extract_api_paths(text)
    drift = sorted(frontend_api_paths - endpoint_paths)
    invalid.extend(f"local_demo.api_path:{path}" for path in drift)

    client, load_error = _load_fastapi_test_client(app_path, manifest)
    if load_error:
        invalid.append(load_error)
    elif client is not None:
        smoke_paths = {"/"}
        if entrypoint and entrypoint.is_file():
            smoke_paths.update(_extract_static_urls_from_html(_read_text(entrypoint)))
        for endpoint in _iter_backend_endpoints(manifest):
            method = _normalize_method(endpoint.get("method"))
            path = endpoint.get("path")
            if not isinstance(path, str):
                continue
            path = _normalize_endpoint_path(path)
            sample_request = endpoint.get("sample_request")
            if method == "GET":
                smoke_paths.add(path)
            elif sample_request is not None:
                try:
                    response = client.request(method, path, json=sample_request)
                except Exception as exc:
                    invalid.append(f"local_demo.api_smoke:{method} {path}:{exc}")
                    continue
                if response.status_code >= 400:
                    invalid.append(f"local_demo.api_smoke:{method} {path}:{response.status_code}")
        for path in sorted(smoke_paths):
            try:
                response = client.get(path)
            except Exception as exc:
                invalid.append(f"local_demo.http:{path}:{exc}")
                continue
            if response.status_code >= 400:
                invalid.append(f"local_demo.http:{path}:{response.status_code}")

    checks.append(
        {
            "name": "local_demo.smoke",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(blockers, layer, "local demo contract failed: " + ", ".join(invalid))


def _qccp_source_text(app_path: Path, manifest: dict[str, Any] | None) -> tuple[str, Path | None]:
    sfc_path = _resolve_app_ref(app_path, _nested_get(manifest, "qccp_web", "sfc"))
    if not sfc_path:
        sfc_path = _resolve_app_ref(app_path, _nested_get(manifest, "frontend", "qccp", "sfc"))
    if not sfc_path or not sfc_path.is_file():
        return "", sfc_path
    text = _read_text(sfc_path)
    api_path = _resolve_app_ref(app_path, _nested_get(manifest, "qccp_web", "api_module"))
    if not api_path:
        api_path = _resolve_app_ref(app_path, _nested_get(manifest, "frontend", "qccp", "api_module"))
    if api_path and api_path.is_file():
        text += "\n" + _read_text(api_path)
    return text, sfc_path


def _validate_qccp_frontend(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    qccp = _as_dict(_nested_get(manifest, "qccp_web"))
    if not qccp:
        qccp = _as_dict(_nested_get(manifest, "frontend", "qccp"))
    invalid: list[str] = []
    for field in ("pageKey", "route", "sfc", "verification_command"):
        if not _is_present(qccp.get(field)):
            invalid.append(f"qccp_web.{field}")

    text, sfc_path = _qccp_source_text(app_path, manifest)
    if not sfc_path or not sfc_path.is_file():
        invalid.append("qccp_web.sfc:file")
    else:
        if "<script setup" not in text:
            invalid.append("qccp_web.sfc:script_setup")
        if not re.search(r"<style[^>]*scoped[^>]*lang=['\"]scss['\"]|<style[^>]*lang=['\"]scss['\"][^>]*scoped", text):
            invalid.append("qccp_web.sfc:scoped_scss")
        if "useI18n" not in text:
            invalid.append("qccp_web.sfc:i18n")
        if "<el-" not in text and "element-plus" not in text:
            invalid.append("qccp_web.sfc:element_plus")
        if re.search(r"<html\b|<script\s+src=|https://unpkg|cdn.jsdelivr", text, re.I):
            invalid.append("qccp_web.sfc:standalone_or_cdn")

        backend_paths = _endpoint_set(manifest)
        frontend_paths = _extract_api_paths(text)
        for api_path in _as_list(qccp.get("api_paths")):
            if isinstance(api_path, str):
                frontend_paths.add(_normalize_endpoint_path(api_path))
        for proxy_path in _as_list(qccp.get("proxy_paths")):
            if isinstance(proxy_path, str):
                backend_paths.add(_normalize_endpoint_path(proxy_path))
        drift = sorted(frontend_paths - backend_paths)
        if drift:
            invalid.extend(f"qccp_web.api_path:{path}" for path in drift)
        if "echarts" in text.lower():
            if not re.search(r"import\s+(?:\*\s+as\s+)?echarts|from ['\"]echarts['\"]", text):
                invalid.append("qccp_web.echarts:import")
            for token in ("nextTick", "resize", "dispose", "onBeforeUnmount"):
                if token not in text:
                    invalid.append(f"qccp_web.echarts:{token}")

    checks.append(
        {
            "name": "qccp_web.frontend_contract",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(blockers, "qccp_web", "qccp frontend contract is inconsistent: " + ", ".join(invalid))


def _validate_qccp_ui_evidence(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    text, sfc_path = _qccp_source_text(app_path, manifest)
    invalid: list[str] = []
    if not sfc_path or not sfc_path.is_file():
        invalid.append("qccp_web.sfc:file")
    else:
        if _contains_emoji(text):
            invalid.append("qccp_web.ui:emoji")
        if re.search(r"linear-gradient|radial-gradient", text, re.I):
            invalid.append("qccp_web.ui:gradient")
        unexpected_colors = sorted(_extract_hex_colors(text) - ALLOWED_QCCP_HEX_COLORS)
        invalid.extend(f"qccp_web.ui.color:{color}" for color in unexpected_colors)
        for radius in re.findall(r"border-radius\s*:\s*(\d+)px", text):
            if int(radius) not in {4, 6, 8}:
                invalid.append(f"qccp_web.ui.radius:{radius}px")

    checks.append(
        {
            "name": "qccp_web.ui_evidence",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(blockers, "qccp_web", "qccp UI evidence violates the platform spec: " + ", ".join(invalid))


def _validate_docs_consistency(
    app_path: Path,
    manifest: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> None:
    invalid: list[str] = []
    backend_paths = _endpoint_set(manifest)
    static_paths = {
        _normalize_endpoint_path(asset["url"])
        for asset in _local_demo_assets(manifest)
        if isinstance(asset.get("url"), str)
    }
    qccp_route = _nested_get(manifest, "qccp_web", "route")
    if not qccp_route:
        qccp_route = _nested_get(manifest, "frontend", "qccp", "route")
    for name in ("README.md", "INTEGRATE.md", "verification_report.md"):
        path = _artifact_path(app_path, manifest, name)
        if not path.is_file():
            continue
        text = _read_text(path)
        drift = sorted(_extract_api_paths(text) - backend_paths)
        invalid.extend(f"{name}.endpoint:{api_path}" for api_path in drift)
        static_drift = sorted(
            url for url in _extract_local_urls(text)
            if url.startswith("/static/") and url not in static_paths
        )
        invalid.extend(f"{name}.static:{static_path}" for static_path in static_drift)
        if name == "INTEGRATE.md" and isinstance(qccp_route, str) and qccp_route not in text:
            invalid.append("INTEGRATE.md.route")

    checks.append(
        {
            "name": "docs.contract_consistency",
            "status": "passed" if not invalid else "blocked",
            "missing_or_invalid": invalid,
        }
    )
    if invalid:
        _add_blocker(blockers, "docs", "documentation is inconsistent with the application contract: " + ", ".join(invalid))


def _compare_metrics(
    baseline: dict[str, Any] | None,
    quantum: dict[str, Any] | None,
    *,
    require_quantum_improvement: bool,
    blockers: list[str],
    layer: str = "algorithm",
) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        "comparable": False,
        "quantum_improved": None,
    }
    if baseline is None or quantum is None:
        return comparison

    comparable_fields = ("task", "data", "primary_metric", "higher_is_better")
    mismatched = [
        field
        for field in comparable_fields
        if not _stable_equal(baseline.get(field), quantum.get(field))
    ]
    baseline_value = baseline.get("value")
    quantum_value = quantum.get("value")
    higher_is_better = baseline.get("higher_is_better")
    comparison.update(
        {
            "primary_metric": baseline.get("primary_metric"),
            "higher_is_better": higher_is_better,
            "baseline_value": baseline_value,
            "quantum_value": quantum_value,
            "mismatched_fields": mismatched,
        }
    )
    if mismatched:
        _add_blocker(blockers, layer, f"metric reports are not comparable: {', '.join(mismatched)}")
        return comparison

    comparison["comparable"] = True
    delta = quantum_value - baseline_value
    improved = delta > 0 if higher_is_better else delta < 0
    comparison.update(
        {
            "delta": delta,
            "quantum_improved": improved,
        }
    )
    if require_quantum_improvement and not improved:
        direction = "higher" if higher_is_better else "lower"
        _add_blocker(
            blockers,
            layer,
            f"quantum result must be {direction} than baseline for "
            f"{baseline.get('primary_metric')}",
        )
    return comparison


def validate_quantum_application_artifacts(
    app_dir: str,
    *,
    require_quantum_improvement: bool = True,
    require_packaging: bool = True,
) -> dict[str, Any]:
    """Validate a quantum application artifact directory and return a dict."""
    app_path = _resolve_app_dir(app_dir)
    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    if not app_path.exists() or not app_path.is_dir():
        blockers.append(f"application directory not found: {app_path}")

    manifest = None
    manifest_path = app_path / "application_manifest.json"
    if manifest_path.is_file():
        manifest = _read_json(manifest_path, blockers)

    requirements = None
    requirements_path = _artifact_path(app_path, manifest, "requirements.json")
    if requirements_path.is_file():
        requirements = _read_json(requirements_path, blockers)

    require_quantum_improvement = _requirements_flag(
        requirements,
        ("require_quantum_improvement", "quantum_improvement_required"),
        require_quantum_improvement,
    )
    require_packaging = _requirements_flag(
        requirements,
        ("require_packaging", "packaging_required"),
        require_packaging,
    )
    profile = _delivery_profile(manifest, require_packaging=require_packaging)
    layers = _profile_layers(profile)

    required_artifacts = list(REQUIRED_BASE_ARTIFACTS)
    if "docs" in layers:
        required_artifacts.extend(REQUIRED_PACKAGING_ARTIFACTS)
    missing_artifacts = [
        artifact for artifact in required_artifacts if not _artifact_exists(app_path, manifest, artifact)
    ]
    checks.append(
        {
            "name": "required_artifacts",
            "status": "passed" if not missing_artifacts else "blocked",
            "missing": missing_artifacts,
        }
    )
    if missing_artifacts:
        blockers.append(f"missing artifacts: {', '.join(missing_artifacts)}")

    baseline = None
    quantum = None
    baseline_path = _artifact_path(app_path, manifest, "baseline_report.json")
    quantum_path = _artifact_path(app_path, manifest, "quantum_report.json")
    if baseline_path.is_file():
        baseline = _read_json(baseline_path, blockers)
    if quantum_path.is_file():
        quantum = _read_json(quantum_path, blockers)

    _validate_application_manifest(
        app_path,
        manifest,
        required_artifacts,
        profile,
        checks,
        blockers,
    )

    _validate_report_schema("baseline_report", baseline, checks, blockers, layer="algorithm")
    _validate_report_schema("quantum_report", quantum, checks, blockers, layer="algorithm")

    metric_comparison = _compare_metrics(
        baseline,
        quantum,
        require_quantum_improvement=require_quantum_improvement,
        blockers=blockers,
        layer="algorithm",
    )
    checks.append(
        {
            "name": "algorithm.metric_comparison",
            "status": "passed"
            if metric_comparison.get("comparable")
            and (
                not require_quantum_improvement
                or metric_comparison.get("quantum_improved") is True
            )
            else "blocked",
        }
    )

    if "local_demo" in layers:
        _validate_local_demo(app_path, manifest, checks, blockers)
    if "qccp_web" in layers:
        _validate_qccp_frontend(app_path, manifest, checks, blockers)
        _validate_qccp_ui_evidence(app_path, manifest, checks, blockers)
    if "docs" in layers:
        _validate_docs_consistency(app_path, manifest, checks, blockers)

    # Preserve insertion order while removing duplicate blocker messages.
    blockers = list(dict.fromkeys(blockers))
    return {
        "status": "passed" if not blockers else "blocked",
        "app_dir": str(app_path),
        "delivery_profile": profile,
        "validation_layers": list(layers),
        "checks": checks,
        "missing_artifacts": missing_artifacts,
        "application_manifest": {
            "present": manifest is not None,
            "delivery_profile": (manifest or {}).get("delivery_profile"),
            "algorithm": _as_dict((manifest or {}).get("algorithm")),
        },
        "metric_comparison": metric_comparison,
        "blockers": blockers,
    }


@tool(parse_docstring=True)
def validate_quantum_application(
    app_dir: str,
    require_quantum_improvement: bool = True,
    require_packaging: bool = True,
) -> str:
    """Validate quantum application delivery artifacts and return JSON.

    Args:
        app_dir: Application artifact directory. Absolute paths are used directly
            when they exist; otherwise paths are resolved under the active workspace.
        require_quantum_improvement: Require quantum_report.value to beat the
            baseline_report.value using the shared primary metric direction.
        require_packaging: Require README.md, INTEGRATE.md, and qccp/API/frontend
            packaging evidence.

    Returns:
        A JSON object string with status, delivery_profile, validation_layers,
        checks, missing_artifacts, metric_comparison, and layer-prefixed blockers.
    """
    result = validate_quantum_application_artifacts(
        app_dir,
        require_quantum_improvement=require_quantum_improvement,
        require_packaging=require_packaging,
    )
    return json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
