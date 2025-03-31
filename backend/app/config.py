import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = "postgresql://neondb_owner:npg_mIEGkf40blQP@ep-royal-rice-a144e1mt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
