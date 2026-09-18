from datetime import UTC, datetime

from contracts.analytics import ConversionInput, MetricSnapshotInput


def test_metric_snapshot():
    snapshot = MetricSnapshotInput(
        impressions=1000,
        views=800,
        saves=20,
        completion_rate=0.4,
        raw_metrics={"provider": "fixture"},
        captured_at=datetime.now(UTC),
    )

    assert snapshot.impressions == 1000


def test_waitlist_conversion_without_email():
    conversion = ConversionInput(
        conversion_id="signup_123",
        conversion_type="WAITLIST_SIGNUP",
        qualified=True,
        visitor_id="visitor_xyz",
        converted_at=datetime.now(UTC),
    )

    assert conversion.qualified is True
