from typing import Any, Protocol


class APIResponse(Protocol):
    status_code: int

    def json(self) -> Any: ...

    def __getitem__(self, key: str) -> str: ...

    def has_header(self, header: str) -> bool: ...


class APIClient(Protocol):
    def get(self, path: str, data: Any = None, **extra: Any) -> APIResponse: ...

    def options(self, path: str, data: Any = None, **extra: Any) -> APIResponse: ...

    def post(
        self,
        path: str,
        data: Any = None,
        format: str | None = None,
        content_type: str | None = None,
        **extra: Any,
    ) -> APIResponse: ...
