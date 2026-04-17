from google import genai
import time
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def classify_email(email_text):

    prompt = f"""
    You are an email classifier.

    Determine if the email below is a NEW RFQ (Request for Quotation).

    RFQ means the sender is asking for:
    - price
    - quotation
    - costing
    - estimate
    - PCB fabrication quote
    - manufacturing cost

    Return ONLY one word:

    RFQ
    NOT_RFQ

    Important rules:
    - If the email is a reply or ongoing conversation → NOT_RFQ
    - If the sender is thanking for a quote → NOT_RFQ
    - If the sender is sending invoice/payment → NOT_RFQ
    - If the sender asks price or quotation → RFQ
    - spelling mistakes should still count (example: quotetion)

    EMAIL:
    {email_text}
    """

    max_retries = 5

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text.strip().upper()

            if "RFQ" in result:
                return "RFQ"

            return "NOT_RFQ"

        except Exception as e:

            error_text = str(e)

            print("AI error:", error_text)

            if "429" in error_text or "503" in error_text:

                wait_time = 15 * (attempt + 1)

                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

                continue

            return "NOT_RFQ"

    return "NOT_RFQ"