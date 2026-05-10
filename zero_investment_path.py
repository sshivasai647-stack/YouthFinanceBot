"""
zero_investment_path.py
========================
Zero Investment Earning Path for Youth Financial Guardian Chatbot.

This module provides comprehensive guidance for youth looking to earn money
with little to no initial investment. Focuses on skill-building, freelancing,
and low-barrier entry opportunities in the Indian context.

Author: Youth Financial Guardian Project
Compliance: DPDPA 2023 — no PII stored beyond session
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 1. ENUMS
# ─────────────────────────────────────────────

class InvestmentLevel(Enum):
    """Investment required to start"""
    ZERO     = "₹0"
    LOW      = "₹100-500"
    MEDIUM   = "₹500-2000"
    HIGH     = "₹2000+"

class TimeToStart(Enum):
    """Time needed to start earning"""
    IMMEDIATE = "Start Today"
    WEEK      = "1 Week"
    MONTH     = "1 Month"
    QUARTER   = "3 Months"

class SkillLevel(Enum):
    """Required skill level"""
    BEGINNER   = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED   = "Advanced"

# ─────────────────────────────────────────────
# 2. DATACLASSES
# ─────────────────────────────────────────────

@dataclass
class EarningOpportunity:
    """Represents a single earning opportunity"""
    title: str
    description: str
    platform: str
    investment: InvestmentLevel
    time_to_start: TimeToStart
    skill_required: SkillLevel
    potential_earning: str  # e.g., "₹500-2000/month"
    category: str  # e.g., "Freelancing", "Content Creation"
    steps: List[str]  # Step-by-step guide
    tips: List[str]   # Success tips
    resources: List[str]  # Learning resources
    trending: bool = False

@dataclass
class UserProfile:
    """User's earning profile"""
    age: int
    skills: List[str]
    location: str = "India"
    has_smartphone: bool = True
    has_internet: bool = True
    available_hours: int = 4  # hours per day

# ─────────────────────────────────────────────
# 3. EARNING OPPORTUNITIES DATABASE
# ─────────────────────────────────────────────

EARNING_DATABASE = [
    # ── Zero Investment, Immediate Start ──────────────────
    EarningOpportunity(
        title="YouTube Shorts Creator",
        description="Create and upload 15-30 second videos on trending topics",
        platform="YouTube, Instagram Reels, TikTok",
        investment=InvestmentLevel.ZERO,
        time_to_start=TimeToStart.IMMEDIATE,
        skill_required=SkillLevel.BEGINNER,
        potential_earning="₹1000-5000/month",
        category="Content Creation",
        steps=[
            "Download free video editing apps (CapCut, InShot)",
            "Learn basic editing in 1 day from YouTube tutorials",
            "Create 2-3 shorts daily on trending topics",
            "Post consistently and engage with comments",
            "Monetize after 1K subscribers or 10M views"
        ],
        tips=[
            "Use trending audio and challenges",
            "Keep videos under 30 seconds",
            "Post at peak times (evening)",
            "Collaborate with other creators"
        ],
        resources=[
            "YouTube: 'How to make YouTube Shorts'",
            "Free stock videos: Pexels, Pixabay",
            "Trending topics: YouTube Trends, Google Trends"
        ],
        trending=True
    ),

    EarningOpportunity(
        title="Freelance Writing",
        description="Write articles, blog posts, or social media content",
        platform="Fiverr, Upwork, Freelancer",
        investment=InvestmentLevel.ZERO,
        time_to_start=TimeToStart.WEEK,
        skill_required=SkillLevel.BEGINNER,
        potential_earning="₹2000-8000/month",
        category="Freelancing",
        steps=[
            "Create free profiles on freelancing platforms",
            "Start with simple tasks (article writing, reviews)",
            "Build portfolio with 3-5 samples",
            "Bid on entry-level projects",
            "Deliver high-quality work to get reviews"
        ],
        tips=[
            "Focus on niches you know (education, lifestyle)",
            "Use Grammarly free version",
            "Communicate clearly with clients",
            "Start with ₹100-300 per article"
        ],
        resources=[
            "Fiverr: Create seller account",
            "Free writing courses: Coursera audit",
            "Writing samples: Reddit writing prompts"
        ]
    ),

    EarningOpportunity(
        title="Social Media Management",
        description="Manage social media accounts for small businesses",
        platform="Instagram, Facebook, LinkedIn",
        investment=InvestmentLevel.ZERO,
        time_to_start=TimeToStart.WEEK,
        skill_required=SkillLevel.INTERMEDIATE,
        potential_earning="₹3000-10000/month",
        category="Digital Marketing",
        steps=[
            "Learn social media basics (posting, engagement)",
            "Create sample strategies for different businesses",
            "Offer services to local shops/restaurants",
            "Use free tools: Canva for graphics, Buffer for scheduling",
            "Build case studies from free work"
        ],
        tips=[
            "Start with friends/family businesses",
            "Track engagement metrics",
            "Learn from successful pages in your niche",
            "Offer packages: ₹1000/month for basic management"
        ],
        resources=[
            "Free courses: Google Digital Garage",
            "Tools: Canva, Buffer free plans",
            "Templates: Free social media templates online"
        ]
    ),

    # ── Low Investment Opportunities ──────────────────────
    EarningOpportunity(
        title="Meesho Reselling",
        description="Source products from wholesalers and sell on Meesho",
        platform="Meesho, WhatsApp",
        investment=InvestmentLevel.LOW,
        time_to_start=TimeToStart.WEEK,
        skill_required=SkillLevel.BEGINNER,
        potential_earning="₹2000-15000/month",
        category="E-commerce",
        steps=[
            "Register on Meesho as seller (₹100-200)",
            "Find wholesale suppliers on IndiaMart",
            "Start with 5-10 products (₹500-1000 investment)",
            "Take professional photos with phone",
            "List products with detailed descriptions",
            "Handle customer service via WhatsApp"
        ],
        tips=[
            "Start with trending products (fashion, accessories)",
            "Offer COD for trust building",
            "Provide excellent customer service",
            "Reinvest profits in more inventory"
        ],
        resources=[
            "Meesho seller guide",
            "IndiaMart for suppliers",
            "Free photography tips on YouTube"
        ],
        trending=True
    ),

    EarningOpportunity(
        title="Online Tutoring",
        description="Teach subjects you excel in online",
        platform="UrbanPro, TutorIndia, Whiteboard.fi",
        investment=InvestmentLevel.LOW,
        time_to_start=TimeToStart.WEEK,
        skill_required=SkillLevel.INTERMEDIATE,
        potential_earning="₹5000-20000/month",
        category="Education",
        steps=[
            "Identify your strong subjects",
            "Create free profile on tutoring platforms",
            "Get basic certification if needed (₹500-1000)",
            "Practice teaching with friends/family",
            "Start with demo classes for free",
            "Build schedule for regular students"
        ],
        tips=[
            "Focus on CBSE/ICSE/competitive exams",
            "Use free online whiteboards",
            "Record sessions for student reference",
            "Offer group classes for more income"
        ],
        resources=[
            "UrbanPro: Free registration",
            "Free teaching resources: Khan Academy",
            "Certification: Coursera specializations"
        ]
    ),

    # ── Medium Investment Opportunities ───────────────────
    EarningOpportunity(
        title="Mobile Photography Service",
        description="Offer photography services for events, products",
        platform="Local clients, Instagram",
        investment=InvestmentLevel.MEDIUM,
        time_to_start=TimeToStart.MONTH,
        skill_required=SkillLevel.INTERMEDIATE,
        potential_earning="₹5000-25000/month",
        category="Services",
        steps=[
            "Learn photography basics (₹1000 online course)",
            "Buy basic equipment (₹1000-2000): tripod, lights",
            "Create portfolio with free shoots",
            "Build Instagram presence",
            "Offer services: ₹500-2000 per event",
            "Network locally for clients"
        ],
        tips=[
            "Start with family events for experience",
            "Edit photos using free apps (Snapseed, Lightroom mobile)",
            "Offer packages with different deliverables",
            "Get business cards printed (₹200)"
        ],
        resources=[
            "Free courses: Skillshare free trial",
            "Apps: Lightroom, Snapseed",
            "Portfolio sites: Free Behance account"
        ]
    ),

    EarningOpportunity(
        title="App Development Freelancing",
        description="Create simple mobile apps for small businesses",
        platform="Fiverr, Upwork",
        investment=InvestmentLevel.MEDIUM,
        time_to_start=TimeToStart.MONTH,
        skill_required=SkillLevel.ADVANCED,
        potential_earning="₹10000-50000/month",
        category="Technology",
        steps=[
            "Learn app development (Flutter/React Native)",
            "Build 2-3 practice apps",
            "Create Fiverr/Upwork profile with portfolio",
            "Start with simple apps (₹5000-10000)",
            "Use free development tools",
            "Deliver projects on time"
        ],
        tips=[
            "Specialize in business apps (inventory, CRM)",
            "Use free APIs for functionality",
            "Offer maintenance packages",
            "Build testimonials from initial clients"
        ],
        resources=[
            "Flutter docs: Official documentation",
            "Free courses: YouTube, Udemy free previews",
            "Tools: VS Code, Android Studio free"
        ]
    )
]

# ─────────────────────────────────────────────
# 4. CORE FUNCTIONS
# ─────────────────────────────────────────────

def get_zero_investment_opportunities(
    user_profile: UserProfile,
    max_results: int = 10
) -> List[EarningOpportunity]:
    """
    Get personalized earning opportunities based on user profile.

    Args:
        user_profile: User's profile information
        max_results: Maximum number of opportunities to return

    Returns:
        List of suitable earning opportunities
    """
    try:
        # Filter by investment level (focus on zero/low)
        suitable = [
            opp for opp in EARNING_DATABASE
            if opp.investment in [InvestmentLevel.ZERO, InvestmentLevel.LOW]
        ]

        # Filter by skill match
        user_skills_lower = [s.lower() for s in user_profile.skills]
        skill_matched = []

        for opp in suitable:
            # Check if opportunity matches user's skills or is beginner-friendly
            if opp.skill_required == SkillLevel.BEGINNER:
                skill_matched.append(opp)
            elif any(skill in opp.title.lower() or skill in opp.description.lower()
                    for skill in user_skills_lower):
                skill_matched.append(opp)

        # If no skill matches, include beginner opportunities
        if not skill_matched:
            skill_matched = [opp for opp in suitable if opp.skill_required == SkillLevel.BEGINNER]

        # Sort by time to start (immediate first), then trending
        skill_matched.sort(key=lambda x: (
            x.time_to_start != TimeToStart.IMMEDIATE,
            not x.trending
        ))

        return skill_matched[:max_results]

    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        return []

def create_earning_plan(
    user_profile: UserProfile,
    selected_opportunities: List[EarningOpportunity],
    months: int = 3
) -> Dict[str, Any]:
    """
    Create a personalized earning plan.

    Args:
        user_profile: User's profile
        selected_opportunities: Opportunities user wants to pursue
        months: Planning period in months

    Returns:
        Plan dictionary with timeline and milestones
    """
    try:
        plan = {
            "timeline": [],
            "total_investment": 0,
            "expected_monthly_income": 0,
            "milestones": [],
            "resources_needed": []
        }

        current_month = 1
        cumulative_investment = 0
        cumulative_income = 0

        for opp in selected_opportunities:
            # Calculate investment
            if opp.investment == InvestmentLevel.LOW:
                cumulative_investment += 300  # Average low investment
            elif opp.investment == InvestmentLevel.MEDIUM:
                cumulative_investment += 1000

            # Estimate income based on potential
            min_income, max_income = _parse_earning_range(opp.potential_earning)
            avg_income = (min_income + max_income) / 2
            cumulative_income += avg_income

            # Create timeline entry
            timeline_entry = {
                "month": current_month,
                "opportunity": opp.title,
                "action": f"Start {opp.title}",
                "investment": cumulative_investment,
                "expected_income": avg_income,
                "steps": opp.steps[:3]  # First 3 steps
            }
            plan["timeline"].append(timeline_entry)

            # Add milestones
            plan["milestones"].append({
                "description": f"Complete first {opp.title} project",
                "month": current_month + 1,
                "reward": f"₹{avg_income * 0.5:.0f} first earnings"
            })

            current_month += 1
            if current_month > months:
                break

        plan["total_investment"] = cumulative_investment
        plan["expected_monthly_income"] = cumulative_income / len(selected_opportunities)

        # Collect all resources
        all_resources = set()
        for opp in selected_opportunities:
            all_resources.update(opp.resources)
        plan["resources_needed"] = list(all_resources)

        return plan

    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        return {}

def get_skill_building_path(
    current_skills: List[str],
    target_opportunity: EarningOpportunity
) -> List[Dict[str, Any]]:
    """
    Get skill building steps to prepare for an opportunity.

    Args:
        current_skills: User's current skills
        target_opportunity: Target earning opportunity

    Returns:
        List of skill building steps
    """
    try:
        steps = []

        # Basic digital literacy if needed
        if not any(s.lower() in ['computer', 'internet', 'smartphone'] for s in current_skills):
            steps.append({
                "skill": "Basic Digital Literacy",
                "duration": "1 week",
                "resources": ["YouTube: Digital Literacy tutorials", "Free online courses"],
                "cost": "₹0"
            })

        # Opportunity-specific skills
        if target_opportunity.skill_required == SkillLevel.BEGINNER:
            steps.append({
                "skill": f"Basic {target_opportunity.category} Skills",
                "duration": "2 weeks",
                "resources": target_opportunity.resources,
                "cost": "₹0-500"
            })
        elif target_opportunity.skill_required == SkillLevel.INTERMEDIATE:
            steps.append({
                "skill": f"Intermediate {target_opportunity.category} Skills",
                "duration": "4 weeks",
                "resources": target_opportunity.resources,
                "cost": "₹500-1000"
            })

        return steps

    except Exception as e:
        logger.error(f"Error getting skill path: {e}")
        return []

# ─────────────────────────────────────────────
# 5. HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _parse_earning_range(earning_str: str) -> tuple[int, int]:
    """Parse earning range string like '₹1000-5000/month'"""
    try:
        # Extract numbers
        import re
        numbers = re.findall(r'\d+', earning_str)
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            val = int(numbers[0])
            return val, val * 2  # Estimate upper bound
        else:
            return 1000, 5000  # Default
    except:
        return 1000, 5000

def get_opportunity_by_title(title: str) -> Optional[EarningOpportunity]:
    """Get opportunity by title"""
    for opp in EARNING_DATABASE:
        if opp.title == title:
            return opp
    return None

def filter_by_investment_level(level: InvestmentLevel) -> List[EarningOpportunity]:
    """Filter opportunities by investment level"""
    return [opp for opp in EARNING_DATABASE if opp.investment == level]

def filter_by_category(category: str) -> List[EarningOpportunity]:
    """Filter opportunities by category"""
    return [opp for opp in EARNING_DATABASE if opp.category.lower() == category.lower()]

# ─────────────────────────────────────────────
# 6. MAIN INTERFACE FUNCTION
# ─────────────────────────────────────────────

def handle_zero_investment_path(
    user_input: str,
    user_profile: Optional[UserProfile] = None
) -> Dict[str, Any]:
    """
    Main handler for zero investment earning path.

    Args:
        user_input: User's message or query
        user_profile: User's profile (optional)

    Returns:
        Response dictionary with opportunities, plan, etc.
    """
    try:
        # Default profile if not provided
        if not user_profile:
            user_profile = UserProfile(
                age=18,
                skills=["basic computer skills"],
                has_smartphone=True,
                has_internet=True
            )

        # Get suitable opportunities
        opportunities = get_zero_investment_opportunities(user_profile)

        # Create basic plan
        plan = create_earning_plan(user_profile, opportunities[:3])

        response = {
            "opportunities": [
                {
                    "title": opp.title,
                    "description": opp.description,
                    "platform": opp.platform,
                    "investment": opp.investment.value,
                    "time_to_start": opp.time_to_start.value,
                    "potential_earning": opp.potential_earning,
                    "category": opp.category,
                    "trending": opp.trending
                }
                for opp in opportunities
            ],
            "plan": plan,
            "message": (
                "Here are some earning opportunities that require little to no investment. "
                "Start with what matches your skills and interests!"
            )
        }

        return response

    except Exception as e:
        logger.error(f"Error handling zero investment path: {e}")
        return {
            "error": "Unable to generate earning suggestions right now.",
            "message": "Please try again later."
        }