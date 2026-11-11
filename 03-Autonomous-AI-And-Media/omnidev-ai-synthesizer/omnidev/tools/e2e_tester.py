import requests
import time
from typing import Dict, Any, List, Optional

class E2ETester:
    """
    Automated testing engine to verify API endpoints, CRUD operations,
    and frontend page responses.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def discover_endpoints(self) -> List[str]:
        """
        Queries /openapi.json to discover all registered API paths dynamically.
        """
        try:
            resp = requests.get(f"{self.base_url}/openapi.json", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                return list(data.get("paths", {}).keys())
        except Exception:
            pass
        return []

    def test_health(self, path: str = "/") -> Dict[str, Any]:
        """
        Tests if the root or health endpoint responds with HTTP 200/300 range.
        """
        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(url, timeout=5)
            passed = resp.status_code in [200, 201, 301, 302, 304]
            return {
                "step": f"Health check ({path})",
                "passed": passed,
                "status_code": resp.status_code,
                "content_preview": resp.text[:200]
            }
        except Exception as e:
            return {
                "step": f"Health check ({path})",
                "passed": False,
                "error": str(e)
            }

    def test_crud_lifecycle(
        self,
        endpoint: str,
        sample_payload: Dict[str, Any],
        update_payload: Dict[str, Any],
        id_field: str = "id"
    ) -> Dict[str, Any]:
        """
        Tests full CRUD lifecycle:
        1. CREATE (POST)
        2. READ ALL (GET)
        3. READ ONE (GET by ID)
        4. UPDATE (PUT/PATCH)
        5. DELETE (DELETE)
        """
        clean_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        full_url = f"{self.base_url}{clean_endpoint}"
        steps = []
        created_id = None

        # 1. CREATE
        try:
            r_create = requests.post(full_url, json=sample_payload, timeout=5)
            if r_create.status_code in [200, 201]:
                data = r_create.json() if "application/json" in r_create.headers.get("Content-Type", "") else {}
                created_id = data.get(id_field)
                steps.append({"action": "CREATE (POST)", "passed": True, "status": r_create.status_code, "id": created_id})
            else:
                steps.append({"action": "CREATE (POST)", "passed": False, "status": r_create.status_code, "error": r_create.text})
                return {"all_passed": False, "steps": steps, "failed_at": "CREATE"}
        except Exception as e:
            steps.append({"action": "CREATE (POST)", "passed": False, "error": str(e)})
            return {"all_passed": False, "steps": steps, "failed_at": "CREATE"}

        # 2. READ ALL
        try:
            r_read = requests.get(full_url, timeout=5)
            if r_read.status_code == 200:
                steps.append({"action": "READ ALL (GET)", "passed": True, "status": 200})
            else:
                steps.append({"action": "READ ALL (GET)", "passed": False, "status": r_read.status_code, "error": r_read.text})
                return {"all_passed": False, "steps": steps, "failed_at": "READ ALL"}
        except Exception as e:
            steps.append({"action": "READ ALL (GET)", "passed": False, "error": str(e)})
            return {"all_passed": False, "steps": steps, "failed_at": "READ ALL"}

        # 3. READ ONE (if id available)
        if created_id is not None:
            one_url = f"{full_url}/{created_id}"
            try:
                r_one = requests.get(one_url, timeout=5)
                if r_one.status_code == 200:
                    steps.append({"action": "READ ONE (GET)", "passed": True, "status": 200})
                else:
                    steps.append({"action": "READ ONE (GET)", "passed": False, "status": r_one.status_code, "error": r_one.text})
            except Exception as e:
                steps.append({"action": "READ ONE (GET)", "passed": False, "error": str(e)})

            # 4. UPDATE
            try:
                r_up = requests.put(one_url, json=update_payload, timeout=5)
                if r_up.status_code in [200, 204]:
                    steps.append({"action": "UPDATE (PUT)", "passed": True, "status": r_up.status_code})
                else:
                    # Try PATCH
                    r_patch = requests.patch(one_url, json=update_payload, timeout=5)
                    if r_patch.status_code in [200, 204]:
                        steps.append({"action": "UPDATE (PATCH)", "passed": True, "status": r_patch.status_code})
                    else:
                        steps.append({"action": "UPDATE", "passed": False, "status": r_up.status_code, "error": r_up.text})
            except Exception as e:
                steps.append({"action": "UPDATE", "passed": False, "error": str(e)})

            # 5. DELETE
            try:
                r_del = requests.delete(one_url, timeout=5)
                if r_del.status_code in [200, 204]:
                    steps.append({"action": "DELETE", "passed": True, "status": r_del.status_code})
                else:
                    steps.append({"action": "DELETE", "passed": False, "status": r_del.status_code, "error": r_del.text})
            except Exception as e:
                steps.append({"action": "DELETE", "passed": False, "error": str(e)})

        all_passed = all(s.get("passed", False) for s in steps)
        return {"all_passed": all_passed, "steps": steps}
