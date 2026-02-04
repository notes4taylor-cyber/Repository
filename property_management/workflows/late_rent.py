"""
Late Rent Workflow for PropertyFlow.

Automates the entire rent collection escalation chain:
1. Rent due -> Friendly reminder
2. Grace period ending -> Warning
3. Late (after grace period) -> Late notice with fee
4. Severely late (15+ days) -> Formal notice
5. Collections threshold -> Legal notice preparation

Pattern: "When X happens, do Y, tell Z"
"""

from datetime import datetime, date, timedelta
from typing import TYPE_CHECKING

from ..core.events import Event, EventBus, EventType, EventResult
from ..core.notifications import NotificationService, NotificationType, NotificationPriority
from ..core.models import Tenant, Lease, Property, RentStatus

if TYPE_CHECKING:
    from ..core.engine import AutomationEngine


class LateRentWorkflow:
    """
    Automates rent collection follow-up and escalation.

    This workflow handles the entire late rent process automatically:
    - Sends friendly reminders when rent is due
    - Escalates with late notices when grace period expires
    - Notifies owners of late payments
    - Prepares documentation for legal action when needed
    """

    def __init__(self):
        self.engine: "AutomationEngine" = None
        self.event_bus: EventBus = None
        self.notifications: NotificationService = None

        # Configuration
        self.config = {
            "friendly_reminder_day": 1,  # Day rent is due
            "warning_before_late": 1,  # Days before late fee kicks in
            "late_notice_day": 6,  # After grace period (typically 5 days)
            "severely_late_day": 15,
            "collections_day": 30,
            "cure_period_days": 5,  # Days to pay before legal action
        }

    def register(self, engine: "AutomationEngine"):
        """Register this workflow with the automation engine."""
        self.engine = engine
        self.event_bus = engine.event_bus
        self.notifications = engine.notifications

        # Subscribe to rent-related events
        self.event_bus.subscribe(
            EventType.RENT_DUE,
            self.handle_rent_due,
            "LateRentWorkflow.handle_rent_due"
        )

        self.event_bus.subscribe(
            EventType.RENT_GRACE_PERIOD_ENDING,
            self.handle_grace_period_ending,
            "LateRentWorkflow.handle_grace_period_ending"
        )

        self.event_bus.subscribe(
            EventType.RENT_LATE,
            self.handle_rent_late,
            "LateRentWorkflow.handle_rent_late"
        )

        self.event_bus.subscribe(
            EventType.RENT_SEVERELY_LATE,
            self.handle_severely_late,
            "LateRentWorkflow.handle_severely_late"
        )

        self.event_bus.subscribe(
            EventType.RENT_PAYMENT_RECEIVED,
            self.handle_payment_received,
            "LateRentWorkflow.handle_payment_received"
        )

    def handle_rent_due(self, event: Event) -> EventResult:
        """
        Handle rent due date - send friendly reminder.

        Trigger: First day of rent due date
        Actions:
        - Send friendly email reminder to tenant
        - Send SMS reminder if preferred
        """
        tenant: Tenant = event.payload.get("tenant")
        lease: Lease = event.payload.get("lease")

        if not tenant or not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LateRentWorkflow.handle_rent_due",
                errors=["Missing tenant or lease data"]
            )

        actions_taken = []

        # Get property for address
        property = self.engine.get_property(lease.property_id)
        property_address = str(property.address) if property and property.address else "your rental property"

        # Prepare template data
        template_data = {
            "tenant_name": tenant.name,
            "rent_amount": f"{lease.monthly_rent:,.2f}",
            "property_address": property_address,
            "due_date": f"{date.today().strftime('%B')} {lease.rent_due_day}",
        }

        # Send friendly email reminder
        if tenant.contact and tenant.contact.email:
            self.notifications.send_from_template(
                template_id="rent_reminder_friendly",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
                priority=NotificationPriority.NORMAL,
            )
            actions_taken.append(f"Sent friendly reminder email to {tenant.contact.email}")

        # Log communication
        tenant.log_communication(
            comm_type="email",
            subject="Rent Due Reminder",
            details="Friendly reminder sent on due date"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LateRentWorkflow.handle_rent_due",
            message="Rent due reminder sent",
            actions_taken=actions_taken,
        )

    def handle_grace_period_ending(self, event: Event) -> EventResult:
        """
        Handle grace period ending - send warning before late fee.

        Trigger: Day before grace period ends
        Actions:
        - Send warning email about upcoming late fee
        - Send SMS alert
        """
        tenant: Tenant = event.payload.get("tenant")
        lease: Lease = event.payload.get("lease")
        days_late: int = event.payload.get("days_late", 0)

        if not tenant or not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LateRentWorkflow.handle_grace_period_ending",
                errors=["Missing tenant or lease data"]
            )

        actions_taken = []

        property = self.engine.get_property(lease.property_id)
        property_address = str(property.address) if property and property.address else "your rental property"

        # Calculate late fee
        if lease.late_fee_type == "percentage":
            late_fee = lease.monthly_rent * (lease.late_fee / 100)
        else:
            late_fee = lease.late_fee

        template_data = {
            "tenant_name": tenant.name,
            "rent_amount": f"{lease.monthly_rent:,.2f}",
            "property_address": property_address,
            "due_date": f"{date.today().strftime('%B')} {lease.rent_due_day}",
            "late_fee": f"{late_fee:,.2f}",
            "grace_period_end": (date.today() + timedelta(days=1)).strftime("%B %d, %Y"),
        }

        # Build warning message
        subject = f"URGENT: Rent Late Fee Applies Tomorrow - {property_address}"
        body = f"""Dear {tenant.name},

This is an urgent reminder that your rent payment of ${lease.monthly_rent:,.2f} for {property_address} is still outstanding.

Your grace period ends TOMORROW. If payment is not received by end of day tomorrow, a late fee of ${late_fee:,.2f} will be applied to your account.

Please submit your payment today to avoid this additional charge.

Payment Methods:
- Online: {self.notifications.company_info['payment_portal_url']}
- Mail: {self.notifications.company_info['company_address']}

Questions? Contact us at {self.notifications.company_info['company_phone']}.

{self.notifications.company_info['company_name']}
"""

        if tenant.contact and tenant.contact.email:
            self.notifications.send_email(
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                subject=subject,
                body=body,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append(f"Sent grace period warning email to {tenant.contact.email}")

        # Send SMS for urgency
        if tenant.contact and tenant.contact.phone:
            sms_body = f"URGENT: Rent for {property_address} is due. Late fee of ${late_fee:,.2f} applies tomorrow if unpaid. Pay now or call {self.notifications.company_info['company_phone']}."
            self.notifications.send_sms(
                recipient_id=tenant.id,
                recipient_phone=tenant.contact.phone,
                body=sms_body,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append(f"Sent SMS warning to {tenant.contact.phone}")

        tenant.log_communication(
            comm_type="email+sms",
            subject="Grace Period Warning",
            details="Warning sent about impending late fee"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LateRentWorkflow.handle_grace_period_ending",
            message="Grace period warning sent",
            actions_taken=actions_taken,
        )

    def handle_rent_late(self, event: Event) -> EventResult:
        """
        Handle rent becoming officially late - send late notice.

        Trigger: Day after grace period ends
        Actions:
        - Apply late fee to account
        - Send formal late notice to tenant
        - Notify property owner
        """
        tenant: Tenant = event.payload.get("tenant")
        lease: Lease = event.payload.get("lease")
        property: Property = event.payload.get("property")

        if not tenant or not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LateRentWorkflow.handle_rent_late",
                errors=["Missing tenant or lease data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "rental property"

        # Calculate days late and fees
        today = date.today()
        due_date = date(today.year, today.month, lease.rent_due_day)
        days_late = (today - due_date).days

        if lease.late_fee_type == "percentage":
            late_fee = lease.monthly_rent * (lease.late_fee / 100)
        else:
            late_fee = lease.late_fee

        total_due = lease.monthly_rent + late_fee

        template_data = {
            "tenant_name": tenant.name,
            "rent_amount": f"{lease.monthly_rent:,.2f}",
            "property_address": property_address,
            "days_late": days_late,
            "late_fee": f"{late_fee:,.2f}",
            "total_due": f"{total_due:,.2f}",
        }

        # Send formal late notice
        if tenant.contact and tenant.contact.email:
            self.notifications.send_from_template(
                template_id="rent_late_notice",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append(f"Sent late notice email to {tenant.contact.email}")

        # Send SMS
        if tenant.contact and tenant.contact.phone:
            self.notifications.send_from_template(
                template_id="rent_late_sms",
                recipient_id=tenant.id,
                recipient_phone=tenant.contact.phone,
                template_data=template_data,
                notification_type=NotificationType.SMS,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append(f"Sent late notice SMS to {tenant.contact.phone}")

        # Notify owner
        owner = self.engine.get_owner(lease.owner_id)
        if owner and owner.contact and owner.contact.email:
            owner_subject = f"Late Rent Notice: {property_address}"
            owner_body = f"""Dear {owner.name},

This is to inform you that rent is now {days_late} days late for your property at {property_address}.

Tenant: {tenant.name}
Monthly Rent: ${lease.monthly_rent:,.2f}
Late Fee Applied: ${late_fee:,.2f}
Total Due: ${total_due:,.2f}

We have sent the tenant a formal late notice and will continue our collection procedures. We will keep you updated on the status.

If you have any questions, please contact us.

{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=owner_subject,
                body=owner_body,
                priority=NotificationPriority.NORMAL,
            )
            actions_taken.append(f"Notified owner {owner.name} of late rent")

        # Update tenant record
        tenant.late_payment_count += 1
        tenant.log_communication(
            comm_type="email",
            subject="Late Rent Notice",
            details=f"Formal late notice sent. Days late: {days_late}. Late fee: ${late_fee:,.2f}"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LateRentWorkflow.handle_rent_late",
            message=f"Late rent notice sent - {days_late} days late",
            actions_taken=actions_taken,
        )

    def handle_severely_late(self, event: Event) -> EventResult:
        """
        Handle severely late rent - send formal legal notice.

        Trigger: 15+ days past due
        Actions:
        - Send formal demand letter with cure period
        - Prepare documentation for potential legal action
        - Urgent notification to owner
        """
        tenant: Tenant = event.payload.get("tenant")
        lease: Lease = event.payload.get("lease")
        property: Property = event.payload.get("property")

        if not tenant or not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LateRentWorkflow.handle_severely_late",
                errors=["Missing tenant or lease data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "rental property"

        # Calculate totals
        today = date.today()
        due_date = date(today.year, today.month, lease.rent_due_day)
        days_late = (today - due_date).days

        if lease.late_fee_type == "percentage":
            late_fee = lease.monthly_rent * (lease.late_fee / 100)
        else:
            late_fee = lease.late_fee

        total_due = lease.monthly_rent + late_fee

        template_data = {
            "tenant_name": tenant.name,
            "rent_amount": f"{lease.monthly_rent:,.2f}",
            "property_address": property_address,
            "days_late": days_late,
            "late_fee": f"{late_fee:,.2f}",
            "total_due": f"{total_due:,.2f}",
            "cure_period": self.config["cure_period_days"],
        }

        # Send severely late / demand notice
        if tenant.contact and tenant.contact.email:
            self.notifications.send_from_template(
                template_id="rent_severely_late",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
                priority=NotificationPriority.URGENT,
            )
            actions_taken.append(f"Sent formal demand letter to {tenant.contact.email}")

        # Urgent owner notification
        owner = self.engine.get_owner(lease.owner_id)
        if owner and owner.contact and owner.contact.email:
            owner_subject = f"URGENT: Severely Late Rent - {property_address}"
            owner_body = f"""Dear {owner.name},

URGENT: The rent for your property at {property_address} is now severely past due.

Current Status:
- Days Late: {days_late}
- Tenant: {tenant.name}
- Total Due: ${total_due:,.2f}

Action Taken:
We have sent the tenant a formal demand letter with a {self.config['cure_period_days']}-day cure period. This letter puts them on notice that failure to pay may result in legal proceedings.

Next Steps:
If payment is not received within the cure period, we will need to discuss options including:
1. Payment plan arrangement
2. Cash for keys agreement
3. Initiation of eviction proceedings

Please contact us at {self.notifications.company_info['company_phone']} to discuss how you would like to proceed.

{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=owner_subject,
                body=owner_body,
                priority=NotificationPriority.URGENT,
            )
            actions_taken.append(f"Sent urgent notification to owner {owner.name}")

        tenant.log_communication(
            comm_type="email",
            subject="Formal Demand Letter",
            details=f"Severely late notice sent. {self.config['cure_period_days']}-day cure period issued."
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LateRentWorkflow.handle_severely_late",
            message=f"Severely late notice sent - {days_late} days late",
            actions_taken=actions_taken,
        )

    def handle_payment_received(self, event: Event) -> EventResult:
        """
        Handle payment received - send confirmation and update status.

        Trigger: Rent payment recorded
        Actions:
        - Send payment confirmation to tenant
        - Notify owner of payment
        - Reset late status
        """
        payment = event.payload.get("payment")
        tenant: Tenant = event.payload.get("tenant")
        lease: Lease = event.payload.get("lease")
        property: Property = event.payload.get("property")

        actions_taken = []

        if tenant and tenant.contact and tenant.contact.email:
            property_address = str(property.address) if property and property.address else "your rental"

            subject = f"Payment Received - Thank You!"
            body = f"""Dear {tenant.name},

Thank you! We have received your payment.

Property: {property_address}
Amount Received: ${payment.amount if payment else lease.monthly_rent:,.2f}
Date: {date.today().strftime('%B %d, %Y')}

Your account is now current. Thank you for your prompt payment.

{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent payment confirmation to tenant")

            tenant.log_communication(
                comm_type="email",
                subject="Payment Confirmation",
                details=f"Confirmed receipt of payment"
            )

        return EventResult(
            success=True,
            event=event,
            handler_name="LateRentWorkflow.handle_payment_received",
            message="Payment confirmation sent",
            actions_taken=actions_taken,
        )
