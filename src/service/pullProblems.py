import httpx
import random
import time
from typing import Optional
from stem import Signal
from stem.control import Controller
from src.service.mongo_service import mongo_client, get_collection, insert_one, find_one
from src.model.problemDetails import ProblemDetail

# from src.utils.settings import settings

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

LEETCODE_SESSION = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTgxMzk4NzkiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTA0NzlmZTQzYzE4MmZjYTBlN2VkYzQ3ZmNjNjI5Mzc5M2FmYjUzN2Q4NDYzMGE2ZjYxNGRlODRiNjQ4Mzk4Iiwic2Vzc2lvbl91dWlkIjoiNzNjMmNkY2IiLCJpZCI6MTgxMzk4NzksImVtYWlsIjoibWVtZXJ0aGV1bHRpbWF0ZUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im5yUUtBY0NTSksiLCJ1c2VyX3NsdWciOiJuclFLQWNDU0pLIiwiYXZhdGFyIjoiaHR0cHM6Ly9hc3NldHMubGVldGNvZGUuY29tL3VzZXJzL25yUUtBY0NTSksvYXZhdGFyXzE3NTA5MjMxMzUucG5nIiwicmVmcmVzaGVkX2F0IjoxNzUxNDM4MDc1LCJpcCI6IjJhMDI6NmVhMDpjMDQxOjIzODA6OjEyIiwiaWRlbnRpdHkiOiJjYTg2YjAwOGZjM2UyYzNkMzAxNjA2ZDUwYTJmMTIwZSIsImRldmljZV93aXRoX2lwIjpbImYyN2VjNTBkZDViMGRkMTBjMTk4MmYwMDJkZjJkZDA1IiwiMmEwMjo2ZWEwOmMwNDE6MjM4MDo6MTIiXX0.2E0cg_FSq6oY-JhlzBz1frReI40wEGHSMDweDdyjGds"
CSRF_TOKEN = "Gy47Wgl6Vig6yLpVSDhDl5Ay0FhTATi6aeAMY0Mllh4Q8mrWx6jsK6ETvdMKh4eZ"

TOR_SOCKS_PROXY = "socks5h://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051

def rotate_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()  # Uses default cookie auth
            controller.signal(Signal.NEWNYM)
            print("🔄 New Tor identity requested.")
    except Exception as e:
        print(f"❌ Failed to rotate IP: {e}")

class LeetCodeClient:
    def __init__(self):
        self.proxy = TOR_SOCKS_PROXY
        self.retry_limit = 3
        self.request_count = 0
        self.rotation_frequency = 20  # Rotate IP every 20 requests

    def fetch_problem_detail(self, slug: str) -> Optional[dict]:
        query = {
            "query": """
            query getQuestionDetail($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId title titleSlug difficulty content stats
                    topicTags { name slug }
                    codeSnippets { lang langSlug code }
                }
            }""",
            "variables": {"titleSlug": slug}
        }

        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/problems/{slug}/",
            "User-Agent": random.choice(USER_AGENTS),
            "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN};",
            "X-CSRFToken": CSRF_TOKEN
        }

        for attempt in range(self.retry_limit):
            try:
                with httpx.Client(
                    headers=headers,
                    proxy=self.proxy,
                    timeout=20
                ) as client:
                    resp = client.post("https://leetcode.com/graphql/", json=query)

                if resp.status_code == 200:
                    self.request_count += 1
                    if self.request_count % self.rotation_frequency == 0:
                        rotate_tor_ip()

                    return resp.json().get("data", {}).get("question")

                elif resp.status_code == 403:
                    print("❌ 403 Forbidden: Check LEETCODE_SESSION or CSRF token.")
                    return None
                elif resp.status_code == 429:
                    print("⏳ Rate limited. Waiting...")
                    time.sleep(5 + random.uniform(1, 3))
                else:
                    print(f"⚠️ Unexpected status {resp.status_code}")
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2 ** attempt)

        print(f"❌ Failed to fetch {slug} after {self.retry_limit} attempts")
        return None

def pull_problem_dets():
    metadata_collection = get_collection("problems_metadata")
    details_collection = get_collection("problem_details")

    all_meta = list(metadata_collection.find({}))
    client = LeetCodeClient()

    for i, meta in enumerate(all_meta):
        if meta.get("paid_only"):
            continue

        slug = meta["slug"]
        if find_one({"slug": slug}, "problem_details"):
            continue

        print(f"[{i+1}/{len(all_meta)}] ⏳ Fetching: {slug}")
        problem = client.fetch_problem_detail(slug)

        if problem:
            doc = ProblemDetail(
                metadata_id=str(meta["_id"]),
                id=int(problem["questionId"]),
                slug=problem["titleSlug"],
                title=problem["title"],
                difficulty=problem["difficulty"],
                content=problem["content"],
                stats=problem["stats"],
                tags=problem["topicTags"],
                code_snippets=problem["codeSnippets"]
            )
            details_collection.insert_one(doc.model_dump())

            print(f"✅ Stored: {slug}")
        else:
            print(f"❌ Skipped: {slug}")

        time.sleep(random.uniform(2.5, 6))



# Test if proxy is working
def scrape_test():
    client = LeetCodeClient()
    data = client.fetch_problem_detail("two-sum")
    if data:
        print("✅ Fetched:", data["title"])
    else:
        print("❌ Failed to fetch")

scrape_test()
