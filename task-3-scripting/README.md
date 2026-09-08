# Task 3: HTTP Health Checker

I built a Python health checker that reads endpoint settings, sends HTTP GET
requests, retries failures, and prints a JSON report. I used only Python's
standard library, so no package installation or AWS credentials are needed.

## Files

| File | What I use it for |
|---|---|
| `endpoints.json` | List URLs, expected status codes, and retry settings |
| `config.py` | Read and validate the settings |
| `checks.py` | Measure requests and retry failures |
| `healthcheck.py` | Run every check, print JSON, and set the exit code |
| `test_config.py` | Test settings and invalid inputs |
| `test_checks.py` | Test retry decisions and timeout handling |
| `test_cli.py` | Test the full command against a local HTTP server |
| `../.github/workflows/healthcheck.yml` | Run these tests on GitHub |

## Run it

I run these commands from the repository root with Python 3.9 or newer.
The example configuration expects the Task 2 application on localhost:8080.
Start that app in a separate terminal:

```bash
python3 task-2-cicd/app.py
```

If the Docker app is already running on port 8080, I use that instead.
Then I run:

```bash
python3 task-3-scripting/healthcheck.py
```

To use a different JSON file:

```bash
python3 task-3-scripting/healthcheck.py --config task-3-scripting/endpoints.json
```

For the deployed app, I can supply settings through an environment variable:

```bash
HEALTHCHECK_CONFIG='{"attempts":3,"timeout":10,"backoff":1,"endpoints":[{"url":"http://assessment-alb-784103789.eu-west-1.elb.amazonaws.com/healthz","expected_status":200}]}' \
  python3 task-3-scripting/healthcheck.py
```

`HEALTHCHECK_CONFIG`, when set, overrides the file, including `--config`.
I keep passwords and tokens out of URLs because URLs appear in the report.

## Settings and results

- `attempts`: maximum requests per endpoint, including the first; default 3.
- `timeout`: positive socket timeout in seconds; default 5.
- `backoff`: delay multiplier in seconds; default 1. Before retries I wait
  `backoff × failed attempt number`: with three attempts, the waits are 1s and 2s.
- `endpoints`: nonempty list of HTTP(S) URLs and `expected_status` (default 200).

I stop retrying an endpoint as soon as its response matches the expected
status. I still check the other endpoints when one fails. A configured 404
or 302 can pass; redirects are reported directly rather than followed.

The JSON report includes `total`, `failed`, overall `passed`, and `results`.
Each result includes the URL, expected status, actual `status_code`,
`response_time_ms`, pass/fail, and the full attempt history. A connection
failure has a null status and an error message. The top-level endpoint
status and response time refer to its final attempt.

I use these exit codes for automation:

| Code | Meaning |
|---|---|
| 0 | Every endpoint passed |
| 1 | At least one endpoint failed after its attempts |
| 2 | Invalid/unreadable configuration (or command-line usage error) |

To save a report and inspect the exit code immediately:

```bash
python3 task-3-scripting/healthcheck.py > /tmp/assessment-health.json
echo $?
```

## What I verified

```bash
python3 -m unittest discover -s task-3-scripting -v
```

I verified eleven tests covering configuration, retries, increasing backoff,
timeout handling, expected error/redirect statuses, JSON output, and exit
codes. The integration tests start their own local HTTP server; they need
no cloud resources. I also ran the checker against the deployed `/healthz`
on 9 September 2026: it returned HTTP 200 and exit code 0.

## Production extensions and limitations

I kept this version sequential and status-based. It measures time until
response headers arrive, not the complete body download. Socket timeout is
not a strict total deadline, especially for DNS resolution. It does not
validate response bodies, latency thresholds, certificates nearing expiry,
or application dependencies. Many endpoints or retries increase total runtime.

For production, I would schedule checks, publish metrics to CloudWatch or
Prometheus, and alert on sustained failures to reduce noise. I would add
latency thresholds, response-content checks, bounded parallelism, retry
jitter, and checks from multiple locations. These are proposed extensions;
this script does not install a monitoring service or send alerts.

I stop a manually started app with Ctrl+C. The checker itself leaves no
running service or AWS resources; saved JSON reports can be deleted.
