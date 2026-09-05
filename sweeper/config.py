import getpass
import os
import keyring


SERVICE_NAME = "AutoUnsub"


def load_credentials():
    address = os.environ.get("GMAIL_ADDRESS")

    if not address:
        address = input("Gmail address: ").strip()

    app_password = keyring.get_password(
        SERVICE_NAME,
        address
    )

    if not app_password:
        app_password = getpass.getpass(
            "Gmail app password: "
        ).strip().replace(" ", "")

        keyring.set_password(
            SERVICE_NAME,
            address,
            app_password
        )

        print("app password saved securely")

    return {
        "address": address,
        "app_password": app_password
    }