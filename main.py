import requests, os, threading, getpass, dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

dotenv.load_dotenv()
API_KEY = os.environ.get("MAPLEAI_API_KEY") or getpass.getpass("Enter your MapleAI API key: ")
models = requests.get("https://api.mapleai.de/v1/models").json()['data']
account_status = requests.get(
	"https://api.mapleai.de/v1/key-info",
	headers={"Authorization": f"Bearer {API_KEY}"}
).json()

modelstatus = {}
lock = threading.Lock()
count = 0
done = 0

for model in models:
	if not "/v1/chat/completions" in model['type']:
		continue
	count += 1

def check_model(model):
	payload = {
		"model": model['id'],
		"messages": [{"role": "user", "content": "a"}],
	}

	if model['id'].startswith("gpt-5") or model['id'].startswith("o"):
		payload["max_completion_tokens"] = 1
	else:
		payload["max_tokens"] = 1

	resp = requests.post(
		"https://api.mapleai.de/v1/chat/completions",
		json=payload,
		headers={"Authorization": f"Bearer {API_KEY}"},
	)

	with lock:
		modelstatus[model['id']] = (resp.status_code == 200)

remaining = (
	account_status['rpd'] - account_status['rpd_used'] - count
	if account_status['rpd'] != "unlimited"
	else "unlimited"
)
print(f"This operation will use {count} requests, leaving you with {remaining} requests left.")
print("0", end="")

with ThreadPoolExecutor(max_workers=15) as executor:
	futures = [executor.submit(check_model, model) for model in models if "/v1/chat/completions" in model['type']]
	for future in as_completed(futures):
		done += 1
		print("\033[2J\033[H", end="")
		print(f"{done}/{count}")
		print("\n\nWorking models:")
		for model_id, status in modelstatus.items():
			if status:
				print(model_id, end=" ")

		print("\n\nNon-working models:")
		for model_id, status in modelstatus.items():
			if not status:
				print(model_id, end=" ")