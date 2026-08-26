/**
 * Football Match Prediction Engine
 * Analyzes head-to-head, form, and betting patterns
 */

class PredictionEngine {
  constructor() {
    this.MIN_CONFIDENCE = 0.65;
    this.WEIGHTS = {
      h2h: 0.30,
      form: 0.25,
      homeAdvantage: 0.15,
      odds: 0.20,
      recent: 0.10
    };
  }

  /**
   * Main prediction function
   */
  predict(match) {
    const h2h = this.analyzeH2H(match);
    const form = this.analyzeForm(match);
    const home = this.homeAdvantageBonus(match);
    const odds = this.analyzeOdds(match);
    const recent = this.recentMomentum(match);

    const score =
      h2h * this.WEIGHTS.h2h +
      form * this.WEIGHTS.form +
      home * this.WEIGHTS.homeAdvantage +
      odds * this.WEIGHTS.odds +
      recent * this.WEIGHTS.recent;

    return {
      confidence: Math.round(score * 100),
      prediction: this.getPrediction(score),
      details: { h2h, form, home, odds, recent },
      shouldShow: score >= this.MIN_CONFIDENCE
    };
  }

  /**
   * Analyze head-to-head history
   */
  analyzeH2H(match) {
    const h2h = match.head_to_head || {};
    const total = h2h.total_matches || 0;

    if (total < 2) return 0.5; // Not enough data

    const homeWinRate = h2h.home_win_rate || 0;
    const awayWinRate = h2h.away_win_rate || 0;
    const drawRate = 1 - homeWinRate - awayWinRate;

    // Home team advantage in h2h
    if (homeWinRate > 0.5) return 0.7;
    if (awayWinRate > 0.45) return 0.3;
    if (drawRate > 0.3) return 0.5;

    return 0.5;
  }

  /**
   * Analyze recent form (last 10 matches)
   */
  analyzeForm(match) {
    const h2h = match.head_to_head || {};
    const recent = h2h.recent_matches || [];

    if (recent.length < 3) return 0.5;

    let homeWins = 0;
    let awayWins = 0;

    recent.slice(0, 5).forEach(m => {
      if (m.home_team_id === match.home_team_id && m.home_score > m.away_score) homeWins++;
      if (m.away_team_id === match.home_team_id && m.away_score > m.home_score) homeWins++;
      
      if (m.home_team_id === match.away_team_id && m.home_score > m.away_score) awayWins++;
      if (m.away_team_id === match.away_team_id && m.away_score > m.home_score) awayWins++;
    });

    if (homeWins > awayWins) return 0.65;
    if (awayWins > homeWins) return 0.35;
    return 0.5;
  }

  /**
   * Home advantage bonus
   */
  homeAdvantageBonus(match) {
    // Standard home advantage: ~55% win rate
    let score = 0.55;

    // Adjust based on venue
    if (match.is_local_derby) score += 0.05; // Derby boost
    if (match.is_neutral_ground) score -= 0.10; // Neutral field

    return Math.min(Math.max(score, 0.3), 0.7);
  }

  /**
   * Analyze betting odds (if available)
   */
  analyzeOdds(match) {
    // Default: home slight favorite
    return 0.55;
  }

  /**
   * Recent momentum (last 1-2 matches)
   */
  recentMomentum(match) {
    const h2h = match.head_to_head || {};
    const recent = h2h.recent_matches || [];

    if (recent.length === 0) return 0.5;

    const lastMatch = recent[0];
    const avgGoals = h2h.avg_total_goals || 2.5;

    // Over/Under analysis
    const matchGoals = (lastMatch.home_score || 0) + (lastMatch.away_score || 0);

    if (matchGoals > avgGoals + 1) return 0.55; // High scoring tendency
    if (matchGoals < avgGoals - 1) return 0.45; // Low scoring

    return 0.5;
  }

  /**
   * Determine prediction outcome
   */
  getPrediction(score) {
    if (score >= 0.65) return "HOME";
    if (score <= 0.35) return "AWAY";
    return "DRAW";
  }

  /**
   * Get prediction reasoning
   */
  getReason(prediction, details) {
    const reasons = [];

    if (details.h2h > 0.6) reasons.push("Home team dominate H2H");
    if (details.h2h < 0.4) reasons.push("Away team strong H2H record");

    if (details.form > 0.6) reasons.push("Home team in good form");
    if (details.form < 0.4) reasons.push("Away team on winning streak");

    if (details.home > 0.6) reasons.push("Strong home advantage");

    if (reasons.length === 0) reasons.push("Closely matched teams");

    return reasons;
  }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PredictionEngine;
}
