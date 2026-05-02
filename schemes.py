# schemes.py
# Purpose: Scalable rules engine to recommend Indian government schemes

import copy
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ─── Scheme Database ─────────────────────────────────────────
# state rule contract:
#   "ALL"              → national scheme, any state eligible
#   ["State1","State2"]→ only those states eligible
#   key absent         → no state restriction
SCHEMES_DB: List[Dict[str, Any]] = [
    {
        "id"         : "APY_01",
        "name"       : "Atal Pension Yojana",
        "description": "Get a fixed pension every month after age 60.",
        "benefit"    : "₹1000 - ₹5000/month after retirement",
        "emoji"      : "🏦",
        "link"       : "https://npscra.nsdl.co.in/scheme-details.php",
        "rules"      : {
            "age_min"             : 18,
            "age_max"             : 40,
            "income_max"          : 25000,   # ₹25k/month ~₹3L/year
            "exclude_occupations" : ["Government Employee", "Tax Payer"],
        },
        "base_score" : 40,
    },
    {
        "id"         : "PMMY_01",
        "name"       : "PM Mudra Yojana",
        "description": "Get a loan to start your own small business.",
        "benefit"    : "Loan up to ₹10 Lakhs",
        "emoji"      : "💼",
        "link"       : "https://www.mudra.org.in/",
        "rules"      : {
            "age_min"    : 18,
            "occupations": ["Entrepreneur", "Unemployed", "Self-employed"],
        },
        "base_score" : 50,
    },
    {
        "id"         : "PMK_01",
        "name"       : "PM-KISAN",
        "description": "Income support for landholding farmer families.",
        "benefit"    : "₹6000/year in 3 equal installments",
        "emoji"      : "🌾",
        "link"       : "https://pmkisan.gov.in/",
        "rules"      : {
            "occupations"         : ["Farmer"],
            "exclude_occupations" : ["Institutional Landholder", "Tax Payer"],
            "state"               : "ALL",
        },
        "base_score" : 70,
    },
    {
        "id"         : "SSY_01",
        "name"       : "Sukanya Samriddhi Yojana",
        "description": "Savings scheme specially designed for girl child.",
        "benefit"    : "High interest + tax benefit",
        "emoji"      : "👧",
        "link"       : "https://www.indiapost.gov.in/",
        "rules"      : {
            "gender" : "female",
            "age_max": 10,
        },
        "base_score" : 60,
    },
    {
        "id"         : "VLOAN_01",
        "name"       : "PM Vidya Lakshmi",
        "description": "Easy education loans for students from any bank.",
        "benefit"    : "Education loan up to ₹10 Lakhs",
        "emoji"      : "🎓",
        "link"       : "https://www.vidyalakshmi.co.in/",
        "rules"      : {
            "age_min"    : 15,
            "age_max"    : 28,
            "occupations": ["Student"],
        },
        "base_score" : 50,
    },
]


def match_scheme(user: Dict[str, Any], scheme: Dict[str, Any]) -> float:
    """
    Evaluates a user against scheme eligibility rules.

    Returns:
        0.0  if user is ineligible
        >0.0 eligibility score (capped at 100) if eligible
    """
    user_age    = user.get("age", 0)
    user_gender = user.get("gender", "").lower().strip()
    user_occ    = user.get("occupation", "").strip()
    user_income = user.get("income", 0)     # monthly ₹
    user_state  = user.get("state", "").strip()

    rules = scheme.get("rules", {})
    score = float(scheme.get("base_score", 10))

    # ── Hard Exclusions ───────────────────────────────────────

    if "age_min" in rules and user_age < rules["age_min"]:
        return 0.0

    if "age_max" in rules and user_age > rules["age_max"]:
        return 0.0

    if "gender" in rules and user_gender != rules["gender"].lower():
        return 0.0

    # ✅ Fixed — case-insensitive occupation exclusion
    if "exclude_occupations" in rules:
        excl_lower = [o.lower() for o in rules["exclude_occupations"]]
        if user_occ.lower() in excl_lower:
            return 0.0

    # ✅ Fixed — monthly income * 12 for annual comparison
    if "income_max" in rules and (user_income * 12) > (rules["income_max"] * 12):
        return 0.0

    # State check — "ALL" means any state qualifies
    if "state" in rules:
        if rules["state"] != "ALL":
            allowed_states = rules["state"] if isinstance(rules["state"], list) else []
            if user_state not in allowed_states:
                return 0.0

    # ── Soft Matches ──────────────────────────────────────────

    # ✅ Fixed — case-insensitive occupation matching
    if "occupations" in rules:
        occ_lower = [o.lower() for o in rules["occupations"]]
        if user_occ.lower() in occ_lower:
            score += 20.0
        else:
            return 0.0   # occupation listed → strict requirement

    # ✅ Fixed — compare annual income correctly (monthly × 12)
    if (user_income * 12) < 300000:
        score += 15.0

    logger.debug(f"Matched {scheme['name']} — score={score:.1f}")
    return min(score, 100.0)


def get_relevant_schemes(
    user_profile: Dict[str, Any],
    top_n       : int = 5,
) -> List[Dict[str, Any]]:
    """
    Returns top N ranked eligible schemes for a user profile.

    Args:
        user_profile : dict with keys: age, gender, income, state, occupation
        top_n        : max schemes to return (default 5)

    Returns:
        List of scheme dicts with added 'eligibility_score' key
    """
    eligible: List[Dict[str, Any]] = []

    for scheme in SCHEMES_DB:
        score = match_scheme(user_profile, scheme)
        if score > 0:
            # ✅ Fixed — deep copy prevents mutating SCHEMES_DB
            scheme_result = copy.deepcopy(scheme)
            scheme_result["eligibility_score"] = score
            eligible.append(scheme_result)

    if not eligible:
        # ✅ Fixed — log safe fields only, not full profile (PII)
        logger.info(
            f"No schemes matched — "
            f"age={user_profile.get('age')} | "
            f"occupation={user_profile.get('occupation')} | "
            f"state={user_profile.get('state')}"
        )

    eligible.sort(key=lambda x: x["eligibility_score"], reverse=True)
    return eligible[:top_n]


# ─── Standalone Test ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== Schemes Test ===\n")

    # Test 1: Farmer profile
    farmer = {
        "age"       : 28,
        "gender"    : "female",
        "income"    : 12000,    # ₹12k/month
        "state"     : "Maharashtra",
        "occupation": "Farmer",
    }
    results = get_relevant_schemes(farmer)
    print(f"--- Farmer Profile ({len(results)} matches) ---")
    for s in results:
        print(f"  {s['emoji']} {s['name']} (Score: {s['eligibility_score']:.0f})")
        print(f"     {s['benefit']}")

    # Test 2: Student profile
    student = {
        "age"       : 20,
        "gender"    : "male",
        "income"    : 0,
        "state"     : "Delhi",
        "occupation": "Student",
    }
    results2 = get_relevant_schemes(student)
    print(f"\n--- Student Profile ({len(results2)} matches) ---")
    for s in results2:
        print(f"  {s['emoji']} {s['name']} (Score: {s['eligibility_score']:.0f})")

    # Test 3: No match profile
    tax_payer = {
        "age"       : 35,
        "gender"    : "male",
        "income"    : 80000,
        "state"     : "Mumbai",
        "occupation": "Government Employee",
    }
    results3 = get_relevant_schemes(tax_payer)
    print(f"\n--- Govt Employee Profile ({len(results3)} matches) ---")
    print("  None" if not results3 else results3)

    # Test 4: Case sensitivity fix check
    case_test = {
        "age"       : 22,
        "gender"    : "Male",       # uppercase — should still work
        "income"    : 8000,
        "state"     : "Delhi",
        "occupation": "student",    # lowercase — should still match Student
    }
    results4 = get_relevant_schemes(case_test)
    print(f"\n--- Case Sensitivity Test ({len(results4)} matches) ---")
    for s in results4:
        print(f"  {s['emoji']} {s['name']}")