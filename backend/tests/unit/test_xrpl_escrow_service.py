from __future__ import annotations

import unittest
import uuid

from app.models.enums import EscrowKind, EscrowStatus
from app.models.escrow import Escrow
from app.services.xrpl_escrow_service import EscrowCreateConfirmation, XrplEscrowService, XrplEscrowValidationError


class XrplEscrowServiceUnitTests(unittest.TestCase):
    def test_build_escrow_create_tx_contains_expected_fields(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.BONUS_A, cancel_after_ripple=900)
        tx = XrplEscrowService.build_escrow_create_tx(escrow)

        self.assertEqual(tx["TransactionType"], "EscrowCreate")
        self.assertEqual(tx["Account"], "rPromoter")
        self.assertEqual(tx["Destination"], "rFighter")
        self.assertEqual(tx["Amount"], "250000")
        self.assertEqual(tx["FinishAfter"], 800)
        self.assertEqual(tx["CancelAfter"], 900)

    def test_validate_confirmation_accepts_matching_fields(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.SHOW_A, cancel_after_ripple=None)
        confirmation = EscrowCreateConfirmation(
            tx_hash="ABC123456789",
            offer_sequence=111,
            validated=True,
            engine_result="tesSUCCESS",
            owner_address="rPromoter",
            destination_address="rFighter",
            amount_drops=250_000,
            finish_after_ripple=800,
            cancel_after_ripple=None,
            condition_hex=None,
        )

        XrplEscrowService.validate_escrow_create_confirmation(escrow=escrow, confirmation=confirmation)

    def test_validate_confirmation_rejects_mismatch(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.SHOW_B, cancel_after_ripple=None)
        confirmation = EscrowCreateConfirmation(
            tx_hash="DEF123456789",
            offer_sequence=222,
            validated=True,
            engine_result="tesSUCCESS",
            owner_address="rAnotherOwner",
            destination_address="rFighter",
            amount_drops=250_000,
            finish_after_ripple=800,
            cancel_after_ripple=None,
            condition_hex=None,
        )

        with self.assertRaises(XrplEscrowValidationError) as ctx:
            XrplEscrowService.validate_escrow_create_confirmation(escrow=escrow, confirmation=confirmation)
        self.assertEqual(str(ctx.exception), "ledger_owner_address_mismatch")

    @staticmethod
    def _build_escrow(*, kind: EscrowKind, cancel_after_ripple: int | None) -> Escrow:
        return Escrow(
            id=uuid.uuid4(),
            bout_id=uuid.uuid4(),
            kind=kind,
            status=EscrowStatus.PLANNED,
            owner_address="rPromoter",
            destination_address="rFighter",
            amount_drops=250_000,
            finish_after_ripple=800,
            cancel_after_ripple=cancel_after_ripple,
            condition_hex=None,
            encrypted_preimage_hex=None,
        )


if __name__ == "__main__":
    unittest.main()
