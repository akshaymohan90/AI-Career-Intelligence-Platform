import time
from collections import defaultdict
from statistics import mean

from app.services.serpapi_client import SerpApiClient, SerpApiError
from app.services.skill_taxonomy import estimated_weeks, extract_taxonomy_skills

# Postings list 5-20 detected skills, so a quarter overlap marks a realistic candidate.
REACHABLE_COVERAGE = 0.25
MIN_REQUIREMENTS = 2
EVIDENCE_PER_SKILL = 3
TOP_N = 8
TRENDS_GEO = "IN"
TRENDS_BATCH = 5
TREND_WEIGHT = {"rising": 1.25, "stable": 1.0, "falling": 0.8, "unknown": 1.0}


def trend_term(skill: str) -> str:
    return skill.replace("&", "and").replace("  ", " ")


def momentum_ratio(values: list[float]) -> float | None:
    if len(values) < 6:
        return None
    early = mean(values[:3])
    recent = mean(values[-3:])
    return round((recent + 1) / (early + 1), 2)


def trend_direction(ratio: float | None) -> str:
    if ratio is None:
        return "unknown"
    if ratio >= 1.25:
        return "rising"
    if ratio <= 0.8:
        return "falling"
    return "stable"


def fetch_trends(client: SerpApiClient, skills: list[str], trace: list) -> dict[str, dict]:
    if not skills:
        return {}

    started = time.perf_counter()
    result: dict[str, dict] = {}
    failure = None

    for start in range(0, len(skills), TRENDS_BATCH):
        batch = skills[start:start + TRENDS_BATCH]
        try:
            data = client.search(
                "google_trends",
                q=",".join(trend_term(s) for s in batch),
                data_type="TIMESERIES",
                date="today 12-m",
                geo=TRENDS_GEO,
            )
        except SerpApiError as exc:
            failure = str(exc)
            continue

        series: dict[str, list[float]] = defaultdict(list)
        for point in data.get("interest_over_time", {}).get("timeline_data", []):
            for value in point.get("values", []):
                series[value["query"]].append(float(value.get("extracted_value", 0)))

        for skill in batch:
            ratio = momentum_ratio(series.get(trend_term(skill), []))
            result[skill] = {"direction": trend_direction(ratio), "momentum": ratio}

    rising = [s for s, t in result.items() if t["direction"] == "rising"]
    detail = (
        f"12-month interest in India for {len(result)} skills; "
        f"rising: {', '.join(rising) if rising else 'none'}"
    )
    if failure:
        detail += f" (partial: {failure})"
    trace.append({
        "step": "Google Trends momentum",
        "detail": detail,
        "ms": round((time.perf_counter() - started) * 1000),
    })
    return result


def apply_trends(recommendations: list[dict], trends: dict[str, dict]) -> list[dict]:
    for rec in recommendations:
        info = trends.get(rec["skill"], {"direction": "unknown", "momentum": None})
        rec["trend_direction"] = info["direction"]
        rec["trend_momentum"] = info["momentum"]
        rec["score"] = round(rec["jobs_per_week"] * TREND_WEIGHT[info["direction"]], 3)
    recommendations.sort(key=lambda r: r["score"], reverse=True)
    return recommendations


def fetch_postings(client: SerpApiClient, role: str, location: str, max_pages: int, trace: list) -> list[dict]:
    postings: dict[str, dict] = {}
    next_token = None

    for page in range(1, max_pages + 1):
        started = time.perf_counter()
        params = {"q": role, "location": location}
        if next_token:
            params["next_page_token"] = next_token
        data = client.search("google_jobs", **params)

        results = data.get("jobs_results", [])
        for job in results:
            job_id = job.get("job_id") or job.get("title", "") + job.get("company_name", "")
            postings.setdefault(job_id, job)

        next_token = data.get("serpapi_pagination", {}).get("next_page_token")
        trace.append({
            "step": f"Google Jobs search, page {page}",
            "detail": f"Fetched {len(results)} live postings for '{role}' in {location}",
            "ms": round((time.perf_counter() - started) * 1000),
        })
        if not next_token:
            break

    return list(postings.values())


def build_requirement_sets(postings: list[dict]) -> list[dict]:
    parsed = []
    for job in postings:
        text = f"{job.get('title', '')}\n{job.get('description', '')}"
        required = extract_taxonomy_skills(text)
        if len(required) < MIN_REQUIREMENTS:
            continue
        apply_link = None
        options = job.get("apply_options") or []
        if options:
            apply_link = options[0].get("link")
        parsed.append({
            "title": job.get("title", "Untitled role"),
            "company": job.get("company_name", "Unknown company"),
            "location": job.get("location"),
            "link": apply_link or job.get("share_link"),
            "required": required,
        })
    return parsed


def rank_skill_gaps(have: set[str], postings: list[dict]) -> dict:
    unlock_score: dict[str, float] = defaultdict(float)
    evidence: dict[str, list[dict]] = defaultdict(list)
    already_qualified = 0
    near_matches = 0

    for job in postings:
        missing = job["required"] - have
        if not missing:
            already_qualified += 1
            continue
        coverage = (len(job["required"]) - len(missing)) / len(job["required"])
        if coverage < REACHABLE_COVERAGE:
            continue

        near_matches += 1
        share = 1 / len(missing)
        for skill in missing:
            unlock_score[skill] += share
            evidence[skill].append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "link": job["link"],
                "gaps_in_posting": len(missing),
            })

    ranked = []
    for skill, unlocked in unlock_score.items():
        weeks = estimated_weeks(skill)
        ranked.append({
            "skill": skill,
            "jobs_unlocked": round(unlocked, 2),
            "estimated_weeks": weeks,
            "jobs_per_week": round(unlocked / weeks, 3),
            "evidence": sorted(evidence[skill], key=lambda e: e["gaps_in_posting"])[:EVIDENCE_PER_SKILL],
        })

    ranked.sort(key=lambda r: r["jobs_per_week"], reverse=True)

    return {
        "already_qualified": already_qualified,
        "near_matches": near_matches,
        "recommendations": ranked[:TOP_N],
    }


def run_market_scan(
    client: SerpApiClient,
    role: str,
    location: str,
    resume_text: str,
    max_pages: int = 2,
) -> dict:
    trace: list[dict] = []

    postings = fetch_postings(client, role, location, max_pages, trace)

    started = time.perf_counter()
    parsed = build_requirement_sets(postings)
    trace.append({
        "step": "Extracted required skills",
        "detail": f"Parsed {len(parsed)} of {len(postings)} postings with at least {MIN_REQUIREMENTS} recognised skills",
        "ms": round((time.perf_counter() - started) * 1000),
    })

    started = time.perf_counter()
    have = extract_taxonomy_skills(resume_text)
    ranking = rank_skill_gaps(have, parsed)
    trace.append({
        "step": "Scored skill gaps",
        "detail": (
            f"{ranking['near_matches']} postings where you already cover at least "
            f"{int(REACHABLE_COVERAGE * 100)}% of the requirements; "
            f"ranked {len(ranking['recommendations'])} skills by jobs unlocked per week of learning"
        ),
        "ms": round((time.perf_counter() - started) * 1000),
    })

    trends = fetch_trends(client, [r["skill"] for r in ranking["recommendations"]], trace)
    recommendations = apply_trends(ranking["recommendations"], trends)

    return {
        "role": role,
        "location": location,
        "postings_scanned": len(postings),
        "postings_analyzed": len(parsed),
        "your_skills": sorted(have),
        "already_qualified": ranking["already_qualified"],
        "near_matches": ranking["near_matches"],
        "recommendations": recommendations,
        "agent_trace": trace,
        "serpapi_live_calls": client.live_calls,
        "serpapi_cache_hits": client.cache_hits,
    }
