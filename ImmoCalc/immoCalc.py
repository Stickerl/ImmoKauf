import datetime

def date_in_years(years):
    return datetime.datetime(datetime.datetime.now().year + years, datetime.datetime.now().month, datetime.datetime.now().day)

def compound_interest(start_value, rate, iterations):
    return start_value * pow((1+rate/100), iterations)


class Credit:
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
    
    def serialise_stats(self, date_in=None):
        date = date_in if date_in else self.start_date
        return f"Credit stats for year {date}:\nRest volume: {self.rest_volume(date)}\nAnnual redemption: {self.redemption(date)}\nMonthly redemption: {self.redemption(date)/12}\nAnnual interest: {self.interest(date)}\nMonthly interest: {self.interest(date)/12}\n"

class AcquisitionCosts:
    def __init__(self, purchase_price, agent, notary, land_registry, property_transfer_tax):
        self.purchase_price = purchase_price
        self.agent_percent = agent # markler
        self.notary_percent = notary # notar
        self.land_registry_percent = land_registry # grundbuch eintrag
        self.property_transfer_tax_percent = property_transfer_tax # grunderwerbssteuer
        self.agent_abs = self.purchase_price * self.agent_percent / 100
        self.notary_abs = self.purchase_price *  self.notary_percent / 100
        self.land_registry_abs = self.purchase_price * self.land_registry_percent / 100
        self.property_transfer_tax_abs = self.purchase_price * self.property_transfer_tax_percent / 100

class RealEstate:
    def __init__(self, name, address, price, expected_rate, living_space, cold_rent, warm_rent, rent_increase, cost_rate, date = datetime.datetime.now(), parking = 0):
        self.name = name
        self.address = address
        self.purchase_price = price
        self.purchase_date = date
        self.living_space = living_space  # living space in square meters
        self.initial_cold_rent = cold_rent
        self.initial_warm_rent = warm_rent
        self.annual_rent_increase = rent_increase
        self.annual_cost_increase = cost_rate
        self.parking = parking # number of parking places
        self.annual_value_increase_rate = expected_rate

    def value(self, date_in=None):
        date = date_in if date_in else self.purchase_date
        return compound_interest(self.purchase_price,self.annual_value_increase_rate,(date.year - self.purchase_date.year))

    def cold_rent(self, date_in=None):
        date = date_in if date_in else self.purchase_date
        return compound_interest(self.initial_cold_rent, self.annual_rent_increase, (date.year - self.purchase_date.year))

    def warm_rent(self, date_in=None):
        date = date_in if date_in else self.purchase_date
        return self.cold_rent(date) + compound_interest(self.initial_warm_rent - self.initial_cold_rent, self.annual_cost_increase, (date.year - self.purchase_date.year))

    def serialize_stats(self, date):
        return f"Value of {self.name} in year {date.year} is: {self.value(date)}\nCold rent: {self.cold_rent(date)}\nWarm rent: {self.warm_rent(date)}\n"

def main():
    test_credit = Credit(94000, 4.3,3.0)
    test_real_estate = RealEstate("Test Wohnung", "Test Straße 3", 188000, 6.0, 36.5, 600, 738, 5.0, 5.0)
    print(f"Credit end date {test_credit.end_date}")
    for i in range(20):
        year = datetime.datetime(datetime.datetime.now().year + i, datetime.datetime.now().month, datetime.datetime.now().day)
        print(test_credit.serialise_stats(year))
        print(test_real_estate.serialize_stats(year))


if __name__ == "__main__":
    main()