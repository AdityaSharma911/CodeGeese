import json
import requests

headers = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/problems/two-sum/discuss/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
    "X-CSRFToken": "<TOKEN>",
    "Cookie": "LEETCODE_SESSION=<TOKEN>; csrftoken=<TOKEN>"
}

graphql_query = """
query {
  questionSolutions(filters: {
    questionSlug: "two-sum",
    first: 5,
    skip: 0,
    orderBy: MOST_VOTED
  }) {
    solutions {
      title
      post {
        content
        voteCount
        author {
          username
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://leetcode.com/graphql",
    headers=headers,
    data=json.dumps({"query": graphql_query})
)

print(response.json())