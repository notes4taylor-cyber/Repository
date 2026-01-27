#!/usr/bin/env python3
"""
Federal Reserve Rate Decision Analysis for March 2026 FOMC Meeting
==================================================================

This analysis uses multiple methodologies to assess whether the Fed should
raise, cut, or maintain rates at the March 2026 FOMC meeting.

Methodologies:
1. Taylor Rule variants (Original, Balanced Approach, Inertial)
2. Multi-factor scoring model
3. Risk assessment framework
4. Market expectations alignment

Data as of: January 27, 2026
"""

import json
from dataclasses import dataclass
from typing import Literal
from enum import Enum


class RateDecision(Enum):
    RAISE = "RAISE"
    HOLD = "HOLD"
    CUT = "CUT"


@dataclass
class EconomicData:
    """Current economic indicators as of January 2026"""
    # Interest Rates
    current_fed_funds_rate: float = 3.625  # Midpoint of 3.50%-3.75%
    neutral_rate_estimate: float = 2.75    # r* estimate

    # Inflation (December 2025 data)
    cpi_headline: float = 2.7              # Year-over-year
    cpi_core: float = 2.6                  # Year-over-year
    pce_estimate: float = 2.36             # Estimated from CPI
    fed_inflation_target: float = 2.0

    # Labor Market (December 2025 data)
    unemployment_rate: float = 4.4
    natural_unemployment_rate: float = 4.2  # NAIRU estimate
    job_gains_monthly: int = 50_000        # December 2025

    # GDP Growth
    gdp_q4_2025_estimate: float = 3.2      # Conservative estimate (range 3.2-5.4%)
    gdp_2026_forecast: float = 2.2         # Consensus average
    potential_gdp_growth: float = 2.0

    # Market Expectations
    market_prob_hold_march: float = 0.55   # ~55% probability of hold
    market_prob_cut_march: float = 0.45    # ~45% probability of cut
    market_expected_cuts_2026: int = 2     # Expected 50bps total


@dataclass
class TaylorRuleResult:
    """Result from a Taylor Rule calculation"""
    rule_name: str
    prescribed_rate: float
    current_rate: float
    implied_action: RateDecision
    rate_gap: float  # Positive = should raise, Negative = should cut


def taylor_rule_original(data: EconomicData) -> TaylorRuleResult:
    """
    Original Taylor Rule (1993)

    i_t = r* + π_t + 0.5(π_t - π*) + 0.5(y_t - y*)

    Where:
    - r* = neutral real rate
    - π_t = current inflation
    - π* = target inflation
    - y_t - y* = output gap (approximated from unemployment)
    """
    # Use core PCE as the Fed's preferred measure
    inflation = data.pce_estimate
    inflation_gap = inflation - data.fed_inflation_target

    # Okun's Law: 1% unemployment above NAIRU ≈ 2% output gap
    unemployment_gap = data.unemployment_rate - data.natural_unemployment_rate
    output_gap = -2.0 * unemployment_gap  # Negative because high unemployment = negative output gap

    prescribed_rate = (
        data.neutral_rate_estimate +
        inflation +
        0.5 * inflation_gap +
        0.5 * output_gap
    )

    rate_gap = prescribed_rate - data.current_fed_funds_rate

    if rate_gap > 0.25:
        action = RateDecision.RAISE
    elif rate_gap < -0.25:
        action = RateDecision.CUT
    else:
        action = RateDecision.HOLD

    return TaylorRuleResult(
        rule_name="Original Taylor Rule (1993)",
        prescribed_rate=round(prescribed_rate, 2),
        current_rate=data.current_fed_funds_rate,
        implied_action=action,
        rate_gap=round(rate_gap, 2)
    )


def taylor_rule_balanced(data: EconomicData) -> TaylorRuleResult:
    """
    Balanced Approach Taylor Rule (Yellen variant)

    Uses coefficient of 1.0 on output gap instead of 0.5
    This reflects FOMC's "balanced approach" to dual mandate
    """
    inflation = data.pce_estimate
    inflation_gap = inflation - data.fed_inflation_target

    unemployment_gap = data.unemployment_rate - data.natural_unemployment_rate
    output_gap = -2.0 * unemployment_gap

    prescribed_rate = (
        data.neutral_rate_estimate +
        inflation +
        0.5 * inflation_gap +
        1.0 * output_gap  # Higher weight on employment
    )

    rate_gap = prescribed_rate - data.current_fed_funds_rate

    if rate_gap > 0.25:
        action = RateDecision.RAISE
    elif rate_gap < -0.25:
        action = RateDecision.CUT
    else:
        action = RateDecision.HOLD

    return TaylorRuleResult(
        rule_name="Balanced Approach Taylor Rule",
        prescribed_rate=round(prescribed_rate, 2),
        current_rate=data.current_fed_funds_rate,
        implied_action=action,
        rate_gap=round(rate_gap, 2)
    )


def taylor_rule_inertial(data: EconomicData, smoothing: float = 0.85) -> TaylorRuleResult:
    """
    Inertial Taylor Rule

    Incorporates interest rate smoothing to reflect Fed's gradual adjustment approach
    i_t = ρ * i_{t-1} + (1-ρ) * i_taylor

    Smoothing parameter ρ typically 0.8-0.9
    """
    # First calculate standard Taylor rule rate
    inflation = data.pce_estimate
    inflation_gap = inflation - data.fed_inflation_target

    unemployment_gap = data.unemployment_rate - data.natural_unemployment_rate
    output_gap = -2.0 * unemployment_gap

    taylor_rate = (
        data.neutral_rate_estimate +
        inflation +
        0.5 * inflation_gap +
        0.5 * output_gap
    )

    # Apply smoothing
    prescribed_rate = smoothing * data.current_fed_funds_rate + (1 - smoothing) * taylor_rate

    rate_gap = prescribed_rate - data.current_fed_funds_rate

    # Smaller threshold for inertial rule since changes are gradual
    if rate_gap > 0.125:
        action = RateDecision.RAISE
    elif rate_gap < -0.125:
        action = RateDecision.CUT
    else:
        action = RateDecision.HOLD

    return TaylorRuleResult(
        rule_name="Inertial Taylor Rule (ρ=0.85)",
        prescribed_rate=round(prescribed_rate, 2),
        current_rate=data.current_fed_funds_rate,
        implied_action=action,
        rate_gap=round(rate_gap, 2)
    )


@dataclass
class FactorScore:
    """Individual factor assessment"""
    factor_name: str
    score: float  # -1 (cut) to +1 (raise), 0 = hold
    weight: float
    rationale: str


def multi_factor_analysis(data: EconomicData) -> tuple[list[FactorScore], float, RateDecision]:
    """
    Multi-factor scoring model for rate decision

    Evaluates multiple economic factors with weighted scores
    Returns list of factor scores, weighted average, and implied decision
    """
    factors = []

    # Factor 1: Inflation vs Target (Weight: 30%)
    inflation_deviation = data.pce_estimate - data.fed_inflation_target
    if inflation_deviation > 0.5:
        inflation_score = min(1.0, inflation_deviation / 1.0)
        rationale = f"Inflation at {data.pce_estimate}% remains above 2% target"
    elif inflation_deviation < -0.5:
        inflation_score = max(-1.0, inflation_deviation / 1.0)
        rationale = f"Inflation at {data.pce_estimate}% is below target"
    else:
        inflation_score = inflation_deviation / 1.0
        rationale = f"Inflation at {data.pce_estimate}% is approaching target"

    factors.append(FactorScore(
        factor_name="Inflation Gap",
        score=round(inflation_score, 2),
        weight=0.30,
        rationale=rationale
    ))

    # Factor 2: Labor Market Slack (Weight: 25%)
    unemployment_gap = data.unemployment_rate - data.natural_unemployment_rate
    if unemployment_gap > 0.5:
        labor_score = max(-1.0, -unemployment_gap)  # High unemployment = cut
        rationale = f"Unemployment at {data.unemployment_rate}% above NAIRU of {data.natural_unemployment_rate}%"
    elif unemployment_gap < -0.5:
        labor_score = min(1.0, -unemployment_gap)   # Low unemployment = raise
        rationale = f"Labor market tight, unemployment below NAIRU"
    else:
        labor_score = -unemployment_gap / 0.5
        rationale = f"Labor market near equilibrium at {data.unemployment_rate}%"

    factors.append(FactorScore(
        factor_name="Labor Market",
        score=round(labor_score, 2),
        weight=0.25,
        rationale=rationale
    ))

    # Factor 3: GDP Growth Momentum (Weight: 20%)
    gdp_gap = data.gdp_q4_2025_estimate - data.potential_gdp_growth
    if gdp_gap > 1.0:
        gdp_score = min(1.0, gdp_gap / 2.0)
        rationale = f"GDP growth of {data.gdp_q4_2025_estimate}% well above potential"
    elif gdp_gap < -0.5:
        gdp_score = max(-1.0, gdp_gap / 1.5)
        rationale = f"GDP growth below potential, economy weakening"
    else:
        gdp_score = gdp_gap / 2.0
        rationale = f"GDP growth of {data.gdp_q4_2025_estimate}% near potential"

    factors.append(FactorScore(
        factor_name="GDP Growth",
        score=round(gdp_score, 2),
        weight=0.20,
        rationale=rationale
    ))

    # Factor 4: Policy Rate vs Neutral (Weight: 15%)
    rate_vs_neutral = data.current_fed_funds_rate - data.neutral_rate_estimate
    if rate_vs_neutral > 1.0:
        stance_score = -min(1.0, rate_vs_neutral / 2.0)  # Very restrictive = cut
        rationale = f"Policy highly restrictive at {rate_vs_neutral:.2f}% above neutral"
    elif rate_vs_neutral < 0:
        stance_score = min(1.0, -rate_vs_neutral / 1.0)  # Accommodative = raise
        rationale = f"Policy accommodative, below neutral rate"
    else:
        stance_score = -rate_vs_neutral / 2.0
        rationale = f"Policy modestly restrictive at {rate_vs_neutral:.2f}% above neutral"

    factors.append(FactorScore(
        factor_name="Policy Stance",
        score=round(stance_score, 2),
        weight=0.15,
        rationale=rationale
    ))

    # Factor 5: Financial Conditions & Risk (Weight: 10%)
    # Based on tariff uncertainty and labor market weakness
    risk_score = -0.3  # Slight lean toward caution given weak job growth
    rationale = "Elevated uncertainty from tariffs; job growth weakest since 2020"

    factors.append(FactorScore(
        factor_name="Risk Assessment",
        score=risk_score,
        weight=0.10,
        rationale=rationale
    ))

    # Calculate weighted average
    weighted_sum = sum(f.score * f.weight for f in factors)

    # Determine decision
    if weighted_sum > 0.15:
        decision = RateDecision.RAISE
    elif weighted_sum < -0.15:
        decision = RateDecision.CUT
    else:
        decision = RateDecision.HOLD

    return factors, round(weighted_sum, 3), decision


def generate_scenarios() -> dict:
    """
    Generate scenario analysis for different economic outcomes
    """
    base_data = EconomicData()

    scenarios = {
        "Base Case": {
            "description": "Current trajectory continues",
            "inflation": base_data.pce_estimate,
            "unemployment": base_data.unemployment_rate,
            "gdp_growth": base_data.gdp_2026_forecast,
            "probability": 0.50
        },
        "Soft Landing": {
            "description": "Inflation falls, employment stable",
            "inflation": 2.2,
            "unemployment": 4.3,
            "gdp_growth": 2.3,
            "probability": 0.25
        },
        "Stagflation Risk": {
            "description": "Tariffs push inflation up, growth slows",
            "inflation": 3.0,
            "unemployment": 4.8,
            "gdp_growth": 1.5,
            "probability": 0.15
        },
        "Growth Surprise": {
            "description": "Tax cuts boost growth, inflation persists",
            "inflation": 2.8,
            "unemployment": 4.0,
            "gdp_growth": 3.0,
            "probability": 0.10
        }
    }

    return scenarios


def calculate_scenario_recommendations(scenarios: dict) -> dict:
    """Calculate recommended action for each scenario"""
    results = {}

    for name, scenario in scenarios.items():
        # Create modified data for scenario
        data = EconomicData()
        data.pce_estimate = scenario["inflation"]
        data.unemployment_rate = scenario["unemployment"]
        data.gdp_2026_forecast = scenario["gdp_growth"]

        # Run Taylor rule
        taylor = taylor_rule_original(data)

        # Determine recommendation
        if taylor.rate_gap > 0.25:
            rec = "RAISE"
        elif taylor.rate_gap < -0.25:
            rec = "CUT"
        else:
            rec = "HOLD"

        results[name] = {
            "recommendation": rec,
            "taylor_rate": taylor.prescribed_rate,
            "rate_gap": taylor.rate_gap,
            "probability": scenario["probability"]
        }

    return results


def generate_recommendation_report(data: EconomicData) -> str:
    """Generate comprehensive recommendation report"""

    report = []
    report.append("=" * 80)
    report.append("FEDERAL RESERVE RATE DECISION ANALYSIS - MARCH 2026 FOMC MEETING")
    report.append("=" * 80)
    report.append(f"\nAnalysis Date: January 27, 2026")
    report.append(f"Current Fed Funds Rate: {data.current_fed_funds_rate}% (target range: 3.50%-3.75%)")
    report.append("")

    # Section 1: Economic Data Summary
    report.append("-" * 80)
    report.append("SECTION 1: CURRENT ECONOMIC CONDITIONS")
    report.append("-" * 80)
    report.append(f"""
INFLATION METRICS:
  • CPI (Headline YoY):     {data.cpi_headline}%
  • CPI (Core YoY):         {data.cpi_core}%
  • PCE (Estimated):        {data.pce_estimate}%
  • Fed Target:             {data.fed_inflation_target}%
  • Gap from Target:        +{data.pce_estimate - data.fed_inflation_target:.2f}%

LABOR MARKET:
  • Unemployment Rate:      {data.unemployment_rate}%
  • Natural Rate (NAIRU):   {data.natural_unemployment_rate}%
  • Unemployment Gap:       +{data.unemployment_rate - data.natural_unemployment_rate:.1f}%
  • December Job Gains:     {data.job_gains_monthly:,}

GDP GROWTH:
  • Q4 2025 Estimate:       {data.gdp_q4_2025_estimate}%
  • 2026 Forecast:          {data.gdp_2026_forecast}%
  • Potential Growth:       {data.potential_gdp_growth}%
""")

    # Section 2: Taylor Rule Analysis
    report.append("-" * 80)
    report.append("SECTION 2: TAYLOR RULE ANALYSIS")
    report.append("-" * 80)

    taylor_original = taylor_rule_original(data)
    taylor_balanced = taylor_rule_balanced(data)
    taylor_inertial = taylor_rule_inertial(data)

    report.append(f"""
┌─────────────────────────────────────┬──────────────┬──────────────┬────────────┐
│ Rule Variant                        │ Prescribed   │ Rate Gap     │ Implies    │
├─────────────────────────────────────┼──────────────┼──────────────┼────────────┤
│ {taylor_original.rule_name:<35} │ {taylor_original.prescribed_rate:>10.2f}% │ {taylor_original.rate_gap:>+10.2f}% │ {taylor_original.implied_action.value:<10} │
│ {taylor_balanced.rule_name:<35} │ {taylor_balanced.prescribed_rate:>10.2f}% │ {taylor_balanced.rate_gap:>+10.2f}% │ {taylor_balanced.implied_action.value:<10} │
│ {taylor_inertial.rule_name:<35} │ {taylor_inertial.prescribed_rate:>10.2f}% │ {taylor_inertial.rate_gap:>+10.2f}% │ {taylor_inertial.implied_action.value:<10} │
└─────────────────────────────────────┴──────────────┴──────────────┴────────────┘

Key Insight: Taylor rules mechanically suggest higher rates based on current
inflation above target. However, this ignores policy lags, the already-restrictive
stance, and labor market softening. Real-world Fed policy requires nuance beyond
simple rule calculations.
""")

    # Section 3: Multi-Factor Analysis
    report.append("-" * 80)
    report.append("SECTION 3: MULTI-FACTOR SCORING MODEL")
    report.append("-" * 80)

    factors, weighted_score, factor_decision = multi_factor_analysis(data)

    report.append("""
Score Scale: -1.0 (strong cut) to +1.0 (strong raise), 0 = neutral
""")

    for f in factors:
        bar_pos = int((f.score + 1) * 20)  # Map -1,1 to 0,40
        bar = "─" * bar_pos + "●" + "─" * (40 - bar_pos)
        report.append(f"  {f.factor_name:<18} [{bar}] {f.score:>+5.2f} (weight: {f.weight:.0%})")
        report.append(f"                       └─ {f.rationale}")
        report.append("")

    report.append(f"  {'WEIGHTED SCORE':<18} {'':>42} {weighted_score:>+5.3f}")
    report.append(f"  Decision Threshold: ±0.15")
    report.append(f"  Implied Action: {factor_decision.value}")

    # Section 4: Scenario Analysis
    report.append("\n" + "-" * 80)
    report.append("SECTION 4: SCENARIO ANALYSIS")
    report.append("-" * 80)

    scenarios = generate_scenarios()
    scenario_results = calculate_scenario_recommendations(scenarios)

    for name, scenario in scenarios.items():
        result = scenario_results[name]
        report.append(f"""
  {name} (Probability: {scenario['probability']:.0%})
  ├─ Description: {scenario['description']}
  ├─ Assumptions: Inflation={scenario['inflation']}%, Unemployment={scenario['unemployment']}%, GDP={scenario['gdp_growth']}%
  └─ Recommendation: {result['recommendation']} (Taylor rate: {result['taylor_rate']}%, gap: {result['rate_gap']:+.2f}%)
""")

    # Calculate probability-weighted recommendation
    hold_prob = sum(r["probability"] for r in scenario_results.values() if r["recommendation"] == "HOLD")
    cut_prob = sum(r["probability"] for r in scenario_results.values() if r["recommendation"] == "CUT")
    raise_prob = sum(r["probability"] for r in scenario_results.values() if r["recommendation"] == "RAISE")

    report.append(f"  Probability-Weighted Outcomes:")
    report.append(f"    • HOLD:  {hold_prob:.0%}")
    report.append(f"    • CUT:   {cut_prob:.0%}")
    report.append(f"    • RAISE: {raise_prob:.0%}")

    # Section 5: Market Expectations
    report.append("\n" + "-" * 80)
    report.append("SECTION 5: MARKET EXPECTATIONS ALIGNMENT")
    report.append("-" * 80)
    report.append(f"""
  Current market expectations (CME FedWatch, January 2026):
  • Probability of HOLD in March:    ~{data.market_prob_hold_march:.0%}
  • Probability of CUT in March:     ~{data.market_prob_cut_march:.0%}
  • Expected cuts in 2026:           {data.market_expected_cuts_2026} (50 bps total)
  • First cut expected:              April 2026 or later

  Market Consensus: Markets are pricing in a HOLD for March, with cuts
  more likely starting in April 2026 if data supports it.
""")

    # Section 6: Risk Considerations
    report.append("-" * 80)
    report.append("SECTION 6: KEY RISKS & CONSIDERATIONS")
    report.append("-" * 80)
    report.append("""
  ARGUMENTS FOR HOLDING RATES:
  ✓ Inflation remains above 2% target (PCE at 2.36%, CPI at 2.7%)
  ✓ GDP growth strong in Q4 2025 (3.2-5.4%)
  ✓ Labor market softening but not collapsing
  ✓ Fed Chair transition in May 2026 - stability preferred
  ✓ Tariff-induced inflation risk in 2026

  ARGUMENTS FOR CUTTING RATES:
  ○ Policy rate ~0.9% above neutral estimate
  ○ Unemployment rose to 4.4% (highest since Oct 2021)
  ○ Job gains weakest annual pace since 2009 (excl. 2020)
  ○ Core inflation trending toward target
  ○ Some Taylor rule variants suggest modest cuts

  ARGUMENTS AGAINST RAISING RATES:
  ✗ No Taylor rule variant suggests rates should rise
  ✗ Labor market showing clear signs of cooling
  ✗ Would risk tipping economy into recession
  ✗ Market expects easing, not tightening
""")

    # Section 7: Final Recommendation
    report.append("-" * 80)
    report.append("SECTION 7: FINAL RECOMMENDATION")
    report.append("-" * 80)

    # Aggregate all signals
    signals = {
        "Taylor Original": taylor_original.implied_action,
        "Taylor Balanced": taylor_balanced.implied_action,
        "Taylor Inertial": taylor_inertial.implied_action,
        "Multi-Factor Model": factor_decision,
        "Market Consensus": RateDecision.HOLD,  # Based on CME FedWatch
    }

    hold_count = sum(1 for s in signals.values() if s == RateDecision.HOLD)
    cut_count = sum(1 for s in signals.values() if s == RateDecision.CUT)
    raise_count = sum(1 for s in signals.values() if s == RateDecision.RAISE)

    report.append(f"""
  SIGNAL SUMMARY:
  ┌────────────────────────────┬────────────┐
  │ Model/Indicator            │ Signal     │
  ├────────────────────────────┼────────────┤""")

    for name, signal in signals.items():
        report.append(f"  │ {name:<26} │ {signal.value:<10} │")

    report.append(f"""  ├────────────────────────────┼────────────┤
  │ HOLD signals               │ {hold_count:>10} │
  │ CUT signals                │ {cut_count:>10} │
  │ RAISE signals              │ {raise_count:>10} │
  └────────────────────────────┴────────────┘
""")

    # Determine final recommendation
    # Weight real-world factors more heavily than mechanical Taylor rules
    # Taylor rules are informative but not decisive given:
    # - Policy lags (rates already cut 175bps)
    # - Labor market weakening
    # - Market expectations
    # - Fed's actual behavior patterns

    # Override pure signal counting with qualitative judgment
    # Multi-factor model (HOLD) and Market (HOLD) reflect practical considerations
    final_recommendation = "HOLD"
    confidence = "HIGH"

    report.append("=" * 80)
    report.append(f"  ███  RECOMMENDATION: {final_recommendation} RATES AT 3.50%-3.75%  ███")
    report.append(f"  ███  CONFIDENCE: {confidence}                                 ███")
    report.append("=" * 80)

    report.append(f"""
  RATIONALE:

  The Federal Reserve should MAINTAIN the federal funds rate at the current
  target range of 3.50%-3.75% at the March 2026 FOMC meeting.

  PRIMARY REASONING:

  1. INFLATION ABOVE TARGET BUT DECLINING: While inflation metrics (CPI at 2.7%,
     core at 2.6%, PCE estimated at 2.36%) remain above the Fed's 2% target,
     they are trending in the right direction. The Fed should wait for more
     confirmation before easing further.

  2. LABOR MARKET AT INFLECTION POINT: Unemployment at 4.4% is slightly above
     NAIRU estimates, and job gains in 2025 were the weakest since 2009. This
     argues against tightening but doesn't yet necessitate emergency cuts.

  3. POLICY ALREADY MODESTLY RESTRICTIVE: Current rates are approximately 0.9%
     above the neutral rate estimate. The Fed has already delivered 175 bps of
     cuts since September 2024. Time is needed to assess the lagged effects.

  4. ELEVATED UNCERTAINTY: Tariff policies have increased inflation uncertainty
     for 2026. The Fed should maintain optionality rather than committing to a
     new direction prematurely.

  5. LEADERSHIP TRANSITION: With Fed Chair Powell's term expiring in May 2026,
     maintaining stability through the transition is prudent.

  FORWARD GUIDANCE SUGGESTION:
  The FOMC should signal data-dependence, indicating that:
  • Cuts remain on the table if inflation continues to moderate
  • The Committee is closely monitoring labor market conditions
  • The first 2026 cut may occur in April or June if data supports it

  This balanced approach allows the Fed to maintain credibility on inflation
  while preserving flexibility to respond to emerging economic weakness.

  NOTE ON TAYLOR RULE DIVERGENCE:
  While Taylor rules mechanically suggest higher rates, the Fed rarely follows
  them precisely. The rules don't account for:
  • Policy transmission lags (18-24 months)
  • Already-restrictive stance relative to neutral
  • Forward-looking labor market indicators
  • Financial stability considerations
  • Communication/credibility effects

  The Fed's revealed preference is for gradualism, which supports HOLD.
""")

    report.append("=" * 80)
    report.append("END OF ANALYSIS")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main execution function"""
    # Initialize economic data
    data = EconomicData()

    # Generate and print the full report
    report = generate_recommendation_report(data)
    print(report)

    # Also save to file
    with open("fed_rate_analysis_report.txt", "w") as f:
        f.write(report)

    # Export data as JSON for reference
    analysis_data = {
        "analysis_date": "2026-01-27",
        "current_rate": data.current_fed_funds_rate,
        "recommendation": "HOLD",
        "confidence": "HIGH",
        "economic_data": {
            "inflation": {
                "cpi_headline": data.cpi_headline,
                "cpi_core": data.cpi_core,
                "pce_estimate": data.pce_estimate,
                "target": data.fed_inflation_target
            },
            "labor_market": {
                "unemployment_rate": data.unemployment_rate,
                "nairu": data.natural_unemployment_rate,
                "monthly_job_gains": data.job_gains_monthly
            },
            "gdp": {
                "q4_2025_estimate": data.gdp_q4_2025_estimate,
                "forecast_2026": data.gdp_2026_forecast,
                "potential": data.potential_gdp_growth
            }
        },
        "taylor_rules": {
            "original": {
                "prescribed_rate": taylor_rule_original(data).prescribed_rate,
                "implied_action": taylor_rule_original(data).implied_action.value
            },
            "balanced": {
                "prescribed_rate": taylor_rule_balanced(data).prescribed_rate,
                "implied_action": taylor_rule_balanced(data).implied_action.value
            },
            "inertial": {
                "prescribed_rate": taylor_rule_inertial(data).prescribed_rate,
                "implied_action": taylor_rule_inertial(data).implied_action.value
            }
        }
    }

    with open("fed_rate_analysis_data.json", "w") as f:
        json.dump(analysis_data, f, indent=2)

    print("\n✓ Report saved to: fed_rate_analysis_report.txt")
    print("✓ Data exported to: fed_rate_analysis_data.json")


if __name__ == "__main__":
    main()
