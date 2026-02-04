"""
Lease Renewal Workflow for PropertyFlow.

Automates the entire lease renewal process:
1. 90 days before expiry -> Internal alert
2. 60 days before expiry -> Send renewal offer to tenant
3. No response after 14 days -> Send reminder
4. No response after 30 days -> Begin marketing unit
5. Tenant declines -> Prepare for turnover
6. Tenant accepts -> Generate renewal lease

This replaces the manual "remember to send renewal" process.
"""

from datetime import datetime, date, timedelta
from typing import TYPE_CHECKING, List

from ..core.events import Event, EventBus, EventType, EventResult
from ..core.notifications import NotificationService, NotificationType, NotificationPriority
from ..core.models import Lease, LeaseStatus, Tenant, Property, Owner, PropertyStatus

if TYPE_CHECKING:
    from ..core.engine import AutomationEngine


class LeaseRenewalWorkflow:
    """
    Automates lease renewal outreach and tracking.

    Handles:
    - Proactive renewal offers at 60 days
    - Follow-up reminders if no response
    - Coordination with marketing for non-renewals
    - Move-out preparation for vacating tenants
    """

    def __init__(self):
        self.engine: "AutomationEngine" = None
        self.event_bus: EventBus = None
        self.notifications: NotificationService = None

        # Configuration
        self.config = {
            "first_offer_days": 60,  # Days before expiry to send offer
            "reminder_days": 14,  # Days after offer to send reminder
            "final_deadline_days": 30,  # Days after offer to begin marketing
            "rent_increase_percent": 3.0,  # Default annual increase
            "deposit_return_days": 30,  # Days to return deposit after move-out
        }

        # Renewal options template
        self.renewal_options = [
            {"term": 12, "increase": 0, "description": "12-month lease at current rate"},
            {"term": 12, "increase": 3.0, "description": "12-month lease with 3% increase"},
            {"term": 6, "increase": 5.0, "description": "6-month lease with 5% increase"},
            {"term": 1, "increase": 10.0, "description": "Month-to-month with 10% increase"},
        ]

    def register(self, engine: "AutomationEngine"):
        """Register this workflow with the automation engine."""
        self.engine = engine
        self.event_bus = engine.event_bus
        self.notifications = engine.notifications

        # Subscribe to lease events
        self.event_bus.subscribe(
            EventType.LEASE_EXPIRING_90_DAYS,
            self.handle_90_day_warning,
            "LeaseRenewalWorkflow.handle_90_day_warning"
        )

        self.event_bus.subscribe(
            EventType.LEASE_EXPIRING_60_DAYS,
            self.handle_60_day_offer,
            "LeaseRenewalWorkflow.handle_60_day_offer"
        )

        self.event_bus.subscribe(
            EventType.LEASE_EXPIRING_30_DAYS,
            self.handle_30_day_deadline,
            "LeaseRenewalWorkflow.handle_30_day_deadline"
        )

        self.event_bus.subscribe(
            EventType.LEASE_RENEWAL_ACCEPTED,
            self.handle_renewal_accepted,
            "LeaseRenewalWorkflow.handle_renewal_accepted"
        )

        self.event_bus.subscribe(
            EventType.LEASE_RENEWAL_DECLINED,
            self.handle_renewal_declined,
            "LeaseRenewalWorkflow.handle_renewal_declined"
        )

        # Daily check for lease expirations
        self.event_bus.subscribe(
            EventType.DAILY_CHECK,
            self.check_lease_renewals,
            "LeaseRenewalWorkflow.check_lease_renewals"
        )

    def handle_90_day_warning(self, event: Event) -> EventResult:
        """
        Handle 90-day lease expiration warning - internal alert.

        Trigger: Lease expires in 90 days
        Actions:
        - Log internal alert
        - Prepare renewal strategy
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LeaseRenewalWorkflow.handle_90_day_warning",
                errors=["Missing lease data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "property"

        # Notify owner about upcoming expiration
        if owner and owner.contact and owner.contact.email:
            subject = f"Upcoming Lease Expiration: {property_address}"
            body = f"""Dear {owner.name},

This is an advance notice that the lease for your property at {property_address} will expire in 90 days.

Current Details:
- Tenant: {tenant.name if tenant else 'N/A'}
- Lease End Date: {lease.end_date.strftime('%B %d, %Y')}
- Current Rent: ${lease.monthly_rent:,.2f}/month

Our Renewal Process:
1. In 30 days (at 60 days before expiry), we will send the tenant a renewal offer
2. We'll follow up if they don't respond
3. If they decline, we'll begin marketing the unit

If you would like to:
- Adjust the renewal terms (rent increase, lease length options)
- Not offer a renewal to this tenant
- Make any changes to the property

Please let us know within the next 30 days so we can incorporate your preferences into the renewal offer.

Best regards,
{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent 90-day advance notice to owner")

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.handle_90_day_warning",
            message=f"90-day warning processed for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_60_day_offer(self, event: Event) -> EventResult:
        """
        Handle 60-day expiration - send renewal offer.

        Trigger: Lease expires in 60 days
        Actions:
        - Generate renewal options
        - Send renewal offer to tenant
        - Set response deadline
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")

        if not lease or not tenant:
            return EventResult(
                success=False,
                event=event,
                handler_name="LeaseRenewalWorkflow.handle_60_day_offer",
                errors=["Missing lease or tenant data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your rental"

        # Generate renewal options
        options_text = self._generate_renewal_options_text(lease)

        # Calculate response deadline
        response_deadline = date.today() + timedelta(days=self.config["final_deadline_days"])

        template_data = {
            "tenant_name": tenant.name,
            "property_address": property_address,
            "lease_end_date": lease.end_date.strftime("%B %d, %Y"),
            "current_rent": f"{lease.monthly_rent:,.2f}",
            "renewal_options": options_text,
            "response_deadline": response_deadline.strftime("%B %d, %Y"),
        }

        # Send renewal offer
        if tenant.contact and tenant.contact.email:
            self.notifications.send_from_template(
                template_id="lease_renewal_offer",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent renewal offer to tenant")

        # Update lease record
        lease.renewal_offered = True
        lease.renewal_offer_date = date.today()
        lease.renewal_response = "pending"

        tenant.log_communication(
            comm_type="email",
            subject="Lease Renewal Offer",
            details=f"Renewal offer sent. Response deadline: {response_deadline}"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.handle_60_day_offer",
            message=f"Renewal offer sent for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_30_day_deadline(self, event: Event) -> EventResult:
        """
        Handle 30-day expiration - final deadline or begin marketing.

        Trigger: Lease expires in 30 days
        Actions:
        - If no response: Send final reminder and prepare marketing
        - If declined: Prepare for turnover
        - If accepted: Verify renewal is in progress
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LeaseRenewalWorkflow.handle_30_day_deadline",
                errors=["Missing lease data"]
            )

        actions_taken = []
        follow_up_events = []

        property_address = str(property.address) if property and property.address else "your rental"

        # Check renewal status
        if lease.renewal_response == "pending":
            # No response yet - send reminder
            if tenant and tenant.contact and tenant.contact.email:
                template_data = {
                    "tenant_name": tenant.name,
                    "property_address": property_address,
                    "offer_date": lease.renewal_offer_date.strftime("%B %d, %Y") if lease.renewal_offer_date else "recently",
                    "lease_end_date": lease.end_date.strftime("%B %d, %Y"),
                    "response_deadline": (date.today() + timedelta(days=7)).strftime("%B %d, %Y"),
                }

                self.notifications.send_from_template(
                    template_id="lease_renewal_reminder",
                    recipient_id=tenant.id,
                    recipient_email=tenant.contact.email,
                    template_data=template_data,
                    priority=NotificationPriority.HIGH,
                )
                actions_taken.append("Sent final renewal reminder to tenant")

                # Also send SMS
                if tenant.contact.phone:
                    self.notifications.send_from_template(
                        template_id="lease_renewal_reminder_sms",
                        recipient_id=tenant.id,
                        recipient_phone=tenant.contact.phone,
                        template_data={
                            "property_address": property_address,
                            "response_deadline": (date.today() + timedelta(days=7)).strftime("%B %d"),
                        },
                        notification_type=NotificationType.SMS,
                        priority=NotificationPriority.HIGH,
                    )
                    actions_taken.append("Sent SMS reminder to tenant")

            # Notify owner that we may need to market
            if owner and owner.contact and owner.contact.email:
                subject = f"Lease Renewal Update: {property_address} - No Response Yet"
                body = f"""Dear {owner.name},

The tenant at {property_address} has not yet responded to our lease renewal offer.

Current Status:
- Lease Expires: {lease.end_date.strftime('%B %d, %Y')}
- Renewal Offer Sent: {lease.renewal_offer_date.strftime('%B %d, %Y') if lease.renewal_offer_date else 'Recently'}
- Tenant Response: Pending

We have sent a final reminder with a 7-day deadline. If we don't receive a response, we will begin preparing the unit for marketing.

We'll keep you updated.

{self.notifications.company_info['company_name']}
"""
                self.notifications.send_email(
                    recipient_id=owner.id,
                    recipient_email=owner.contact.email,
                    subject=subject,
                    body=body,
                )
                actions_taken.append("Notified owner of pending status")

            # Trigger event for no response
            follow_up_events.append(Event(
                EventType.LEASE_RENEWAL_NO_RESPONSE,
                {"lease": lease, "tenant": tenant, "property": property, "owner": owner}
            ))

        elif lease.renewal_response == "declined":
            # Already declined - should be preparing for turnover
            actions_taken.append("Lease previously declined - turnover in progress")

        elif lease.renewal_response == "accepted":
            # Already accepted - verify renewal is being processed
            actions_taken.append("Lease renewal already accepted")

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.handle_30_day_deadline",
            message=f"30-day deadline handled for lease {lease.id}",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    def handle_renewal_accepted(self, event: Event) -> EventResult:
        """
        Handle tenant accepting renewal.

        Trigger: Tenant accepts renewal offer
        Actions:
        - Confirm acceptance with tenant
        - Generate renewal lease
        - Notify owner
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")
        renewal_term: int = event.payload.get("renewal_term", 12)
        new_rent: float = event.payload.get("new_rent", lease.monthly_rent)

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LeaseRenewalWorkflow.handle_renewal_accepted",
                errors=["Missing lease data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your rental"

        # Update lease record
        lease.renewal_response = "accepted"
        lease.renewal_response_date = date.today()

        # Calculate new lease dates
        new_start = lease.end_date + timedelta(days=1)
        new_end = new_start + timedelta(days=renewal_term * 30)  # Approximate

        # Send confirmation to tenant
        if tenant and tenant.contact and tenant.contact.email:
            subject = f"Lease Renewal Confirmed - {property_address}"
            body = f"""Dear {tenant.name},

Thank you for renewing your lease at {property_address}!

Renewal Details:
─────────────────────────────
New Lease Term: {renewal_term} months
New Start Date: {new_start.strftime('%B %d, %Y')}
New End Date: {new_end.strftime('%B %d, %Y')}
Monthly Rent: ${new_rent:,.2f}
─────────────────────────────

Next Steps:
1. We will prepare your renewal lease agreement
2. You will receive the lease for signature within the next few days
3. Please sign and return before your current lease expires

Thank you for being a valued tenant. We look forward to another great year!

{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""
            self.notifications.send_email(
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Sent renewal confirmation to tenant")

        # Notify owner
        if owner and owner.contact and owner.contact.email:
            subject = f"Great News! Lease Renewed at {property_address}"
            body = f"""Dear {owner.name},

Great news! The tenant at {property_address} has renewed their lease.

Renewal Details:
- Tenant: {tenant.name if tenant else 'N/A'}
- New Term: {renewal_term} months
- New Rent: ${new_rent:,.2f}/month
- Previous Rent: ${lease.monthly_rent:,.2f}/month
- Change: ${new_rent - lease.monthly_rent:+,.2f}/month

New Lease Period: {new_start.strftime('%B %d, %Y')} to {new_end.strftime('%B %d, %Y')}

We will prepare and execute the renewal lease agreement.

Best regards,
{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
            )
            actions_taken.append("Notified owner of renewal")

        tenant.log_communication(
            comm_type="email",
            subject="Lease Renewal Confirmed",
            details=f"Renewal accepted: {renewal_term} months at ${new_rent}/month"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.handle_renewal_accepted",
            message=f"Renewal accepted for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def handle_renewal_declined(self, event: Event) -> EventResult:
        """
        Handle tenant declining renewal.

        Trigger: Tenant declines renewal offer
        Actions:
        - Confirm move-out date with tenant
        - Send move-out instructions
        - Begin marketing unit
        - Notify owner
        """
        lease: Lease = event.payload.get("lease")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not lease:
            return EventResult(
                success=False,
                event=event,
                handler_name="LeaseRenewalWorkflow.handle_renewal_declined",
                errors=["Missing lease data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your rental"

        # Update lease record
        lease.renewal_response = "declined"
        lease.renewal_response_date = date.today()

        # Send move-out instructions to tenant
        if tenant and tenant.contact and tenant.contact.email:
            template_data = {
                "tenant_name": tenant.name,
                "property_address": property_address,
                "lease_end_date": lease.end_date.strftime("%B %d, %Y"),
                "security_deposit": f"{lease.security_deposit:,.2f}",
                "deposit_return_days": self.config["deposit_return_days"],
            }

            self.notifications.send_from_template(
                template_id="lease_not_renewing_notice",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent move-out instructions to tenant")

        # Notify owner and discuss next steps
        if owner and owner.contact and owner.contact.email:
            subject = f"Tenant Not Renewing: {property_address}"
            body = f"""Dear {owner.name},

The tenant at {property_address} has decided not to renew their lease.

Current Status:
- Tenant: {tenant.name if tenant else 'N/A'}
- Move-Out Date: {lease.end_date.strftime('%B %d, %Y')}
- Current Rent: ${lease.monthly_rent:,.2f}/month

Next Steps:
1. We will schedule a move-out inspection
2. Marketing of the unit will begin (if you approve)
3. We'll coordinate showings with the current tenant
4. Security deposit will be processed after move-out inspection

Market Analysis:
Based on current market conditions in the area, we recommend listing at ${lease.monthly_rent * 1.03:,.2f}/month (3% increase).

Please let us know if you have any special instructions for marketing the unit or if you'd like to discuss the listing price.

{self.notifications.company_info['company_name']}
{self.notifications.company_info['company_phone']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append("Notified owner of non-renewal")

        # Update property status
        if property:
            property.status = PropertyStatus.PENDING_MOVE_OUT
            actions_taken.append("Updated property status to pending move-out")

        tenant.log_communication(
            comm_type="email",
            subject="Move-Out Instructions",
            details=f"Tenant declining renewal. Move-out: {lease.end_date}"
        )

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.handle_renewal_declined",
            message=f"Non-renewal processed for lease {lease.id}",
            actions_taken=actions_taken,
        )

    def check_lease_renewals(self, event: Event) -> EventResult:
        """
        Daily check for lease renewal follow-ups.

        Trigger: Daily check event
        Actions:
        - Check for leases needing reminder (14 days after offer, no response)
        - Check for leases past final deadline
        """
        actions_taken = []

        today = date.today()

        for lease in self.engine.get_active_leases():
            # Check if we need to send a reminder
            if (lease.renewal_offered and
                lease.renewal_response == "pending" and
                lease.renewal_offer_date):

                days_since_offer = (today - lease.renewal_offer_date).days

                # Send reminder at 14 days if no response
                if days_since_offer == self.config["reminder_days"]:
                    tenant = self.engine.get_tenant(lease.tenant_id)
                    property = self.engine.get_property(lease.property_id)
                    owner = self.engine.get_owner(lease.owner_id)

                    property_address = str(property.address) if property and property.address else "your rental"

                    if tenant and tenant.contact and tenant.contact.email:
                        template_data = {
                            "tenant_name": tenant.name,
                            "property_address": property_address,
                            "offer_date": lease.renewal_offer_date.strftime("%B %d, %Y"),
                            "lease_end_date": lease.end_date.strftime("%B %d, %Y"),
                            "response_deadline": (today + timedelta(days=16)).strftime("%B %d, %Y"),
                        }

                        self.notifications.send_from_template(
                            template_id="lease_renewal_reminder",
                            recipient_id=tenant.id,
                            recipient_email=tenant.contact.email,
                            template_data=template_data,
                        )
                        actions_taken.append(f"Sent renewal reminder for lease {lease.id}")

        return EventResult(
            success=True,
            event=event,
            handler_name="LeaseRenewalWorkflow.check_lease_renewals",
            message="Daily lease renewal check completed",
            actions_taken=actions_taken,
        )

    # =================
    # Helper Methods
    # =================

    def _generate_renewal_options_text(self, lease: Lease) -> str:
        """Generate formatted renewal options text."""
        options_lines = []

        for i, option in enumerate(self.renewal_options, 1):
            new_rent = lease.monthly_rent * (1 + option["increase"] / 100)
            term_text = f"{option['term']}-month" if option['term'] > 1 else "Month-to-month"
            increase_text = f"({option['increase']}% increase)" if option["increase"] > 0 else "(no increase)"

            options_lines.append(
                f"Option {i}: {term_text} at ${new_rent:,.2f}/month {increase_text}"
            )

        return "\n".join(options_lines)
