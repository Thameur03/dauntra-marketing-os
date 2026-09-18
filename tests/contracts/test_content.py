import pytest
from pydantic import ValidationError

from contracts.content import InstagramCarouselContent


def test_instagram_carousel_contract():
    content = InstagramCarouselContent(
        content_family="C02",
        hook="You're probably overthinking protein timing.",
        slides=[
            {
                "slide_number": 1,
                "headline": "Protein timing",
                "body": "The useful answer is more nuanced than a magic window.",
            },
            {
                "slide_number": 2,
                "headline": "Start here",
                "body": "Daily intake and distribution both matter.",
            },
        ],
        caption="A practical breakdown of protein timing.",
        cta="Save this for later.",
        claims_used=["Daily protein intake matters."],
        capabilities_used=[],
    )

    assert content.platform == "instagram"
    assert content.format == "carousel"


def test_carousel_needs_at_least_two_slides():
    with pytest.raises(ValidationError):
        InstagramCarouselContent(
            content_family="C02",
            hook="Hook",
            slides=[
                {
                    "slide_number": 1,
                    "body": "Only one slide.",
                }
            ],
            caption="Caption",
        )
