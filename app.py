import json
import os

from dotenv import load_dotenv
from jsonschema import validate
from groq import Groq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)

# Load schema
with open("schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

# Load prompt
with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# Load samples
with open("samples.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

os.makedirs("outputs", exist_ok=True)

results = []

for i, message in enumerate(samples, start=1):

    final_prompt = prompt.replace("{{MESSAGE}}", message)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": final_prompt}
        ],
        temperature=0,
        # Forces the model to return a single valid JSON object, no extra text
        response_format={"type": "json_object"}
    )

    output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(output)

        validate(instance=parsed, schema=schema)

        print(f"✅ Sample {i}: PASS")

        results.append({
            "sample": i,
            "valid": True,
            "json": parsed
        })

    except Exception as e:

        print(f"❌ Sample {i}: FAIL")

        results.append({
            "sample": i,
            "valid": False,
            "error": str(e),
            "response": output
        })

with open("outputs/test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("\nFinished.")