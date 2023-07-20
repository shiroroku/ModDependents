import json
from argparse import ArgumentParser

from selenium import webdriver
from selenium.webdriver.common.by import By

parser = ArgumentParser(description="Creates a JSON file containing all dependents for a CurseForge project.")
parser.add_argument("-p", type=str, required=True, help="Project Slug", metavar="STRING")
parser.add_argument("-o", type=str, required=False, help="Generated output JSON.", metavar="*.JSON")
args = parser.parse_args()

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
json_output = []
for i in range(1, total_pages + 1):
	print(f"Scraping page {i} of {total_pages}:\n")

	projects = driver.find_element(By.CSS_SELECTOR, ".listing.listing-project.project-listing").find_elements(By.CSS_SELECTOR, "div.flex.flex-col")

	for x in projects:
		title = x.find_element(By.CSS_SELECTOR, "h3").text
		link = x.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
		downloads = x.find_element(By.CSS_SELECTOR, "span").text.split(' ')[0]

		print(f"[{title}][{downloads}][{link}]")
		project = {
			"title": title,
			"link": link,
			"downloads": downloads
		}
		json_output.append(project)
	print()

	if i != total_pages:
		driver.get(f"{curseforge_url}?page={i + 1}")
		assert "Related Dependents" in driver.title

# Format downloads to int
print("Formatting...")
for project in json_output:
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
print("Writing to disk...")
file = f"./{mod_slug}.json"
if args.o is not None:
	file = args.o
with open(file, "w") as f:
	json.dump(json_output, f, indent=4)

driver.close()
print("Finished.")
