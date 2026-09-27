# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

import json
import copy
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox
import tempfile
import os

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
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options)
        driver.set_page_load_timeout(3)
        driver.implicitly_wait(1)
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

        records = {}
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
                    records[current["Aktenzeichen"]] = current
                    current = {}
            except Exception as e:
                print_exception(e, "parse_page", f"failed at record {len(records)+1}")
        return records

class RecordsFile:
    def __init__(self, file_path):
        self.file_path = file_path
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                self.records = json.load(f)
        except Exception as e:
            print_exception(e, "RecordsFile", "empty file created")
            self.records = {}
            self.save()

    @classmethod
    def copy(cls, source, file_path=None):
        if file_path is None:
            path = Path(source.file_path)
            file_path = path.with_name(f"{path.stem} copy{path.suffix}")

        new_file = cls(file_path)
        new_file.records = copy.deepcopy(source.records)
        new_file.save()

        return new_file

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)

    def mark_enty(self, object, mark):
        self.records[object["Aktenzeichen"]]["Mark"] = mark
        self.save()

    def compare(self, old, new):
        for trait in old:
            if trait == "Mark":
                continue
            if old[trait] != new[trait]:
                return "Changed"
        mark = None
        try:
            mark = old["Mark"]
        except Exception as e:
            print_exception(e, "RecordsFile.compare", f"entry {old["Aktenzeichen"]} is not marked so far!")
        return mark

    def check_for_differences(self, other):
        for entry in self.records:
            old = other.get(entry)
            if old:
                result = self.compare(other.get(entry), self.get(entry))
                if result:
                    self.mark_enty(self.get(entry), result)

    def get(self, entry_id):
        return self.records[entry_id]

    def update(self, data):
        self.records.update(data)

    def merge(self, other):
        for key, value in other.records.items():
            if key not in self.records:
                self.records[key] = copy.deepcopy(value)
        self.save()

class ZVGExplorer:
    def __init__(self):
        self.temp_file_path = None
        self.temp_records_file = None
        self.root = tk.Tk()
        self.root.title("ZVG Explorer")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.file_path = filedialog.asksaveasfilename(title="Select records database", defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not self.file_path:
            self.root.destroy()
            return

        if not os.path.exists(self.file_path):
            if not messagebox.askyesno("Create database", f"The file does not exist:\n{self.file_path}\n\nCreate it?"):
                self.root.destroy()
                return

        self.records_file = RecordsFile(self.file_path)
        self.update_button = tk.Button(self.root, text="Update database", command=self.on_update_database)
        self.update_button.pack(padx=20, pady=20)

    def on_update_database(self):
        data_grabber = DataGrabber()
        data_grabber.execute_search()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            self.temp_file_path = temp_file.name
        self.temp_records_file = RecordsFile(self.temp_file_path)
        self.temp_records_file.update(data_grabber.parse_page())
        self.records_file.merge(self.temp_records_file)
        self.records_file.check_for_differences(self.temp_records_file)
        self.records_file.save()
        self.temp_records_file.save()
        data_grabber.driver.quit()

    def on_close(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    explorer = ZVGExplorer()
    explorer.run()

if __name__ == '__main__':
    main()