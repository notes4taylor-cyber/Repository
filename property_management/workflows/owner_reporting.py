"""
Owner Reporting Workflow for PropertyFlow.

Automates monthly financial reporting for property owners:
1. End of month -> Generate statement for each property
2. Calculate income (rent, late fees) and expenses (maintenance, management fee)
3. Generate professional statement
4. Email to owner
5. Track delivery confirmation

Every month, for every property - fully automated.
"""

from datetime import datetime, date, timedelta
from calendar import monthrange
from typing import TYPE_CHECKING, List, Dict, Any

from ..core.events import Event, EventBus, EventType, EventResult
from ..core.notifications import NotificationService, NotificationPriority
from ..core.models import (
    Owner, Property, Tenant, Lease, OwnerStatement,
    RentPayment, Expense, MaintenanceRequest, MaintenanceStatus
)

if TYPE_CHECKING:
    from ..core.engine import AutomationEngine


class OwnerReportingWorkflow:
    """
    Automates monthly owner statement generation and delivery.

    Handles:
    - Monthly statement generation
    - Income/expense calculation
    - Professional formatting
    - Email delivery
    - Year-end summaries
    """

    def __init__(self):
        self.engine: "AutomationEngine" = None
        self.event_bus: EventBus = None
        self.notifications: NotificationService = None

        # Configuration
        self.config = {
            "statement_day": 1,  # Day of month to send statements (for previous month)
            "include_maintenance_details": True,
            "include_tenant_status": True,
            "year_end_summary": True,
        }

    def register(self, engine: "AutomationEngine"):
        """Register this workflow with the automation engine."""
        self.engine = engine
        self.event_bus = engine.event_bus
        self.notifications = engine.notifications

        # Subscribe to reporting events
        self.event_bus.subscribe(
            EventType.MONTHLY_CHECK,
            self.handle_monthly_check,
            "OwnerReportingWorkflow.handle_monthly_check"
        )

        self.event_bus.subscribe(
            EventType.OWNER_STATEMENT_GENERATED,
            self.handle_statement_generated,
            "OwnerReportingWorkflow.handle_statement_generated"
        )

        # Daily check (to trigger on statement day)
        self.event_bus.subscribe(
            EventType.DAILY_CHECK,
            self.check_statement_day,
            "OwnerReportingWorkflow.check_statement_day"
        )

    def check_statement_day(self, event: Event) -> EventResult:
        """
        Check if today is statement day.

        Trigger: Daily check
        Actions:
        - If first of month, trigger monthly statement generation
        """
        today = date.today()

        if today.day == self.config["statement_day"]:
            # Generate statements for all owners
            return self.generate_all_statements()

        return EventResult(
            success=True,
            event=event,
            handler_name="OwnerReportingWorkflow.check_statement_day",
            message="Not statement day",
            actions_taken=[],
        )

    def handle_monthly_check(self, event: Event) -> EventResult:
        """
        Handle monthly check - generate all owner statements.

        Trigger: Monthly check event
        Actions:
        - Generate statement for each active property
        - Send to owners
        """
        return self.generate_all_statements()

    def generate_all_statements(self) -> EventResult:
        """Generate statements for all properties."""
        actions_taken = []
        follow_up_events = []

        # Calculate previous month's date range
        today = date.today()
        first_of_this_month = date(today.year, today.month, 1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        first_of_prev_month = date(last_of_prev_month.year, last_of_prev_month.month, 1)

        # Generate statement for each property
        for property in self.engine.data.properties.values():
            if not property.owner_id:
                continue

            owner = self.engine.get_owner(property.owner_id)
            if not owner:
                continue

            try:
                statement = self._generate_property_statement(
                    property=property,
                    owner=owner,
                    period_start=first_of_prev_month,
                    period_end=last_of_prev_month,
                )

                if statement:
                    # Trigger statement generated event
                    follow_up_events.append(Event(
                        EventType.OWNER_STATEMENT_GENERATED,
                        {
                            "statement": statement,
                            "owner": owner,
                            "property": property,
                        }
                    ))
                    actions_taken.append(f"Generated statement for {property.address}")

            except Exception as e:
                actions_taken.append(f"Error generating statement for property {property.id}: {str(e)}")

        return EventResult(
            success=True,
            event=Event(EventType.MONTHLY_CHECK, {}),
            handler_name="OwnerReportingWorkflow.generate_all_statements",
            message=f"Generated {len(follow_up_events)} owner statements",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    def _generate_property_statement(
        self,
        property: Property,
        owner: Owner,
        period_start: date,
        period_end: date,
    ) -> OwnerStatement:
        """Generate a statement for a single property."""

        statement = OwnerStatement(
            owner_id=owner.id,
            property_id=property.id,
            statement_period_start=period_start,
            statement_period_end=period_end,
        )

        # Calculate rent collected
        for payment_id, payment in self.engine.data.rent_payments.items():
            if payment.property_id != property.id:
                continue
            if not (period_start <= payment.payment_date <= period_end):
                continue

            statement.rent_collected += payment.amount
            statement.late_fees_collected += payment.late_fee_applied
            statement.payment_records.append(payment_id)

        # Calculate expenses
        for expense_id, expense in self.engine.data.expenses.items():
            if expense.property_id != property.id:
                continue
            if not (period_start <= expense.date <= period_end):
                continue

            if expense.category == "maintenance":
                statement.maintenance_expenses += expense.amount
            elif expense.category == "management":
                statement.management_fee += expense.amount
            else:
                statement.other_expenses += expense.amount
            statement.expense_records.append(expense_id)

        # Calculate management fee if not already recorded
        if statement.management_fee == 0 and statement.rent_collected > 0:
            statement.management_fee = statement.rent_collected * (property.management_fee_percent / 100)

        # Get maintenance summary
        statement.maintenance_summary = self._get_maintenance_summary(
            property.id, period_start, period_end
        )

        # Store the statement
        self.engine.data.owner_statements[statement.id] = statement

        return statement

    def _get_maintenance_summary(
        self,
        property_id: str,
        period_start: date,
        period_end: date,
    ) -> List[Dict[str, Any]]:
        """Get summary of maintenance work during the period."""
        summary = []

        for request in self.engine.data.maintenance_requests.values():
            if request.property_id != property_id:
                continue

            # Check if request was active during this period
            created_date = request.created_at.date() if request.created_at else None
            if created_date and not (period_start <= created_date <= period_end):
                # Check if it was completed during this period
                completed_date = request.completed_date.date() if request.completed_date else None
                if not completed_date or not (period_start <= completed_date <= period_end):
                    continue

            summary.append({
                "request_id": request.id,
                "title": request.title,
                "status": request.status.value,
                "created": request.created_at.strftime("%m/%d/%Y") if request.created_at else "N/A",
                "completed": request.completed_date.strftime("%m/%d/%Y") if request.completed_date else "Pending",
                "cost": request.actual_cost or 0,
            })

        return summary

    def handle_statement_generated(self, event: Event) -> EventResult:
        """
        Handle statement generated - send to owner.

        Trigger: Statement has been generated
        Actions:
        - Format statement
        - Send email to owner
        - Mark as sent
        """
        statement: OwnerStatement = event.payload.get("statement")
        owner: Owner = event.payload.get("owner")
        property: Property = event.payload.get("property")

        if not statement or not owner:
            return EventResult(
                success=False,
                event=event,
                handler_name="OwnerReportingWorkflow.handle_statement_generated",
                errors=["Missing statement or owner data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your property"

        # Format the statement period
        statement_period = f"{statement.statement_period_start.strftime('%B %Y')}"

        # Get tenant info
        tenant = None
        lease = None
        if property and property.current_tenant_id:
            tenant = self.engine.get_tenant(property.current_tenant_id)
        if property and property.current_lease_id:
            lease = self.engine.get_lease(property.current_lease_id)

        # Build maintenance summary text
        maintenance_text = ""
        if statement.maintenance_summary:
            maintenance_text = "\nMAINTENANCE ACTIVITY:\n"
            for item in statement.maintenance_summary:
                cost_str = f"${item['cost']:,.2f}" if item['cost'] else "Pending"
                maintenance_text += f"  • {item['title']} ({item['status']}) - {cost_str}\n"
        else:
            maintenance_text = "\nMAINTENANCE ACTIVITY:\n  No maintenance activity this period.\n"

        # Build tenant status text
        tenant_text = ""
        if tenant and lease:
            rent_status = "Current" if tenant.rent_status.value == "current" else tenant.rent_status.value.title()
            tenant_text = f"""
TENANT STATUS:
  Tenant: {tenant.name}
  Rent Status: {rent_status}
  Lease Expires: {lease.end_date.strftime('%B %d, %Y')}
"""

        # Determine payment status
        if statement.net_income > 0:
            payment_status = "scheduled for direct deposit"
        else:
            payment_status = "N/A (expenses exceeded income)"

        # Build template data
        template_data = {
            "owner_name": owner.name,
            "property_address": property_address,
            "statement_period": statement_period,
            "rent_collected": f"{statement.rent_collected:,.2f}",
            "late_fees": f"{statement.late_fees_collected:,.2f}",
            "other_income": f"{statement.other_income:,.2f}",
            "total_income": f"{statement.total_income:,.2f}",
            "maintenance_expenses": f"{statement.maintenance_expenses:,.2f}",
            "management_fee": f"{statement.management_fee:,.2f}",
            "other_expenses": f"{statement.other_expenses:,.2f}",
            "total_expenses": f"{statement.total_expenses:,.2f}",
            "net_income": f"{statement.net_income:,.2f}",
            "maintenance_summary": maintenance_text,
            "tenant_status": tenant_text,
            "payment_status": payment_status,
        }

        # Send statement email
        if owner.contact and owner.contact.email:
            self.notifications.send_from_template(
                template_id="owner_monthly_statement",
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                template_data=template_data,
            )
            actions_taken.append(f"Sent statement to {owner.contact.email}")

            # Mark as sent
            statement.sent_to_owner = True
            statement.sent_date = datetime.now()

        return EventResult(
            success=True,
            event=event,
            handler_name="OwnerReportingWorkflow.handle_statement_generated",
            message=f"Statement sent for {property_address}",
            actions_taken=actions_taken,
        )

    def generate_year_end_summary(self, owner_id: str, year: int) -> Dict[str, Any]:
        """Generate a year-end summary for an owner."""
        owner = self.engine.get_owner(owner_id)
        if not owner:
            return {}

        # Get all properties for this owner
        properties = self.engine.get_properties_by_owner(owner_id)

        year_summary = {
            "owner_id": owner_id,
            "owner_name": owner.name,
            "year": year,
            "properties": [],
            "totals": {
                "rent_collected": 0,
                "late_fees": 0,
                "maintenance_expenses": 0,
                "management_fees": 0,
                "other_expenses": 0,
                "net_income": 0,
            }
        }

        for property in properties:
            property_summary = {
                "property_id": property.id,
                "address": str(property.address) if property.address else "N/A",
                "rent_collected": 0,
                "late_fees": 0,
                "maintenance_expenses": 0,
                "management_fees": 0,
                "other_expenses": 0,
                "net_income": 0,
            }

            # Sum up all statements for this property for the year
            for statement in self.engine.data.owner_statements.values():
                if statement.property_id != property.id:
                    continue
                if statement.statement_period_start.year != year:
                    continue

                property_summary["rent_collected"] += statement.rent_collected
                property_summary["late_fees"] += statement.late_fees_collected
                property_summary["maintenance_expenses"] += statement.maintenance_expenses
                property_summary["management_fees"] += statement.management_fee
                property_summary["other_expenses"] += statement.other_expenses

            property_summary["net_income"] = (
                property_summary["rent_collected"] +
                property_summary["late_fees"] -
                property_summary["maintenance_expenses"] -
                property_summary["management_fees"] -
                property_summary["other_expenses"]
            )

            year_summary["properties"].append(property_summary)

            # Add to totals
            for key in year_summary["totals"]:
                year_summary["totals"][key] += property_summary.get(key, 0)

        return year_summary

    def send_year_end_summary(self, owner_id: str, year: int) -> EventResult:
        """Generate and send year-end summary to an owner."""
        owner = self.engine.get_owner(owner_id)
        if not owner or not owner.contact or not owner.contact.email:
            return EventResult(
                success=False,
                event=Event(EventType.OWNER_STATEMENT_SENT, {}),
                handler_name="OwnerReportingWorkflow.send_year_end_summary",
                errors=["Owner not found or no email"],
            )

        summary = self.generate_year_end_summary(owner_id, year)

        # Build summary text
        properties_text = ""
        for prop in summary["properties"]:
            properties_text += f"""
{prop['address']}:
  Rent Collected:     ${prop['rent_collected']:>12,.2f}
  Late Fees:          ${prop['late_fees']:>12,.2f}
  Maintenance:        ${prop['maintenance_expenses']:>12,.2f}
  Management Fees:    ${prop['management_fees']:>12,.2f}
  Other Expenses:     ${prop['other_expenses']:>12,.2f}
  ─────────────────────────────────
  Net Income:         ${prop['net_income']:>12,.2f}
"""

        subject = f"Year-End Summary {year} - Your Property Portfolio"
        body = f"""Dear {owner.name},

Please find below your year-end property management summary for {year}.

{'═' * 50}
ANNUAL SUMMARY - {year}
{'═' * 50}

PROPERTY BREAKDOWN:
{properties_text}

{'═' * 50}
PORTFOLIO TOTALS:
{'═' * 50}
  Total Rent Collected:     ${summary['totals']['rent_collected']:>12,.2f}
  Total Late Fees:          ${summary['totals']['late_fees']:>12,.2f}
  Total Maintenance:        ${summary['totals']['maintenance_expenses']:>12,.2f}
  Total Management Fees:    ${summary['totals']['management_fees']:>12,.2f}
  Total Other Expenses:     ${summary['totals']['other_expenses']:>12,.2f}
  ─────────────────────────────────────────────────
  TOTAL NET INCOME:         ${summary['totals']['net_income']:>12,.2f}
{'═' * 50}

This summary is for your records and may be useful for tax preparation. Please consult with your tax advisor regarding deductions and reporting requirements.

Thank you for your continued trust in our services.

Best regards,
{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""

        self.notifications.send_email(
            recipient_id=owner_id,
            recipient_email=owner.contact.email,
            subject=subject,
            body=body,
        )

        return EventResult(
            success=True,
            event=Event(EventType.OWNER_STATEMENT_SENT, {}),
            handler_name="OwnerReportingWorkflow.send_year_end_summary",
            message=f"Year-end summary sent to {owner.name}",
            actions_taken=[f"Sent {year} summary to {owner.contact.email}"],
        )
