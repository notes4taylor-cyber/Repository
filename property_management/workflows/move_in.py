"""
Move-In Workflow for PropertyFlow.

Automates the entire new tenant onboarding process:
1. Lease signed -> Welcome packet + setup instructions
2. 7 days before move-in -> Reminder with checklist
3. 1 day before -> Final reminder
4. Move-in day -> Inspection scheduling
5. After inspection -> Account activation complete

One trigger, five automated actions.
"""

from datetime import datetime, date, timedelta
from typing import TYPE_CHECKING

from ..core.events import Event, EventBus, EventType, EventResult
from ..core.notifications import NotificationService, NotificationType, NotificationPriority
from ..core.models import Lease, LeaseStatus, Tenant, TenantStatus, Property, PropertyStatus, Owner

if TYPE_CHECKING:
    from ..core.engine import AutomationEngine


class MoveInWorkflow:
    """
    Automates new tenant move-in process.

    Handles:
    - Welcome packet delivery
    - Utility setup instructions
    - Move-in inspection scheduling
    - Rent collection account setup
    - Owner notifications
    """

    def __init__(self):
        self.engine: "AutomationEngine" = None
        self.event_bus: EventBus = None
        self.notifications: NotificationService = None

        # Configuration
        self.config = {
            "send_welcome_packet": True,
            "inspection_reminder_days": 1,
            "pre_move_in_reminder_days": 7,
        }

        # Local utility information (configurable per region)
        self.utility_info = {
            "electric_company": "Dominion Energy",
            "electric_phone": "(866) 366-4357",
            "gas_company": "Washington Gas",
            "gas_phone": "(844) 927-4427",
            "water_company": "Loudoun Water",
            "water_phone": "(571) 291-7880",
        }

    def register(self, engine: "AutomationEngine"):
        """Register this workflow with the automation engine."""
        self.engine = engine
        self.event_bus = engine.event_bus
        self.notifications = engine.notifications

        # Subscribe to move-in events
        self.event_bus.subscribe(
            EventType.LEASE_SIGNED,
            self.handle_lease_signed,
            "MoveInWorkflow.handle_lease_signed"
        )

        self.event_bus.subscribe(
            EventType.MOVE_IN_SCHEDULED,
            self.handle_move_in_scheduled,
            "MoveInWorkflow.handle_move_in_scheduled"
        )

        self.event_bus.subscribe(
            EventType.MOVE_IN_7_DAYS,
            self.handle_7_day_reminder,
            "MoveInWorkflow.handle_7_day_reminder"
        )

        self.event_bus.subscribe(
            EventType.MOVE_IN_1_DAY,
            self.handle_1_day_reminder,
            "MoveInWorkflow.handle_1_day_reminder"
        )

        self.event_bus.subscribe(
            EventType.MOVE_IN_INSPECTION_COMPLETED,
            self.handle_inspection_completed,
            "MoveInWorkflow.handle_inspection_completed"
        )

        self.event_bus.subscribe(
            EventType.MOVE_IN_COMPLETED,
            self.handle_move_in_completed,
            "MoveInWorkflow.handle_move_in_completed"
        )

        # Daily check for upcoming move-ins
        self.event_bus.subscribe(
            EventType.DAILY_CHECK,
            self.check_upcoming_move_ins,
            "MoveInWorkflow.check_upcoming_move_ins"
        )

    def handle_lease_signed(self, event: Event) -> EventResult:
        """
        Handle lease signed - send welcome packet.

        Trigger: New lease is signed
        Actions:
        - Send welcome email with all essential information
        - Send utility setup instructions
        - Send payment setup information
        - Schedule move-in inspection
        - Notify owner
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not lease or not tenant:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_lease_signed",
                errors=["Missing lease or tenant data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your new home"

        # Prepare template data for welcome packet
        inspection_date = lease.start_date
        inspection_time = "10:00 AM"  # Default, should be scheduled

        template_data = {
            "tenant_name": tenant.name,
            "property_address": property_address,
            "move_in_date": lease.start_date.strftime("%B %d, %Y"),
            "monthly_rent": f"{lease.monthly_rent:,.2f}",
            "rent_due_day": self._ordinal(lease.rent_due_day),
            "inspection_date": inspection_date.strftime("%B %d, %Y"),
            "inspection_time": inspection_time,
            "key_pickup_instructions": "Keys will be provided at the move-in inspection.",
            "payment_instructions": f"Rent is due on the {self._ordinal(lease.rent_due_day)} of each month. You can pay online at {self.notifications.company_info['payment_portal_url']} or by check mailed to our office.",
            **self.utility_info,
        }

        # Send welcome packet email
        if tenant.contact and tenant.contact.email:
            self.notifications.send_from_template(
                template_id="move_in_welcome",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent welcome packet to tenant")

        # Update tenant status
        tenant.status = TenantStatus.PENDING
        tenant.move_in_date = lease.start_date
        tenant.property_id = lease.property_id

        # Update property status
        if property:
            property.status = PropertyStatus.PENDING_MOVE_IN
            property.current_tenant_id = tenant.id
            property.current_lease_id = lease.id

        # Notify owner
        if owner and owner.contact and owner.contact.email:
            subject = f"New Tenant Move-In Scheduled: {property_address}"
            body = f"""Dear {owner.name},

Great news! A new tenant has signed a lease for your property at {property_address}.

Tenant Details:
- Name: {tenant.name}
- Move-In Date: {lease.start_date.strftime('%B %d, %Y')}
- Lease Term: {(lease.end_date - lease.start_date).days // 30} months
- Monthly Rent: ${lease.monthly_rent:,.2f}
- Security Deposit: ${lease.security_deposit:,.2f}

Next Steps:
1. Move-in inspection scheduled for {inspection_date.strftime('%B %d, %Y')}
2. Tenant will set up utilities in their name
3. First rent payment due on move-in

We will keep you updated throughout the process.

Best regards,
{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Notified owner of new tenant")

        # Set up move-in inspection
        lease.move_in_inspection_date = lease.start_date

        tenant.log_communication(
            comm_type="email",
            subject="Welcome Packet",
            details="Sent welcome packet with move-in instructions"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_lease_signed",
            message=f"Welcome packet sent for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_move_in_scheduled(self, event: Event) -> EventResult:
        """
        Handle move-in being scheduled.

        Trigger: Move-in date is confirmed/scheduled
        Actions:
        - Confirm date with tenant
        - Schedule inspection
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_move_in_scheduled",
                errors=["Missing lease data"]
            )

        actions_taken = []

        # Confirmation already sent in welcome packet
        # This event is for any additional scheduling needs

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_move_in_scheduled",
            message=f"Move-in scheduled for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_7_day_reminder(self, event: Event) -> EventResult:
        """
        Handle 7-day move-in reminder.

        Trigger: 7 days before move-in date
        Actions:
        - Send reminder with checklist
        - Verify utility setup
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")

        if not lease or not tenant:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_7_day_reminder",
                errors=["Missing lease or tenant data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your new home"

        if tenant.contact and tenant.contact.email:
            subject = f"7 Days Until Move-In: {property_address}"
            body = f"""Dear {tenant.name},

Your move-in date is just one week away! Here's a quick reminder of everything you need to have ready.

Move-In Date: {lease.start_date.strftime('%B %d, %Y')}
Property: {property_address}

PRE-MOVE-IN CHECKLIST:
□ Set up utilities in your name (electric, gas, water)
□ Arrange renters insurance (required)
□ Prepare first month's rent + any remaining deposit
□ Schedule movers or moving truck
□ Notify post office of address change
□ Update address with bank, employer, etc.

MOVE-IN DAY:
□ Bring photo ID
□ Bring payment (if not already submitted)
□ Plan to arrive on time for inspection
□ Be ready to do a walkthrough of the unit

Inspection Time: {lease.move_in_inspection_date.strftime('%B %d, %Y') if lease.move_in_inspection_date else lease.start_date.strftime('%B %d, %Y')} at 10:00 AM

Questions? Call us at {self.notifications.company_info['company_phone']}

See you soon!
{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent 7-day reminder to tenant")

        tenant.log_communication(
            comm_type="email",
            subject="7-Day Move-In Reminder",
            details="Sent pre-move-in checklist"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_7_day_reminder",
            message=f"7-day reminder sent for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_1_day_reminder(self, event: Event) -> EventResult:
        """
        Handle 1-day move-in reminder.

        Trigger: 1 day before move-in
        Actions:
        - Send final reminder
        - Confirm inspection time
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")

        if not lease or not tenant:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_1_day_reminder",
                errors=["Missing lease or tenant data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your new home"
        inspection_date = lease.move_in_inspection_date or lease.start_date

        # Send email reminder
        if tenant.contact and tenant.contact.email:
            template_data = {
                "tenant_name": tenant.name,
                "property_address": property_address,
                "inspection_date": inspection_date.strftime("%B %d, %Y"),
                "inspection_time": "10:00 AM",
            }

            self.notifications.send_from_template(
                template_id="move_in_inspection_reminder",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent day-before reminder email")

        # Send SMS reminder
        if tenant.contact and tenant.contact.phone:
            self.notifications.send_from_template(
                template_id="move_in_reminder_sms",
                recipient_id=tenant.id,
                recipient_phone=tenant.contact.phone,
                template_data={
                    "property_address": property_address,
                    "inspection_time": "10:00 AM",
                },
                notification_type=NotificationType.SMS,
            )
            actions_taken.append("Sent day-before reminder SMS")

        tenant.log_communication(
            comm_type="email+sms",
            subject="Move-In Tomorrow Reminder",
            details="Sent final move-in reminder"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_1_day_reminder",
            message=f"1-day reminder sent for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_inspection_completed(self, event: Event) -> EventResult:
        """
        Handle move-in inspection completed.

        Trigger: Inspection is completed
        Actions:
        - Record inspection completion
        - Send inspection report to tenant
        - Update lease record
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_inspection_completed",
                errors=["Missing lease data"]
            )

        actions_taken = []

        # Update lease record
        lease.move_in_inspection_completed = True
        lease.move_in_inspection_date = date.today()
        actions_taken.append("Recorded inspection completion")

        property_address = str(property.address) if property and property.address else "your new home"

        # Send inspection confirmation to tenant
        if tenant and tenant.contact and tenant.contact.email:
            subject = f"Move-In Inspection Complete - {property_address}"
            body = f"""Dear {tenant.name},

Your move-in inspection has been completed for {property_address}.

The condition of the unit has been documented and you should have received a copy of the inspection report. Please review it and let us know within 48 hours if you notice any discrepancies.

Your tenancy is now officially active! Here are some important reminders:

RENT INFORMATION:
- Monthly Rent: ${lease.monthly_rent:,.2f}
- Due Date: {self._ordinal(lease.rent_due_day)} of each month
- Grace Period: {lease.grace_period_days} days
- Late Fee: ${lease.late_fee:,.2f} after grace period

MAINTENANCE REQUESTS:
To submit a maintenance request, email us at {self.notifications.company_info['company_email']} or call {self.notifications.company_info['company_phone']}.

For emergencies (water leak, no heat, fire, etc.), call our emergency line: {self.notifications.company_info['emergency_phone']}

Welcome home!

{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""
            self.notifications.send_email(
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent inspection completion notice to tenant")

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_inspection_completed",
            message=f"Inspection completed for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_move_in_completed(self, event: Event) -> EventResult:
        """
        Handle move-in completed.

        Trigger: Tenant has moved in
        Actions:
        - Activate tenant account
        - Update property status
        - Final notification to owner
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not lease or not tenant:
            return EventResult(
                success=False,
                event=event,
                handler_name="MoveInWorkflow.handle_move_in_completed",
                errors=["Missing lease or tenant data"]
            )

        actions_taken = []

        # Activate tenant
        tenant.status = TenantStatus.ACTIVE
        tenant.move_in_date = date.today()
        actions_taken.append("Activated tenant account")

        # Activate lease
        lease.status = LeaseStatus.ACTIVE
        actions_taken.append("Activated lease")

        # Update property
        if property:
            property.status = PropertyStatus.OCCUPIED
            property.is_listed = False
            actions_taken.append("Updated property status to occupied")

        property_address = str(property.address) if property and property.address else "the property"

        # Notify owner
        if owner and owner.contact and owner.contact.email:
            subject = f"Move-In Complete: {property_address}"
            body = f"""Dear {owner.name},

The new tenant has successfully moved into your property at {property_address}.

Move-In Summary:
- Tenant: {tenant.name}
- Move-In Date: {date.today().strftime('%B %d, %Y')}
- Monthly Rent: ${lease.monthly_rent:,.2f}
- Lease End Date: {lease.end_date.strftime('%B %d, %Y')}

The move-in inspection has been completed and documented. Rent collection is now active.

You will receive your first owner statement at the end of this month.

Best regards,
{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent move-in completion notice to owner")

        tenant.log_communication(
            comm_type="system",
            subject="Move-In Completed",
            details="Tenant move-in process completed, account activated"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.handle_move_in_completed",
            message=f"Move-in completed for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def check_upcoming_move_ins(self, event: Event) -> EventResult:
        """
        Daily check for upcoming move-ins that need reminders.

        Trigger: Daily check event
        Actions:
        - Find leases with move-in in 7 days -> send reminder
        - Find leases with move-in tomorrow -> send final reminder
        """
        actions_taken = []
        follow_up_events = []

        today = date.today()

        for lease in self.engine.data.leases.values():
            if lease.status != LeaseStatus.PENDING:
                continue

            if not lease.start_date:
                continue

            days_until_move_in = (lease.start_date - today).days
            tenant = self.engine.get_tenant(lease.tenant_id)
            property = self.engine.get_property(lease.property_id)

            # 7-day reminder
            if days_until_move_in == 7:
                follow_up_events.append(Event(
                    EventType.MOVE_IN_7_DAYS,
                    {
                        "lease": lease,
                        "tenant": tenant,
                        "property": property,
                    }
                ))
                actions_taken.append(f"Triggered 7-day reminder for lease {lease.id}")

            # 1-day reminder
            elif days_until_move_in == 1:
                follow_up_events.append(Event(
                    EventType.MOVE_IN_1_DAY,
                    {
                        "lease": lease,
                        "tenant": tenant,
                        "property": property,
                    }
                ))
                actions_taken.append(f"Triggered 1-day reminder for lease {lease.id}")

        return EventResult(
            success=True,
            event=event,
            handler_name="MoveInWorkflow.check_upcoming_move_ins",
            message="Daily move-in check completed",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    # =================
    # Helper Methods
    # =================

    def _ordinal(self, n: int) -> str:
        """Convert a number to its ordinal representation."""
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return f"{n}{suffix}"
