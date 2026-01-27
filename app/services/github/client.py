from datetime import datetime, timezone
import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

async def fetch_github_activity(*, token: str, from_date: datetime, to_date: datetime,):
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
        }
      }
    }
    """

    variables = {
        "from": from_date.astimezone(timezone.utc).isoformat(),
        "to": to_date.astimezone(timezone.utc).isoformat(),
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )
    
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub GraphQL failed: {response.status_code} {response.text}"
        )

    payload = response.json()

    if "errors" in payload:
        raise RuntimeError(f"Github Graphql error: {payload["errors"]}")

    print(f"payload: {payload}")

    
