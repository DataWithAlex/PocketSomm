import toml
import os

# Define output file path
output_file = ".streamlit/secrets.toml"

# Ensure .streamlit directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open("firebase_key.json") as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open(output_file, "w") as target:
    target.write(toml_config)
