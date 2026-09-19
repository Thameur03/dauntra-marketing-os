#!/usr/bin/env bash
set +e

echo
echo "=========================================="
echo " SECTION 4B CHECK"
echo "=========================================="
echo

python3 -m py_compile \
  app/rendering/video_models.py \
  app/rendering/lab_motion.py \
  scripts/render_lab_motion_demo.py

PY_STATUS=$?

echo "Syntax: $PY_STATUS"
echo

.venv/bin/python -m pytest -q tests/rendering/test_lab_motion.py
TEST_STATUS=$?

echo
echo "Tests: $TEST_STATUS"
echo

if command -v ffmpeg >/dev/null 2>&1; then
  echo "FFMPEG: PASS"
  FF_STATUS=0
else
  echo "FFMPEG: FAIL"
  FF_STATUS=1
fi

echo
echo "=========================================="
echo " RESULT"
echo "=========================================="
echo
echo "Syntax: $PY_STATUS"
echo "Tests:  $TEST_STATUS"
echo "FFmpeg: $FF_STATUS"
