"""Send HTTP GET requests and retry unsuccessful checks."""
import time
import urllib.error
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None  # Report redirects as their actual HTTP status.


def request_once(url, timeout):
    start = time.perf_counter()
    status, error = None, None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "assessment-healthcheck/1"})
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code  # A 404 may be the expected response.
        exc.close()
    except (urllib.error.URLError, OSError, ValueError) as exc:
        error = str(exc)
    return {"status_code": status,
            "response_time_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": error}


def check_endpoint(endpoint, config):
    attempts = []
    for number in range(1, config["attempts"] + 1):
        result = request_once(endpoint["url"], config["timeout"])
        result["passed"] = result["status_code"] == endpoint["expected_status"]
        attempts.append({"attempt": number, **result})
        if result["passed"]:
            break
        if number < config["attempts"]:
            time.sleep(config["backoff"] * number)
    return {**endpoint, **result, "attempts": attempts}
