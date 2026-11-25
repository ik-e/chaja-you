"""Logical port bindings; no product engine, external IO or credential handling.

All payloads are JSON objects validated against the pinned named schema.
These Protocols are a candidate Python binding, not a replacement for JSON.
A synchronous call contract does not require the worker or HTTP handler to
block an event loop: async libraries belong behind each provider bridge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, TypeAlias, Literal, Any

JSONObject: TypeAlias = dict[str, Any]
OpaqueContext: TypeAlias = object
OpaquePermit: TypeAlias = object
TerminalState: TypeAlias = Literal["done", "stopped"]


class PortFailure(Exception):
    """Typed safe Error payload; caller must validate before exposing it."""

    def __init__(self, error: JSONObject):
        super().__init__("Port failure")
        self.error = error


class Registry(Protocol):
    # I1 and pinned lookup (no network or re-resolution).
    def resolve(self, selector: str) -> JSONObject: ...
    def get_profile(self, profile_ref: JSONObject) -> JSONObject: ...


class PreparationPort(Protocol):
    # I2: PrepareInput -> Preparation
    def prepare(self, request: JSONObject) -> JSONObject: ...


class ExecutionPort(Protocol):
    # I3: AuthInput -> AuthOutput (internal; public view separately redacted)
    def authenticate(self, request: JSONObject) -> JSONObject: ...
    # I4: ExecuteInput -> ExecutionReport; accepted worker only
    def execute(self, request: JSONObject) -> JSONObject: ...


class ResultPort(Protocol):
    # I5: EvaluateInput -> Result; pure, no browser or state writes
    def evaluate(self, request: JSONObject) -> JSONObject: ...


class CoordinatorStore(Protocol):
    # S-ACCEPT atomic and idempotent; returns RegistrationView.
    def accept(self, owner: str, registration_id: str, start: JSONObject,
               scope: JSONObject) -> JSONObject: ...
    # S-FENCE; CO owns lifecycle and terminal result.
    def fence(self, registration_id: str, error: JSONObject) -> None: ...
    def finalize(self, registration_id: str, result: JSONObject) -> TerminalState: ...


class GatewayStore(Protocol):
    # S-ADMIT and S-OBSERVE must be durable and atomic at real implementation.
    # OpaquePermit belongs to runtime, never adapter/browser client.
    def admit(self, context: OpaqueContext, operation: JSONObject) -> OpaquePermit: ...
    def record_observation(self, context: OpaqueContext, observation: JSONObject,
                           evidence: list[JSONObject]) -> JSONObject: ...
    def fence(self, registration_id: str, error: JSONObject) -> None: ...


class RuntimeGateway(Protocol):
    # RT-01 authorized by CO; same verified connection and exclusive lease.
    def with_verified_connection(self, accepted: JSONObject) -> OpaqueContext: ...
    def list_operations(self, context: OpaqueContext) -> list[JSONObject]: ...
    def perform(self, context: OpaqueContext, operation: JSONObject) -> JSONObject: ...
    def observe_goal(self, context: OpaqueContext) -> JSONObject: ...


class BoundGateway(Protocol):
    """Adapter only receives an already scoped capability (RT-02/03/04).

    No driver, session token, raw arguments, lease or store is exposed here.
    Actual runtime must enforce registry/permission/lease/fence/admission.
    """
    def list_operations(self) -> list[JSONObject]: ...
    def perform(self, operation: JSONObject) -> JSONObject: ...
    def observe_goal(self) -> JSONObject: ...


class PlatformAdapter(Protocol):
    # Candidate adapter binding: runtime supplies a scoped capability.
    # Exact operation registry and binding manifest are provider decisions.
    def run(self, gateway: BoundGateway) -> JSONObject: ...


@dataclass(frozen=True)
class Providers:
    registry: Registry
    preparation: PreparationPort
    execution: ExecutionPort
    result: ResultPort

    def methods(self) -> Mapping[str, Callable[..., JSONObject]]:
        return {
            "I1": self.registry.resolve,
            "I2": self.preparation.prepare,
            "I3": self.execution.authenticate,
            "I4": self.execution.execute,
            "I5": self.result.evaluate,
        }
