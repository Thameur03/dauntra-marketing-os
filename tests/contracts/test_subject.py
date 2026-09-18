import pytest
from pydantic import ValidationError

from contracts.subject import SubjectCreate


def test_valid_subject():
    subject = SubjectCreate(
        subject="Does protein timing matter for hypertrophy?",
        note="Focus on practical implications.",
        content_family="C02",
    )

    assert subject.market == "GLOBAL"
    assert subject.language == "en"
    assert subject.content_family == "C02"


def test_empty_subject_rejected():
    with pytest.raises(ValidationError):
        SubjectCreate(subject="")
