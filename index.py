import json
import os
import sys
import urllib.request

PROJECT = "Echo-Unvaulted"

def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)

def fetch_json(url):
	req = urllib.request.Request(url, headers={"User-Agent": f"{PROJECT}/1.0.0"})
	with urllib.request.urlopen(req) as res:
		return json.load(res)

def recover_plugin(internal_name, final):
	if not os.path.exists("./repo/index.json"):
		print("!!! Tried to recover plugin when repo isn't generated", file=sys.stderr)
		sys.exit(1)

	old_repo = load_json("./repo/index.json")
	plugin = next((p for p in old_repo if p.get("InternalName") == internal_name), None)
	if plugin is None:
		print(f"!!! {internal_name} not found in old repo", file=sys.stderr)
		sys.exit(1)

	final.append(plugin)
	print(f"Recovered {internal_name} from last manifest")

def do_repo(url, plugins, final):
	print(f"Fetching {url}...")
	repo = fetch_json(url)

	for internal_name in plugins:
		plugin = next((p for p in repo if p.get("InternalName") == internal_name), None)
		if plugin is None:
			print(f"!!! {internal_name} not found in {url}")
			recover_plugin(internal_name, final)
			continue

		tags = plugin.get("Tags") or []
		tags.append(PROJECT)
		plugin["Tags"] = tags

		final.append(plugin)

def main():
	repos_meta = load_json("./meta.json")
	final = []

	for meta in repos_meta:
		try:
			do_repo(meta["repo"], meta["plugins"], final)
		except Exception as e:
			print(f"!!! Failed to fetch {meta['repo']}", file=sys.stderr)
			print(e, file=sys.stderr)
			for plugin in meta["plugins"]:
				recover_plugin(plugin, final)

	os.makedirs("./repo", exist_ok=True)
	with open("./repo/index.json", "w", encoding="utf-8") as f:
		json.dump(final, f, indent="\t")
	print(f"Wrote {len(final)} plugins to repo/index.json")

if __name__ == "__main__":
	main()
