def compute_score(carbon, cost, delay, weights):
    return (
        weights["carbon"] * carbon +
        weights["cost"]   * cost   +
        weights["delay"]  * delay
    )