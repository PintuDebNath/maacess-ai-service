"""
main.py
-------
Entry point for the maacess-ai-service.

Initializes the OmniDimension (OmniDim) SDK client and provides a
placeholder function to sync leads from the Laravel MySQL database
with OmniDim outbound calls / knowledge base updates.
"""

import os
import sys
import time
from dotenv import load_dotenv
from omnidimension import Client  # OmniDim SDK client
from database import get_connection, close_connection

# Load environment variables from .env
load_dotenv()


def init_omnidim_client() -> Client:
    """
    Initialize and return the OmniDimension SDK client.

    Returns:
        Client: An authenticated OmniDim client instance.

    Raises:
        ValueError: If the API key is not set.
    """
    api_key = os.getenv("OMNIDIM_API_KEY")
    if not api_key:
        raise ValueError(
            "[OmniDim] OMNIDIM_API_KEY is not set. "
            "Please copy .env.example to .env and fill in your credentials."
        )

    client = Client(api_key=api_key)
    print("[OmniDim] Client initialized successfully.")
    return client


def sync_leads_to_ai(client: Client) -> None:
    """
    Query the 'omni_leads' table from the Laravel MySQL database
    and use the OmniDim SDK to trigger an outbound call for each new lead.

    Args:
        client (Client): An authenticated OmniDim client instance.
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM omni_leads WHERE call_status IS NULL")
        leads = cursor.fetchall()

        if leads:
            print(f"[Sync] Fetched {len(leads)} new lead(s) from the database.")

        for lead in leads:
            lead_id = lead.get("id")
            customer_name = lead.get("customer_name", "Unknown")
            phone_number = lead.get("phone_number", "")
            requirement = lead.get("requirement", "")

            print(f"[Sync] Processing lead #{lead_id} — {customer_name} ({phone_number})")

            try:
                response = client.calls.dispatch_call(
                    agent_id="151580",
                    to_number=phone_number,
                    call_context={"customer_name": customer_name, "requirement": requirement}
                )
                print(f"[OmniDim] Call dispatched: {response}")

                update_query = "UPDATE omni_leads SET call_status = 'dispatched', updated_at = NOW() WHERE id = %s"
                cursor.execute(update_query, (lead_id,))
                connection.commit()
                print(f"[DB] Updated lead #{lead_id} status to 'dispatched'")

            except Exception as call_e:
                print(f"[Sync] Error dispatching call for lead #{lead_id}: {call_e}")

    except Exception as e:
        print(f"[Sync] Error during lead sync: {e}")

    finally:
        if connection:
            close_connection(connection)


if __name__ == "__main__":
    # Force unbuffered output so logs appear instantly in journalctl
    sys.stdout.reconfigure(line_buffering=True)

    print("=" * 50)
    print("  maacess-ai-service — Starting up")
    print("=" * 50)

    # 1. Initialize OmniDim client
    try:
        omni_client = init_omnidim_client()
    except Exception as e:
        print(f"[Main] Failed to initialize client: {e}")
        exit(1)

    # 2. Run in a loop every 60 seconds
    print("[Main] Starting lead sync loop...")
    while True:
        try:
            sync_leads_to_ai(omni_client)
        except Exception as e:
            print(f"[Main] Loop error: {e}")
        
        print("[Main] Sleeping for 60 seconds...")
        time.sleep(60)
