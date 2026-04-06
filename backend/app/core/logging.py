"""
Structured logging with audit trail support for SouthDrift.

Provides JSON-formatted logs with correlation IDs for end-to-end tracing
and audit-relevant fields for HIPAA compliance.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

from pythonjsonlogger import jsonlogger

# Context var for correlation ID that spans async operations
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class AuditLogger(logging.LoggerAdapter):
    """
    Logger adapter that adds audit-relevant fields to every log entry.

    Fields:
    - correlation_id: Trace a request across services
    - service: Service name (backend, transcribe, etc.)
    - user_id: User performing the action
    - patient_id: Patient record affected
    - action: What action was performed
    """

    def __init__(self, logger: logging.Logger, service: str):
        super().__init__(logger, {"service": service})
        self.service = service

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Add audit fields to every log."""
        extra = kwargs.get("extra", {})

        # Add correlation ID from context
        correlation_id = correlation_id_var.get()
        if correlation_id:
            extra["correlation_id"] = correlation_id

        # Always include service name
        extra["service"] = self.service

        kwargs["extra"] = extra
        return msg, kwargs

    def audit(
        self, action: str, user_id: str | None = None, patient_id: str | None = None, **kwargs: Any
    ) -> None:
        """
        Log an audit event with required compliance fields.

        Usage:
            logger.audit(
                action="patient_record_accessed",
                user_id="user_123",
                patient_id="patient_456",
                method="GET",
                endpoint="/api/v1/patients/456"
            )
        """
        extra = {
            "action": action,
            "audit": True,  # Flag for easy filtering
        }

        if user_id:
            extra["user_id"] = user_id
        if patient_id:
            extra["patient_id"] = patient_id

        extra.update(kwargs)

        self.info(f"AUDIT: {action}", extra=extra)


def setup_structured_logging(service_name: str) -> AuditLogger:
    """
    Configure structured JSON logging for a service.

    Args:
        service_name: Name of the service (backend, transcribe, etc.)

    Returns:
        AuditLogger instance for the service
    """
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    # Configure handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Return audit logger for this service
    return AuditLogger(root_logger, service_name)


def get_correlation_id() -> str:
    """Get or generate a correlation ID for this request context."""
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for this request context."""
    correlation_id_var.set(correlation_id)
