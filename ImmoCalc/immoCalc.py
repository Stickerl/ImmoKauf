#import datetime
import datetime

def date_in_years(years):
    return datetime.datetime(datetime.datetime.now().year + years, datetime.datetime.now().month, datetime.datetime.now().day)

class Credit:
    volume = 0.0
    interest_rate = 0.0
    redemption_rate = 0.0
    annual_credit_rate = 0.0
    start_date = 0
    end_date = 0

    def __init__(self, initial_volume, interest, redemption, date = datetime.datetime.now()):
        self.volume = initial_volume
        self.interest_rate = interest
        self.redemption_rate = redemption
        self.annual_credit_rate = 0.0
        self.start_date = date
        self.calc_rate()
        cnt = 0
        while self.rest_volume(date_in_years(cnt)) > 0:
            cnt+=1
        self.end_date = date_in_years(cnt)

    def calc_rate(self):
        # credit rate is calculated on an annual basis but payed monthly
        self.annual_credit_rate = (self.volume * (self.interest_rate + self.redemption_rate) / 100)

    def rest_volume(self, date):
        if date.year == self.start_date.year:
            return self.volume

        years = date.year - self.start_date.year
        current_redemption = self.volume * self.redemption_rate / 100
        current_volume = self.volume - current_redemption

        for i in range(years - 1):
            current_volume = current_volume - (self.annual_credit_rate - current_volume * self.interest_rate / 100)
        return current_volume

    def redemption(self, date):
        return self.annual_credit_rate - (self.rest_volume(date) * self.interest_rate / 100)

    def interest(self, date):
        return self.rest_volume(date) * self.interest_rate / 100
    
    def serialise_stats(self, date=None):
        year = self.start_date
        if date:
            year = date
        return f"Credit stats for year {year}:\nRest volume: {self.rest_volume(year)}\nAnnual redemption: {self.redemption(year)}\nMonthly redemption: {self.redemption(year)/12}\nAnnual interest: {self.interest(year)}\nMonthly interest: {self.interest(year)/12}\n"

class AcquisitionCosts:
    purchase_price = 0.0
    broker_percent = 0.0 # markler
    notary_percent = 0.0 # notar
    land_registry_percent = 0.0 # grundbuch eintrag
    property_transfer_tax_percent = 0.0 # grunderwerbssteuer


class Immobilie:
    name = ""
    address = ""
    buy_date = datetime.date.year
    living_space = 0.0  # living space in square meters
    parking = 0 # number of parking places
    annual_value_increase_rate = 6.0


def main():
    test_credit = Credit(94000, 4.3,3.0)
    print(f"Credit end date {test_credit.end_date}")
    for i in range(20):
        next_year = datetime.datetime(datetime.datetime.now().year + i, datetime.datetime.now().month, datetime.datetime.now().day)
        print(test_credit.serialise_stats(next_year))

if __name__ == "__main__":
    main()