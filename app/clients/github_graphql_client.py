from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GithubClientError(RuntimeError):
    pass


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


async def graphql_request(
    *,
    token: str,
    query: str,
    variables: dict[str, Any],
    timeout: float = 15.0,
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            GITHUB_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=_auth_headers(token),
        )

    if response.status_code != 200:
        raise GithubClientError(
            f"GitHub GraphQL HTTP {response.status_code}: {response.text}"
        )

    payload = response.json()

    if "errors" in payload:
        raise GithubClientError(f"GitHub GraphQL error: {payload['errors']}")

    return payload["data"]


async def fetch_contributions_overview(
    *,
    token: str,
    from_date: datetime,
    to_date: datetime,
) -> dict[str, Any]:
    query = """
    query ($from: DateTime!, $to: DateTime!) {
      viewer {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
          commitContributionsByRepository {
            repository {
              name
              owner { login }
              primaryLanguage {
                name
              }
            }
            contributions {
              totalCount
            }
          }
        }
      }
    }
    """

    variables = {
        "from": from_date.astimezone(timezone.utc).isoformat(),
        "to": to_date.astimezone(timezone.utc).isoformat(),
    }

    data = await graphql_request(
        token=token,
        query=query,
        variables=variables,
    )

    return data["viewer"]["contributionsCollection"]


async def fetch_repo_commit_dates(
    *,
    token: str,
    owner: str,
    name: str,
    from_date: datetime,
    to_date: datetime,
    limit: int = 100,
) -> list[datetime]:
    query = """
    query (
      $owner: String!
      $name: String!
      $from: GitTimestamp!
      $to: GitTimestamp!
      $limit: Int!
    ) {
      repository(owner: $owner, name: $name) {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: $limit, since: $from, until: $to) {
                nodes {
                  committedDate
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "owner": owner,
        "name": name,
        "from": from_date.astimezone(timezone.utc).isoformat(),
        "to": to_date.astimezone(timezone.utc).isoformat(),
        "limit": limit,
    }

    data = await graphql_request(
        token=token,
        query=query,
        variables=variables,
    )

    history = (
        data["repository"]
        .get("defaultBranchRef", {})
        .get("target", {})
        .get("history", {})
        .get("nodes", [])
    )

    return [
        datetime.fromisoformat(node["committedDate"].replace("Z", "+00:00"))
        for node in history
    ]

