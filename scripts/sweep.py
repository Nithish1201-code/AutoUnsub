from sweeper.sweep import run


if not run(days=30, limit=50):
    raise SystemExit(1)