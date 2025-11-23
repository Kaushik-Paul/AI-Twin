from mangum import Mangum
from backend.main.server import app

# Create the Lambda handler
handler = Mangum(app)
