# Systems Operations Lab

## ℹ️ About

A case-based systems troubleshooting simulation for practicing incident-style investigation, CLI evidence gathering, log analysis, API health checks, AWS cloud networking, and Bash/Python automation across Linux systems, networking, applications/APIs, and identity scenarios.

The lab uses realistic operational scenarios to practice moving from reported symptoms to checks, findings, and resolution. The emphasis is on understanding how systems fail, command-line evidence gathering, interpreting system, application, and network behavior, and building small utilities that make troubleshooting repeatable.

## 🧪 What This Lab Demonstrates
<!-- markdownlint-disable MD001 -->
#### 🐧 Linux Services & Runtime Behavior

- Investigating service state, listening ports, permissions, logs, and runtime symptoms with tools such as `systemctl`/`journalctl`, `ls`, `chmod`, `curl` and `tail`
- Connecting Linux CLI evidence to real service/application failure modes, including startup failures, unavailable applications, repeated errors, and access issues

#### 🌐 Networking & Connectivity Diagnosis

- Troubleshooting DNS resolution, host reachability, routing, port access, and service availability with tools such as `dig`/`nslookup`, `nc`, `ss`, `ping`, `ip route`, and `curl`
- Separating network reachability from application availability by reasoning through path, transport connectivity, and service behavior

#### ☁️ Cloud Networking & Segmentation

> Case files adapted from completed work in the [Learn to Cloud Networking Lab](https://github.com/learntocloud/networking-lab).

- Troubleshooting and fixing broken cloud network infrastructure involving private subnet egress, private DNS resolution, tier-to-tier connectivity, and segmentation controls
- Using AWS CLI to inspect and correct route tables, NAT Gateway paths, Route 53 private hosted zones, security group and NACL configuration, and least-privilege access

#### 🔌 Applications, APIs & Logs

- Investigating HTTP/API behavior through status codes, authentication/authorization failures, health checks, dependency checks, configuration issues, and application logs
- Practicing request/response inspection and log analysis with `curl`, custom headers, `tail`, and `grep`

#### 🔐 Identity, Access & Auth Signals

- Reviewing access-policy behavior, suspicious sign-in patterns, and authorization-related failures
- Tracing identity issues from reported access impact to auth, policy, and verification

#### ⚙️ Automation & Diagnostic Utilities

- Building Bash and Python utilities for diagnostics, evidence collection, and repeatable investigation workflows
- Using automation to standardize evidence gathering and improve troubleshooting reviewability

## 📦 Artifacts

### 🎫 Featured Cases

Primary incident-style scenarios used to practice technical investigation, evidence gathering, troubleshooting, findings, and verification.
<!-- markdownlint-disable MD060 -->
|            |            |
| ---------- | ---------- |
|**Applications and APIs**| • [`application-dependency-failure.md`](docs/cases/applications-apis/application-dependency-failure.md)<br> • [`application-running-endpoint-failing.md`](docs/cases/applications-apis/application-running-endpoint-failing.md)<br> • [`api-auth-failure.md`](docs/cases/applications-apis/api-auth-failure.md)<br> • [`api-invalid-request-payload.md`](docs/cases/applications-apis/api-invalid-request-payload.md) |
|   **Cloud Networking**  | • [`private-subnet-egress-failure.md`](docs/cases/cloud-networking/private-subnet-egress-failure.md)<br> • [`private-dns-service-discovery.md`](docs/cases/cloud-networking/private-dns-service-discovery.md)<br> • [`tier-to-tier-connectivity-blocked.md`](docs/cases/cloud-networking/tier-to-tier-connectivity-blocked.md)<br> • [`network-segmentation-exposure.md`](docs/cases/cloud-networking/network-segmentation-exposure.md) |
|        **Linux**        | • [`service-running-application-unavailable.md`](docs/cases/linux/service-running-application-unavailable.md)<br> • [`repeated-application-errors.md`](docs/cases/linux/repeated-application-errors.md)<br> • [`service-will-not-start.md`](docs/cases/linux/service-will-not-start.md)<br> • [`permissions-blocking-access.md`](docs/cases/linux/permissions-blocking-access.md) |
|     **Networking**      | • [`dns-resolves-service-still-fails.md`](docs/cases/networking/dns-resolves-service-still-fails.md)<br> • [`host-reachable-application-unreachable.md`](docs/cases/networking/host-reachable-application-unreachable.md)<br> • [`invalid-default-route.md`](docs/cases/networking/invalid-default-route.md)<br> • [`dns-config-issue.md`](docs/cases/networking/dns-config-issue.md) |
|  **Identity & Access**  | • [`suspicious-login-report.md`](docs/cases/identity-access/suspicious-login-report.md)<br> • [`policy-blocked-sign-in.md`](docs/cases/identity-access/policy-blocked-sign-in.md) |
|   **Windows Endpoint**  | • [`mapped-network-drive-unavailable.md`](docs/cases/windows-endpoint/mapped-network-drive-unavailable.md)<br> • [`no-internet-dns-failure.md`](docs/cases/windows-endpoint/no-internet-dns-failure.md) |

### 🐚 Bash Scripts

Bash utilities for diagnostics, evidence gathering, and repeatable command-line investigation.

- [`evidence-collect.sh`](tools/bash/evidence-collect.sh) — reusable Linux evidence collection. Accepts an optional service name, URL, and/or IP address. Collects host, service, journal, port, routing, and reachability evidence, and writes results to a timestamped file.
- [`disk-triage.sh`](tools/bash/disk-triage.sh) — disk usage triage utility. Accepts a target path, usage threshold, and depth value. Reports filesystem usage, flags filesystems above the threshold, shows the target path size and largest entries, and can save results to a timestamped file.

### 🐍 Python Scripts

Python utilities for API checks, log analysis, and operational automation.

- [`log_summary.py`](tools/python/log_summary.py) — command-line log analysis utility. Accepts a log file, optional case-insensitive keyword filter, and number of repeated patterns to show. Reports total and matching lines, counts severity markers, normalizes timestamps and request/trace IDs to group repeated messages, shows the first and last matching lines, and returns exit codes based on severity findings for use in automation.

**Planned:**

- `api_health_check.py`

## 🗂️ Repository Structure

- [`docs/cases/`](docs/cases/) → troubleshooting incident case
- [`docs/kb-articles/`](docs/kb-articles/) → technical notes
- [`docs/runbooks/`](docs/runbooks/) → operational guides
- [`tools/bash/`](tools/bash/) → Bash diagnostic utilities
- [`tools/python/`](tools/python/) → Python automation utilities
