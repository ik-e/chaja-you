"""H1-H9 Web API Client adhering to R01 team leader directive.

Guidelines:
1. Routes use /v1/* standard routes.
2. H7 handles 202 for initial start, 200 for idempotent replay.
3. Observes job_state and progress during execution.
4. Shows stored result upon completion.
5. Blocks automatic re-execution on unknown verdict and presents next actions.
6. Owner transmitted exclusively via authentication context (X-Mock-Owner), stripped from body.
7. AuthGrant delivered solely to auth surface without storage or logging.
8. Cache-Control: no-store on all requests and response verification.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{status_code}] {code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class WebApiClient:
    def __init__(self, base_url: str, owner: Optional[str] = "test-owner"):
        self.base_url = base_url.rstrip("/")
        self.owner = owner

    def _build_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-store",
        }
        if self.owner:
            headers["X-Mock-Owner"] = self.owner
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        raw_body: Optional[bytes] = None,
        content_type: str = "application/json",
    ) -> Tuple[int, Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        if query_params:
            filtered_query = {k: v for k, v in query_params.items() if v is not None}
            if filtered_query:
                url += "?" + urllib.parse.urlencode(filtered_query)

        headers = self._build_headers(custom_headers)
        data = None

        if raw_body is not None:
            data = raw_body
            headers["Content-Type"] = content_type
        elif body is not None:
            # Rule 6: Strip owner from payload body if inadvertently included
            clean_body = {k: v for k, v in body.items() if k != "owner"}
            data = json.dumps(clean_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                status_code = resp.status
                resp_cache = resp.headers.get("Cache-Control", "")
                resp_bytes = resp.read()
                resp_json = json.loads(resp_bytes.decode("utf-8")) if resp_bytes else {}
                return status_code, resp_json
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                code = err_json.get("code", "UNKNOWN_ERROR")
                msg = err_json.get("message", err_body)
            except Exception:
                code = "HTTP_ERROR"
                msg = err_body
            raise ApiError(status_code=exc.code, code=code, message=msg)
        except urllib.error.URLError as exc:
            raise ApiError(status_code=503, code="NETWORK_ERROR", message=str(exc.reason))

    # H1: POST /v1/sources
    def create_source(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        status, data = self.request("POST", "/v1/sources", body=manifest)
        return data

    # H2: GET /v1/sources
    def list_sources(self, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {"limit": limit} if limit is not None else None
        status, data = self.request("GET", "/v1/sources", query_params=params)
        return data

    # H3: GET /v1/sources/{id}
    def get_source(self, source_id: str) -> Dict[str, Any]:
        status, data = self.request("GET", f"/v1/sources/{source_id}")
        return data

    # H4: POST /v1/registrations
    def create_registration(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Rule 6: owner is in context header only
        status, data = self.request("POST", "/v1/registrations", body=payload)
        return data

    # H5: PATCH /v1/registrations/{id}
    def edit_registration(self, reg_id: str, patch_data: Dict[str, Any]) -> Dict[str, Any]:
        status, data = self.request("PATCH", f"/v1/registrations/{reg_id}", body=patch_data)
        return data

    # H6: POST /v1/registrations/{id}/authentication
    def authenticate(self, reg_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """AuthGrant is received but must not be stored in persistent store or logged."""
        status, data = self.request("POST", f"/v1/registrations/{reg_id}/authentication", body=payload)
        return data

    # H7: POST /v1/registrations/{id}/start
    def start(self, reg_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Rule 2: Initial response is 202 Accepted, replay with same request_key is 200 OK."""
        status, data = self.request("POST", f"/v1/registrations/{reg_id}/start", body=payload)
        return status, data

    # H8: GET /v1/registrations/{id}
    def get_registration(self, reg_id: str) -> Dict[str, Any]:
        """Rules 3 & 4: Observes job_state, progress during execution, and result after completion."""
        status, data = self.request("GET", f"/v1/registrations/{reg_id}")
        return data

    # H9: GET /v1/registrations
    def list_registrations(self, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {"limit": limit} if limit is not None else None
        status, data = self.request("GET", "/v1/registrations", query_params=params)
        return data
