# PropertyFlow - Property Management Automation

A lightweight, powerful automation layer for property management companies. Built specifically for NoVA property managers who need efficiency without bloat.

## The Problem

Property management companies in Northern Virginia are doing massive chunks of their work manually or with clunky generic software. The daily grind is incredibly repetitive:

- **Late Rent**: Someone manually checks → sends reminder → waits → sends another → eventually files paperwork
- **Maintenance**: Request comes in → triage → call vendor → schedule → follow up → confirm → notify owner (6-8 manual touches!)
- **Lease Renewal**: Remember to check → send offer → track response → maybe market unit → schedule showings
- **Move-in**: Create accounts → send welcome packet → schedule inspection → set up rent collection → notify owner

## The Solution

PropertyFlow automates all of this with a simple event-driven architecture:
**"When X happens, do Y, tell Z"**

## Features

### 🏠 Late Rent Escalation
- Automatic friendly reminders on due date
- Grace period warnings before late fees kick in
- Formal late notices with calculated fees
- Severely late notices with cure period
- Owner notifications at every step
- Full documentation trail for legal action

### 🔧 Maintenance Workflow
- Instant acknowledgment to tenants
- Auto-triage based on keywords (emergency/urgent/normal)
- Automatic vendor matching by specialty and location
- Work orders sent directly to vendors
- Follow-up reminders for non-responsive vendors
- Owner approval workflow for expensive repairs
- Completion notifications to all parties

### 📋 Lease Renewal
- 90-day advance notice to owners
- 60-day renewal offers to tenants with multiple options
- Automatic follow-up reminders
- Non-renewal triggers move-out process and marketing
- All communication logged and tracked

### 🚪 Move-In Automation
- Welcome packet with all essential information
- Utility setup instructions (local providers)
- 7-day and 1-day reminders
- Inspection scheduling
- Owner notifications throughout

### 📊 Owner Reporting
- Automatic monthly statement generation
- Income/expense calculation
- Maintenance activity summary
- Tenant status updates
- Year-end summary reports

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd property_management

# No external dependencies required - uses Python standard library only!
python -m property_management.cli demo
```

## Quick Start

Run the demonstration to see all workflows in action:

```bash
python -m property_management.cli demo
```

This will:
1. Create sample properties, tenants, owners, and vendors
2. Register all automation workflows
3. Demonstrate late rent handling
4. Demonstrate maintenance request processing
5. Demonstrate lease renewal workflow

## Architecture

```
property_management/
├── __init__.py           # Package initialization
├── cli.py                # Command-line interface
├── core/
│   ├── __init__.py
│   ├── engine.py         # Main automation engine
│   ├── events.py         # Event-driven architecture
│   ├── models.py         # Data models (Property, Tenant, etc.)
│   └── notifications.py  # Email/SMS notification service
└── workflows/
    ├── __init__.py
    ├── late_rent.py      # Rent collection escalation
    ├── maintenance.py    # Maintenance request handling
    ├── lease_renewal.py  # Lease renewal automation
    ├── move_in.py        # New tenant onboarding
    └── owner_reporting.py # Monthly owner statements
```

### Event-Driven Design

The system uses an event bus pattern where:
- **Events** represent things that happen (rent is late, maintenance requested)
- **Handlers** respond to events and take action
- **Follow-up Events** can trigger additional workflows

Example flow:
```
MAINTENANCE_REQUEST_CREATED
    → Auto-triage (detect priority)
    → Send acknowledgment to tenant
    → Trigger MAINTENANCE_TRIAGED

MAINTENANCE_TRIAGED
    → Find matching vendor
    → Assign vendor
    → Trigger MAINTENANCE_VENDOR_ASSIGNED

MAINTENANCE_VENDOR_ASSIGNED
    → Send work order to vendor
    → Schedule follow-up reminder
```

## Configuration

Edit the configuration in `cli.py` or pass to `AutomationEngine`:

```python
config = {
    "notifications": {
        "company_name": "Your Company Name",
        "company_phone": "(703) 555-0100",
        "company_email": "info@yourcompany.com",
        "company_address": "123 Main St, Leesburg, VA 20176",
        "emergency_phone": "(703) 555-0199",
        "payment_portal_url": "https://pay.yourcompany.com",
    },
    "log_level": "INFO",
}
```

## Extending the System

### Adding a New Workflow

1. Create a new file in `workflows/`
2. Define a class with `register(engine)` method
3. Subscribe to relevant events
4. Implement handler methods

```python
class MyCustomWorkflow:
    def register(self, engine):
        self.engine = engine
        engine.event_bus.subscribe(
            EventType.SOME_EVENT,
            self.handle_event,
            "MyWorkflow.handle_event"
        )

    def handle_event(self, event):
        # Your automation logic here
        return EventResult(success=True, event=event, ...)
```

### Adding New Event Types

Add to `EventType` enum in `core/events.py`:

```python
class EventType(Enum):
    # ... existing events
    MY_NEW_EVENT = "my_new_event"
```

## Target Market

This software is designed for property management companies in Northern Virginia, specifically:
- **Loudoun County** (Leesburg, Ashburn, Lansdowne, Brambleton)
- **Fairfax County**
- **Prince William County**
- **Arlington**

These areas have:
- High property values ($2,500-4,000/month rentals typical)
- High concentration of investment properties
- Owners who travel/relocate for government/defense/tech jobs
- Many small-to-medium property management companies

## ROI Calculator

For a property management company with 100 units:

| Automation | Manual Touches/Month | Time Saved |
|------------|---------------------|------------|
| Maintenance (30 requests) | 180-240 | ~15-20 hours |
| Lease Renewals (8/month) | 40+ | ~5 hours |
| Rent Follow-ups | 100+ | ~10 hours |
| Owner Reports | 100 | ~8 hours |
| **Total** | **420+** | **~40 hours** |

At $49-79/month, this pays for itself in the first week.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Support

- Email: support@propertyflow.com
- Phone: (703) 555-0100
- GitHub Issues: [Create an issue](../../issues)

---

Built with ❤️ for NoVA property managers
