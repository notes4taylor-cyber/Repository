"""
Core Automation Engine for PropertyFlow.

This is the heart of the system - it coordinates all workflows,
manages data, and orchestrates automation across the platform.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Type
import json
import logging
import os

from .events import Event, EventBus, EventScheduler, EventType
from .notifications import NotificationService
from .models import (
    Property, Tenant, Owner, Vendor, Lease, MaintenanceRequest,
    RentPayment, Expense, OwnerStatement,
    PropertyStatus, TenantStatus, LeaseStatus, RentStatus, MaintenanceStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class DataStore:
    """
    In-memory data store for the automation engine.

    In production, this would be replaced with a proper database,
    but this allows the system to run standalone for demos and small shops.
    """
    properties: Dict[str, Property] = field(default_factory=dict)
    tenants: Dict[str, Tenant] = field(default_factory=dict)
    owners: Dict[str, Owner] = field(default_factory=dict)
    vendors: Dict[str, Vendor] = field(default_factory=dict)
    leases: Dict[str, Lease] = field(default_factory=dict)
    maintenance_requests: Dict[str, MaintenanceRequest] = field(default_factory=dict)
    rent_payments: Dict[str, RentPayment] = field(default_factory=dict)
    expenses: Dict[str, Expense] = field(default_factory=dict)
    owner_statements: Dict[str, OwnerStatement] = field(default_factory=dict)

    def save_to_file(self, filepath: str):
        """Save all data to a JSON file."""
        data = {
            "properties": {k: self._to_dict(v) for k, v in self.properties.items()},
            "tenants": {k: self._to_dict(v) for k, v in self.tenants.items()},
            "owners": {k: self._to_dict(v) for k, v in self.owners.items()},
            "vendors": {k: self._to_dict(v) for k, v in self.vendors.items()},
            "leases": {k: self._to_dict(v) for k, v in self.leases.items()},
            "maintenance_requests": {k: self._to_dict(v) for k, v in self.maintenance_requests.items()},
            "rent_payments": {k: self._to_dict(v) for k, v in self.rent_payments.items()},
            "expenses": {k: self._to_dict(v) for k, v in self.expenses.items()},
            "owner_statements": {k: self._to_dict(v) for k, v in self.owner_statements.items()},
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Data saved to {filepath}")

    def _to_dict(self, obj: Any) -> Dict:
        """Convert a dataclass to a dictionary."""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name in obj.__dataclass_fields__:
                value = getattr(obj, field_name)
                if hasattr(value, 'value'):  # Enum
                    result[field_name] = value.value
                elif isinstance(value, (datetime, date)):
                    result[field_name] = value.isoformat()
                elif hasattr(value, '__dataclass_fields__'):
                    result[field_name] = self._to_dict(value)
                else:
                    result[field_name] = value
            return result
        return obj


class AutomationEngine:
    """
    The main automation engine for PropertyFlow.

    Manages all data, workflows, and automation for property management.
    This is the central coordinator that property managers interact with.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the automation engine."""
        self.config = config or {}
        self.data = DataStore()
        self.event_bus = EventBus()
        self.scheduler = EventScheduler(self.event_bus)
        self.notifications = NotificationService(self.config.get("notifications", {}))

        # Track registered workflows
        self._workflows: List[Any] = []

        # Setup logging
        self._setup_logging()

        logger.info("PropertyFlow Automation Engine initialized")

    def _setup_logging(self):
        """Configure logging for the engine."""
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def register_workflow(self, workflow):
        """Register a workflow with the engine."""
        workflow.register(self)
        self._workflows.append(workflow)
        logger.info(f"Registered workflow: {workflow.__class__.__name__}")

    # ===================
    # Property Management
    # ===================

    def add_property(self, property: Property) -> Property:
        """Add a new property to the system."""
        self.data.properties[property.id] = property

        # Link to owner
        if property.owner_id and property.owner_id in self.data.owners:
            owner = self.data.owners[property.owner_id]
            if property.id not in owner.property_ids:
                owner.property_ids.append(property.id)

        logger.info(f"Added property: {property.id} - {property.address}")
        return property

    def get_property(self, property_id: str) -> Optional[Property]:
        """Get a property by ID."""
        return self.data.properties.get(property_id)

    def get_properties_by_owner(self, owner_id: str) -> List[Property]:
        """Get all properties for an owner."""
        return [p for p in self.data.properties.values() if p.owner_id == owner_id]

    def update_property_status(self, property_id: str, status: PropertyStatus):
        """Update a property's status."""
        property = self.get_property(property_id)
        if property:
            old_status = property.status
            property.status = status
            logger.info(f"Property {property_id} status: {old_status.value} -> {status.value}")

            if status == PropertyStatus.VACANT:
                self.event_bus.publish(Event(
                    EventType.PROPERTY_VACANT,
                    {"property_id": property_id, "property": property}
                ))

    # ================
    # Tenant Management
    # ================

    def add_tenant(self, tenant: Tenant) -> Tenant:
        """Add a new tenant to the system."""
        self.data.tenants[tenant.id] = tenant
        logger.info(f"Added tenant: {tenant.id} - {tenant.name}")
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        return self.data.tenants.get(tenant_id)

    def get_tenant_by_property(self, property_id: str) -> Optional[Tenant]:
        """Get the current tenant for a property."""
        for tenant in self.data.tenants.values():
            if tenant.property_id == property_id and tenant.status == TenantStatus.ACTIVE:
                return tenant
        return None

    def update_tenant_rent_status(self, tenant_id: str, status: RentStatus):
        """Update a tenant's rent status and trigger appropriate events."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return

        old_status = tenant.rent_status
        tenant.rent_status = status

        logger.info(f"Tenant {tenant_id} rent status: {old_status.value} -> {status.value}")

        # Trigger appropriate events
        event_map = {
            RentStatus.LATE: EventType.RENT_LATE,
            RentStatus.SEVERELY_LATE: EventType.RENT_SEVERELY_LATE,
            RentStatus.CURRENT: EventType.RENT_PAYMENT_RECEIVED,
        }

        if status in event_map:
            lease = self.get_lease(tenant.lease_id) if tenant.lease_id else None
            property = self.get_property(tenant.property_id) if tenant.property_id else None

            self.event_bus.publish(Event(
                event_map[status],
                {
                    "tenant_id": tenant_id,
                    "tenant": tenant,
                    "lease": lease,
                    "property": property,
                }
            ))

    # ===============
    # Owner Management
    # ===============

    def add_owner(self, owner: Owner) -> Owner:
        """Add a new owner to the system."""
        self.data.owners[owner.id] = owner
        logger.info(f"Added owner: {owner.id} - {owner.name}")
        return owner

    def get_owner(self, owner_id: str) -> Optional[Owner]:
        """Get an owner by ID."""
        return self.data.owners.get(owner_id)

    # ================
    # Vendor Management
    # ================

    def add_vendor(self, vendor: Vendor) -> Vendor:
        """Add a new vendor to the system."""
        self.data.vendors[vendor.id] = vendor
        logger.info(f"Added vendor: {vendor.id} - {vendor.company_name}")
        return vendor

    def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        """Get a vendor by ID."""
        return self.data.vendors.get(vendor_id)

    def find_vendor_for_maintenance(self, request: MaintenanceRequest) -> Optional[Vendor]:
        """Find the best available vendor for a maintenance request."""
        property = self.get_property(request.property_id)
        if not property or not property.address:
            return None

        matching_vendors = []
        for vendor in self.data.vendors.values():
            if not vendor.is_available:
                continue

            # Check if vendor handles this category
            if not vendor.matches_category(request.category):
                continue

            # Check service area (by ZIP code)
            if vendor.service_areas and property.address.zip_code not in vendor.service_areas:
                continue

            matching_vendors.append(vendor)

        if not matching_vendors:
            return None

        # Sort by preference: preferred vendors first, then by rating
        matching_vendors.sort(key=lambda v: (-v.is_preferred, -v.rating))
        return matching_vendors[0]

    # ===============
    # Lease Management
    # ===============

    def add_lease(self, lease: Lease) -> Lease:
        """Add a new lease to the system."""
        self.data.leases[lease.id] = lease

        # Link to property and tenant
        if lease.property_id:
            property = self.get_property(lease.property_id)
            if property:
                property.current_lease_id = lease.id

        if lease.tenant_id:
            tenant = self.get_tenant(lease.tenant_id)
            if tenant:
                tenant.lease_id = lease.id
                tenant.property_id = lease.property_id

        logger.info(f"Added lease: {lease.id}")

        self.event_bus.publish(Event(
            EventType.LEASE_CREATED,
            {"lease_id": lease.id, "lease": lease}
        ))

        return lease

    def get_lease(self, lease_id: str) -> Optional[Lease]:
        """Get a lease by ID."""
        return self.data.leases.get(lease_id)

    def get_active_leases(self) -> List[Lease]:
        """Get all active leases."""
        return [l for l in self.data.leases.values() if l.status == LeaseStatus.ACTIVE]

    def check_lease_expirations(self):
        """Check for upcoming lease expirations and trigger events."""
        today = date.today()

        for lease in self.get_active_leases():
            days_until = lease.days_until_expiry

            event_thresholds = [
                (90, EventType.LEASE_EXPIRING_90_DAYS),
                (60, EventType.LEASE_EXPIRING_60_DAYS),
                (30, EventType.LEASE_EXPIRING_30_DAYS),
            ]

            for threshold, event_type in event_thresholds:
                if days_until == threshold:
                    tenant = self.get_tenant(lease.tenant_id)
                    property = self.get_property(lease.property_id)
                    owner = self.get_owner(lease.owner_id)

                    self.event_bus.publish(Event(
                        event_type,
                        {
                            "lease": lease,
                            "tenant": tenant,
                            "property": property,
                            "owner": owner,
                            "days_until_expiry": days_until,
                        }
                    ))

    # =======================
    # Maintenance Management
    # =======================

    def create_maintenance_request(self, request: MaintenanceRequest) -> MaintenanceRequest:
        """Create a new maintenance request."""
        self.data.maintenance_requests[request.id] = request

        # Link to property
        property = self.get_property(request.property_id)
        if property:
            property.maintenance_request_ids.append(request.id)

        logger.info(f"Created maintenance request: {request.id} - {request.title}")

        # Get related entities for the event
        tenant = self.get_tenant(request.tenant_id) if request.tenant_id else None
        owner = self.get_owner(request.owner_id) if request.owner_id else None

        self.event_bus.publish(Event(
            EventType.MAINTENANCE_REQUEST_CREATED,
            {
                "request": request,
                "property": property,
                "tenant": tenant,
                "owner": owner,
            }
        ))

        return request

    def get_maintenance_request(self, request_id: str) -> Optional[MaintenanceRequest]:
        """Get a maintenance request by ID."""
        return self.data.maintenance_requests.get(request_id)

    def update_maintenance_status(
        self,
        request_id: str,
        status: MaintenanceStatus,
        notes: str = "",
        vendor_id: str = None,
        scheduled_date: datetime = None,
        cost: float = None,
    ):
        """Update a maintenance request's status."""
        request = self.get_maintenance_request(request_id)
        if not request:
            return

        old_status = request.status
        request.update_status(status, notes)

        if vendor_id:
            request.vendor_id = vendor_id

        if scheduled_date:
            request.scheduled_date = scheduled_date

        if cost is not None:
            request.actual_cost = cost

        logger.info(f"Maintenance {request_id} status: {old_status.value} -> {status.value}")

        # Get related entities
        property = self.get_property(request.property_id)
        tenant = self.get_tenant(request.tenant_id) if request.tenant_id else None
        owner = self.get_owner(request.owner_id)
        vendor = self.get_vendor(request.vendor_id) if request.vendor_id else None

        # Map status to event type
        status_event_map = {
            MaintenanceStatus.TRIAGED: EventType.MAINTENANCE_TRIAGED,
            MaintenanceStatus.VENDOR_ASSIGNED: EventType.MAINTENANCE_VENDOR_ASSIGNED,
            MaintenanceStatus.SCHEDULED: EventType.MAINTENANCE_SCHEDULED,
            MaintenanceStatus.IN_PROGRESS: EventType.MAINTENANCE_STARTED,
            MaintenanceStatus.COMPLETED: EventType.MAINTENANCE_COMPLETED,
            MaintenanceStatus.PENDING_APPROVAL: EventType.MAINTENANCE_PENDING_APPROVAL,
            MaintenanceStatus.CLOSED: EventType.MAINTENANCE_CLOSED,
        }

        if status in status_event_map:
            self.event_bus.publish(Event(
                status_event_map[status],
                {
                    "request": request,
                    "property": property,
                    "tenant": tenant,
                    "owner": owner,
                    "vendor": vendor,
                }
            ))

    def get_open_maintenance_requests(self) -> List[MaintenanceRequest]:
        """Get all open maintenance requests."""
        open_statuses = {
            MaintenanceStatus.NEW,
            MaintenanceStatus.TRIAGED,
            MaintenanceStatus.VENDOR_ASSIGNED,
            MaintenanceStatus.SCHEDULED,
            MaintenanceStatus.IN_PROGRESS,
            MaintenanceStatus.PENDING_APPROVAL,
        }
        return [
            r for r in self.data.maintenance_requests.values()
            if r.status in open_statuses
        ]

    # ====================
    # Financial Management
    # ====================

    def record_rent_payment(self, payment: RentPayment) -> RentPayment:
        """Record a rent payment."""
        self.data.rent_payments[payment.id] = payment

        # Update tenant status
        tenant = self.get_tenant(payment.tenant_id)
        if tenant:
            tenant.rent_status = RentStatus.CURRENT
            tenant.last_payment_date = payment.payment_date

        logger.info(f"Recorded payment: {payment.id} - ${payment.amount}")

        lease = self.get_lease(payment.lease_id)
        property = self.get_property(payment.property_id)

        self.event_bus.publish(Event(
            EventType.RENT_PAYMENT_RECEIVED,
            {
                "payment": payment,
                "tenant": tenant,
                "lease": lease,
                "property": property,
            }
        ))

        return payment

    def record_expense(self, expense: Expense) -> Expense:
        """Record a property expense."""
        self.data.expenses[expense.id] = expense
        logger.info(f"Recorded expense: {expense.id} - ${expense.amount} - {expense.description}")
        return expense

    def generate_owner_statement(
        self,
        owner_id: str,
        property_id: str,
        period_start: date,
        period_end: date,
    ) -> OwnerStatement:
        """Generate a monthly owner statement."""
        owner = self.get_owner(owner_id)
        property = self.get_property(property_id)

        if not owner or not property:
            raise ValueError("Owner or property not found")

        statement = OwnerStatement(
            owner_id=owner_id,
            property_id=property_id,
            statement_period_start=period_start,
            statement_period_end=period_end,
        )

        # Calculate income
        for payment in self.data.rent_payments.values():
            if (payment.property_id == property_id and
                period_start <= payment.payment_date <= period_end):
                statement.rent_collected += payment.amount
                statement.late_fees_collected += payment.late_fee_applied
                statement.payment_records.append(payment.id)

        # Calculate expenses
        for expense in self.data.expenses.values():
            if (expense.property_id == property_id and
                period_start <= expense.date <= period_end):
                if expense.category == "maintenance":
                    statement.maintenance_expenses += expense.amount
                elif expense.category == "management":
                    statement.management_fee += expense.amount
                else:
                    statement.other_expenses += expense.amount
                statement.expense_records.append(expense.id)

        # If no management fee was recorded, calculate it
        if statement.management_fee == 0:
            statement.management_fee = statement.rent_collected * (property.management_fee_percent / 100)

        self.data.owner_statements[statement.id] = statement

        logger.info(f"Generated statement {statement.id} for owner {owner_id}, property {property_id}")

        self.event_bus.publish(Event(
            EventType.OWNER_STATEMENT_GENERATED,
            {
                "statement": statement,
                "owner": owner,
                "property": property,
            }
        ))

        return statement

    # ==============
    # Daily Operations
    # ==============

    def run_daily_checks(self):
        """Run all daily automation checks."""
        logger.info("Running daily checks...")

        # Check lease expirations
        self.check_lease_expirations()

        # Check rent due dates
        self._check_rent_status()

        # Check maintenance follow-ups
        self._check_maintenance_status()

        # Fire any scheduled events
        self.scheduler.check_and_fire()

        # Publish daily check event for any additional handlers
        self.event_bus.publish(Event(EventType.DAILY_CHECK, {}))

        logger.info("Daily checks completed")

    def _check_rent_status(self):
        """Check all tenants for rent status updates."""
        today = date.today()

        for lease in self.get_active_leases():
            tenant = self.get_tenant(lease.tenant_id)
            if not tenant or tenant.rent_status == RentStatus.CURRENT:
                continue

            # Calculate days late
            due_date = date(today.year, today.month, lease.rent_due_day)
            if today < due_date:
                continue  # Not due yet

            days_late = (today - due_date).days

            if days_late == 0:
                # Rent just became due
                self.event_bus.publish(Event(
                    EventType.RENT_DUE,
                    {"tenant": tenant, "lease": lease}
                ))
            elif days_late == lease.grace_period_days:
                # Grace period ending
                self.event_bus.publish(Event(
                    EventType.RENT_GRACE_PERIOD_ENDING,
                    {"tenant": tenant, "lease": lease, "days_late": days_late}
                ))
            elif days_late > lease.grace_period_days and tenant.rent_status != RentStatus.LATE:
                # Now officially late
                self.update_tenant_rent_status(tenant.id, RentStatus.LATE)
            elif days_late > 15 and tenant.rent_status != RentStatus.SEVERELY_LATE:
                # Severely late
                self.update_tenant_rent_status(tenant.id, RentStatus.SEVERELY_LATE)

    def _check_maintenance_status(self):
        """Check maintenance requests for follow-up needs."""
        now = datetime.now()

        for request in self.get_open_maintenance_requests():
            # Check if vendor hasn't responded in 24 hours
            if (request.status == MaintenanceStatus.VENDOR_ASSIGNED and
                request.vendor_id):
                hours_since_update = (now - request.updated_at).total_seconds() / 3600
                if hours_since_update > 24:
                    self.event_bus.publish(Event(
                        EventType.VENDOR_NO_RESPONSE,
                        {
                            "request": request,
                            "vendor": self.get_vendor(request.vendor_id),
                        }
                    ))

    # =============
    # Persistence
    # =============

    def save(self, filepath: str = "propertyflow_data.json"):
        """Save all data to file."""
        self.data.save_to_file(filepath)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        return {
            "properties": len(self.data.properties),
            "tenants": len(self.data.tenants),
            "owners": len(self.data.owners),
            "vendors": len(self.data.vendors),
            "active_leases": len(self.get_active_leases()),
            "open_maintenance": len(self.get_open_maintenance_requests()),
            "registered_workflows": len(self._workflows),
        }
