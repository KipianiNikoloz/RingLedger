from __future__ import annotations

import unittest
import uuid

from app.models.enums import EscrowKind, EscrowStatus
from app.models.escrow import Escrow
from app.services.xrpl_escrow_service import (
    EscrowCreateConfirmation,
    EscrowPayoutAction,
    EscrowPayoutConfirmation,
    XrplEscrowService,
    XrplEscrowValidationError,
)


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

    def test_build_escrow_finish_tx_contains_fulfillment_when_provided(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.BONUS_A, cancel_after_ripple=900)
        tx = XrplEscrowService.build_escrow_finish_tx(escrow=escrow, fulfillment_hex="AA")

        self.assertEqual(tx["TransactionType"], "EscrowFinish")
        self.assertEqual(tx["Account"], "rPromoter")
        self.assertEqual(tx["Owner"], "rPromoter")
        self.assertEqual(tx["OfferSequence"], 901)
        self.assertEqual(tx["Fulfillment"], "AA")

    def test_validate_payout_confirmation_accepts_expected_bonus_finish(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.BONUS_A, cancel_after_ripple=900)
        confirmation = EscrowPayoutConfirmation(
            tx_hash="PAYOUT001",
            validated=True,
            engine_result="tesSUCCESS",
            transaction_type="EscrowFinish",
            owner_address="rPromoter",
            offer_sequence=901,
            close_time_ripple=801,
            fulfillment_hex="AA",
        )

        XrplEscrowService.validate_payout_confirmation(
            escrow=escrow,
            confirmation=confirmation,
            expected_action=EscrowPayoutAction.FINISH,
            expected_fulfillment_hex="aa",
        )

    def test_validate_payout_confirmation_rejects_cancel_before_cancel_after(self) -> None:
        escrow = self._build_escrow(kind=EscrowKind.BONUS_B, cancel_after_ripple=900)
        confirmation = EscrowPayoutConfirmation(
            tx_hash="PAYOUT002",
            validated=True,
            engine_result="tesSUCCESS",
            transaction_type="EscrowCancel",
            owner_address="rPromoter",
            offer_sequence=901,
            close_time_ripple=899,
            fulfillment_hex=None,
        )

        with self.assertRaises(XrplEscrowValidationError) as ctx:
            XrplEscrowService.validate_payout_confirmation(
                escrow=escrow,
                confirmation=confirmation,
                expected_action=EscrowPayoutAction.CANCEL,
                expected_fulfillment_hex=None,
            )
        self.assertEqual(str(ctx.exception), "ledger_cancel_before_allowed")

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
            offer_sequence=901,
        )


if __name__ == "__main__":
    unittest.main()
