---
tags: [feature, investment, core]
status: in-progress
---

# Investment Guide

## Purpose
Provides investment recommendations based on user's financial situation, risk profile, and goals.

## Key Functions
- `calculate_risk_profile()` - Assess user's risk tolerance
- `suggest_investments()` - Recommend investment options
- `calculate_returns()` - Project potential returns
- `validate_investment()` - Check if investment is suitable

## Known Issues
- Bug in return calculation (currently fixing)
- Risk assessment needs adjustment for young users

## Connected To
- [[debt-handler]] - Uses debt burden to adjust recommendations
- [[goal-tracker]] - Aligns investments with goals
- [[mental-health]] - Considers stress levels

## Files
- `investment_guide.py` - Main logic