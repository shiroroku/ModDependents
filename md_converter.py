import json
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(description="Converts the dependent JSON file into a readable Markdown format.")
parser.add_argument("-f", type=str, required=True, help="JSON file", metavar="*.JSON")
parser.add_argument("-o", type=str, required=False, help="Output Markdown file", metavar="*.MD")
args = parser.parse_args()

print(f"Loading JSON [{args.f}]...")
with open(args.f, "r") as f:
	print("Formatting...")
	deps = json.load(f)
	# Sort by downloads
	sort = sorted(deps, key=lambda d: d["downloads"])
	sort.reverse()
	file = f"./{Path(f.name).stem}.md"
	if args.o is not None:
		file = args.o
	print(f"Writing MD [{file}]...")
	with open(file, "w", encoding="utf-8") as w:
		w.write("| Project | Downloads |\n")
		w.write("| --- | --- |\n")
		for project in sort:
			title = str(project["title"]).replace("|", "\\")  # "|" will break md table so replace it
			downloads = "{:,}".format(project["downloads"])  # adds commas for easier reading
			link = project["link"]
			w.write(f"| [{title}]({link}) | {downloads} |\n")
print("Finished.")
