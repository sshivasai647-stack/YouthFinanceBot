# Graph Report - youth_finance_bot  (2026-05-09)

## Corpus Check
- 67 files · ~54,163 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 546 nodes · 1031 edges · 38 communities detected
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.67)
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
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]

## God Nodes (most connected - your core abstractions)
1. `LLMError` - 42 edges
2. `get_db()` - 38 edges
3. `Debt` - 31 edges
4. `to_jsonable()` - 28 edges
5. `GoalOptimizer` - 27 edges
6. `CrisisLevel` - 27 edges
7. `DebtType` - 26 edges
8. `ChatRouter` - 20 edges
9. `gather_route_modules()` - 19 edges
10. `_user_oid()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `analyze_spending()` --calls--> `spending_analyse()`  [INFERRED]
  analyzer.py → backend\routes\citizen.py
- `get_saving_tip()` --calls--> `spending_analyse()`  [INFERRED]
  analyzer.py → backend\routes\citizen.py
- `assess_betting_behavior()` --calls--> `betting_assess()`  [INFERRED]
  betting_alternative.py → backend\routes\citizen.py
- `assess_betting_behavior()` --calls--> `gather_route_modules()`  [INFERRED]
  betting_alternative.py → backend\services\chat_router.py
- `chat_router.py ============== Central router for the Youth Financial Guardian` --uses--> `LLMError`  [INFERRED]
  chat_router.py → llm_engine.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (64): get_db(), Return request-scoped MongoDB database connection.      The connection is memo, _admin_oid(), analytics_ai_usage(), analytics_export(), analytics_modules(), analytics_trends(), assign_counsellor() (+56 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (43): Exception, sync_process_message(), ChatMessage, ChatRouter, create_router(), chat_router.py ============== Central router for the Youth Financial Guardian, Classification of response type for UI rendering., Single message in conversation history. (+35 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (42): BettingSchema, ChatSchema, DebtAnalyseSchema, DebtEmiSchema, EmergencyFundSchema, GoalCreateSchema, GoalOptimizeSchema, goals_optimize() (+34 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (40): BettingPage(), DashboardHome(), DebtPage(), GoalsPage(), ProfilePage(), SpendingPage(), crisisColor(), formatCurrency() (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (35): debt_emi(), _build_system_addon(), _debts_from_payload(), _detection_payload(), gather_route_modules(), _goal_focused(), _map_debt_type(), path_to_route() (+27 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (37): Enum, AlertLevel, Debt alert severity levels, assess_legal_situation(), get_legal_protection_info(), LegalIssueType, LegalProtectorResult, _match_keywords() (+29 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (25): assess_investment_readiness(), calculate_investment_growth(), _clamp(), _confidence_from_score(), create_investment_plan(), detect_investment_scams(), get_government_schemes(), _goal_to_horizon() (+17 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (23): alerts_for_assigned_users(), _latest_user_chat_text(), Citizens assigned to this counsellor with score > threshold., Return (score, detail) using Section 6.3 weights:        crisis CRITICAL / Imme, score_citizen(), _synthetic_trap_history(), assess_betting_behavior(), BettingAlternativeResult (+15 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (18): create_app(), Create and configure the Flask app instance., Create and configure the Flask app instance., Create and configure the Flask app instance., Create and configure the Flask app instance., Config, DevelopmentConfig, ProductionConfig (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.18
Nodes (18): assess_mental_health(), _format_helplines(), get_crisis_level_from_string(), handle_followup(), _match(), MentalHealthResult, _overwhelmed_response(), mental_health_guardian.py ========================= Mental Health & Crisis Sup (+10 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (16): detect_situation(), DetectionResult, _get_clarification_question(), _get_onboarding_question(), _get_routing_message(), _match_keywords(), situation_detector.py ===================== Entry point router for Youth Finan, Analyse user's free-text input and route to the correct path.      Priority or (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (14): calculate_financial_features(), calculate_risk_score(), get_trend(), load_model(), predict_future_with_ci(), Save trained model to disk., Load trained model from disk., Predict future savings with 95% confidence intervals.     Uses matrix leverage (+6 more)

### Community 12 - "Community 12"
Cohesion: 0.3
Nodes (11): analyze_statement(), _build_recommendations(), _categorize_description(), _detect_direction(), _normalize_text(), _parse_amount(), parse_statement_lines(), statement_analyzer.py ====================== Bank statement analyzer for Youth F (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.38
Nodes (9): add_note(), citizen_detail(), counsellor_alerts(), _counsellor_oid(), list_citizens(), NoteSchema, patch_status(), StatusSchema (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.25
Nodes (8): calculate_emergency_fund(), get_building_plan(), get_emergency_tip(), _months_to_save(), Returns actionable tip based on current savings rate (0-100 scale)., Calculates minimum and recommended emergency fund targets.     Standard rule: 3, Returns months needed or 'N/A' if monthly contribution is zero., Creates 3 realistic speed-based plans to build emergency fund.      Args:

### Community 15 - "Community 15"
Cohesion: 0.38
Nodes (5): guest_chat(), guest_clear_session(), GuestChatSchema, Clear guest chat from the server session cookie., _utc_now()

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (4): get_relevant_schemes(), match_scheme(), Returns top N ranked eligible schemes for a user profile.      Args:, Evaluates a user against scheme eligibility rules.      Returns:         0.0

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (2): Restrict a view to users whose JWT ``role`` claim is in ``allowed_roles``., role_required()

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (2): init_collections_and_indexes(), Create required collections and indexes.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Clear guest chat from the server session cookie.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Verify registration OTP and activate account.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Authenticate user and issue access + refresh cookies.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Issue a new access token using a valid refresh token cookie.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Generate a reset token and send password reset email.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Reset password using a valid reset token.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Create required collections and indexes.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Local development settings.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Strips any character Helvetica/latin-1 cannot encode.     Handles ₹, emoji, Dev

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Generates a complete PDF financial report.     Returns PDF as bytes for Streaml

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Return Indian government-supported scheme suggestions.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Detect possible investment scam red flags.      Fix #2: Regex catches ANY guar

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Run all test scenarios

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Analyse user's free-text input and route to the correct path.      Priority or

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Return list of keywords found in text.

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Return hit count and matched keywords for a keyword bank.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Return a single clarifying question when confidence is low.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): First question shown to a brand-new user.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Streamlit-friendly wrapper. Returns a plain dict for easy st.session_state use.

## Knowledge Gaps
- **128 isolated node(s):** `Analyzes user spending and returns complete financial summary.      Args:`, `Returns personalized saving tip based on savings rate (0-100 scale).`, `betting_alternative.py ====================== Gambling / betting alternative mod`, `Preserves all legacy financial triggers with no softening.`, `Multi-signal crisis assessment: financial, keyword, and behavioral.     Default` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 17`** (3 nodes): `role_required.py`, `Restrict a view to users whose JWT ``role`` claim is in ``allowed_roles``.`, `role_required()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (3 nodes): `init_mongo.py`, `init_collections_and_indexes()`, `Create required collections and indexes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Clear guest chat from the server session cookie.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Verify registration OTP and activate account.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Authenticate user and issue access + refresh cookies.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Issue a new access token using a valid refresh token cookie.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Generate a reset token and send password reset email.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Reset password using a valid reset token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Create required collections and indexes.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Local development settings.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Strips any character Helvetica/latin-1 cannot encode.     Handles ₹, emoji, Dev`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Generates a complete PDF financial report.     Returns PDF as bytes for Streaml`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Return Indian government-supported scheme suggestions.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Detect possible investment scam red flags.      Fix #2: Regex catches ANY guar`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Run all test scenarios`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Analyse user's free-text input and route to the correct path.      Priority or`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Return list of keywords found in text.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Return hit count and matched keywords for a keyword bank.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Return a single clarifying question when confidence is low.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `First question shown to a brand-new user.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Streamlit-friendly wrapper. Returns a plain dict for easy st.session_state use.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_db()` connect `Community 0` to `Community 8`, `Community 3`, `Community 13`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `run_chat_pipeline()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 9`, `Community 10`, `Community 15`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `to_jsonable()` connect `Community 0` to `Community 2`, `Community 4`, `Community 5`, `Community 13`, `Community 15`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LLMError` (e.g. with `ResponseType` and `ChatMessage`) actually correct?**
  _`LLMError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `get_db()` (e.g. with `platform_stats()` and `list_users()`) actually correct?**
  _`get_db()` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `Debt` (e.g. with `InvestmentPlanSchema` and `InvestmentGrowthSchema`) actually correct?**
  _`Debt` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `to_jsonable()` (e.g. with `list_users()` and `audit_logs_list()`) actually correct?**
  _`to_jsonable()` has 26 INFERRED edges - model-reasoned connections that need verification._