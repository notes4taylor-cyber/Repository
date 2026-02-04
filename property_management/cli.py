#!/usr/bin/env python3
"""
PropertyFlow CLI - Command Line Interface for Property Management Automation

Usage:
    python -m property_management.cli [command] [options]

Commands:
    demo        Run a demonstration with sample data
    status      Show system status
    daily       Run daily automation checks
    add-tenant  Add a new tenant (interactive)
    add-request Add a maintenance request (interactive)
    report      Generate owner report
"""

import argparse
import sys
from datetime import date, datetime, timedelta
from typing import Optional

from .core.engine import AutomationEngine
from .core.models import (
    Property, Tenant, Owner, Vendor, Lease, MaintenanceRequest,
    Address, ContactInfo,
    PropertyType, PropertyStatus, TenantStatus, LeaseStatus,
    MaintenanceCategory, MaintenancePriority, MaintenanceStatus,
    VendorSpecialty, RentStatus
)
from .workflows import (
    LateRentWorkflow,
    MaintenanceWorkflow,
    LeaseRenewalWorkflow,
    MoveInWorkflow,
    OwnerReportingWorkflow,
)


def create_sample_data(engine: AutomationEngine):
    """Create sample data for demonstration."""
    print("\n📦 Creating sample data for Loudoun County properties...\n")

    # Create owners
    owner1 = Owner(
        id="owner001",
        name="Michael Thompson",
        contact=ContactInfo(
            email="mthompson@email.com",
            phone="703-555-0101",
        ),
        address=Address(
            street="456 Investor Lane",
            city="Leesburg",
            state="VA",
            zip_code="20176",
        ),
    )
    engine.add_owner(owner1)
    print(f"  ✓ Created owner: {owner1.name}")

    owner2 = Owner(
        id="owner002",
        name="Sarah Williams",
        contact=ContactInfo(
            email="swilliams@email.com",
            phone="703-555-0102",
        ),
    )
    engine.add_owner(owner2)
    print(f"  ✓ Created owner: {owner2.name}")

    # Create properties
    property1 = Property(
        id="prop001",
        address=Address(
            street="123 King Street",
            city="Leesburg",
            state="VA",
            zip_code="20176",
            unit="A",
        ),
        owner_id="owner001",
        property_type=PropertyType.TOWNHOUSE,
        status=PropertyStatus.OCCUPIED,
        bedrooms=3,
        bathrooms=2.5,
        square_feet=1800,
        market_rent=2500.00,
        management_fee_percent=8.0,
    )
    engine.add_property(property1)
    print(f"  ✓ Created property: {property1.address}")

    property2 = Property(
        id="prop002",
        address=Address(
            street="789 Ashburn Village Blvd",
            city="Ashburn",
            state="VA",
            zip_code="20147",
        ),
        owner_id="owner001",
        property_type=PropertyType.SINGLE_FAMILY,
        status=PropertyStatus.OCCUPIED,
        bedrooms=4,
        bathrooms=3.0,
        square_feet=2400,
        market_rent=3200.00,
        management_fee_percent=8.0,
    )
    engine.add_property(property2)
    print(f"  ✓ Created property: {property2.address}")

    property3 = Property(
        id="prop003",
        address=Address(
            street="555 Lansdowne Town Center",
            city="Lansdowne",
            state="VA",
            zip_code="20176",
            unit="302",
        ),
        owner_id="owner002",
        property_type=PropertyType.CONDO,
        status=PropertyStatus.OCCUPIED,
        bedrooms=2,
        bathrooms=2.0,
        square_feet=1200,
        market_rent=2100.00,
        management_fee_percent=10.0,
    )
    engine.add_property(property3)
    print(f"  ✓ Created property: {property3.address}")

    # Create vendors
    vendor1 = Vendor(
        id="vendor001",
        company_name="Loudoun Plumbing Pros",
        contact_name="Bob Smith",
        contact=ContactInfo(
            email="bob@loudounplumbing.com",
            phone="703-555-0201",
        ),
        specialties=[VendorSpecialty.PLUMBER],
        service_areas=["20176", "20147", "20148"],
        hourly_rate=95.00,
        is_preferred=True,
        rating=4.8,
    )
    engine.add_vendor(vendor1)
    print(f"  ✓ Created vendor: {vendor1.company_name}")

    vendor2 = Vendor(
        id="vendor002",
        company_name="NoVA HVAC Solutions",
        contact_name="Maria Garcia",
        contact=ContactInfo(
            email="maria@novahvac.com",
            phone="703-555-0202",
        ),
        specialties=[VendorSpecialty.HVAC_TECH],
        service_areas=["20176", "20147", "20148", "20175"],
        hourly_rate=120.00,
        is_preferred=True,
        rating=4.9,
    )
    engine.add_vendor(vendor2)
    print(f"  ✓ Created vendor: {vendor2.company_name}")

    vendor3 = Vendor(
        id="vendor003",
        company_name="All-Around Handyman Services",
        contact_name="Tom Johnson",
        contact=ContactInfo(
            email="tom@allaroundhandyman.com",
            phone="703-555-0203",
        ),
        specialties=[VendorSpecialty.HANDYMAN, VendorSpecialty.GENERAL_CONTRACTOR],
        service_areas=["20176", "20147", "20148", "20175", "20165"],
        hourly_rate=65.00,
        is_preferred=False,
        rating=4.5,
    )
    engine.add_vendor(vendor3)
    print(f"  ✓ Created vendor: {vendor3.company_name}")

    # Create tenants
    tenant1 = Tenant(
        id="tenant001",
        name="John Davis",
        contact=ContactInfo(
            email="jdavis@email.com",
            phone="703-555-0301",
        ),
        property_id="prop001",
        status=TenantStatus.ACTIVE,
        move_in_date=date(2024, 1, 15),
        rent_status=RentStatus.CURRENT,
    )
    engine.add_tenant(tenant1)
    print(f"  ✓ Created tenant: {tenant1.name}")

    tenant2 = Tenant(
        id="tenant002",
        name="Emily Chen",
        contact=ContactInfo(
            email="echen@email.com",
            phone="703-555-0302",
        ),
        property_id="prop002",
        status=TenantStatus.ACTIVE,
        move_in_date=date(2023, 8, 1),
        rent_status=RentStatus.LATE,  # For demonstration
        late_payment_count=1,
    )
    engine.add_tenant(tenant2)
    print(f"  ✓ Created tenant: {tenant2.name}")

    tenant3 = Tenant(
        id="tenant003",
        name="Robert Martinez",
        contact=ContactInfo(
            email="rmartinez@email.com",
            phone="703-555-0303",
        ),
        property_id="prop003",
        status=TenantStatus.ACTIVE,
        move_in_date=date(2024, 3, 1),
        rent_status=RentStatus.CURRENT,
    )
    engine.add_tenant(tenant3)
    print(f"  ✓ Created tenant: {tenant3.name}")

    # Create leases
    lease1 = Lease(
        id="lease001",
        property_id="prop001",
        tenant_id="tenant001",
        owner_id="owner001",
        start_date=date(2024, 1, 15),
        end_date=date(2025, 1, 14),
        status=LeaseStatus.ACTIVE,
        monthly_rent=2500.00,
        security_deposit=2500.00,
        rent_due_day=1,
        grace_period_days=5,
        late_fee=150.00,
    )
    engine.add_lease(lease1)
    tenant1.lease_id = lease1.id
    property1.current_tenant_id = tenant1.id
    property1.current_lease_id = lease1.id
    print(f"  ✓ Created lease: {lease1.id} for {tenant1.name}")

    # Lease expiring soon (for renewal demo)
    lease2 = Lease(
        id="lease002",
        property_id="prop002",
        tenant_id="tenant002",
        owner_id="owner001",
        start_date=date(2023, 8, 1),
        end_date=date.today() + timedelta(days=55),  # Expires in ~55 days
        status=LeaseStatus.ACTIVE,
        monthly_rent=3200.00,
        security_deposit=3200.00,
        rent_due_day=1,
        grace_period_days=5,
        late_fee=175.00,
    )
    engine.add_lease(lease2)
    tenant2.lease_id = lease2.id
    property2.current_tenant_id = tenant2.id
    property2.current_lease_id = lease2.id
    print(f"  ✓ Created lease: {lease2.id} for {tenant2.name} (expiring in 55 days)")

    lease3 = Lease(
        id="lease003",
        property_id="prop003",
        tenant_id="tenant003",
        owner_id="owner002",
        start_date=date(2024, 3, 1),
        end_date=date(2025, 2, 28),
        status=LeaseStatus.ACTIVE,
        monthly_rent=2100.00,
        security_deposit=2100.00,
        rent_due_day=1,
        grace_period_days=5,
        late_fee=125.00,
    )
    engine.add_lease(lease3)
    tenant3.lease_id = lease3.id
    property3.current_tenant_id = tenant3.id
    property3.current_lease_id = lease3.id
    print(f"  ✓ Created lease: {lease3.id} for {tenant3.name}")

    print("\n✅ Sample data created successfully!")
    return engine


def register_workflows(engine: AutomationEngine):
    """Register all workflows with the engine."""
    print("\n🔧 Registering automation workflows...\n")

    engine.register_workflow(LateRentWorkflow())
    print("  ✓ Late Rent Workflow")

    engine.register_workflow(MaintenanceWorkflow())
    print("  ✓ Maintenance Workflow")

    engine.register_workflow(LeaseRenewalWorkflow())
    print("  ✓ Lease Renewal Workflow")

    engine.register_workflow(MoveInWorkflow())
    print("  ✓ Move-In Workflow")

    engine.register_workflow(OwnerReportingWorkflow())
    print("  ✓ Owner Reporting Workflow")

    print("\n✅ All workflows registered!")


def show_status(engine: AutomationEngine):
    """Display current system status."""
    summary = engine.get_summary()

    print("\n" + "=" * 60)
    print("   PropertyFlow - System Status")
    print("=" * 60)

    print(f"\n📊 Data Summary:")
    print(f"   Properties:        {summary['properties']}")
    print(f"   Tenants:           {summary['tenants']}")
    print(f"   Owners:            {summary['owners']}")
    print(f"   Vendors:           {summary['vendors']}")
    print(f"   Active Leases:     {summary['active_leases']}")
    print(f"   Open Maintenance:  {summary['open_maintenance']}")

    print(f"\n⚙️  Workflows Registered: {summary['registered_workflows']}")

    # Show properties detail
    print(f"\n🏠 Properties:")
    for prop in engine.data.properties.values():
        tenant = engine.get_tenant(prop.current_tenant_id) if prop.current_tenant_id else None
        tenant_name = tenant.name if tenant else "Vacant"
        rent_status = tenant.rent_status.value if tenant else "N/A"
        print(f"   • {prop.address}")
        print(f"     Tenant: {tenant_name} | Rent Status: {rent_status} | ${prop.market_rent:,.0f}/mo")

    # Show upcoming events
    print(f"\n📅 Upcoming Events:")
    for lease in engine.get_active_leases():
        if lease.days_until_expiry <= 90:
            tenant = engine.get_tenant(lease.tenant_id)
            print(f"   • Lease expiring in {lease.days_until_expiry} days: {tenant.name if tenant else 'Unknown'}")

    print("\n" + "=" * 60)


def demo_late_rent(engine: AutomationEngine):
    """Demonstrate the late rent workflow."""
    print("\n" + "-" * 60)
    print("  Demo: Late Rent Workflow")
    print("-" * 60)

    # Get the tenant with late rent
    tenant = engine.get_tenant("tenant002")
    lease = engine.get_lease(tenant.lease_id)
    property = engine.get_property(tenant.property_id)

    print(f"\n📋 Scenario: {tenant.name} is late on rent for {property.address}")
    print(f"   Rent Due: ${lease.monthly_rent:,.2f}")
    print(f"   Late Fee: ${lease.late_fee:,.2f}")
    print(f"   Current Status: {tenant.rent_status.value}")

    print("\n🚀 Triggering late rent event...")

    from .core.events import Event, EventType
    event = Event(
        EventType.RENT_LATE,
        {
            "tenant": tenant,
            "lease": lease,
            "property": property,
        }
    )
    results = engine.event_bus.publish(event)

    print("\n📨 Actions Taken:")
    for result in results:
        if result.success:
            for action in result.actions_taken:
                print(f"   ✓ {action}")
        else:
            for error in result.errors:
                print(f"   ✗ Error: {error}")


def demo_maintenance(engine: AutomationEngine):
    """Demonstrate the maintenance workflow."""
    print("\n" + "-" * 60)
    print("  Demo: Maintenance Request Workflow")
    print("-" * 60)

    tenant = engine.get_tenant("tenant001")
    property = engine.get_property(tenant.property_id)
    owner = engine.get_owner(property.owner_id)

    print(f"\n📋 Scenario: {tenant.name} reports a plumbing issue")
    print(f"   Property: {property.address}")

    # Create maintenance request
    request = MaintenanceRequest(
        property_id=property.id,
        tenant_id=tenant.id,
        owner_id=owner.id,
        title="Kitchen sink leaking",
        description="Water is dripping from under the kitchen sink. It's not a lot but the cabinet is getting wet.",
        category=MaintenanceCategory.PLUMBING,
        priority=MaintenancePriority.NORMAL,
        tenant_permission_to_enter=True,
        access_instructions="Please call ahead. Dog is friendly but loud.",
    )

    print("\n🚀 Creating maintenance request...")
    engine.create_maintenance_request(request)

    print("\n📨 Actions Taken (check notification log):")
    for notification in engine.notifications.get_notification_log()[-5:]:
        if notification.sent:
            print(f"   ✓ {notification.notification_type.value.upper()}: {notification.subject or notification.body[:50]}...")


def demo_lease_renewal(engine: AutomationEngine):
    """Demonstrate the lease renewal workflow."""
    print("\n" + "-" * 60)
    print("  Demo: Lease Renewal Workflow")
    print("-" * 60)

    # Get the lease expiring soon
    lease = engine.get_lease("lease002")
    tenant = engine.get_tenant(lease.tenant_id)
    property = engine.get_property(lease.property_id)
    owner = engine.get_owner(lease.owner_id)

    print(f"\n📋 Scenario: {tenant.name}'s lease expires in {lease.days_until_expiry} days")
    print(f"   Property: {property.address}")
    print(f"   Lease End: {lease.end_date}")
    print(f"   Current Rent: ${lease.monthly_rent:,.2f}/month")

    print("\n🚀 Triggering 60-day renewal offer...")

    from .core.events import Event, EventType
    event = Event(
        EventType.LEASE_EXPIRING_60_DAYS,
        {
            "lease": lease,
            "tenant": tenant,
            "property": property,
            "owner": owner,
            "days_until_expiry": lease.days_until_expiry,
        }
    )
    results = engine.event_bus.publish(event)

    print("\n📨 Actions Taken:")
    for result in results:
        if result.success:
            for action in result.actions_taken:
                print(f"   ✓ {action}")


def run_demo(args):
    """Run a full demonstration of the system."""
    print("\n" + "=" * 60)
    print("   PropertyFlow - Property Management Automation")
    print("   Demo for NoVA Property Managers")
    print("=" * 60)

    # Initialize engine
    config = {
        "notifications": {
            "company_name": "PropertyFlow Management",
            "company_phone": "(703) 555-0100",
            "company_email": "info@propertyflow.com",
            "company_address": "123 King Street, Leesburg, VA 20176",
            "emergency_phone": "(703) 555-0199",
            "payment_portal_url": "https://pay.propertyflow.com",
        },
        "log_level": "WARNING",  # Reduce noise for demo
    }

    engine = AutomationEngine(config)

    # Create sample data
    create_sample_data(engine)

    # Register workflows
    register_workflows(engine)

    # Show status
    show_status(engine)

    # Run demos
    print("\n" + "=" * 60)
    print("   Running Workflow Demonstrations")
    print("=" * 60)

    demo_late_rent(engine)
    demo_maintenance(engine)
    demo_lease_renewal(engine)

    # Summary
    print("\n" + "=" * 60)
    print("   Demo Complete!")
    print("=" * 60)

    print("""
✅ PropertyFlow automated the following workflows:

1. LATE RENT ESCALATION
   • Sent late notice to tenant with fees calculated
   • Notified property owner of late payment
   • All documentation logged for potential legal action

2. MAINTENANCE REQUEST
   • Acknowledged request to tenant immediately
   • Auto-triaged based on description
   • Found and assigned appropriate vendor
   • Sent work order to vendor
   • Owner kept informed throughout

3. LEASE RENEWAL
   • Detected lease expiring in 60 days
   • Sent renewal offer with multiple options
   • Tracking response deadline
   • Owner notified of renewal status

This eliminates 6-8 manual touches per maintenance request and
automates the entire rent collection escalation chain.

For a property management company with 100 units:
• ~30 maintenance requests/month = 180-240 touches saved
• ~8 lease renewals/month = 40+ touches saved
• 100 rent follow-ups/month = automated

At $49-79/month, this pays for itself in the first week.
""")

    # Save data
    engine.save("propertyflow_demo_data.json")
    print("💾 Demo data saved to propertyflow_demo_data.json\n")


def run_daily(args):
    """Run daily automation checks."""
    print("Running daily automation checks...")

    config = {"log_level": "INFO"}
    engine = AutomationEngine(config)
    register_workflows(engine)

    # Load existing data if available
    # (In production, this would load from database)

    engine.run_daily_checks()
    print("Daily checks completed.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PropertyFlow - Property Management Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m property_management.cli demo     Run demonstration
  python -m property_management.cli status   Show system status
  python -m property_management.cli daily    Run daily checks
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demonstration with sample data")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")

    # Daily command
    daily_parser = subparsers.add_parser("daily", help="Run daily automation checks")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(args)
    elif args.command == "status":
        print("Status command - initialize with data first using 'demo'")
    elif args.command == "daily":
        run_daily(args)
    else:
        parser.print_help()
        print("\n💡 Tip: Run 'python -m property_management.cli demo' to see the system in action!")


if __name__ == "__main__":
    main()
