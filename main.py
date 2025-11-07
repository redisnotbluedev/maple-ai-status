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
		return {"success": True, "message": resp.choices[0].message.content, "model": model.id}
	except APIError as e:
		return {"success": False, "message": e.body, "model": model.id}

async def main():
	print("Getting models...")
	models = await maple.models.list()
	tasks = []
	data = {}

	print("Filtering models...")
	async for model in models:
		if "/v1/chat/completions" in model.type:
			data[model.id] = "pending"
			tasks.append(test_model(model, PROMPT))
	
	print(f"Queued {len(tasks)} prompts.")

	results = await asyncio.gather(*tasks)
	for result in results:
		data[result["model"]] = "success" if result["success"] else "failed"
	
	print(f"Successful models:\n{", ".join([k for k, v in data.items() if v == "success"])}")
	print(f"\nFailed models:\n{", ".join([k for k, v in data.items() if v == "failed"])}")

if __name__ == "__main__":
	asyncio.run(main())