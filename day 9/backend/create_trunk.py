import asyncio
import os
import sys
from livekit import api
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(".env.local")


async def main():
    lk = api.LiveKitAPI()
    try:
        # Get existing trunks
        trunks = await lk.sip.list_sip_outbound_trunk(api.ListSIPOutboundTrunkRequest())

        trunk_id = None
        for t in trunks.items:
            if t.name == "linphone-trunk":
                trunk_id = t.sip_trunk_id
                break

        if trunk_id:
            print(f"Found existing trunk: {trunk_id}")
            with open(".env.local", "a") as f:
                f.write(f"\nLIVEKIT_SIP_OUTBOUND_TRUNK_ID={trunk_id}\n")
            print("Added LIVEKIT_SIP_OUTBOUND_TRUNK_ID to .env.local!")
        else:
            print("Trunk not found, please recreate it.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await lk.aclose()


if __name__ == "__main__":
    asyncio.run(main())
