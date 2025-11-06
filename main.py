from openai import OpenAI, APIError
import os, dotenv, json

dotenv.load_dotenv()

key = "MAPLEAI_API_KEY"

if not key in os.environ:
	raise RuntimeError(f"You must set {key} in the .env to use this tool.")

maple = OpenAI(
	api_key=os.getenv(key),
	base_url="https://api.mapleai.de/v1"
)
models = maple.models.list()

print("==== MODELS ====")
for model in models:
	if "/v1/chat/completions" in model.type:
		try:
			resp = maple.chat.completions.create(
				messages=[{"role": "user", "content": "hi"}],
				model=model.id
			)
			print(model.id + ": " + resp.choices[0].message.content[:200])
		except APIError as e:
			text = e.request.content
			print(f"{model.id}: Failed ({e.code}): {e.body}")