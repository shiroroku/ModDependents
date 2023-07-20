import json
from argparse import ArgumentParser

from selenium import webdriver
from selenium.webdriver.common.by import By

parser = ArgumentParser(description="Scrapes a CurseForge project dependents.")
parser.add_argument("-p", type=str, required=True, help="Project Slug", metavar="STRING")
parser.add_argument("-j", type=str, required=False, help="Output as JSON.", metavar="*.JSON")
parser.add_argument("-m", type=str, required=False, help="Output as Markdown.", metavar="*.MD")
args = parser.parse_args()

if args.j is None and args.m is None:
	raise RuntimeError("Please specify an output format")

mod_slug = args.p
curseforge_url = f"https://legacy.curseforge.com/minecraft/mc-mods/{mod_slug}/relations/dependents"

print(f"Loading WebDriver for [{curseforge_url}]...")

# Load up webdriver
options = webdriver.FirefoxOptions()
options.add_argument("-headless")
options.set_preference("javascript.enabled", False)
driver = webdriver.Firefox(options=options)
driver.get(curseforge_url)
if "Related Dependents" not in driver.title:
	raise RuntimeError("Curseforge response returned invalid dependents page")

# Get total pages of deps
total_pages = int(driver.find_element(By.CSS_SELECTOR, ".pagination.pagination-top").find_elements(By.CSS_SELECTOR, "span")[-1].text)

print(f"Page found. Total pages of dependents: {total_pages}\n")

# Load each page and record projects as a json object
projects_output = []
for i in range(1, total_pages + 1):
	print(f"Scraping page {i} of {total_pages}:\n")
	for project_element in driver.find_element(By.CSS_SELECTOR, ".listing.listing-project.project-listing").find_elements(By.CSS_SELECTOR, "div.flex.flex-col"):
		title = project_element.find_element(By.CSS_SELECTOR, "h3").text
		link = project_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
		downloads = project_element.find_element(By.CSS_SELECTOR, "span").text.split(' ')[0]

		print(f"[{title}][{downloads}][{link}]")
		project = {
			"title": title,
			"link": link,
			"downloads": downloads
		}
		projects_output.append(project)
	print()

	if i != total_pages:
		driver.get(f"{curseforge_url}?page={i + 1}")
		if "Related Dependents" not in driver.title:
			raise RuntimeError("Curseforge response returned invalid dependents page")

driver.close()

# Format downloads to int
print("Formatting...")
for project in projects_output:
	downloads = project["downloads"]
	if "K" in downloads:
		project["downloads"] = int(float(downloads[:-1]) * 1000)
	elif "M" in downloads:
		project["downloads"] = int(float(downloads[:-1]) * 1000000)
	elif "-" in downloads:
		project["downloads"] = 0
	else:
		project["downloads"] = int(downloads)

# Output json to file
if args.j is not None:
	print(f"Writing to JSON ({args.j})...")
	with open(args.j, "w", encoding="utf-8") as f:
		json.dump(projects_output, f, indent=4)

# Output to markdown
if args.m is not None:
	print(f"Writing to Markdown ({args.m})...")
	# Sort by downloads
	sort = sorted(projects_output, key=lambda d: d["downloads"])
	sort.reverse()
	with open(args.m, "w", encoding="utf-8") as w:
		w.write("| Project | Downloads |\n")
		w.write("| --- | --- |\n")
		for project in sort:
			title = project["title"].replace("|", "\\")  # "|" will break md table so replace it
			downloads = "{:,}".format(project["downloads"])  # adds commas for easier reading
			link = project["link"]
			w.write(f"| [{title}]({link}) | {downloads} |\n")

print("Finished.")
