"""
PropertyFlow - Property Management Automation System

A lightweight, powerful automation layer for property management companies.
Automates tenant follow-ups, maintenance coordination, lease renewals,
move-in processes, and owner reporting.

Built for NoVA property managers who need efficiency without bloat.
"""

__version__ = "1.0.0"
__author__ = "PropertyFlow"

from .core.engine import AutomationEngine
from .core.models import Property, Tenant, Owner, Vendor, MaintenanceRequest, Lease
from .workflows import (
    LateRentWorkflow,
    MaintenanceWorkflow,
    LeaseRenewalWorkflow,
    MoveInWorkflow,
    OwnerReportingWorkflow,
)

__all__ = [
    "AutomationEngine",
    "Property",
    "Tenant",
    "Owner",
    "Vendor",
    "MaintenanceRequest",
    "Lease",
    "LateRentWorkflow",
    "MaintenanceWorkflow",
    "LeaseRenewalWorkflow",
    "MoveInWorkflow",
    "OwnerReportingWorkflow",
]
