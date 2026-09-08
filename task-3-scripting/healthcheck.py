"""Run all configured checks, print JSON, and return a useful exit code."""
import argparse
import json
from pathlib import Path

from checks import check_endpoint
from config import load_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=Path(__file__).with_name("endpoints.json"))
    args = parser.parse_args()
    try:
        config = load_config(args.config)
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}))
        return 2
    results = [check_endpoint(endpoint, config) for endpoint in config["endpoints"]]
    failures = sum(not result["passed"] for result in results)
    print(json.dumps({"passed": failures == 0, "total": len(results),
                      "failed": failures, "results": results}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
