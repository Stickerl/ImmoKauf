import datetime

def date_in_years(years, date= datetime.datetime.now()):
    return date.replace(year=date.year + years)

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

    def rest_volume(self, date_in):
        date = date_in if date_in else self.start_date
        if date.year == self.start_date.year:
            return self.volume

        years = date.year - self.start_date.year
        current_redemption = self.volume * self.redemption_rate / 100
        current_volume = self.volume - current_redemption

        for i in range(years - 1):
            current_volume = current_volume - (self.annual_credit_rate - current_volume * self.interest_rate / 100)
        return current_volume

    def redemption(self, date_in):
        date = date_in if date_in else self.start_date
        redemption = self.annual_credit_rate - (self.rest_volume(date) * self.interest_rate / 100)
        return 0 if self.rest_volume(date) <= 0 else redemption


    def interest(self, date):
        interest = self.rest_volume(date) * self.interest_rate / 100
        return 0 if interest < 0 else interest
    
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

    def get_total_acquisition_costs(self):
        return self.purchase_price + self.agent_abs + self.notary_abs + self.land_registry_abs + self.property_transfer_tax_abs


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
        return compound_interest(self.purchase_price,self.annual_value_increase_rate, self.get_ownership_years(date_in))

    def cold_rent(self, date_in=None):
        return compound_interest(self.initial_cold_rent, self.annual_rent_increase, self.get_ownership_years(date_in))

    def warm_rent(self, date_in=None):
        return self.cold_rent(date_in) + compound_interest(self.initial_warm_rent - self.initial_cold_rent, self.annual_cost_increase, self.get_ownership_years(date_in))

    def serialize_stats(self, date):
        return f"Value of {self.name} in year {date.year} is: {self.value(date)}\nCold rent: {self.cold_rent(date)}\nWarm rent: {self.warm_rent(date)}\n"

    def get_living_space(self):
        return self.living_space

    def get_ownership_years(self, date_in=None):
        date = date_in if date_in else self.purchase_date
        return date.year - self.purchase_date.year

    def get_annual_cost_increase(self):
        return self.annual_cost_increase

    def calc_pre_tax_rent_return(self, date_in=None):
        return (12 * self.cold_rent(date_in)) / self.purchase_price

    def calc_post_tax_rent_return(self, running_costs, reserves, date_in=None):
        return (self.cold_rent(date_in) + running_costs.none_allocatable(reserves, date_in)) / self.purchase_price

    def calc_rent_performance_figures(self, running_costs, reserves, date_in=None):
        return { self.calc_pre_tax_rent_return(date_in), (1 /self.calc_pre_tax_rent_return(date_in)), self.calc_post_tax_rent_return(running_costs, reserves, date_in)}


class Deprecations:
    def __init__(self, afa_capital, afa_rate, afa_percent, start_date, time_frame=40):
        self.afa_capital = afa_capital * afa_percent / 100
        self.afa_rate = afa_rate
        self.annual_afa = self.afa_capital * self.afa_rate / 100
        self.end_date = date_in_years(time_frame, start_date)

    def linear_per_year(self, date_in=None):
        if date_in:
            if date_in.year >= self.end_date.year:
                return 0
        return self.afa_capital * self.afa_rate / 100


class Reserves:
    def __init__(self, per_square_meter, percent_of_rent, real_estate: RealEstate):
        self.per_square_meter = per_square_meter
        self.percent_of_rent = percent_of_rent
        self.real_estate = real_estate

    def reserve_at_year(self, date_in=None):
        private_reserve = compound_interest(self.real_estate.get_living_space() * self.per_square_meter / 12, self.real_estate.get_annual_cost_increase(), self.real_estate.get_ownership_years(date_in))
        return private_reserve + self.expected_rent_loss(date_in)

    def reserve_accumulated(self, date_in=None):
        accumulated = 0
        ownership_years = self.real_estate.get_ownership_years(date_in)
        date = datetime.datetime(date_in.year - ownership_years, date_in.month, date_in.day)
        for i in range(ownership_years):
            accumulated += self.reserve_at_year(date)
            date.replace(year=date.year + i)
        return accumulated

    def expected_rent_loss(self, date_in=None):
        return self.real_estate.warm_rent(date_in) * self.percent_of_rent / 100

    def serialize_stats(self, date):
        return f"Reserve in year {date.year} is: {self.reserve_at_year(date)}\nAccumulated reserve in year {date.year}: {self.reserve_accumulated(date)}\nExpected rent loss in year {date.year}: {self.expected_rent_loss(date)}\n"


class RunningCosts:
    def __init__(self, cottage_deduction_allocatable, cottage_deduction_none_allocatable, property_tax, weg_reserve, real_estate: RealEstate):
        self.cottage_deduction_allocatable = cottage_deduction_allocatable # Hausgeld umlagefähig
        self.cottage_deduction_none_allocatable = cottage_deduction_none_allocatable # Hausgeld nicht umlagefähig
        self.property_tax = property_tax # Grundsteuer
        self.weg_reserve = weg_reserve
        self.real_estate  = real_estate

    def allocatable(self, date_in=None):
        # Note: The excel tool applies compound interest to property_tax which we think is wrong as the property tax is calculated based on square meters and a fixed percentage
        # return compound_interest(self.cottage_deduction_allocatable, self.real_estate.get_annual_cost_increase(), self.real_estate.get_ownership_years(date_in)) + self.property_tax
        return compound_interest(self.cottage_deduction_allocatable + self.property_tax, self.real_estate.get_annual_cost_increase(), self.real_estate.get_ownership_years(date_in))

    def none_allocatable(self, reserve: Reserves, date_in=None):
        return compound_interest(self.cottage_deduction_none_allocatable, self.real_estate.get_annual_cost_increase(), self.real_estate.get_ownership_years(date_in)) + reserve.reserve_at_year(date_in)

    def total(self, reserve: Reserves, date_in=None):
        return self.allocatable(date_in) + self.none_allocatable(reserve, date_in)

    def get_cottage_deduction_sum(self, date_in=None):
        return compound_interest(self.cottage_deduction_allocatable + self.cottage_deduction_none_allocatable, self.real_estate.get_annual_cost_increase(), self.real_estate.get_ownership_years(date_in))

    def serialize_stats(self, reserve: Reserves, date):
        return f"RunningCosts in year {date.year} is:\nAllocatable: {self.allocatable(date)}\nNon allocatable: {self.none_allocatable(reserve, date)}\nSum: {self.total(reserve, date)}\nCottage deduction: {self.get_cottage_deduction_sum(date)}\nToDo: RunningCosts::allocatable still calculates according to the excel sheet wich is flawed!\n"


class Cashflow:
    def __init__(self, real_estate: RealEstate, credit: Credit, running_cost: RunningCosts, reserves: Reserves, deprecations: Deprecations, tax_rate=42):
        self.real_estate = real_estate
        self.credit = credit
        self.running_cost = running_cost
        self.reserves = reserves
        self.deprecations = deprecations
        self.tax_rate = tax_rate

    def taxed_cash_flow(self, date_in=None):
        warm_rent = self.real_estate.warm_rent(date_in)
        total_running_cost = self.running_cost.total(self.reserves, date_in)
        reserves = self.reserves.reserve_at_year(date_in)
        monthly_interest = self.credit.interest(date_in) / 12
        monthly_deprecations = self.deprecations.linear_per_year(date_in)/12
        result = warm_rent - (total_running_cost - reserves + monthly_interest + monthly_deprecations)
        return result

    def taxes(self, date_in=None):
        return self.taxed_cash_flow(date_in) * self.tax_rate / 100

    def operative_cash_flow(self, date_in=None):
        warm_rent = self.real_estate.warm_rent(date_in)
        running_cost = self.running_cost.total(self.reserves, date_in)
        monthly_redemption = self.credit.redemption(date_in) / 12
        monthly_interest = self.credit.interest(date_in) / 12
        return  warm_rent - (running_cost + monthly_redemption + monthly_interest)

    def post_tax_cash_flow(self, date_in=None):
        return self.operative_cash_flow(date_in) - self.taxes(date_in)

    def serialize_stats(self, date):
        return f"Cashflow in year {date.year} is:\nOperative: {self.operative_cash_flow(date)}\nTaxed cash flow: {self.taxed_cash_flow(date)}\nTaxes: {self.taxes(date)}\nPost taxes: {self.post_tax_cash_flow(date)}\n"

    #ToDo: calculation of retuns and capital growth


def main():
    test_credit = Credit(94000, 4.3,3.0)
    test_real_estate = RealEstate("Test Wohnung", "Test Straße 3", 188000, 6.0, 36.5, 600, 738, 5.0, 5.0)
    test_reserve = Reserves(10, 3, test_real_estate)
    test_running_cost =  RunningCosts(131, 167, 7, 28, test_real_estate)
    test_acquisition_cost = AcquisitionCosts(test_real_estate.purchase_price,3.57, 1.5,0.5,3.5)
    test_deprecations = Deprecations(test_acquisition_cost.get_total_acquisition_costs(), 2.5, 75, test_real_estate.purchase_date)
    test_cash_flow = Cashflow(test_real_estate, test_credit, test_running_cost, test_reserve, test_deprecations)

    print(f"Credit end date {test_credit.end_date}")
    for i in range(50):
        year = datetime.datetime(datetime.datetime.now().year + i, datetime.datetime.now().month, datetime.datetime.now().day)
        print(test_credit.serialise_stats(year))
        print(test_real_estate.serialize_stats(year))
        print(test_reserve.serialize_stats(year))
        print(test_running_cost.serialize_stats(test_reserve, year))
        print(test_cash_flow.serialize_stats(year))
        print("\n\n")


if __name__ == "__main__":
    main()