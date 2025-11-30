
# Scoring Weights
DEFAULT_SMART_BALANCE_WEIGHTS = {
    "urgency": 0.4,
    "importance": 0.3,
    "effort": 0.2,
    "dependencies": 0.1,
}

# Priority Thresholds
PRIORITY_THRESHOLDS = {
    "HIGH": 8.0,
    "MEDIUM": 5.0,
}

# Defaults
DEFAULT_IMPORTANCE = 5
DEFAULT_EFFORT_SCORE_FOR_MISSING = 5  # Medium effort if unknown
MAX_IMPORTANCE = 10
MAX_EFFORT_HOURS = 100 # Cap for normalization
