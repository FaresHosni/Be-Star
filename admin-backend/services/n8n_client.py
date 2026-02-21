import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# N8N Webhook URLs (configured in .env or hardcoded for now)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "https://n8n.growhubeg.com/webhook/be-star-approval")

async def trigger_ticket_approved_workflow(ticket_data: dict):
    """
    Triggers the n8n workflow when a ticket is approved.
    Sends ticket details to n8n to generate/send PDF via WhatsApp.
    """
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Triggering n8n webhook at: {N8N_WEBHOOK_URL} for ticket {ticket_data.get('code')}")
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=ticket_data,
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Successfully triggered n8n workflow for ticket {ticket_data.get('code')}")
            return True
    except Exception as e:
        logger.error(f"Failed to trigger n8n workflow: {str(e)}")
        return False
