from dotenv import load_dotenv
from mri_swarm.main import mri_swarm


load_dotenv()


result = mri_swarm(
    task="@MRI-Clinical-Correlation-Agent Analyze this brain MRI for any abnormalities",
    img="images/test.webp",
    return_log=True,
)

print(result)
