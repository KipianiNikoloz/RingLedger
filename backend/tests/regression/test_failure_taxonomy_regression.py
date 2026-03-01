from __future__ import annotations

import unittest

from app.services.failure_taxonomy import build_failure_reason, classify_confirmation_failure


class FailureTaxonomyRegressionTests(unittest.TestCase):
    def test_declined_engine_results_remain_mapped_to_signing_declined(self) -> None:
        for engine_result in [
            "declined",
            "DECLINED",
            "user_declined",
            "xaman_declined",
            "canceled",
            " cancelled ",
        ]:
            with self.subTest(engine_result=engine_result):
                code = classify_confirmation_failure(
                    validation_error="ledger_tx_not_success",
                    validated=False,
                    engine_result=engine_result,
                )
                self.assertEqual(code, "signing_declined")

    def test_timeout_engine_results_remain_mapped_to_confirmation_timeout(self) -> None:
        for engine_result in [
            "timeout",
            "timed_out",
            "confirmation_timeout",
            "ledger_timeout",
            "tx_timeout",
            "timeout_pending",
        ]:
            with self.subTest(engine_result=engine_result):
                code = classify_confirmation_failure(
                    validation_error="ledger_tx_not_validated",
                    validated=False,
                    engine_result=engine_result,
                )
                self.assertEqual(code, "confirmation_timeout")

    def test_tec_tem_rejections_remain_explicitly_classified(self) -> None:
        for engine_result in ["tecUNFUNDED_OFFER", "temMALFORMED", "temBAD_EXPIRATION"]:
            with self.subTest(engine_result=engine_result):
                code = classify_confirmation_failure(
                    validation_error="ledger_tx_not_success",
                    validated=True,
                    engine_result=engine_result,
                )
                self.assertEqual(code, "ledger_tec_tem")

    def test_non_tec_ledger_not_success_falls_back_to_ledger_not_success(self) -> None:
        code = classify_confirmation_failure(
            validation_error="ledger_tx_not_success",
            validated=True,
            engine_result="tefPAST_SEQ",
        )
        self.assertEqual(code, "ledger_not_success")

    def test_validated_false_not_validated_remains_timeout_class(self) -> None:
        code = classify_confirmation_failure(
            validation_error="ledger_tx_not_validated",
            validated=False,
            engine_result="pending",
        )
        self.assertEqual(code, "confirmation_timeout")

    def test_unknown_validation_error_remains_invalid_confirmation(self) -> None:
        code = classify_confirmation_failure(
            validation_error="unexpected_validation_error",
            validated=True,
            engine_result="tesSUCCESS",
        )
        self.assertEqual(code, "invalid_confirmation")

    def test_failure_reason_format_remains_machine_parseable(self) -> None:
        reason = build_failure_reason(
            validation_error="ledger_tx_not_success",
            validated=False,
            engine_result=" temMALFORMED ",
        )
        self.assertEqual(
            reason,
            "validation_error=ledger_tx_not_success;validated=false;engine_result=temMALFORMED",
        )


if __name__ == "__main__":
    unittest.main()
