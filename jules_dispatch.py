#!/usr/bin/env python3
"""
Jules REST API Dispatcher & Session Manager for Sting Engine.
Provides programmatic control over Google Jules autonomous coding sessions.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://jules.googleapis.com/v1alpha"
DEFAULT_SOURCE = "sources/github/Evgenii-Zinner/Sting"
DEFAULT_BRANCH = "main"

def get_api_key() -> str:
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
    sys.stderr.write("Error: JULES_API_KEY environment variable or tools/.jules_key file not found.\n")
    sys.exit(1)


def api_request(path: str, method: str = "GET", data: dict | None = None) -> dict:
    url = f"{API_BASE}/{path.lstrip('/')}"
    headers = {
        "x-goog-api-key": get_api_key(),
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            if not content:
                return {}
            return json.loads(content)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        sys.stderr.write(f"HTTP Error {e.code}: {err_msg}\n")
        sys.exit(1)
    except urllib.error.URLError as e:
        sys.stderr.write(f"URL Error: {e.reason}\n")
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    query = urllib.parse.urlencode({"pageSize": args.page_size})
    res = api_request(f"sessions?{query}")
    sessions = res.get("sessions", [])
    if not sessions:
        print("No active or previous sessions found.")
        return

    print(f"Found {len(sessions)} session(s):")
    for s in sessions:
        s_id = s.get("id") or s.get("name", "").split("/")[-1]
        title = s.get("title", "Untitled")
        state = s.get("state", "UNKNOWN")
        url = s.get("url", "")
        outputs = s.get("outputs")
        pr = ""
        if isinstance(outputs, dict):
            pr = outputs.get("pullRequest", {}).get("url", "")
        elif isinstance(outputs, list):
            for out in outputs:
                if isinstance(out, dict) and "pullRequest" in out:
                    pr = out["pullRequest"].get("url", "")
                    break
        pr_str = f" | PR: {pr}" if pr else ""
        print(f"  [{state:12}] {s_id}: {title} ({url}){pr_str}")


def cmd_get(args: argparse.Namespace) -> None:
    session_id = args.session_id.split("/")[-1]
    res = api_request(f"sessions/{session_id}")
    print(json.dumps(res, indent=2))


def cmd_create(args: argparse.Namespace) -> None:
    payload = {
        "prompt": args.prompt,
        "sourceContext": {
            "source": args.source,
            "githubRepoContext": {
                "startingBranch": args.branch,
            },
        },
        "automationMode": "AUTO_CREATE_PR" if args.auto_pr else "AUTOMATION_MODE_UNSPECIFIED",
        "requirePlanApproval": args.require_plan_approval,
    }
    if args.title:
        payload["title"] = args.title

    res = api_request("sessions", method="POST", data=payload)
    print("Session created successfully:")
    print(json.dumps(res, indent=2))


def cmd_activities(args: argparse.Namespace) -> None:
    session_id = args.session_id.split("/")[-1]
    query = urllib.parse.urlencode({"pageSize": args.page_size})
    res = api_request(f"sessions/{session_id}/activities?{query}")
    print(json.dumps(res, indent=2))


def cmd_message(args: argparse.Namespace) -> None:
    session_id = args.session_id.split("/")[-1]
    payload = {"message": args.message}
    res = api_request(f"sessions/{session_id}:sendMessage", method="POST", data=payload)
    print("Message sent successfully:")
    print(json.dumps(res, indent=2))


def cmd_approve(args: argparse.Namespace) -> None:
    session_id = args.session_id.split("/")[-1]
    res = api_request(f"sessions/{session_id}:approvePlan", method="POST", data={})
    print("Plan approved successfully:")
    print(json.dumps(res, indent=2))


def cmd_delete(args: argparse.Namespace) -> None:
    session_id = args.session_id.split("/")[-1]
    res = api_request(f"sessions/{session_id}", method="DELETE")
    print(f"Session {session_id} deleted successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jules REST API CLI for Sting Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="List sessions")
    p_list.add_argument("--page-size", type=int, default=30, help="Number of sessions")
    p_list.set_defaults(func=cmd_list)

    # get
    p_get = subparsers.add_parser("get", help="Get session details")
    p_get.add_argument("session_id", help="Session ID or resource name")
    p_get.set_defaults(func=cmd_get)

    # create
    p_create = subparsers.add_parser("create", help="Create a new task session")
    p_create.add_argument("--prompt", required=True, help="Task instructions for Jules")
    p_create.add_argument("--title", help="Optional title for the session")
    p_create.add_argument("--source", default=DEFAULT_SOURCE, help=f"Source repo resource (default: {DEFAULT_SOURCE})")
    p_create.add_argument("--branch", default=DEFAULT_BRANCH, help=f"Starting branch (default: {DEFAULT_BRANCH})")
    p_create.add_argument("--auto-pr", action="store_true", default=True, help="Automatically create PR")
    p_create.add_argument("--require-plan-approval", action="store_true", default=False, help="Require explicit approval")
    p_create.set_defaults(func=cmd_create)

    # activities
    p_act = subparsers.add_parser("activities", help="Get session activities")
    p_act.add_argument("session_id", help="Session ID")
    p_act.add_argument("--page-size", type=int, default=50, help="Number of activities")
    p_act.set_defaults(func=cmd_activities)

    # message
    p_msg = subparsers.add_parser("message", help="Send a message to an ongoing session")
    p_msg.add_argument("session_id", help="Session ID")
    p_msg.add_argument("--message", required=True, help="Message text")
    p_msg.set_defaults(func=cmd_message)

    # approve
    p_app = subparsers.add_parser("approve", help="Approve plan for a session")
    p_app.add_argument("session_id", help="Session ID")
    p_app.set_defaults(func=cmd_approve)

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a session")
    p_del.add_argument("session_id", help="Session ID")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
