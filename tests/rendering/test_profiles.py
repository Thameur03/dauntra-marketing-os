from app.rendering.profiles import (
    instagram_feed_profile,
)


def test_instagram_feed_profile():

    profile = (
        instagram_feed_profile()
    )


    assert (
        profile.profile_id
        == "INSTAGRAM_FEED"
    )

    assert (
        profile.width
        == 1080
    )

    assert (
        profile.height
        == 1350
    )

    assert (
        profile.mime_type
        == "image/jpeg"
    )

    assert (
        profile.extension
        == "jpg"
    )
