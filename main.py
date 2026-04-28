"""
main.py
-------
Entry point for the maacess-ai-service.

Initializes the OmniDimension (OmniDim) SDK client and provides a
placeholder function to sync leads from the Laravel MySQL database
with OmniDim outbound calls / knowledge base updates.
"""

import os
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
    Placeholder: Query the 'leads' table from the Laravel MySQL database
    and use the OmniDim SDK to trigger an outbound call or update the
    knowledge base for each lead.

    Args:
        client (Client): An authenticated OmniDim client instance.

    TODO:
        - Query leads that have not yet been contacted (e.g. status='new').
        - For each lead, call client.calls.create(...) to trigger an outbound call,
          OR call client.knowledge_base.update(...) to update the KB.
        - Mark each lead as processed in the DB after a successful API call.
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # ── Placeholder query ──────────────────────────────────────────────
        # Replace with your actual lead-fetching logic, e.g.:
        # cursor.execute("SELECT * FROM leads WHERE status = 'new' LIMIT 50")
        cursor.execute("SELECT * FROM leads LIMIT 10")
        leads = cursor.fetchall()
        # ──────────────────────────────────────────────────────────────────

        print(f"[Sync] Fetched {len(leads)} lead(s) from the database.")

        for lead in leads:
            lead_id = lead.get("id")
            lead_name = lead.get("name", "Unknown")
            lead_phone = lead.get("phone", "")

            print(f"[Sync] Processing lead #{lead_id} — {lead_name} ({lead_phone})")

            # ── Placeholder OmniDim action ─────────────────────────────────
            # Example: trigger an outbound call via OmniDim SDK
            # response = client.calls.create(
            #     to=lead_phone,
            #     agent_id="your_agent_id",
            #     metadata={"lead_id": lead_id, "name": lead_name},
            # )
            # print(f"[OmniDim] Call triggered: {response}")
            #
            # Example: update knowledge base
            # client.knowledge_base.update(
            #     kb_id="your_kb_id",
            #     content=f"Lead: {lead_name}, Phone: {lead_phone}",
            # )
            # ──────────────────────────────────────────────────────────────

        print("[Sync] sync_leads_to_ai() placeholder complete — implement above TODOs.")

    except Exception as e:
        print(f"[Sync] Error during lead sync: {e}")
        raise

    finally:
        if connection:
            close_connection(connection)


if __name__ == "__main__":
    print("=" * 50)
    print("  maacess-ai-service — Starting up")
    print("=" * 50)

    # 1. Initialize OmniDim client
    omni_client = init_omnidim_client()

    # 2. Sync leads from the Laravel MySQL database to OmniDim
    sync_leads_to_ai(omni_client)

    print("\n[Main] Service run complete.")
