"""Print a signed JSON body for POST /transactions."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

from src.application.dtos.payment import ProcessPaymentInput
from src.infrastructure.config.settings import AppSettings
from src.infrastructure.services.sha256_payment_signature import Sha256PaymentSignature

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Собрать тело POST /transactions с подписью",
    )
    parser.add_argument("--user-id", type=int, default=2)
    parser.add_argument("--account-id", type=int, default=2)
    parser.add_argument("--amount", type=int, default=50)
    parser.add_argument("--transaction-id", default=None)
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    transaction_id = args.transaction_id or str(uuid4())
    draft = ProcessPaymentInput(
        transaction_id=transaction_id,
        account_id=args.account_id,
        user_id=args.user_id,
        amount=args.amount,
        signature="",
    )
    signature = Sha256PaymentSignature(AppSettings()).sign(draft)
    print(
        json.dumps(
            {
                "transaction_id": transaction_id,
                "user_id": args.user_id,
                "account_id": args.account_id,
                "amount": args.amount,
                "signature": signature,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
