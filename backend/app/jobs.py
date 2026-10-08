"""Job search (free APIs) aur cover-letter drafting. Koi auto-apply/form-fill NAHI karta -
job apply karne ke liye link diya jata hai, aap khud submit karte ho."""
from typing import List

import httpx

from . import connections, llm


def search(query: str, location: str = "", remote_only: bool = False, limit: int = 8) -> str:
    limit = max(1, min(int(limit or 8), 15))
    results: List[str] = []

    # Remotive - free, bina key ke, remote jobs
    try:
        r = httpx.get("https://remotive.com/api/remote-jobs", params={"search": query}, timeout=20)
        r.raise_for_status()
        for j in r.json().get("jobs", [])[:limit]:
            results.append(
                f"[Remotive] {j['title']} @ {j['company_name']} ({j.get('candidate_required_location', 'Remote')})\n"
                f"   {j['url']}"
            )
    except Exception as e:
        results.append(f"Remotive se masla: {e}")

    # Adzuna - free key ke saath, location-based
    d = connections.get("adzuna")
    if d and not remote_only:
        try:
            country = "gb"  # default; user chahe to location string me country code de sakta hai
            r = httpx.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={
                    "app_id": d["app_id"],
                    "app_key": d["app_key"],
                    "what": query,
                    "where": location,
                    "results_per_page": limit,
                },
                timeout=20,
            )
            r.raise_for_status()
            for j in r.json().get("results", [])[:limit]:
                results.append(
                    f"[Adzuna] {j['title']} @ {j.get('company', {}).get('display_name', '')} ({j.get('location', {}).get('display_name', '')})\n"
                    f"   {j['redirect_url']}"
                )
        except Exception as e:
            results.append(f"Adzuna se masla: {e}")

    if not results:
        return "Koi job nahi mila. Query badal kar dekho, ya Settings > Connections me Adzuna key lagao (zyada results ke liye)."
    return "\n".join(results)


async def draft_cover_letter(job_title: str, company: str, background: str, tone: str = "professional") -> str:
    system = (
        "Write a concise, personalized cover letter (150-220 words) in clear English for a job application. "
        "No placeholders like [Your Name] left generic - use what the candidate gave. Output only the letter text."
    )
    user = f"Job title: {job_title}\nCompany: {company}\nCandidate background: {background}\nTone: {tone}"
    res = await llm.chat_completion(
        [{"role": "system", "content": system}, {"role": "user", "content": user}], provider="auto", temperature=0.6
    )
    return res["message"]["content"].strip()
