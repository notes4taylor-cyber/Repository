"""
Event system for PropertyFlow.

This module implements an event-driven architecture that powers all
automation workflows. Events follow the pattern:
"When X happens, do Y, tell Z"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All event types in the system."""

    # Rent Events
    RENT_DUE = "rent_due"
    RENT_LATE = "rent_late"
    RENT_GRACE_PERIOD_ENDING = "rent_grace_period_ending"
    RENT_SEVERELY_LATE = "rent_severely_late"
    RENT_PAYMENT_RECEIVED = "rent_payment_received"
    RENT_PARTIAL_PAYMENT = "rent_partial_payment"

    # Maintenance Events
    MAINTENANCE_REQUEST_CREATED = "maintenance_request_created"
    MAINTENANCE_TRIAGED = "maintenance_triaged"
    MAINTENANCE_VENDOR_ASSIGNED = "maintenance_vendor_assigned"
    MAINTENANCE_SCHEDULED = "maintenance_scheduled"
    MAINTENANCE_STARTED = "maintenance_started"
    MAINTENANCE_COMPLETED = "maintenance_completed"
    MAINTENANCE_PENDING_APPROVAL = "maintenance_pending_approval"
    MAINTENANCE_APPROVED = "maintenance_approved"
    MAINTENANCE_CLOSED = "maintenance_closed"
    MAINTENANCE_ESCALATED = "maintenance_escalated"

    # Lease Events
    LEASE_CREATED = "lease_created"
    LEASE_SIGNED = "lease_signed"
    LEASE_EXPIRING_90_DAYS = "lease_expiring_90_days"
    LEASE_EXPIRING_60_DAYS = "lease_expiring_60_days"
    LEASE_EXPIRING_30_DAYS = "lease_expiring_30_days"
    LEASE_RENEWAL_OFFERED = "lease_renewal_offered"
    LEASE_RENEWAL_ACCEPTED = "lease_renewal_accepted"
    LEASE_RENEWAL_DECLINED = "lease_renewal_declined"
    LEASE_RENEWAL_NO_RESPONSE = "lease_renewal_no_response"
    LEASE_EXPIRED = "lease_expired"
    LEASE_TERMINATED = "lease_terminated"

    # Move-in Events
    MOVE_IN_SCHEDULED = "move_in_scheduled"
    MOVE_IN_7_DAYS = "move_in_7_days"
    MOVE_IN_1_DAY = "move_in_1_day"
    MOVE_IN_COMPLETED = "move_in_completed"
    MOVE_IN_INSPECTION_SCHEDULED = "move_in_inspection_scheduled"
    MOVE_IN_INSPECTION_COMPLETED = "move_in_inspection_completed"

    # Move-out Events
    MOVE_OUT_SCHEDULED = "move_out_scheduled"
    MOVE_OUT_30_DAYS = "move_out_30_days"
    MOVE_OUT_COMPLETED = "move_out_completed"
    MOVE_OUT_INSPECTION_SCHEDULED = "move_out_inspection_scheduled"
    MOVE_OUT_INSPECTION_COMPLETED = "move_out_inspection_completed"

    # Property Events
    PROPERTY_LISTED = "property_listed"
    PROPERTY_SHOWING_SCHEDULED = "property_showing_scheduled"
    PROPERTY_APPLICATION_RECEIVED = "property_application_received"
    PROPERTY_VACANT = "property_vacant"
    PROPERTY_INSPECTION_DUE = "property_inspection_due"

    # Owner Events
    OWNER_STATEMENT_GENERATED = "owner_statement_generated"
    OWNER_STATEMENT_SENT = "owner_statement_sent"
    OWNER_PAYMENT_SENT = "owner_payment_sent"

    # Vendor Events
    VENDOR_ASSIGNED = "vendor_assigned"
    VENDOR_NO_RESPONSE = "vendor_no_response"
    VENDOR_JOB_COMPLETED = "vendor_job_completed"

    # System Events
    DAILY_CHECK = "daily_check"
    WEEKLY_CHECK = "weekly_check"
    MONTHLY_CHECK = "monthly_check"


@dataclass
class Event:
    """
    An event in the system.

    Events carry all the context needed for handlers to process them
    without needing to look up additional data.
    """
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    correlation_id: Optional[str] = None  # For tracking related events
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Event({self.event_type.value}, id={self.event_id})"


@dataclass
class EventResult:
    """Result of processing an event."""
    success: bool
    event: Event
    handler_name: str
    message: str = ""
    actions_taken: List[str] = field(default_factory=list)
    follow_up_events: List[Event] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


EventHandler = Callable[[Event], EventResult]


class EventBus:
    """
    Central event bus for the automation system.

    Manages event subscriptions and dispatches events to handlers.
    Supports synchronous processing with full traceability.
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[tuple[str, EventHandler]]] = {}
        self._event_log: List[Event] = []
        self._result_log: List[EventResult] = []
        self._global_handlers: List[tuple[str, EventHandler]] = []

    def subscribe(self, event_type: EventType, handler: EventHandler, name: str = None):
        """Subscribe a handler to an event type."""
        handler_name = name or handler.__name__
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append((handler_name, handler))
        logger.debug(f"Handler '{handler_name}' subscribed to {event_type.value}")

    def subscribe_all(self, handler: EventHandler, name: str = None):
        """Subscribe a handler to ALL events (useful for logging/auditing)."""
        handler_name = name or handler.__name__
        self._global_handlers.append((handler_name, handler))
        logger.debug(f"Global handler '{handler_name}' subscribed to all events")

    def unsubscribe(self, event_type: EventType, handler_name: str):
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                (name, h) for name, h in self._handlers[event_type]
                if name != handler_name
            ]

    def publish(self, event: Event) -> List[EventResult]:
        """
        Publish an event to all subscribed handlers.

        Returns a list of results from all handlers.
        """
        self._event_log.append(event)
        results = []

        logger.info(f"Publishing event: {event}")

        # Run global handlers first
        for handler_name, handler in self._global_handlers:
            try:
                result = handler(event)
                results.append(result)
                self._result_log.append(result)
            except Exception as e:
                error_result = EventResult(
                    success=False,
                    event=event,
                    handler_name=handler_name,
                    errors=[str(e)],
                )
                results.append(error_result)
                self._result_log.append(error_result)
                logger.error(f"Global handler '{handler_name}' failed: {e}")

        # Run specific handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler_name, handler in handlers:
            try:
                result = handler(event)
                results.append(result)
                self._result_log.append(result)

                # Process any follow-up events
                for follow_up in result.follow_up_events:
                    follow_up.correlation_id = event.event_id
                    follow_up_results = self.publish(follow_up)
                    results.extend(follow_up_results)

            except Exception as e:
                error_result = EventResult(
                    success=False,
                    event=event,
                    handler_name=handler_name,
                    errors=[str(e)],
                )
                results.append(error_result)
                self._result_log.append(error_result)
                logger.error(f"Handler '{handler_name}' failed: {e}")

        return results

    def get_event_log(self, limit: int = 100) -> List[Event]:
        """Get recent events."""
        return self._event_log[-limit:]

    def get_results_for_event(self, event_id: str) -> List[EventResult]:
        """Get all results for a specific event."""
        return [r for r in self._result_log if r.event.event_id == event_id]

    def get_handlers_for_event(self, event_type: EventType) -> List[str]:
        """Get names of handlers subscribed to an event type."""
        return [name for name, _ in self._handlers.get(event_type, [])]


class ScheduledEvent:
    """
    Represents an event scheduled to fire at a specific time.
    Used for reminders, follow-ups, and deadline-based triggers.
    """

    def __init__(
        self,
        event: Event,
        scheduled_time: datetime,
        recurrence: Optional[str] = None,  # "daily", "weekly", "monthly"
    ):
        self.event = event
        self.scheduled_time = scheduled_time
        self.recurrence = recurrence
        self.fired = False
        self.last_fired: Optional[datetime] = None

    def should_fire(self, current_time: datetime = None) -> bool:
        """Check if this event should fire now."""
        current_time = current_time or datetime.now()

        if self.recurrence:
            # For recurring events, check if enough time has passed
            if self.last_fired is None:
                return current_time >= self.scheduled_time
            # Simple recurrence check
            return current_time >= self.scheduled_time and not self.fired
        else:
            # One-time event
            return current_time >= self.scheduled_time and not self.fired


class EventScheduler:
    """
    Scheduler for time-based events.

    Manages scheduled events and fires them when their time comes.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._scheduled: List[ScheduledEvent] = []

    def schedule(self, event: Event, scheduled_time: datetime, recurrence: str = None):
        """Schedule an event to fire at a specific time."""
        scheduled = ScheduledEvent(event, scheduled_time, recurrence)
        self._scheduled.append(scheduled)
        logger.info(f"Scheduled event {event.event_type.value} for {scheduled_time}")

    def check_and_fire(self, current_time: datetime = None) -> List[EventResult]:
        """Check all scheduled events and fire any that are due."""
        current_time = current_time or datetime.now()
        results = []

        for scheduled in self._scheduled:
            if scheduled.should_fire(current_time):
                scheduled.fired = True
                scheduled.last_fired = current_time
                event_results = self.event_bus.publish(scheduled.event)
                results.extend(event_results)

        # Clean up non-recurring events that have fired
        self._scheduled = [
            s for s in self._scheduled
            if s.recurrence or not s.fired
        ]

        return results

    def get_pending_events(self) -> List[ScheduledEvent]:
        """Get all pending scheduled events."""
        return [s for s in self._scheduled if not s.fired]

    def cancel_event(self, event_id: str):
        """Cancel a scheduled event by its event ID."""
        self._scheduled = [
            s for s in self._scheduled
            if s.event.event_id != event_id
        ]
