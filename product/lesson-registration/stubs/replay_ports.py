"""Stateless exact-input fixture providers for contract/composition tests only."""
from copy import deepcopy
from contracts.interfaces import Providers, PortFailure


class ReplayProviders:
    def __init__(self, platform_fixture: dict):
        self._cases = deepcopy(platform_fixture["cases"])
        self.calls = []

    def _call(self, key, value):
        self.calls.append(key)
        row = self._cases[key]
        if value != row["input"]:
            raise PortFailure({"code": "INVALID_REQUEST", "message": "Synthetic replay input mismatch"})
        return deepcopy(row["output"])

    def resolve(self, selector):
        return self._call("I1", selector)

    def get_profile(self, profile_ref):
        profile = self._cases["I1"]["output"]["profile"]
        if profile_ref != profile["ref"]:
            raise PortFailure({"code": "PROFILE_CHANGED", "message": "Synthetic profile pin mismatch"})
        return deepcopy(profile)

    def prepare(self, request):
        key = "I2-missing" if request == self._cases["I2-missing"]["input"] else "I2"
        return self._call(key, request)

    def authenticate(self, request):
        return self._call("I3", request)

    def execute(self, request):
        # Does NOT simulate admission, external effect or worker lease.
        return self._call("I4", request)

    def evaluate(self, request):
        key = "I5-unknown" if request == self._cases["I5-unknown"]["input"] else "I5"
        return self._call(key, request)

    def bind(self):
        return Providers(self, self, self, self)
