"""Minimal stand-in for pomegranate 0.14.5, used only by ABIDES' OrderSizeModel.

ABIDES pins pomegranate==0.14.5, which does not build on Python 3.11/arm64. ABIDES
uses only ``GeneralMixtureModel.from_json(...).sample(random_state=rs)`` with
LogNormal and Normal components. This shim samples the same mixture (same
weights and parameters) from the caller's RandomState. Draws are deterministic
per agent but not bit-identical to pomegranate's internal sampling order.
"""
import json

import numpy as np


class GeneralMixtureModel:
    def __init__(self, components, weights):
        self.components = components
        self.weights = np.asarray(weights, dtype=float)
        self.weights = self.weights / self.weights.sum()

    @classmethod
    def from_json(cls, s):
        d = json.loads(s)
        comps = [(c["name"], tuple(c["parameters"])) for c in d["distributions"]]
        return cls(comps, d["weights"])

    def sample(self, n=None, random_state=None):
        rs = random_state if random_state is not None else np.random
        k = rs.choice(len(self.weights), p=self.weights)
        name, (a, b) = self.components[k]
        if name == "LogNormalDistribution":
            return float(rs.lognormal(mean=a, sigma=b))
        if name == "NormalDistribution":
            return float(rs.normal(loc=a, scale=b))
        raise NotImplementedError(name)
