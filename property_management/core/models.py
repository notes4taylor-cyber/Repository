"""
Data models for PropertyFlow.

These models represent all the core entities in property management:
properties, tenants, owners, vendors, maintenance requests, and leases.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4


class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    TOWNHOUSE = "townhouse"
    CONDO = "condo"
    APARTMENT = "apartment"
    MULTI_FAMILY = "multi_family"


class PropertyStatus(Enum):
    OCCUPIED = "occupied"
    VACANT = "vacant"
    MAINTENANCE = "maintenance"
    PENDING_MOVE_IN = "pending_move_in"
    PENDING_MOVE_OUT = "pending_move_out"


class TenantStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    PAST = "past"
    EVICTION = "eviction"


class LeaseStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    RENEWED = "renewed"
    TERMINATED = "terminated"


class RentStatus(Enum):
    CURRENT = "current"
    DUE = "due"
    LATE = "late"
    GRACE_PERIOD = "grace_period"
    SEVERELY_LATE = "severely_late"
    COLLECTIONS = "collections"


class MaintenanceStatus(Enum):
    NEW = "new"
    TRIAGED = "triaged"
    VENDOR_ASSIGNED = "vendor_assigned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    COMPLETED = "completed"
    CLOSED = "closed"


class MaintenancePriority(Enum):
    EMERGENCY = "emergency"  # Water leak, no heat, security issue
    URGENT = "urgent"  # AC out in summer, appliance failure
    NORMAL = "normal"  # Standard repairs
    LOW = "low"  # Cosmetic issues


class MaintenanceCategory(Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    APPLIANCE = "appliance"
    STRUCTURAL = "structural"
    EXTERIOR = "exterior"
    PEST_CONTROL = "pest_control"
    CLEANING = "cleaning"
    LANDSCAPING = "landscaping"
    OTHER = "other"


class VendorSpecialty(Enum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    HVAC_TECH = "hvac_tech"
    GENERAL_CONTRACTOR = "general_contractor"
    HANDYMAN = "handyman"
    APPLIANCE_REPAIR = "appliance_repair"
    PEST_CONTROL = "pest_control"
    CLEANING = "cleaning"
    LANDSCAPING = "landscaping"
    LOCKSMITH = "locksmith"
    ROOFER = "roofer"


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())[:8]


@dataclass
class Address:
    """Physical address."""
    street: str
    city: str
    state: str
    zip_code: str
    unit: Optional[str] = None

    def __str__(self) -> str:
        unit_str = f" Unit {self.unit}" if self.unit else ""
        return f"{self.street}{unit_str}, {self.city}, {self.state} {self.zip_code}"


@dataclass
class ContactInfo:
    """Contact information for a person or entity."""
    email: str
    phone: str
    preferred_contact: str = "email"  # "email", "phone", "sms"
    secondary_phone: Optional[str] = None


@dataclass
class Owner:
    """Property owner."""
    id: str = field(default_factory=generate_id)
    name: str = ""
    contact: ContactInfo = None
    address: Optional[Address] = None
    property_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""

    # Reporting preferences
    report_frequency: str = "monthly"  # "weekly", "monthly", "quarterly"
    report_format: str = "pdf"  # "pdf", "email", "both"
    include_photos: bool = True


@dataclass
class Vendor:
    """Service vendor/contractor."""
    id: str = field(default_factory=generate_id)
    company_name: str = ""
    contact_name: str = ""
    contact: ContactInfo = None
    specialties: List[VendorSpecialty] = field(default_factory=list)
    service_areas: List[str] = field(default_factory=list)  # ZIP codes
    hourly_rate: Optional[float] = None
    is_preferred: bool = False
    is_available: bool = True
    rating: float = 5.0  # 1-5 scale
    completed_jobs: int = 0
    notes: str = ""
    license_number: Optional[str] = None
    insurance_expiry: Optional[date] = None

    def matches_category(self, category: MaintenanceCategory) -> bool:
        """Check if vendor can handle a maintenance category."""
        category_to_specialty = {
            MaintenanceCategory.PLUMBING: VendorSpecialty.PLUMBER,
            MaintenanceCategory.ELECTRICAL: VendorSpecialty.ELECTRICIAN,
            MaintenanceCategory.HVAC: VendorSpecialty.HVAC_TECH,
            MaintenanceCategory.APPLIANCE: VendorSpecialty.APPLIANCE_REPAIR,
            MaintenanceCategory.PEST_CONTROL: VendorSpecialty.PEST_CONTROL,
            MaintenanceCategory.CLEANING: VendorSpecialty.CLEANING,
            MaintenanceCategory.LANDSCAPING: VendorSpecialty.LANDSCAPING,
        }

        required_specialty = category_to_specialty.get(category)
        if required_specialty:
            return required_specialty in self.specialties

        # General contractor or handyman can handle most things
        return (VendorSpecialty.GENERAL_CONTRACTOR in self.specialties or
                VendorSpecialty.HANDYMAN in self.specialties)


@dataclass
class Tenant:
    """Tenant/renter."""
    id: str = field(default_factory=generate_id)
    name: str = ""
    contact: ContactInfo = None
    lease_id: Optional[str] = None
    property_id: Optional[str] = None
    status: TenantStatus = TenantStatus.PENDING
    move_in_date: Optional[date] = None
    move_out_date: Optional[date] = None

    # Emergency contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    # Rent tracking
    rent_status: RentStatus = RentStatus.CURRENT
    last_payment_date: Optional[date] = None
    late_payment_count: int = 0

    # Communication tracking
    last_contact_date: Optional[datetime] = None
    communication_log: List[Dict[str, Any]] = field(default_factory=list)

    notes: str = ""

    def log_communication(self, comm_type: str, subject: str, details: str = ""):
        """Log a communication with the tenant."""
        self.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": comm_type,
            "subject": subject,
            "details": details,
        })
        self.last_contact_date = datetime.now()


@dataclass
class Lease:
    """Lease agreement."""
    id: str = field(default_factory=generate_id)
    property_id: str = ""
    tenant_id: str = ""
    owner_id: str = ""

    start_date: date = None
    end_date: date = None
    status: LeaseStatus = LeaseStatus.PENDING

    # Financial terms
    monthly_rent: float = 0.0
    security_deposit: float = 0.0
    pet_deposit: float = 0.0
    rent_due_day: int = 1  # Day of month rent is due
    grace_period_days: int = 5
    late_fee: float = 0.0
    late_fee_type: str = "flat"  # "flat" or "percentage"

    # Renewal tracking
    renewal_offered: bool = False
    renewal_offer_date: Optional[date] = None
    renewal_response: Optional[str] = None  # "accepted", "declined", "pending"
    renewal_response_date: Optional[date] = None

    # Move-in/out
    move_in_inspection_date: Optional[date] = None
    move_in_inspection_completed: bool = False
    move_out_inspection_date: Optional[date] = None
    move_out_inspection_completed: bool = False

    documents: List[str] = field(default_factory=list)  # Document paths/IDs
    notes: str = ""

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until lease expires."""
        if not self.end_date:
            return -1
        return (self.end_date - date.today()).days

    @property
    def is_month_to_month(self) -> bool:
        """Check if lease has converted to month-to-month."""
        return self.status == LeaseStatus.EXPIRED and self.days_until_expiry < 0


@dataclass
class Property:
    """Rental property."""
    id: str = field(default_factory=generate_id)
    address: Address = None
    owner_id: str = ""
    property_type: PropertyType = PropertyType.SINGLE_FAMILY
    status: PropertyStatus = PropertyStatus.VACANT

    # Property details
    bedrooms: int = 0
    bathrooms: float = 0.0
    square_feet: int = 0
    year_built: Optional[int] = None

    # Current occupancy
    current_tenant_id: Optional[str] = None
    current_lease_id: Optional[str] = None

    # Financial
    market_rent: float = 0.0
    management_fee_percent: float = 8.0  # Default 8%

    # Maintenance
    maintenance_request_ids: List[str] = field(default_factory=list)
    last_inspection_date: Optional[date] = None

    # Marketing (for vacant units)
    is_listed: bool = False
    listing_date: Optional[date] = None
    listing_description: str = ""
    showing_instructions: str = ""

    photos: List[str] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def monthly_management_fee(self) -> float:
        """Calculate monthly management fee."""
        return self.market_rent * (self.management_fee_percent / 100)


@dataclass
class MaintenanceRequest:
    """Maintenance/repair request."""
    id: str = field(default_factory=generate_id)
    property_id: str = ""
    tenant_id: Optional[str] = None
    owner_id: str = ""

    # Request details
    title: str = ""
    description: str = ""
    category: MaintenanceCategory = MaintenanceCategory.OTHER
    priority: MaintenancePriority = MaintenancePriority.NORMAL
    status: MaintenanceStatus = MaintenanceStatus.NEW

    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

    # Vendor assignment
    vendor_id: Optional[str] = None
    vendor_notes: str = ""

    # Cost tracking
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    owner_approved: bool = False
    owner_approval_date: Optional[datetime] = None

    # Access
    tenant_permission_to_enter: bool = False
    access_instructions: str = ""

    # Communication log
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)

    def update_status(self, new_status: MaintenanceStatus, notes: str = ""):
        """Update status and log the change."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        self.status_history.append({
            "timestamp": datetime.now().isoformat(),
            "from_status": old_status.value,
            "to_status": new_status.value,
            "notes": notes,
        })


@dataclass
class RentPayment:
    """Rent payment record."""
    id: str = field(default_factory=generate_id)
    lease_id: str = ""
    tenant_id: str = ""
    property_id: str = ""

    amount: float = 0.0
    payment_date: date = None
    due_date: date = None
    payment_method: str = ""  # "check", "ach", "credit_card", "cash"

    late_fee_applied: float = 0.0
    is_partial: bool = False
    notes: str = ""


@dataclass
class Expense:
    """Property expense record."""
    id: str = field(default_factory=generate_id)
    property_id: str = ""
    owner_id: str = ""

    description: str = ""
    category: str = ""  # "maintenance", "utilities", "insurance", "taxes", "management", "other"
    amount: float = 0.0
    date: date = None
    vendor_id: Optional[str] = None
    maintenance_request_id: Optional[str] = None

    receipt_path: Optional[str] = None
    notes: str = ""


@dataclass
class OwnerStatement:
    """Monthly owner statement."""
    id: str = field(default_factory=generate_id)
    owner_id: str = ""
    property_id: str = ""

    statement_period_start: date = None
    statement_period_end: date = None
    generated_at: datetime = field(default_factory=datetime.now)

    # Income
    rent_collected: float = 0.0
    late_fees_collected: float = 0.0
    other_income: float = 0.0

    # Expenses
    maintenance_expenses: float = 0.0
    management_fee: float = 0.0
    other_expenses: float = 0.0

    # Net
    @property
    def total_income(self) -> float:
        return self.rent_collected + self.late_fees_collected + self.other_income

    @property
    def total_expenses(self) -> float:
        return self.maintenance_expenses + self.management_fee + self.other_expenses

    @property
    def net_income(self) -> float:
        return self.total_income - self.total_expenses

    # Details
    payment_records: List[str] = field(default_factory=list)  # RentPayment IDs
    expense_records: List[str] = field(default_factory=list)  # Expense IDs
    maintenance_summary: List[Dict[str, Any]] = field(default_factory=list)

    notes: str = ""
    sent_to_owner: bool = False
    sent_date: Optional[datetime] = None
