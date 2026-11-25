"""r05-remote: remote browser runtime, I3/I4 facade, RT-01..04 gateway, viewer server side (TASK-053).

Mock environment only. Import requires the ``remote`` dependency group (Playwright) at runtime.
"""
from .bindings import Identity, PlatformBinding
from .gateway import BoundGateway, ExecutionGateway
from .page import BrowserScopedPage, NavigationUnknown, PageStructureError, PageView, UploadFile
from .runtime import RemoteRuntime

__all__ = ["BoundGateway", "BrowserScopedPage", "ExecutionGateway", "Identity", "NavigationUnknown",
           "PageStructureError", "PageView", "PlatformBinding", "RemoteRuntime", "UploadFile"]
