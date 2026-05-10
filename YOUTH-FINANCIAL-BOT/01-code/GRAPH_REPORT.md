# Graph Report - youth_finance_bot  (2026-04-29)

## Corpus Check
- 19 files · ~21,277 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 186 nodes · 255 edges · 12 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]

## God Nodes (most connected - your core abstractions)
1. `GoalOptimizer` - 10 edges
2. `recommend_investments()` - 10 edges
3. `main()` - 9 edges
4. `detect_situation()` - 9 edges
5. `main()` - 8 edges
6. `assess_mental_health()` - 8 edges
7. `detect_crisis()` - 7 edges
8. `Debt` - 6 edges
9. `assess_investment_readiness()` - 6 edges
10. `calculate_investment_growth()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `generate_report()` --calls--> `get_saving_tip()`  [INFERRED]
  pdf_report.py → analyzer.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (23): Enum, AlertLevel, calculate_debt_burden(), create_repayment_plan(), Debt, DebtType, detect_debt_trap(), get_legal_protection_info() (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.16
Nodes (23): assess_investment_readiness(), calculate_investment_growth(), _clamp(), _confidence_from_score(), detect_investment_scams(), get_government_schemes(), _goal_to_horizon(), _is_number() (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (14): check_progress(), create_goal(), enhanced_goal_tracker(), GoalOptimizer, _is_unfunded(), Inflation-aware goal optimization engine.      Formulas used:     - Inflation, Single source of truth for 'goal cannot be funded' check., Iterative timeline calculation with inflation-adjusted target.         Capped a (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (18): assess_mental_health(), _format_helplines(), get_crisis_level_from_string(), handle_followup(), _match(), MentalHealthResult, _overwhelmed_response(), mental_health_guardian.py ========================= Mental Health & Crisis Sup (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (16): detect_situation(), DetectionResult, _get_clarification_question(), _get_onboarding_question(), _get_routing_message(), _match_keywords(), situation_detector.py ===================== Entry point router for Youth Finan, Analyse user's free-text input and route to the correct path.      Priority or (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.2
Nodes (12): Exception, BaseLLMClient, build_messages_with_history(), generate_with_retry(), get_advice(), get_llm_client(), get_quick_tip(), GroqClient (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (14): calculate_financial_features(), calculate_risk_score(), get_trend(), load_model(), predict_future_with_ci(), Save trained model to disk., Load trained model from disk., Predict future savings with 95% confidence intervals.     Uses matrix leverage (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.18
Nodes (10): FPDF, analyze_spending(), get_saving_tip(), Analyzes user spending and returns complete financial summary.      Args:, Returns personalized saving tip based on savings rate (0-100 scale)., FinancialReport, generate_report(), Strips any character Helvetica/latin-1 cannot encode.     Handles ₹, emoji, Dev (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.44
Nodes (8): detect_crisis(), _evaluate_behavioral(), _evaluate_financial(), _merge_level(), _normalize_text(), Preserves all legacy financial triggers with no softening., Multi-signal crisis assessment: financial, keyword, and behavioral.     Default, _scan_keywords()

### Community 9 - "Community 9"
Cohesion: 0.25
Nodes (8): calculate_emergency_fund(), get_building_plan(), get_emergency_tip(), _months_to_save(), Returns actionable tip based on current savings rate (0-100 scale)., Calculates minimum and recommended emergency fund targets.     Standard rule: 3, Returns months needed or 'N/A' if monthly contribution is zero., Creates 3 realistic speed-based plans to build emergency fund.      Args:

### Community 10 - "Community 10"
Cohesion: 0.5
Nodes (4): get_relevant_schemes(), match_scheme(), Returns top N ranked eligible schemes for a user profile.      Args:, Evaluates a user against scheme eligibility rules.      Returns:         0.0

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (2): Suggests earning ideas based on age and skills.      Args:         age    : U, suggest_earning()

## Knowledge Gaps
- **65 isolated node(s):** `Analyzes user spending and returns complete financial summary.      Args:`, `Returns personalized saving tip based on savings rate (0-100 scale).`, `Preserves all legacy financial triggers with no softening.`, `Multi-signal crisis assessment: financial, keyword, and behavioral.     Default`, `debt_handler.py - Financial Debt Management Module for Indian Households  This` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (3 nodes): `earn_suggester.py`, `Suggests earning ideas based on age and skills.      Args:         age    : U`, `suggest_earning()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Analyzes user spending and returns complete financial summary.      Args:`, `Returns personalized saving tip based on savings rate (0-100 scale).`, `Preserves all legacy financial triggers with no softening.` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._
- **Should `Community 6` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._