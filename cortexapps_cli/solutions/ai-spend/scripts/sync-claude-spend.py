#!/usr/bin/env python3
"""
sync-claude-spend.py

Pulls per-user spend from the Anthropic Claude Enterprise Analytics API
and pushes weekly cost data to Cortex as custom metric data points.
Also computes per-team rollups by walking the team-member relationship
hierarchy, writing both an ai-spend custom metric and ai-spend-weekly
custom data on each team entity.

Requirements:
    pip install requests

Environment variables:
    ANTHROPIC_ANALYTICS_KEY  Required. Analytics API key from claude.ai org settings.
                             Only the primary owner can create this key at:
                             claude.ai > Organization settings > API
    CORTEX_API_KEY           Required. Cortex API key.
    CORTEX_BASE_URL          Optional. Defaults to https://api.getcortexapp.com
    EMAIL_DOMAIN             Optional. Domain to strip from emails. Defaults to cortex.io

Usage:
    python sync-claude-spend.py
    python sync-claude-spend.py --start 2026-07-21 --end 2026-07-28

Notes:
    - Users who authenticate via API key (not Enterprise OAuth) will show $0 spend
      in the Analytics API and are skipped automatically.
    - The Cortex custom metric definition for "ai-spend" must already exist in your
      Cortex instance before running this script. Create it in the Cortex UI under
      Eng Intel > Custom Metrics.
    - Team rollups require team entities to have team-member relationships pointing
      to employee entities (or other teams, which are resolved recursively).
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests

ANTHROPIC_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"
CORTEX_METRIC_KEY = "ai-spend"
CORTEX_SPEND_DATA_KEY = "ai-spend-weekly"
TEAM_MEMBER_RELATIONSHIP = "team-member"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync Claude Enterprise spend to Cortex custom metrics"
    )
    parser.add_argument(
        "--start",
        help="Start date YYYY-MM-DD (default: 7 days ago)",
        default=None,
    )
    parser.add_argument(
        "--end",
        help="End date YYYY-MM-DD (default: yesterday)",
        default=None,
    )
    return parser.parse_args()


def get_env(key, required=True, default=None):
    value = os.environ.get(key, default)
    if required and not value:
        print(f"ERROR: Environment variable {key} is required", file=sys.stderr)
        sys.exit(1)
    return value


def email_to_entity_tag(email, domain):
    """
    Maps first.last@domain -> employee-first-last.
    Returns None if email doesn't match the expected domain or format.
    """
    if not email.endswith(f"@{domain}"):
        return None
    local = email.split("@")[0]
    parts = local.split(".")
    if len(parts) != 2:
        return None
    return f"employee-{parts[0]}-{parts[1]}"


def fetch_claude_spend(analytics_key, start_date, end_date):
    """
    Fetch per-user cost data from the Claude Enterprise Analytics API.

    Returns list of dicts: {"email": str, "cost_dollars": float}
    Only includes records where cost > 0.

    Endpoint: GET /v1/organizations/analytics/costs
    Verify exact query parameters once an Analytics API key is available.
    """
    headers = {
        "x-api-key": analytics_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    results = []
    cursor = None

    while True:
        params = {
            "starting_at": start_date,
            "ending_at": end_date,
        }
        if cursor:
            params["page"] = cursor

        url = f"{ANTHROPIC_BASE_URL}/v1/organizations/analytics/costs"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        body = response.json()

        for record in body.get("data", []):
            actor = record.get("actor", {})
            email = actor.get("email_address")
            if not email:
                continue

            # Cost is returned as a decimal string in cents (e.g. "14250.000000" = $142.50)
            cost_str = record.get("cost", "0")
            try:
                cost_dollars = float(cost_str) / 100
            except (ValueError, TypeError):
                cost_dollars = 0.0

            if cost_dollars > 0:
                results.append({"email": email, "cost_dollars": cost_dollars})

        if not body.get("has_more"):
            break
        cursor = body.get("next_page")

    return results


def fetch_team_member_relationships(cortex_api_key, cortex_base_url):
    """
    Fetch all team-member relationship instances from Cortex.

    Returns a dict mapping source_tag -> list of dicts {"tag": str, "type": str}
    where type is the entity type (e.g. "employee", "team").
    """
    url = f"{cortex_base_url}/api/v1/relationships/{TEAM_MEMBER_RELATIONSHIP}"
    headers = {
        "Authorization": f"Bearer {cortex_api_key}",
        "Content-Type": "application/json",
    }
    adjacency = defaultdict(list)
    page = 0
    while True:
        params = {"pageSize": 200, "page": page}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        body = response.json()
        for rel in body.get("relationships", []):
            src = rel.get("sourceEntity", {})
            dst = rel.get("destinationEntity", {})
            if src.get("tag") and dst.get("tag"):
                adjacency[src["tag"]].append({
                    "tag": dst["tag"],
                    "type": dst.get("type", ""),
                })
        if not body.get("hasNextPage") and not body.get("has_more"):
            break
        page += 1
    return adjacency


def collect_leaf_employees(team_tag, adjacency, visited=None):
    """
    DFS walk of the team-member hierarchy to collect all leaf employee tags.

    Teams that point to sub-teams are resolved recursively; cycles are guarded
    with the visited set. Returns a set of employee entity tags.
    """
    if visited is None:
        visited = set()
    if team_tag in visited:
        return set()
    visited.add(team_tag)

    employees = set()
    for member in adjacency.get(team_tag, []):
        if member["type"] == "employee":
            employees.add(member["tag"])
        else:
            # Recurse into sub-teams
            employees |= collect_leaf_employees(member["tag"], adjacency, visited)
    return employees


def push_to_cortex(cortex_api_key, cortex_base_url, entity_tag, series):
    """
    Push spend data points for a single entity to Cortex.

    series: list of {"timestamp": str, "value": float}
    Calls: POST /api/v1/eng-intel/custom-metrics/{key}/entity/{tag}/bulk
    """
    url = (
        f"{cortex_base_url}/api/v1/eng-intel/custom-metrics"
        f"/{CORTEX_METRIC_KEY}/entity/{entity_tag}/bulk"
    )
    headers = {
        "Authorization": f"Bearer {cortex_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url, headers=headers, json={"series": series}, timeout=30
    )
    response.raise_for_status()


def push_custom_data(cortex_api_key, cortex_base_url, entity_tag, key, value):
    """
    Write a single custom data value for an entity.

    Calls: POST /api/v1/catalog/{tag}/custom-data
    """
    url = f"{cortex_base_url}/api/v1/catalog/{entity_tag}/custom-data"
    headers = {
        "Authorization": f"Bearer {cortex_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url, headers=headers, json={"key": key, "value": value}, timeout=30
    )
    response.raise_for_status()


def main():
    args = parse_args()

    analytics_key = get_env("ANTHROPIC_ANALYTICS_KEY")
    cortex_api_key = get_env("CORTEX_API_KEY")
    cortex_base_url = get_env(
        "CORTEX_BASE_URL", required=False, default="https://api.getcortexapp.com"
    )
    email_domain = get_env("EMAIL_DOMAIN", required=False, default="cortex.io")

    today = datetime.now(timezone.utc).date()
    start_date = args.start or str(today - timedelta(days=7))
    end_date = args.end or str(today - timedelta(days=1))
    # Use end_date as the metric timestamp (represents the week ending on this date)
    timestamp = f"{end_date}T00:00:00"

    print(f"Fetching Claude spend from {start_date} to {end_date}...")

    try:
        spend_records = fetch_claude_spend(analytics_key, start_date, end_date)
    except requests.HTTPError as e:
        print(f"ERROR: Failed to fetch spend data from Anthropic: {e}", file=sys.stderr)
        sys.exit(1)

    # Map emails to entity tags; collect skips
    entity_series = defaultdict(list)
    skipped = []

    for record in spend_records:
        email = record["email"]
        entity_tag = email_to_entity_tag(email, email_domain)
        if not entity_tag:
            skipped.append((email, "domain mismatch or unexpected format"))
            continue
        entity_series[entity_tag].append({
            "timestamp": timestamp,
            "value": round(record["cost_dollars"], 2),
        })

    if not entity_series:
        print("No spend records matched — nothing to push.")
    else:
        print(f"Pushing spend for {len(entity_series)} employee(s) to Cortex...")
        push_errors = []
        for entity_tag, series in sorted(entity_series.items()):
            try:
                push_to_cortex(cortex_api_key, cortex_base_url, entity_tag, series)
                print(f"  OK: {entity_tag}")
            except requests.HTTPError as e:
                print(f"  FAIL: {entity_tag}: {e}", file=sys.stderr)
                push_errors.append(entity_tag)

        if push_errors:
            print(f"\nERROR: Failed to push {len(push_errors)} entities.", file=sys.stderr)
            sys.exit(1)

    # Build a flat map of employee tag → spend for rollup calculations
    employee_spend = {
        tag: series[0]["value"]
        for tag, series in entity_series.items()
        if series
    }

    # Compute and push team rollups
    print("\nFetching team-member relationships for team rollups...")
    try:
        adjacency = fetch_team_member_relationships(cortex_api_key, cortex_base_url)
    except requests.HTTPError as e:
        print(f"WARNING: Could not fetch team relationships, skipping rollups: {e}", file=sys.stderr)
        adjacency = {}

    if adjacency:
        # Identify all team nodes (source entities that have team-member relationships)
        team_tags = list(adjacency.keys())
        print(f"Computing rollups for {len(team_tags)} team(s)...")
        rollup_errors = []
        teams_updated = 0

        for team_tag in sorted(team_tags):
            leaf_employees = collect_leaf_employees(team_tag, adjacency)
            if not leaf_employees:
                continue

            team_spend = round(
                sum(employee_spend.get(e, 0.0) for e in leaf_employees), 2
            )
            if team_spend == 0:
                continue

            series = [{"timestamp": timestamp, "value": team_spend}]
            try:
                push_to_cortex(cortex_api_key, cortex_base_url, team_tag, series)
                push_custom_data(
                    cortex_api_key, cortex_base_url, team_tag,
                    CORTEX_SPEND_DATA_KEY, team_spend
                )
                print(f"  OK: {team_tag} = ${team_spend:.2f}/wk ({len(leaf_employees)} members)")
                teams_updated += 1
            except requests.HTTPError as e:
                print(f"  FAIL: {team_tag}: {e}", file=sys.stderr)
                rollup_errors.append(team_tag)

        if rollup_errors:
            print(f"\nERROR: Failed to push rollups for {len(rollup_errors)} teams.", file=sys.stderr)
            sys.exit(1)
    else:
        teams_updated = 0

    print(f"\nSummary:")
    print(f"  Employees updated: {len(entity_series)}")
    print(f"  Teams updated: {teams_updated}")
    print(f"  Skipped: {len(skipped)}")
    for email, reason in skipped:
        print(f"    - {email}: {reason}")


if __name__ == "__main__":
    main()
