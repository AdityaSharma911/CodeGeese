import os
import json
from typing import Dict, List, Tuple
from src.model.problemSolution import ProblemSolution
from src.model.problemDetails import ProblemDetail, CodeSnippet
from src.service.mongo_service import get_collection, insert_one, init_mongo
from src.utils.solutionsPrompt import build_prompt
from huggingface_hub import InferenceClient
from src.utils.settings import settings
from openai import OpenAI

# Map directory names/extensions to language keys
LANG_MAP = {
    "C++": ("cpp", ".cpp"),
    "Python": ("python", ".py"),
    "Python3": ("python3", ".py"),
    "Java": ("java", ".java"),
    "MySQL": ("mysql", ".sql"),
    "TypeScript": ("typescript", ".ts"),
    "Shell": ("shell", ".sh"),
    "Swift": ("swift", ".swift"),
    "Rust": ("rust", ".rs"),
    "Ruby": ("ruby", ".rb"),
    "PHP": ("php", ".php"),
    "Golang": ("go", ".go"),
    "Kotlin": ("kotlin", ".kt"),
    "C#": ("csharp", ".cs"),
}

# SOLUTIONS_ROOT = settings.SOLUTIONS_ROOT
SOLUTIONS_ROOT = "/Users/adisbub/Documents/codebase/LeetCode-Solutions"

def find_solutions_for_slug(slug: str) -> Dict[str, str]:
    solutions = {}
    for dir_name, (lang_key, ext) in LANG_MAP.items():
        dir_path = os.path.join(SOLUTIONS_ROOT, dir_name)
        file_path = os.path.join(dir_path, f"{slug}{ext}")
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                solutions[lang_key] = f.read()
    return solutions


def get_llm_pattern_and_tags(title: str, content: str, code_snippets: List[CodeSnippet]) -> Tuple[str, List[str]]:
    from src.utils.solutionsPrompt import build_prompt

    # Debug prints
    print(f"DEBUG - Title: {title}")
    print(f"DEBUG - Content length: {len(content)}")
    print(f"DEBUG - Code snippets count: {len(code_snippets)}")
    print(f"DEBUG - Code snippet languages: {[cs.lang for cs in code_snippets]}")

    prompt = build_prompt(title, content, code_snippets)
    print(f"DEBUG - Prompt length: {len(prompt)}")
    print(f"DEBUG - Prompt preview: {prompt[:500]}...")

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # cheapest recommended
            messages=[
                {"role": "system", "content": "You are a helpful AI that classifies algorithm problems."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        message = response.choices[0].message.content
        print(f"DEBUG - LLM Response: {message}")
        
        result = json.loads(message)
        return result.get("pattern", ""), result.get("tags", [])

    except Exception as e:
        print("[OpenAI API ERROR] Exception during OpenAI call:", e)
        print("Prompt was:\n", prompt)
        return "", []


def batch_process_problem_solutions():
    init_mongo()
    details_collection = get_collection("problem_details")
    solutions_collection = get_collection("problem_solutions")

    all_problems = list(details_collection.find({}))
    # Process remaining problems starting from index 100
    problems_to_process = all_problems[100:]
    
    for i, prob in enumerate(problems_to_process):
        slug = prob["slug"]
        print(f"[{i+1}/{len(problems_to_process)}] Processing: {slug}")

        # Find code solutions
        solutions = find_solutions_for_slug(slug)

        # Prepare code snippets for prompt (if needed)
        code_snippets = [CodeSnippet(lang=lang, code=code) for lang, code in solutions.items()]

        # Get pattern and tags from LLM
        pattern, tags = get_llm_pattern_and_tags(
            prob["title"], prob["content"], code_snippets
        )

        # Build and insert ProblemSolution
        sol_doc = ProblemSolution(
            metadata_id=prob["metadata_id"],
            slug=prob["slug"],
            title=prob["title"],
            difficulty=prob["difficulty"],
            content=prob["content"],
            pattern=pattern,
            tags=tags,
            solutions=solutions,
        )
        insert_one(sol_doc, "problem_solutions")
        print(f"✅ Inserted: {slug}")
    
    print(f"Completed processing {len(problems_to_process)} problems")

if __name__ == "__main__":
    batch_process_problem_solutions()