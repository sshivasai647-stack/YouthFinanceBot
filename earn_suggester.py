# earn_suggester.py
# Purpose: Suggests earning ideas for youth based on age and skills

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ─── Static Trending Tags ────────────────────────────────────
# Updated manually — no API needed
# Based on current India gig economy trends (2024-25)
TRENDING_SKILLS = {
    "ai prompt engineering",
    "shorts editing",
    "linkedin ghostwriting",
    "reels thumbnail",
    "meesho reselling",
}


def suggest_earning(
    age: int,
    skills: List[str],
) -> List[Dict[str, Any]]:
    """
    Suggests earning ideas based on age and skills.

    Args:
        age    : User age (13-25)
        skills : List of skill strings from sidebar

    Returns:
        List of suggestion dicts — each has:
        title, description, platform, earning, emoji,
        tier (immediate/short_term/medium_term), trending
    """
    if age < 13 or age > 25:
        logger.warning(f"suggest_earning called with unusual age: {age}")

    skills_lower = [s.lower() for s in skills]
    suggestions: List[Dict[str, Any]] = []

    # ── Skill-Based Suggestions ───────────────────────────────

    # Coding / Tech
    if any(s in skills_lower for s in ["coding", "programming", "design"]):
        suggestions.append({
            "title"      : "AI Prompt Engineering Gigs",
            "description": "Create prompts for ChatGPT/LLM projects — trending now!",
            "platform"   : "Fiverr, Internshala, LinkedIn",
            "earning"    : "₹500 - ₹2,000 per gig",
            "emoji"      : "💻",
            "tier"       : "immediate",
            "trending"   : True,
        })
        suggestions.append({
            "title"      : "Web Development for Local Businesses",
            "description": "Build websites for shops and restaurants in your city.",
            "platform"   : "Fiverr, Freelancer.in, Justdial",
            "earning"    : "₹10,000 - ₹30,000/month",
            "emoji"      : "🌐",
            "tier"       : "short_term",
            "trending"   : False,
        })

    # Drawing / Art / Design
    if any(s in skills_lower for s in ["drawing", "design"]):
        suggestions.append({
            "title"      : "Reel Thumbnail Design",
            "description": "Create eye-catching thumbnails for Instagram Reels.",
            "platform"   : "Fiverr, Instagram, WorkIndia",
            "earning"    : "₹200 - ₹800 per thumbnail",
            "emoji"      : "🎨",
            "tier"       : "immediate",
            "trending"   : True,
        })

    # Writing
    if "writing" in skills_lower:
        suggestions.append({
            "title"      : "LinkedIn Ghostwriting",
            "description": "Write professional posts for executives — booming in India!",
            "platform"   : "LinkedIn, Fiverr, Internshala",
            "earning"    : "₹1,000 - ₹5,000 per post",
            "emoji"      : "✍️",
            "tier"       : "short_term",
            "trending"   : True,
        })

    # Video Editing
    if "video editing" in skills_lower:
        suggestions.append({
            "title"      : "Shorts & Reels Editing",
            "description": "Edit 15-60 second videos for social media creators.",
            "platform"   : "Fiverr, Instagram, YouTube",
            "earning"    : "₹300 - ₹1,500 per video",
            "emoji"      : "🎬",
            "tier"       : "immediate",
            "trending"   : True,
        })

    # Teaching
    if "teaching" in skills_lower:
        suggestions.append({
            "title"      : "JEE / NEET Prep Tutor",
            "description": "Online coaching for competitive exam students.",
            "platform"   : "Unacademy, Vedantu, BYJU'S",
            "earning"    : "₹300 - ₹800/hour",
            "emoji"      : "📚",
            "tier"       : "medium_term",
            "trending"   : False,
        })

    # Social Media
    if "social media" in skills_lower:
        suggestions.append({
            "title"      : "Instagram Growth Manager",
            "description": "Grow follower base for local businesses and influencers.",
            "platform"   : "Instagram, Fiverr, Urban Company",
            "earning"    : "₹5,000 - ₹15,000/month",
            "emoji"      : "📱",
            "tier"       : "short_term",
            "trending"   : False,
        })

    # ── Age-Based Suggestions ─────────────────────────────────

    if 13 <= age <= 17:
        suggestions.append({
            "title"      : "Sell Study Notes Online",
            "description": "Share your class notes and study materials online.",
            "platform"   : "Instagram, WhatsApp Groups, Notesgen",
            "earning"    : "₹100 - ₹500 per subject",
            "emoji"      : "📝",
            "tier"       : "immediate",
            "trending"   : False,
        })
        suggestions.append({
            "title"      : "YouTube Study Tips Channel",
            "description": "Share exam prep tips and study hacks on YouTube.",
            "platform"   : "YouTube, Instagram",
            "earning"    : "₹1,000 - ₹10,000/month (after growth)",
            "emoji"      : "📹",
            "tier"       : "medium_term",
            "trending"   : False,
        })

    if 18 <= age <= 25:
        suggestions.append({
            "title"      : "Food Delivery Partner",
            "description": "Earn daily with flexible hours on your bike or scooter.",
            "platform"   : "Swiggy, Zomato, Blinkit, Zepto",
            "earning"    : "₹500 - ₹1,200/day",
            "emoji"      : "🛵",
            "tier"       : "immediate",
            "trending"   : False,
        })
        suggestions.append({
            "title"      : "Reselling on Meesho",
            "description": "Source products wholesale and sell via social media.",
            "platform"   : "Meesho, WhatsApp, Instagram",
            "earning"    : "₹5,000 - ₹20,000/month",
            "emoji"      : "🛍️",
            "tier"       : "short_term",
            "trending"   : True,
        })

    # ── Fallback — No Skills Matched ──────────────────────────
    if not suggestions:
        logger.info(f"No skill match for age={age}, skills={skills}")
        suggestions.extend([
            {
                "title"      : "Complete Online Surveys",
                "description": "Take surveys and earn small amounts daily.",
                "platform"   : "Google Opinion Rewards, Toluna, RozDhan",
                "earning"    : "₹200 - ₹1,000/month",
                "emoji"      : "📋",
                "tier"       : "immediate",
                "trending"   : False,
            },
            {
                "title"      : "Home Services Partner",
                "description": "Beauty, cleaning, or repair services in your area.",
                "platform"   : "Urban Company, Housejoy, Justdial",
                "earning"    : "₹300 - ₹800 per service",
                "emoji"      : "🧹",
                "tier"       : "short_term",
                "trending"   : False,
            },
        ])

    # ── Sort — Trending First, Then by Tier ───────────────────
    TIER_ORDER = {"immediate": 0, "short_term": 1, "medium_term": 2}

    suggestions.sort(
        key=lambda x: (
            not x.get("trending", False),          # trending first
            TIER_ORDER.get(x.get("tier", "short_term"), 1),
        )
    )

    logger.info(
        f"suggest_earning: age={age}, skills={skills}, "
        f"matches={len(suggestions)}"
    )

    return suggestions


# ─── Test ────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== Earning Suggestions Test ===\n")

    result = suggest_earning(
        age    = 21,
        skills = ["coding", "video editing"],
    )

    for idea in result:
        trend_marker = " 🔥 TRENDING" if idea.get("trending") else ""
        print(f"{idea['emoji']} {idea['title']}{trend_marker}")
        print(f"   📌 {idea['description']}")
        print(f"   🌐 Platform : {idea['platform']}")
        print(f"   💰 Earning  : {idea['earning']}")
        print(f"   ⏱  Tier     : {idea['tier']}")
        print()