"""
Notification service for PropertyFlow.

Handles sending emails, SMS messages, and other notifications.
Supports templates for consistent, professional communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """A notification to be sent."""
    notification_type: NotificationType
    recipient_id: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: str = ""
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    sent: bool = False
    sent_at: Optional[datetime] = None
    error: Optional[str] = None


# Email templates for various scenarios
EMAIL_TEMPLATES = {
    # Late Rent Templates
    "rent_reminder_friendly": {
        "subject": "Friendly Reminder: Rent Due for {property_address}",
        "body": """Dear {tenant_name},

This is a friendly reminder that your rent payment of ${rent_amount} for {property_address} was due on {due_date}.

If you've already sent your payment, please disregard this message. Otherwise, please submit your payment at your earliest convenience.

If you're experiencing any difficulties, please don't hesitate to reach out to us.

Best regards,
{company_name}
{company_phone}
{company_email}
"""
    },

    "rent_late_notice": {
        "subject": "NOTICE: Rent Past Due for {property_address}",
        "body": """Dear {tenant_name},

This notice is to inform you that your rent payment of ${rent_amount} for {property_address} is now {days_late} days past due.

As of today, a late fee of ${late_fee} has been applied to your account, bringing your total balance to ${total_due}.

Please submit payment immediately to avoid further action.

Payment Methods:
- Online: {payment_portal_url}
- Mail: {company_address}
- In Person: Contact us to arrange

If you have questions or need to discuss a payment arrangement, please contact us immediately at {company_phone}.

Sincerely,
{company_name}
"""
    },

    "rent_severely_late": {
        "subject": "URGENT: Immediate Action Required - Past Due Rent for {property_address}",
        "body": """Dear {tenant_name},

Your rent for {property_address} is now {days_late} days past due. Despite our previous notices, we have not received payment.

Current Balance Due: ${total_due}
(Includes rent of ${rent_amount} and late fees of ${late_fee})

This is a formal notice that failure to pay the full amount within {cure_period} days may result in the initiation of legal proceedings, including eviction.

Please contact us immediately at {company_phone} to resolve this matter.

This notice is being sent in accordance with Virginia landlord-tenant law.

{company_name}
{company_address}
{company_phone}
"""
    },

    # Maintenance Templates
    "maintenance_received": {
        "subject": "Maintenance Request Received - #{request_id}",
        "body": """Dear {tenant_name},

We have received your maintenance request for {property_address}.

Request ID: #{request_id}
Issue: {issue_title}
Priority: {priority}

We will review your request and contact you shortly to schedule the repair. For emergency issues, please call us immediately at {emergency_phone}.

{entry_permission_text}

Thank you,
{company_name}
"""
    },

    "maintenance_scheduled": {
        "subject": "Maintenance Scheduled - #{request_id}",
        "body": """Dear {tenant_name},

Your maintenance request has been scheduled.

Request ID: #{request_id}
Issue: {issue_title}
Scheduled Date: {scheduled_date}
Scheduled Time: {scheduled_time}
Vendor: {vendor_name}
Vendor Phone: {vendor_phone}

{access_instructions}

If you need to reschedule, please contact us at least 24 hours in advance at {company_phone}.

Thank you,
{company_name}
"""
    },

    "maintenance_completed": {
        "subject": "Maintenance Completed - #{request_id}",
        "body": """Dear {tenant_name},

The maintenance work at {property_address} has been completed.

Request ID: #{request_id}
Issue: {issue_title}
Completed Date: {completed_date}
Work Performed: {work_description}

If you have any concerns about the work performed or notice any issues, please contact us within 48 hours.

Thank you for your patience.

{company_name}
{company_phone}
"""
    },

    "maintenance_owner_notification": {
        "subject": "Maintenance Update for {property_address} - #{request_id}",
        "body": """Dear {owner_name},

This is an update regarding maintenance at your property:

Property: {property_address}
Request ID: #{request_id}
Issue: {issue_title}
Status: {status}
{cost_section}

{details}

If you have any questions, please don't hesitate to contact us.

Best regards,
{company_name}
"""
    },

    # Lease Renewal Templates
    "lease_renewal_offer": {
        "subject": "Lease Renewal Offer for {property_address}",
        "body": """Dear {tenant_name},

Your current lease for {property_address} will expire on {lease_end_date}. We value you as a tenant and would like to offer you the opportunity to renew.

Current Rent: ${current_rent}/month
Renewal Options:

{renewal_options}

Please respond by {response_deadline} to secure your preferred option. If we don't hear from you, we'll need to begin preparing the unit for new tenants.

To accept a renewal option, please reply to this email or contact us at {company_phone}.

Thank you for being a great tenant!

Best regards,
{company_name}
"""
    },

    "lease_renewal_reminder": {
        "subject": "Reminder: Lease Renewal Response Needed for {property_address}",
        "body": """Dear {tenant_name},

This is a reminder that we sent you a lease renewal offer on {offer_date}. Your current lease expires on {lease_end_date}, and we haven't received your response yet.

Please let us know your decision by {response_deadline}:
- If you'd like to renew, reply with your preferred lease term
- If you plan to move out, please confirm so we can begin our process

If we don't hear from you by {response_deadline}, we'll begin marketing the unit for new tenants.

Please contact us at {company_phone} if you have any questions.

Thank you,
{company_name}
"""
    },

    "lease_not_renewing_notice": {
        "subject": "Notice: {property_address} Will Be Available",
        "body": """Dear {tenant_name},

This confirms that you will not be renewing your lease for {property_address}. Your lease ends on {lease_end_date}.

Move-Out Checklist:
1. Schedule move-out inspection: Contact us at {company_phone}
2. Return all keys by {lease_end_date}
3. Provide forwarding address for security deposit return
4. Ensure unit is cleaned and all personal belongings removed
5. Cancel utilities effective {lease_end_date}

Security Deposit: Your deposit of ${security_deposit} will be returned within {deposit_return_days} days after move-out, less any deductions for damages or unpaid rent.

Thank you for being our tenant. We wish you the best in your new home.

{company_name}
"""
    },

    # Move-In Templates
    "move_in_welcome": {
        "subject": "Welcome to {property_address}!",
        "body": """Dear {tenant_name},

Welcome to your new home! We're excited to have you as our tenant.

Property Address: {property_address}
Move-In Date: {move_in_date}
Monthly Rent: ${monthly_rent}
Rent Due Date: {rent_due_day}

IMPORTANT INFORMATION:

Move-In Inspection:
Your move-in inspection is scheduled for {inspection_date} at {inspection_time}. Please be present to walk through the unit with us.

Keys & Access:
{key_pickup_instructions}

Setting Up Utilities:
Please set up the following utilities in your name before move-in:
- Electric: {electric_company} ({electric_phone})
- Gas: {gas_company} ({gas_phone})
- Water: {water_company} ({water_phone})

Rent Payment:
{payment_instructions}

Emergency Contacts:
- Maintenance Emergency: {emergency_phone}
- After-Hours Emergency: {after_hours_phone}

Attached Documents:
- Move-In Checklist
- Tenant Handbook
- Emergency Contact List

If you have any questions before your move-in, please don't hesitate to reach out.

Welcome home!

{company_name}
{company_phone}
{company_email}
"""
    },

    "move_in_inspection_reminder": {
        "subject": "Reminder: Move-In Inspection Tomorrow at {property_address}",
        "body": """Dear {tenant_name},

This is a reminder that your move-in inspection is scheduled for tomorrow.

Date: {inspection_date}
Time: {inspection_time}
Location: {property_address}

Please be on time so we can thoroughly document the condition of the unit together. This protects both you and us.

Things to bring:
- Photo ID
- Payment for first month's rent (if not already paid)
- List of any questions you have

See you tomorrow!

{company_name}
{company_phone}
"""
    },

    # Owner Reporting Templates
    "owner_monthly_statement": {
        "subject": "Monthly Statement for {property_address} - {statement_period}",
        "body": """Dear {owner_name},

Please find below your monthly statement for {property_address} for {statement_period}.

SUMMARY
═══════════════════════════════════════
Income:
  Rent Collected:      ${rent_collected}
  Late Fees:           ${late_fees}
  Other Income:        ${other_income}
  ─────────────────────────────────
  Total Income:        ${total_income}

Expenses:
  Maintenance:         ${maintenance_expenses}
  Management Fee:      ${management_fee}
  Other Expenses:      ${other_expenses}
  ─────────────────────────────────
  Total Expenses:      ${total_expenses}

═══════════════════════════════════════
NET INCOME:            ${net_income}
═══════════════════════════════════════

{maintenance_summary}

{tenant_status}

Your payment of ${net_income} has been {payment_status}.

If you have any questions about this statement, please don't hesitate to contact us.

Best regards,
{company_name}
{company_phone}
"""
    },

    # Vendor Templates
    "vendor_work_order": {
        "subject": "Work Order #{request_id} - {property_address}",
        "body": """Hi {vendor_name},

We have a maintenance request for you.

WORK ORDER #{request_id}
─────────────────────────────────────
Property: {property_address}
Issue: {issue_title}
Priority: {priority}
Category: {category}

Description:
{issue_description}

Tenant Contact: {tenant_name} - {tenant_phone}
Access: {access_instructions}

Please confirm you can handle this job by replying to this email or calling {company_phone}.

{scheduling_instructions}

Thank you,
{company_name}
"""
    },

    "vendor_reminder": {
        "subject": "Reminder: Work Order #{request_id} Needs Update",
        "body": """Hi {vendor_name},

We're following up on work order #{request_id} for {property_address}.

Current Status: {status}
Assigned Date: {assigned_date}

Please provide an update on this job:
- If completed, please confirm and provide details
- If scheduled, please confirm date/time
- If there are any issues, please let us know

Contact us at {company_phone} if you need any assistance.

Thank you,
{company_name}
"""
    },
}

# SMS Templates (shorter versions)
SMS_TEMPLATES = {
    "rent_reminder_sms": "Reminder: Your rent of ${rent_amount} for {property_address} was due {due_date}. Please submit payment. Questions? Call {company_phone}",

    "rent_late_sms": "NOTICE: Rent for {property_address} is {days_late} days late. Total due: ${total_due}. Pay now to avoid further fees. Call {company_phone}",

    "maintenance_scheduled_sms": "Maintenance scheduled for {property_address} on {scheduled_date} at {scheduled_time}. Vendor: {vendor_name}. Questions? {company_phone}",

    "maintenance_completed_sms": "Maintenance at {property_address} is complete. Request #{request_id}. Questions? Call {company_phone}",

    "lease_renewal_reminder_sms": "Reminder: Your lease renewal response for {property_address} is due by {response_deadline}. Please respond or call {company_phone}",

    "move_in_reminder_sms": "Reminder: Your move-in inspection at {property_address} is tomorrow at {inspection_time}. See you there!",
}


class NotificationService:
    """
    Service for sending notifications via various channels.

    Supports email, SMS, and templates for consistent messaging.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._notification_log: List[Notification] = []

        # Default company info (should be configured)
        self.company_info = {
            "company_name": self.config.get("company_name", "PropertyFlow Management"),
            "company_phone": self.config.get("company_phone", "(703) 555-0100"),
            "company_email": self.config.get("company_email", "info@propertyflow.com"),
            "company_address": self.config.get("company_address", "123 Main St, Leesburg, VA 20176"),
            "emergency_phone": self.config.get("emergency_phone", "(703) 555-0199"),
            "after_hours_phone": self.config.get("after_hours_phone", "(703) 555-0199"),
            "payment_portal_url": self.config.get("payment_portal_url", "https://pay.propertyflow.com"),
        }

    def send_email(
        self,
        recipient_id: str,
        recipient_email: str,
        subject: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> Notification:
        """Send an email notification."""
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            recipient_id=recipient_id,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            priority=priority,
        )

        # In a real implementation, this would use an email service
        # For now, we log and simulate success
        logger.info(f"Sending email to {recipient_email}: {subject}")
        notification.sent = True
        notification.sent_at = datetime.now()

        self._notification_log.append(notification)
        return notification

    def send_sms(
        self,
        recipient_id: str,
        recipient_phone: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> Notification:
        """Send an SMS notification."""
        notification = Notification(
            notification_type=NotificationType.SMS,
            recipient_id=recipient_id,
            recipient_phone=recipient_phone,
            body=body,
            priority=priority,
        )

        # In a real implementation, this would use Twilio or similar
        logger.info(f"Sending SMS to {recipient_phone}: {body[:50]}...")
        notification.sent = True
        notification.sent_at = datetime.now()

        self._notification_log.append(notification)
        return notification

    def send_from_template(
        self,
        template_id: str,
        recipient_id: str,
        recipient_email: str = None,
        recipient_phone: str = None,
        template_data: Dict[str, Any] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        notification_type: NotificationType = NotificationType.EMAIL,
    ) -> Notification:
        """Send a notification using a template."""
        template_data = template_data or {}

        # Merge company info into template data
        merged_data = {**self.company_info, **template_data}

        if notification_type == NotificationType.EMAIL:
            template = EMAIL_TEMPLATES.get(template_id)
            if not template:
                raise ValueError(f"Unknown email template: {template_id}")

            subject = self._render_template(template["subject"], merged_data)
            body = self._render_template(template["body"], merged_data)

            return self.send_email(
                recipient_id=recipient_id,
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                priority=priority,
            )

        elif notification_type == NotificationType.SMS:
            template = SMS_TEMPLATES.get(template_id)
            if not template:
                raise ValueError(f"Unknown SMS template: {template_id}")

            body = self._render_template(template, merged_data)

            return self.send_sms(
                recipient_id=recipient_id,
                recipient_phone=recipient_phone,
                body=body,
                priority=priority,
            )

        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")

    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render a template with the given data."""
        result = template
        for key, value in data.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value) if value is not None else "")
        return result

    def get_notification_log(self, limit: int = 100) -> List[Notification]:
        """Get recent notifications."""
        return self._notification_log[-limit:]

    def get_notifications_for_recipient(self, recipient_id: str) -> List[Notification]:
        """Get all notifications sent to a specific recipient."""
        return [n for n in self._notification_log if n.recipient_id == recipient_id]


def format_currency(amount: float) -> str:
    """Format a number as currency."""
    return f"{amount:,.2f}"


def format_phone(phone: str) -> str:
    """Format a phone number."""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone
