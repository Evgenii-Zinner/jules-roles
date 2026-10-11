#!/usr/bin/env python3
"""
Jules REST API Batch Dispatcher & Concurrency Manager.
Dispatches batches of strictly disjoint tasks to Google Jules with collision verification.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://jules.googleapis.com/v1alpha"


def detect_git_repo_source() -> str | None:
    """Auto-detects the Jules GitHub repository resource path from git config or environment."""
    if os.environ.get("JULES_SOURCE"):
        return os.environ["JULES_SOURCE"].strip()
    try:
        remote = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        match = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", remote)
        if match:
            owner, repo = match.group(1), match.group(2)
            return f"sources/github/{owner}/{repo}"
    except Exception:
        pass
    return None


def detect_git_branch() -> str:
    """Auto-detects the current branch from git or environment."""
    if os.environ.get("JULES_BRANCH"):
        return os.environ["JULES_BRANCH"].strip()
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if branch and branch != "HEAD":
            return branch
    except Exception:
        pass
    return "main"


def get_api_key() -> str:
    """Retrieves Google Jules API key from environment or local key file."""
    if os.environ.get("JULES_API_KEY"):
        return os.environ["JULES_API_KEY"].strip()
    key_paths = [
        os.path.join(os.path.dirname(__file__), ".jules_key"),
        os.path.join(os.path.dirname(__file__), "..", ".jules_key"),
    ]
    for kp in key_paths:
        if os.path.exists(kp):
            with open(kp, "r") as f:
                k = f.read().strip()
                if k:
                    return k
    sys.stderr.write("Error: JULES_API_KEY environment variable or .jules_key file not found.\n")
    sys.exit(1)


def dispatch_session(task: dict, source: str, branch: str, auto_pr: bool = True) -> dict:
    url = f"{API_BASE}/sessions"
    headers = {
        "x-goog-api-key": get_api_key(),
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": task["prompt"],
        "title": task.get("title", f"Task {task.get('id', 'unnamed')}"),
        "sourceContext": {
            "source": source,
            "githubRepoContext": {
                "startingBranch": branch,
            },
        },
        "automationMode": "AUTO_CREATE_PR" if auto_pr else "AUTOMATION_MODE_UNSPECIFIED",
        "requirePlanApproval": task.get("requirePlanApproval", False),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        sys.stderr.write(f"HTTP Error {e.code} for Task {task.get('id')}: {err}\n")
        return {"error": err, "code": e.code}
    except Exception as e:
        sys.stderr.write(f"Error for Task {task.get('id')}: {e}\n")
        return {"error": str(e)}


def load_tasks(tasks_path: str) -> list[dict]:
    if not os.path.exists(tasks_path):
        sys.stderr.write(f"Error: Tasks file not found at '{tasks_path}'.\n")
        sys.stderr.write("Provide a valid JSON file using --tasks <path>.\n")
        sys.exit(1)

    with open(tasks_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        sys.stderr.write("Error: Tasks JSON file must contain a top-level array of task objects.\n")
        sys.exit(1)

    for idx, t in enumerate(data, start=1):
        if "id" not in t:
            t["id"] = idx
        if "prompt" not in t:
            sys.stderr.write(f"Error: Task {t['id']} is missing required 'prompt' field.\n")
            sys.exit(1)
        if "target_files" not in t:
            t["target_files"] = []
        if "test_files" not in t:
            t["test_files"] = []

    return data


def verify_disjoint_tasks(tasks: list[dict]) -> None:
    """Verifies 100% disjoint target and test file sets across tasks to prevent git conflicts."""
    all_targets: set[str] = set()
    all_tests: set[str] = set()

    for t in tasks:
        task_id = t.get("id", "?")
        for f in t.get("target_files", []):
            if f in all_targets:
                sys.stderr.write(f"Error: File collision detected for target file '{f}' in Task {task_id}!\n")
                sys.exit(1)
            all_targets.add(f)

        for f in t.get("test_files", []):
            if f in all_tests:
                sys.stderr.write(f"Error: File collision detected for test file '{f}' in Task {task_id}!\n")
                sys.exit(1)
            all_tests.add(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch batches of disjoint tasks to Google Jules")
    parser.add_argument(
        "--tasks",
        "-f",
        default="tasks.json",
        help="Path to JSON file containing task definitions (default: tasks.json)",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Source repo resource (e.g. sources/github/<owner>/<repo>). Defaults to auto-detecting current git remote.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Starting branch. Defaults to auto-detecting current branch or 'main'.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print task plan and verify disjoint files without dispatching")
    parser.add_argument("--task", type=int, help="Dispatch only a specific task ID")
    parser.add_argument("--start-task", type=int, default=1, help="Start from a specific task ID")
    parser.add_argument(
        "--registry-file",
        default=".jules/active_sessions.json",
        help="Path to record dispatched session state (default: .jules/active_sessions.json)",
    )
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to delay between session dispatches (default: 1.0)")
    args = parser.parse_args()

    # Determine source repo and branch
    source = args.source or detect_git_repo_source()
    if not source:
        sys.stderr.write(
            "Error: Could not auto-detect repository source. "
            "Please pass --source 'sources/github/<owner>/<repo>' or set JULES_SOURCE.\n"
        )
        sys.exit(1)

    branch = args.branch or detect_git_branch()

    # Load tasks
    tasks = load_tasks(args.tasks)
    verify_disjoint_tasks(tasks)
    print(f"Verified zero file intersection across all {len(tasks)} tasks.")

    selected_tasks = [
        t for t in tasks
        if (args.task is None or t["id"] == args.task) and t["id"] >= args.start_task
    ]

    print(f"Selected {len(selected_tasks)} task(s) to dispatch for {source} on branch '{branch}'.")

    if args.dry_run:
        for t in selected_tasks:
            print(f"\n[DRY RUN] Task {t['id']}: {t.get('title', 'Untitled')}")
            if t.get("role"):
                print(f"  Role: {t['role']}")
            if t.get("target_files"):
                print(f"  Target Files: {t['target_files']}")
            if t.get("test_files"):
                print(f"  Test Files: {t['test_files']}")
        return

    # Load existing registry if present
    existing_results = {}
    if os.path.exists(args.registry_file):
        try:
            with open(args.registry_file, "r", encoding="utf-8") as f:
                for entry in json.load(f):
                    existing_results[entry["taskId"]] = entry
        except Exception:
            pass

    os.makedirs(os.path.dirname(os.path.abspath(args.registry_file)), exist_ok=True)

    for t in selected_tasks:
        print(f"\nDispatching Task {t['id']}: {t.get('title', 'Untitled')}...")
        resp = dispatch_session(t, source=source, branch=branch)
        s_id = resp.get("id") or resp.get("name", "").split("/")[-1]
        url = resp.get("url", "")
        state = resp.get("state", "UNKNOWN")
        print(f" -> Session ID: {s_id}")
        print(f" -> URL: {url}")
        print(f" -> State: {state}")

        existing_results[t["id"]] = {
            "taskId": t["id"],
            "title": t.get("title", ""),
            "role": t.get("role", ""),
            "sessionId": s_id,
            "url": url,
            "state": state,
            "targetFiles": t.get("target_files", []),
            "testFiles": t.get("test_files", []),
        }

        # Update registry after each dispatch
        with open(args.registry_file, "w", encoding="utf-8") as f:
            json.dump(list(existing_results.values()), f, indent=2)

        if args.delay > 0:
            time.sleep(args.delay)

    print(f"\nDispatched {len(selected_tasks)} session(s). Registry updated at {args.registry_file}.")


if __name__ == "__main__":
    main()
