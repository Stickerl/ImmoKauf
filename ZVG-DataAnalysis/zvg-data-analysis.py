# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

import json

def print_exception(exception, location, message=""):
    print(f"Exception occured in {location}:\n{message}\n{exception}\n")

class DataGrabber:
    def __init__(self):
        self.driver = self.setup_driver()
        self.defaultTimeout = 5
        self.retries = 5
        self.current_city = ''
        self.current_url = ''

    @staticmethod
    def setup_driver():
        """Set up and return a Firefox WebDriver."""
        #driver = webdriver.Firefox()  # Ensure GeckoDriver is in PATH
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(3)
        driver.implicitly_wait(3)
        return driver

    def open_page(self):
        return self.driver.get('https://www.zvg-portal.de/index.php?button=Termine%20suchen')

    def execute_search(self):
        self.open_page()
        # Find land selection dropdown and select Bayer
        land_dropdown = Select(WebDriverWait(self.driver, self.defaultTimeout).until(
            EC.presence_of_element_located((By.NAME, "land_abk"))
        ))
        land_dropdown.select_by_visible_text("Bayern")

        # ToDo: select items based on a json file
        obj_list = WebDriverWait(self.driver, self.defaultTimeout).until(
            EC.presence_of_element_located((By.ID, "obj_liste"))
        )
        option = obj_list.find_element(
            #By.XPATH, ".//option[normalize-space()='Eigentumswohnung (ab 5 Zimmer)']" # Test value which gives just 3 results
            By.XPATH, ".//option[normalize-space()='Eigentumswohnung (1 bis 2 Zimmer)']"
        )
        ActionChains(self.driver).double_click(option).perform()

        # Find and Click search button
        search_button = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label=Suchen]")[0]
        search_button.click() # Leads to the next page

        # Find page selection dropdown and select Bayer
        try:
            select = WebDriverWait(self.driver, 0.1).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "select[onchange^='blaettern']"
                ))
            )
            Select(select).select_by_visible_text("alle")
        except Exception as e:
            # actually expected: Page selection does not exist if there are not enough results
            print_exception(e, "execute_search", "Page selection dropdown not found")


    def parse_page(self):
        form = self.driver.find_element(By.NAME, "form_sucheZvg")
        tables = form.find_elements(By.TAG_NAME, "table")
        try:
            table = self.driver.find_element(
                By.XPATH,
                "//comment()[contains(., 'Seiten zum Blaettern Ende')]"
                "/following::table[1]"
            )
        except:
            table = tables[0]

        records = []
        current = {}

        for row in table.find_elements(By.TAG_NAME, "tr"):
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue

                label = cells[0].text.strip()

                if label == "Aktenzeichen":
                    # in case the date was canceled, there is no link at Aktenzeichen
                    try:
                        link = cells[1].find_element(By.TAG_NAME, "a")
                        current["Aktenzeichen"] = link.text.strip()
                        current["url"] = link.get_attribute("href")
                    except:
                        current["Aktenzeichen"] = cells[1].text.strip()
                        current["url"] = ""

                elif label == "Amtsgericht":
                    current["Amtsgericht"] = cells[1].text.strip()

                elif label == "Objekt/Lage":
                    current["Objekt/Lage"] = cells[1].text.strip()

                elif label.startswith("Verkehrswert"):
                    current["Verkehrswert"] = cells[1].text.strip()

                elif label == "Termin":
                    current["Termin"] = cells[1].text.strip()

                elif len(cells) > 1 :
                    if "Amtliche Bekanntmachung" in cells[1].text.strip():
                        # ToDo: link doesnt work
                        current["Amtliche Bekanntmachung"] = cells[1].find_element(By.TAG_NAME, "a").get_attribute("href")

                elif row.find_elements(By.TAG_NAME, "hr"):
                    records.append(current)
                    current = {}
            except Exception as e:
                print_exception(e, "parse_page", f"failed at record {len(records)+1}")
        return records

def main():
    data_grabber = DataGrabber()
    data_grabber.execute_search()
    records = data_grabber.parse_page()
    for record in records:
        continue


if __name__ == '__main__':
    main()