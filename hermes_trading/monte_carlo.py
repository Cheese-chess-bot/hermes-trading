import numpy as np

def generate_gbm_path(current_price, mu=0.0001, sigma=0.02, steps=100):
    """
    Generates a price path using Geometric Brownian Motion (GBM).
    Used to stress-test the model against simulated future price variations.
    """
    path = [current_price]
    for _ in range(steps):
        # GBM formula: S_t = S_{t-1} * exp((mu - 0.5 * sigma^2) + sigma * W_t)
        drift = (mu - 0.5 * sigma**2)
        diffusion = sigma * np.random.normal()
        path.append(path[-1] * np.exp(drift + diffusion))
    return path
