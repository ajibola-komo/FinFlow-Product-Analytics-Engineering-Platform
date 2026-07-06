import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

def run_dbt_models():
    subprocess.run(["dbt", "run"], check=True, cwd="growth_analytics",
                    env=os.environ)
