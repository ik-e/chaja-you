"""Dependency wiring candidate. No domain workflow, fake approval or execution."""
from contracts.interfaces import Providers
from contracts.validation import SchemaCatalog, CheckedPorts


def bind_ports(schema: dict, profiles: dict, common: dict, *, providers: Providers) -> CheckedPorts:
    """Inject exact providers; no default fake/real fallback. Caller owns lifecycle."""
    return CheckedPorts(SchemaCatalog(schema, profiles), common, providers)
