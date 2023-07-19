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
assert "Related Dependents" in driver.title

# Get total pages of deps
total_pages = int(driver.find_element(By.XPATH, "//div[@class='pagination pagination-top flex items-center']").find_elements(By.XPATH, ".//span")[-1].text)

print(f"Page found. Total pages of dependents: {total_pages}\n")

# Load each page and record projects as a json object
json_output = []
for i in range(total_pages):
	print(f"Scraping page {i + 1} of {total_pages}:\n")
	driver.get(f"{curseforge_url}?page={i + 1}")
	assert "Related Dependents" in driver.title

	projects = driver.find_element(By.XPATH, "//ul[@class='listing listing-project project-listing']").find_elements(By.XPATH, ".//div[@class='flex flex-col']")

	for x in projects:
		title = x.find_element(By.XPATH, ".//h3").text
		link = x.find_element(By.XPATH, ".//a").get_attribute("href")
		downloads = x.find_element(By.XPATH, ".//span").text.split(' ')[0]

		print(f"[{title}][{downloads}][{link}]")
		project = {
			"title": title,
			"link": link,
			"downloads": downloads
		}
		json_output.append(project)
	print()

# Format downloads to int
print("Formatting...")
for project in json_output:
	downloads = str(project["downloads"])
	if "K" in downloads:
		downloads = float(downloads.replace('K', '')) * 1000
	elif "M" in downloads:
		downloads = float(downloads.replace('M', '')) * 1000000
	elif "-" in downloads:
		downloads = 0
	project["downloads"] = int(downloads)

# Output json to file
print("Writing to disk...")
file = f"./{mod_slug}.json"
if args.o is not None:
	file = args.o
with open(f"./{mod_slug}.json", "w") as f:
	f.write(json.dumps(json_output, indent=4))

driver.close()
print("Finished.")
