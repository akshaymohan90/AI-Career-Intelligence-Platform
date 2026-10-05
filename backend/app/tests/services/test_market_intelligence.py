from app.services.market_intelligence import (
    apply_trends,
    build_requirement_sets,
    momentum_ratio,
    rank_skill_gaps,
    trend_direction,
)
from app.services.skill_taxonomy import extract_taxonomy_skills


def posting(title, required, company="Acme"):
    return {"title": title, "company": company, "location": "Remote", "link": "https://x", "required": set(required)}


def test_taxonomy_matches_aliases_and_symbol_names():
    found = extract_taxonomy_skills("We use Golang, k8s, Node.js and C++ daily")
    assert {"Go", "Kubernetes", "Node.js", "C++"} <= found


def test_taxonomy_does_not_match_inside_words():
    assert "Go" not in extract_taxonomy_skills("We need a good engineer")


def test_build_requirement_sets_drops_thin_postings():
    jobs = [
        {"title": "Backend", "description": "Python and SQL and Docker", "company_name": "A"},
        {"title": "Designer", "description": "Figma only", "company_name": "B"},
    ]
    parsed = build_requirement_sets(jobs)
    assert len(parsed) == 1
    assert {"Python", "SQL", "Docker"} <= parsed[0]["required"]


def test_gap_ranking_counts_fractional_unlocks():
    have = {"Python", "SQL"}
    postings = [
        posting("A", {"Python", "SQL", "Docker"}),
        posting("B", {"Python", "SQL", "Docker", "Redis"}),
    ]
    result = rank_skill_gaps(have, postings)
    docker = next(r for r in result["recommendations"] if r["skill"] == "Docker")
    redis = next(r for r in result["recommendations"] if r["skill"] == "Redis")
    assert docker["jobs_unlocked"] == 1.0 + 0.5
    assert redis["jobs_unlocked"] == 0.5


def test_postings_below_coverage_threshold_are_excluded():
    have = {"Python"}
    postings = [posting("Far", {"Python", "Go", "Rust", "C++", "Kafka"})]
    result = rank_skill_gaps(have, postings)
    assert result["near_matches"] == 0
    assert result["recommendations"] == []


def test_already_qualified_postings_are_counted_not_recommended():
    have = {"Python", "SQL"}
    postings = [posting("Match", {"Python", "SQL"})]
    result = rank_skill_gaps(have, postings)
    assert result["already_qualified"] == 1
    assert result["recommendations"] == []


def test_ranking_prefers_jobs_per_week_not_raw_count():
    have = {"Python"}
    postings = [
        posting("1", {"Python", "Kubernetes"}),
        posting("2", {"Python", "Kubernetes"}),
        posting("3", {"Python", "Git"}),
    ]
    result = rank_skill_gaps(have, postings)
    assert result["recommendations"][0]["skill"] == "Git"


def test_momentum_detects_rising_interest():
    assert trend_direction(momentum_ratio([5, 5, 5, 20, 30, 40])) == "rising"


def test_momentum_detects_falling_interest():
    assert trend_direction(momentum_ratio([60, 60, 60, 20, 10, 5])) == "falling"


def test_momentum_needs_enough_points():
    assert momentum_ratio([1, 2, 3]) is None
    assert trend_direction(None) == "unknown"


def test_rising_skill_is_boosted_above_higher_raw_score():
    recs = [
        {"skill": "Java", "jobs_per_week": 0.2},
        {"skill": "Kubernetes", "jobs_per_week": 0.18},
    ]
    trends = {
        "Java": {"direction": "falling", "momentum": 0.5},
        "Kubernetes": {"direction": "rising", "momentum": 1.8},
    }
    ranked = apply_trends(recs, trends)
    assert ranked[0]["skill"] == "Kubernetes"
