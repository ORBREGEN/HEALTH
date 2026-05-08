class HEALTHError(Exception):
    """Base exception for all HEALTH errors."""


class ModelNotBuiltError(HEALTHError):
    """Raised when the Healthy Respiratory Model has not been built yet."""


class DataNotAvailableError(HEALTHError):
    """Raised when a required .h5ad file is not on disk."""
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Data file not available: {path}")


class InsufficientGenesError(HEALTHError):
    """Raised when a sample has too few genes for reliable analysis."""
    def __init__(self, provided: int, minimum: int):
        super().__init__(f"Need at least {minimum} genes, got {provided}")
