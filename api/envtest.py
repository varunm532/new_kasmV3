import os
from dotenv import load_dotenv
load_dotenv()
variable = os.getenv('KASM_API_KEY')
print(variable)
