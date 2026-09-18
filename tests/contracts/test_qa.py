from contracts.qa import QACheckResult


def test_qa_contract():
    result = QACheckResult(
        gate="PRODUCT_CAPABILITY",
        result="PASS",
        reason_code="CAPABILITY_ALLOWED",
        message="All product claims are allowlisted.",
    )

    assert result.result == "PASS"
