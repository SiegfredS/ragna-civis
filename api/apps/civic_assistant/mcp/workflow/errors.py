class CivicAssistantGraphError(RuntimeError):
    """Raised when the bounded assistant workflow cannot continue safely."""


class CivicAssistantMCPToolError(RuntimeError):
    """Raised when MCP evidence cannot be safely retrieved."""


class CivicAssistantModelConfigurationError(RuntimeError):
    """Raised when Civic Assistant model configuration is unavailable."""


class CivicAssistantPromptConfigurationError(RuntimeError):
    """Raised when Civic Assistant prompt configuration is invalid."""
