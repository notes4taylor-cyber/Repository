"""
Maintenance Request Workflow for PropertyFlow.

Automates the entire maintenance request lifecycle:
1. Request received -> Triage and acknowledge
2. Triaged -> Auto-assign vendor based on category
3. Vendor assigned -> Send work order, track response
4. Scheduled -> Notify tenant and owner
5. Completed -> Get confirmation, notify tenant, update owner
6. Closed -> Final documentation

This workflow handles the 6-8 manual touches per request automatically.
"""

from datetime import datetime, date, timedelta
from typing import TYPE_CHECKING, Optional

from ..core.events import Event, EventBus, EventType, EventResult
from ..core.notifications import NotificationService, NotificationType, NotificationPriority
from ..core.models import (
    MaintenanceRequest, MaintenanceStatus, MaintenancePriority, MaintenanceCategory,
    Tenant, Property, Owner, Vendor
)

if TYPE_CHECKING:
    from ..core.engine import AutomationEngine


class MaintenanceWorkflow:
    """
    Automates maintenance request handling from creation to completion.

    Handles:
    - Automatic triage based on keywords and category
    - Vendor matching and assignment
    - Scheduling coordination
    - Status notifications to all parties
    - Follow-up reminders when vendors don't respond
    - Cost approval for expensive repairs
    """

    def __init__(self):
        self.engine: "AutomationEngine" = None
        self.event_bus: EventBus = None
        self.notifications: NotificationService = None

        # Configuration
        self.config = {
            "auto_triage": True,
            "auto_assign_vendor": True,
            "owner_approval_threshold": 500.00,  # Require approval for costs over this
            "vendor_response_hours": 24,
            "emergency_response_hours": 4,
            "follow_up_reminder_hours": 48,
        }

        # Keywords for auto-triage priority detection
        self.emergency_keywords = [
            "flood", "flooding", "water everywhere", "gas leak", "no heat",
            "fire", "smoke", "electrical fire", "sparking", "broken pipe",
            "sewage", "security", "break-in", "broken window", "locked out",
            "no hot water", "carbon monoxide"
        ]

        self.urgent_keywords = [
            "ac not working", "air conditioning", "no cooling", "refrigerator",
            "stove not working", "oven broken", "dishwasher leak", "toilet clogged",
            "garbage disposal", "washer leak", "dryer not heating"
        ]

    def register(self, engine: "AutomationEngine"):
        """Register this workflow with the automation engine."""
        self.engine = engine
        self.event_bus = engine.event_bus
        self.notifications = engine.notifications

        # Subscribe to maintenance events
        self.event_bus.subscribe(
            EventType.MAINTENANCE_REQUEST_CREATED,
            self.handle_request_created,
            "MaintenanceWorkflow.handle_request_created"
        )

        self.event_bus.subscribe(
            EventType.MAINTENANCE_TRIAGED,
            self.handle_triaged,
            "MaintenanceWorkflow.handle_triaged"
        )

        self.event_bus.subscribe(
            EventType.MAINTENANCE_VENDOR_ASSIGNED,
            self.handle_vendor_assigned,
            "MaintenanceWorkflow.handle_vendor_assigned"
        )

        self.event_bus.subscribe(
            EventType.MAINTENANCE_SCHEDULED,
            self.handle_scheduled,
            "MaintenanceWorkflow.handle_scheduled"
        )

        self.event_bus.subscribe(
            EventType.MAINTENANCE_COMPLETED,
            self.handle_completed,
            "MaintenanceWorkflow.handle_completed"
        )

        self.event_bus.subscribe(
            EventType.VENDOR_NO_RESPONSE,
            self.handle_vendor_no_response,
            "MaintenanceWorkflow.handle_vendor_no_response"
        )

        self.event_bus.subscribe(
            EventType.MAINTENANCE_PENDING_APPROVAL,
            self.handle_pending_approval,
            "MaintenanceWorkflow.handle_pending_approval"
        )

    def handle_request_created(self, event: Event) -> EventResult:
        """
        Handle new maintenance request - acknowledge and triage.

        Trigger: New maintenance request submitted
        Actions:
        - Send acknowledgment to tenant
        - Auto-triage based on description/category
        - Escalate emergencies immediately
        """
        request: MaintenanceRequest = event.payload.get("request")
        tenant: Tenant = event.payload.get("tenant")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")

        if not request:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_request_created",
                errors=["Missing request data"]
            )

        actions_taken = []
        follow_up_events = []

        property_address = str(property.address) if property and property.address else "the property"

        # Step 1: Send acknowledgment to tenant
        if tenant and tenant.contact and tenant.contact.email:
            entry_text = ""
            if request.tenant_permission_to_enter:
                entry_text = "You have granted permission for our vendor to enter if you're not home."
            else:
                entry_text = "Please ensure someone is available to provide access, or contact us to grant entry permission."

            template_data = {
                "tenant_name": tenant.name,
                "property_address": property_address,
                "request_id": request.id,
                "issue_title": request.title,
                "priority": request.priority.value.title(),
                "entry_permission_text": entry_text,
            }

            self.notifications.send_from_template(
                template_id="maintenance_received",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent acknowledgment to tenant")

        # Step 2: Auto-triage if enabled
        if self.config["auto_triage"]:
            priority = self._auto_detect_priority(request)
            if priority != request.priority:
                request.priority = priority
                actions_taken.append(f"Auto-triaged priority to: {priority.value}")

        # Step 3: Update status to triaged
        request.update_status(MaintenanceStatus.TRIAGED, "Auto-triaged by system")

        # Step 4: Handle emergencies immediately
        if request.priority == MaintenancePriority.EMERGENCY:
            # Immediate owner notification for emergencies
            if owner and owner.contact and owner.contact.email:
                self._send_emergency_owner_notification(request, property, tenant, owner)
                actions_taken.append("Sent emergency notification to owner")

        # Trigger triaged event for next step
        follow_up_events.append(Event(
            EventType.MAINTENANCE_TRIAGED,
            {
                "request": request,
                "property": property,
                "tenant": tenant,
                "owner": owner,
            }
        ))

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_request_created",
            message=f"Request #{request.id} acknowledged and triaged as {request.priority.value}",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    def handle_triaged(self, event: Event) -> EventResult:
        """
        Handle triaged request - find and assign vendor.

        Trigger: Request has been triaged
        Actions:
        - Find appropriate vendor based on category and availability
        - Send work order to vendor
        - Update request status
        """
        request: MaintenanceRequest = event.payload.get("request")
        property: Property = event.payload.get("property")
        tenant: Tenant = event.payload.get("tenant")
        owner: Owner = event.payload.get("owner")

        if not request:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_triaged",
                errors=["Missing request data"]
            )

        actions_taken = []
        follow_up_events = []

        # Find appropriate vendor
        vendor = self.engine.find_vendor_for_maintenance(request)

        if vendor:
            request.vendor_id = vendor.id
            request.update_status(
                MaintenanceStatus.VENDOR_ASSIGNED,
                f"Assigned to {vendor.company_name}"
            )
            actions_taken.append(f"Assigned to vendor: {vendor.company_name}")

            # Trigger vendor assigned event
            follow_up_events.append(Event(
                EventType.MAINTENANCE_VENDOR_ASSIGNED,
                {
                    "request": request,
                    "vendor": vendor,
                    "property": property,
                    "tenant": tenant,
                    "owner": owner,
                }
            ))
        else:
            # No vendor found - notify for manual assignment
            actions_taken.append("No matching vendor found - requires manual assignment")
            request.vendor_notes = "No vendor auto-matched. Manual assignment required."

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_triaged",
            message=f"Request #{request.id} vendor assignment: {'completed' if vendor else 'requires manual action'}",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    def handle_vendor_assigned(self, event: Event) -> EventResult:
        """
        Handle vendor assignment - send work order.

        Trigger: Vendor has been assigned to request
        Actions:
        - Send work order email to vendor
        - Set follow-up reminder for response
        """
        request: MaintenanceRequest = event.payload.get("request")
        vendor: Vendor = event.payload.get("vendor")
        property: Property = event.payload.get("property")
        tenant: Tenant = event.payload.get("tenant")

        if not request or not vendor:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_vendor_assigned",
                errors=["Missing request or vendor data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "See details below"

        # Access instructions
        access_instructions = request.access_instructions or "Contact tenant to arrange access"
        if request.tenant_permission_to_enter:
            access_instructions = "Tenant has granted permission to enter. " + access_instructions

        # Scheduling instructions based on priority
        if request.priority == MaintenancePriority.EMERGENCY:
            scheduling = f"EMERGENCY - Please respond within {self.config['emergency_response_hours']} hours and schedule ASAP."
        elif request.priority == MaintenancePriority.URGENT:
            scheduling = "URGENT - Please respond within 24 hours and schedule within 48 hours."
        else:
            scheduling = "Please respond within 24-48 hours to confirm you can handle this job."

        template_data = {
            "vendor_name": vendor.contact_name or vendor.company_name,
            "request_id": request.id,
            "property_address": property_address,
            "issue_title": request.title,
            "issue_description": request.description,
            "priority": request.priority.value.upper(),
            "category": request.category.value.replace("_", " ").title(),
            "tenant_name": tenant.name if tenant else "N/A",
            "tenant_phone": tenant.contact.phone if tenant and tenant.contact else "N/A",
            "access_instructions": access_instructions,
            "scheduling_instructions": scheduling,
        }

        # Send work order to vendor
        if vendor.contact and vendor.contact.email:
            self.notifications.send_from_template(
                template_id="vendor_work_order",
                recipient_id=vendor.id,
                recipient_email=vendor.contact.email,
                template_data=template_data,
                priority=NotificationPriority.HIGH if request.priority in [MaintenancePriority.EMERGENCY, MaintenancePriority.URGENT] else NotificationPriority.NORMAL,
            )
            actions_taken.append(f"Sent work order to {vendor.company_name} ({vendor.contact.email})")

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_vendor_assigned",
            message=f"Work order sent for request #{request.id}",
            actions_taken=actions_taken,
        )

    def handle_scheduled(self, event: Event) -> EventResult:
        """
        Handle maintenance scheduled - notify tenant and owner.

        Trigger: Vendor has scheduled the work
        Actions:
        - Send schedule confirmation to tenant
        - Notify owner of scheduled work
        """
        request: MaintenanceRequest = event.payload.get("request")
        vendor: Vendor = event.payload.get("vendor")
        property: Property = event.payload.get("property")
        tenant: Tenant = event.payload.get("tenant")
        owner: Owner = event.payload.get("owner")

        if not request:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_scheduled",
                errors=["Missing request data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your property"

        scheduled_date = request.scheduled_date
        if scheduled_date:
            scheduled_date_str = scheduled_date.strftime("%A, %B %d, %Y")
            scheduled_time_str = scheduled_date.strftime("%I:%M %p")
        else:
            scheduled_date_str = "TBD"
            scheduled_time_str = "TBD"

        # Notify tenant
        if tenant and tenant.contact and tenant.contact.email:
            template_data = {
                "tenant_name": tenant.name,
                "property_address": property_address,
                "request_id": request.id,
                "issue_title": request.title,
                "scheduled_date": scheduled_date_str,
                "scheduled_time": scheduled_time_str,
                "vendor_name": vendor.company_name if vendor else "Our service provider",
                "vendor_phone": vendor.contact.phone if vendor and vendor.contact else "Contact our office",
                "access_instructions": request.access_instructions or "Please ensure access is available.",
            }

            self.notifications.send_from_template(
                template_id="maintenance_scheduled",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent schedule confirmation to tenant")

            # Also send SMS reminder
            if tenant.contact.phone:
                self.notifications.send_from_template(
                    template_id="maintenance_scheduled_sms",
                    recipient_id=tenant.id,
                    recipient_phone=tenant.contact.phone,
                    template_data={
                        "property_address": property_address,
                        "scheduled_date": scheduled_date_str,
                        "scheduled_time": scheduled_time_str,
                        "vendor_name": vendor.company_name if vendor else "vendor",
                    },
                    notification_type=NotificationType.SMS,
                )
                actions_taken.append("Sent SMS reminder to tenant")

        # Notify owner
        if owner and owner.contact and owner.contact.email:
            self._send_owner_maintenance_update(
                request, property, owner, vendor,
                status="Scheduled",
                details=f"Work scheduled for {scheduled_date_str} at {scheduled_time_str}"
            )
            actions_taken.append("Notified owner of scheduled maintenance")

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_scheduled",
            message=f"Schedule notifications sent for request #{request.id}",
            actions_taken=actions_taken,
        )

    def handle_completed(self, event: Event) -> EventResult:
        """
        Handle maintenance completed - confirm with tenant, update owner.

        Trigger: Vendor marks work as complete
        Actions:
        - Send completion notice to tenant
        - Send completion summary to owner (with costs if applicable)
        - Request cost approval if over threshold
        """
        request: MaintenanceRequest = event.payload.get("request")
        vendor: Vendor = event.payload.get("vendor")
        property: Property = event.payload.get("property")
        tenant: Tenant = event.payload.get("tenant")
        owner: Owner = event.payload.get("owner")

        if not request:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_completed",
                errors=["Missing request data"]
            )

        actions_taken = []
        follow_up_events = []

        property_address = str(property.address) if property and property.address else "your property"

        request.completed_date = datetime.now()

        # Notify tenant of completion
        if tenant and tenant.contact and tenant.contact.email:
            template_data = {
                "tenant_name": tenant.name,
                "property_address": property_address,
                "request_id": request.id,
                "issue_title": request.title,
                "completed_date": datetime.now().strftime("%B %d, %Y"),
                "work_description": request.vendor_notes or "Work completed as requested.",
            }

            self.notifications.send_from_template(
                template_id="maintenance_completed",
                recipient_id=tenant.id,
                recipient_email=tenant.contact.email,
                template_data=template_data,
            )
            actions_taken.append("Sent completion notice to tenant")

        # Check if cost requires owner approval
        if request.actual_cost and request.actual_cost > self.config["owner_approval_threshold"]:
            request.update_status(MaintenanceStatus.PENDING_APPROVAL, "Awaiting owner approval for cost")

            follow_up_events.append(Event(
                EventType.MAINTENANCE_PENDING_APPROVAL,
                {
                    "request": request,
                    "property": property,
                    "owner": owner,
                    "vendor": vendor,
                }
            ))
            actions_taken.append("Flagged for owner cost approval")
        else:
            # No approval needed - notify owner and close
            if owner and owner.contact and owner.contact.email:
                cost_section = ""
                if request.actual_cost:
                    cost_section = f"Cost: ${request.actual_cost:,.2f}"

                self._send_owner_maintenance_update(
                    request, property, owner, vendor,
                    status="Completed",
                    details=f"Work completed on {datetime.now().strftime('%B %d, %Y')}.\n{cost_section}",
                    include_cost=True,
                )
                actions_taken.append("Sent completion summary to owner")

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_completed",
            message=f"Completion notifications sent for request #{request.id}",
            actions_taken=actions_taken,
            follow_up_events=follow_up_events,
        )

    def handle_pending_approval(self, event: Event) -> EventResult:
        """
        Handle requests pending owner approval for costs.

        Trigger: Completed work exceeds cost threshold
        Actions:
        - Send approval request to owner with cost details
        """
        request: MaintenanceRequest = event.payload.get("request")
        property: Property = event.payload.get("property")
        owner: Owner = event.payload.get("owner")
        vendor: Vendor = event.payload.get("vendor")

        if not request or not owner:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_pending_approval",
                errors=["Missing request or owner data"]
            )

        actions_taken = []

        property_address = str(property.address) if property and property.address else "your property"

        if owner.contact and owner.contact.email:
            subject = f"Approval Required: Maintenance Cost for {property_address} - #{request.id}"
            body = f"""Dear {owner.name},

The following maintenance work has been completed at your property and requires your approval due to the cost.

Property: {property_address}
Request ID: #{request.id}
Issue: {request.title}
Vendor: {vendor.company_name if vendor else 'Service provider'}

COST DETAILS:
─────────────────────────────
Estimated Cost: ${request.estimated_cost or 'N/A':,.2f}
Actual Cost: ${request.actual_cost:,.2f}
─────────────────────────────

Work Description:
{request.vendor_notes or request.description}

Please reply to this email to approve this expense, or contact us at {self.notifications.company_info['company_phone']} if you have questions.

Thank you,
{self.notifications.company_info['company_name']}
"""
            self.notifications.send_email(
                recipient_id=owner.id,
                recipient_email=owner.contact.email,
                subject=subject,
                body=body,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append("Sent cost approval request to owner")

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_pending_approval",
            message=f"Cost approval request sent for #{request.id}",
            actions_taken=actions_taken,
        )

    def handle_vendor_no_response(self, event: Event) -> EventResult:
        """
        Handle vendor not responding - send reminder and escalate.

        Trigger: Vendor hasn't responded within configured time
        Actions:
        - Send reminder to vendor
        - Alert property manager
        - Potentially reassign to another vendor
        """
        request: MaintenanceRequest = event.payload.get("request")
        vendor: Vendor = event.payload.get("vendor")

        if not request or not vendor:
            return EventResult(
                success=False,
                event=event,
                handler_name="MaintenanceWorkflow.handle_vendor_no_response",
                errors=["Missing request or vendor data"]
            )

        actions_taken = []

        property = self.engine.get_property(request.property_id)
        property_address = str(property.address) if property and property.address else "the property"

        # Send reminder to vendor
        if vendor.contact and vendor.contact.email:
            template_data = {
                "vendor_name": vendor.contact_name or vendor.company_name,
                "request_id": request.id,
                "property_address": property_address,
                "status": "Pending Response",
                "assigned_date": request.updated_at.strftime("%B %d, %Y"),
            }

            self.notifications.send_from_template(
                template_id="vendor_reminder",
                recipient_id=vendor.id,
                recipient_email=vendor.contact.email,
                template_data=template_data,
                priority=NotificationPriority.HIGH,
            )
            actions_taken.append(f"Sent follow-up reminder to {vendor.company_name}")

        return EventResult(
            success=True,
            event=event,
            handler_name="MaintenanceWorkflow.handle_vendor_no_response",
            message=f"Vendor reminder sent for request #{request.id}",
            actions_taken=actions_taken,
        )

    # =================
    # Helper Methods
    # =================

    def _auto_detect_priority(self, request: MaintenanceRequest) -> MaintenancePriority:
        """Auto-detect priority based on description keywords."""
        description_lower = (request.description + " " + request.title).lower()

        # Check for emergency keywords
        for keyword in self.emergency_keywords:
            if keyword in description_lower:
                return MaintenancePriority.EMERGENCY

        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in description_lower:
                return MaintenancePriority.URGENT

        return request.priority

    def _send_emergency_owner_notification(
        self,
        request: MaintenanceRequest,
        property: Property,
        tenant: Tenant,
        owner: Owner
    ):
        """Send immediate notification to owner for emergencies."""
        property_address = str(property.address) if property and property.address else "your property"

        subject = f"🚨 EMERGENCY: Maintenance Issue at {property_address}"
        body = f"""Dear {owner.name},

AN EMERGENCY MAINTENANCE ISSUE HAS BEEN REPORTED.

Property: {property_address}
Issue: {request.title}
Priority: EMERGENCY
Reported by: {tenant.name if tenant else 'System'}

Description:
{request.description}

We are immediately dispatching a vendor to address this issue. We will keep you updated on the status.

If you have questions, please call us immediately at {self.notifications.company_info['emergency_phone']}.

{self.notifications.company_info['company_name']}
"""
        self.notifications.send_email(
            recipient_id=owner.id,
            recipient_email=owner.contact.email,
            subject=subject,
            body=body,
            priority=NotificationPriority.URGENT,
        )

    def _send_owner_maintenance_update(
        self,
        request: MaintenanceRequest,
        property: Property,
        owner: Owner,
        vendor: Optional[Vendor],
        status: str,
        details: str,
        include_cost: bool = False,
    ):
        """Send maintenance status update to owner."""
        property_address = str(property.address) if property and property.address else "your property"

        cost_section = ""
        if include_cost and request.actual_cost:
            cost_section = f"\nCost: ${request.actual_cost:,.2f}"
            if request.estimated_cost:
                cost_section += f" (estimated: ${request.estimated_cost:,.2f})"

        template_data = {
            "owner_name": owner.name,
            "property_address": property_address,
            "request_id": request.id,
            "issue_title": request.title,
            "status": status,
            "cost_section": cost_section,
            "details": details,
        }

        self.notifications.send_from_template(
            template_id="maintenance_owner_notification",
            recipient_id=owner.id,
            recipient_email=owner.contact.email,
            template_data=template_data,
        )
