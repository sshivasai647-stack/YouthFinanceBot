---
tags: [feature, mental-health, core]
status: complete
---

# Mental Health Guardian

## Purpose
Monitors user's financial stress and provides mental health support recommendations.

## Key Functions
- `assess_mental_health()` - Evaluate stress levels
- `run_mental_health_guardian()` - Main monitoring function
- `get_support_resources()` - Find help resources
- `detress_alert()` - Trigger when stress high

## Connected To
- [[debt-handler]] - Debt triggers mental health checks
- [[investment-guide]] - Investment risk affects stress
- [[crisis-detector]] - Severe cases escalation

## Files
- `mental_health_gaurdian.py` - Main module