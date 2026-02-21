import os
import httpx
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
        
        if not all([self.api_url, self.api_key, self.instance_name]):
            logger.warning("WhatsApp Service configuration missing. Notifications will not be sent.")

    def _get_headers(self):
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def send_message(self, phone: str, message: str) -> Optional[dict]:
        """Send a text message to a phone number"""
        if not self.api_url or not self.api_key:
            return None

        # Format phone number (ensure country code)
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
             phone = "20" + phone
            
        endpoint = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        payload = {
            "number": phone,
            "text": message
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    json=payload, 
                    headers=self._get_headers(),
                    timeout=30.0
                )
                logger.info(f"WhatsApp Text Response ({phone}): {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {phone}: {str(e)}")
            return None

    async def send_pdf_ticket(self, phone: str, pdf_url: str, caption: str = "تذكرتك من Be Star") -> Optional[dict]:
        """Send a PDF ticket to a phone number (Using Media Message)"""
        if not self.api_url or not self.api_key:
            return None

         # Format phone number
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
             phone = "20" + phone

        endpoint = f"{self.api_url}/message/sendMedia/{self.instance_name}"
        
        payload = {
            "number": phone,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "caption": caption,
            "media": pdf_url,
            "fileName": "ticket.pdf"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    json=payload, 
                    headers=self._get_headers(),
                    timeout=60.0
                )
                logger.info(f"WhatsApp PDF Response ({phone}): {response.status_code} - {response.text}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send PDF ticket to {phone}: {str(e)}")
            return None

    async def send_image(self, phone: str, base64_data: str, caption: str = "") -> Optional[dict]:
        """Send an image via base64 to a phone number"""
        if not self.api_url or not self.api_key:
            return None

        # Format phone number
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
             phone = "20" + phone

        endpoint = f"{self.api_url}/message/sendMedia/{self.instance_name}"
        
        payload = {
            "number": phone,
            "mediatype": "image",
            "mimetype": "image/jpeg",
            "caption": caption,
            "media": base64_data,
            "fileName": "image.jpg"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    json=payload, 
                    headers=self._get_headers(),
                    timeout=60.0
                )
                logger.info(f"WhatsApp Image Response ({phone}): {response.status_code}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send image to {phone}: {str(e)}")
            return None

    async def send_link(self, phone: str, url: str, title: str = "", description: str = "") -> Optional[dict]:
        """Send a link message to a phone number"""
        if not self.api_url or not self.api_key:
            return None

        # Format phone number
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
             phone = "20" + phone

        # Send as formatted text with link
        message = f"🔗 *{title}*\n{description}\n\n{url}" if title else url
        return await self.send_message(phone, message)

    async def send_certificate(self, phone: str, pdf_base64: str, guest_name: str, rank: int = 0) -> Optional[dict]:
        """Send a certificate PDF document via WhatsApp"""
        if not self.api_url or not self.api_key:
            logger.error("WhatsApp not configured (missing api_url or api_key)")
            return None

        # Format phone number
        if phone.startswith("0") and len(phone) == 11:
            phone = "20" + phone[1:]
        elif not phone.startswith("20") and len(phone) == 10:
             phone = "20" + phone

        rank_text = f" 🏆 (المركز {rank})" if rank else ""
        caption = f"🌟 مبروك يا {guest_name}!{rank_text}\n\nدي شهادة تقديرك من إيفنت كن نجماً ⭐\nفخورين بيك وبمشاركتك! 🎉"

        endpoint = f"{self.api_url}/message/sendMedia/{self.instance_name}"
        
        payload = {
            "number": phone,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "caption": caption,
            "media": pdf_base64,
            "fileName": "BeStarCertificate.pdf"
        }

        try:
            logger.info(f"Sending certificate to {phone}, base64 length: {len(pdf_base64)}")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    json=payload, 
                    headers=self._get_headers(),
                    timeout=120.0
                )
                logger.info(f"WhatsApp Certificate Response ({phone}): {response.status_code} - {response.text[:500]}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send certificate to {phone}: {str(e)}")
            return None


