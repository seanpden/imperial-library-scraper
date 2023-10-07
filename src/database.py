import os
from dotenv import load_dotenv


load_dotenv()

CNXN_STR = os.environ["CNXN_STR"]
ENGINE = os.environ["ENGINE"]
