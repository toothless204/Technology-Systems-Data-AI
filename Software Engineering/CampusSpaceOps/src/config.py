import os

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, "campus_space_ops.db")
SCHEMA    = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_FILE = os.path.join(BASE_DIR, "data", "seed", "seed_data.sql")

APP_TITLE  = "CampusSpaceOps"
APP_WIDTH  = 1100
APP_HEIGHT = 700

HASH_ALGORITHM  = "sha256"
HASH_ITERATIONS = 260_000
HASH_SALT       = b"campsalt"
