from openai import AsyncOpenAI, APIError
import os, dotenv, asyncio

dotenv.load_dotenv()

key = "MAPLEAI_API_KEY"
PROMPT = "hi"

if not key in os.environ:
	raise RuntimeError(f"You must set {key} in the .env to use this tool.")

maple = AsyncOpenAI(
	api_key=os.getenv(key),
	base_url="https://api.mapleai.de/v1"
)

async def test_model(model, prompt):
	try:
		resp = await maple.chat.completions.create(
			messages=[{"role": "user", "content": prompt}],
			model=model.id
		)
		return (model.id + ": " + resp.choices[0].message.content[:200])
	except APIError as e:
		return (f"{model.id}: Failed ({e.code}): {e.body}")

async def main():
	models = maple.models.list()
	
	tasks = []
	for model in models:
		if "/v1/chat/completions" in model.type:
			tasks.append(test_model(model, PROMPT))

	results = asyncio.gather(*tasks)
	print("==== Models ====")
	for result in results:
		print(result)

if __name__ == "__main__":
	asyncio.run(main())