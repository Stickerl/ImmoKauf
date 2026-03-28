import datetime
import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as numpy


def date_in_years(years, date=datetime.datetime.now()):
    return date.replace(year=date.year + years)


def compound_interest(start_value, rate, iterations):
    return start_value * pow((1 + rate / 100), iterations)


class Credit:
    def __init__(self, initial_volume, interest, redemption, date=datetime.datetime.now()):
        self.volume = initial_volume
        self.interest_rate = interest
        self.redemption_rate = redemption
        self.annual_credit_rate = 0.0
        self.start_date = date
        self.calc_rate()
        cnt = 0
        while self.rest_volume(date_in_years(cnt)) > 0:
            cnt += 1
        self.end_date = date_in_years(cnt)

    @classmethod
    def from_config(cls, cfg, date):
        return cls(cfg["initial_volume"], cfg["interest"], cfg["redemption"], date)

    def calc_rate(self):
        self.annual_credit_rate = (self.volume * (self.interest_rate + self.redemption_rate) / 100)

    def rest_volume(self, date_in=None):
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
    
    def serialize_stats(self, date_in=None):
        date = date_in if date_in else self.start_date
        return f"\nCredit stats for year {date}:\nRest volume: {self.rest_volume(date)}\nAnnual redemption: {self.redemption(date)}\nMonthly redemption: {self.redemption(date)/12}\nAnnual interest: {self.interest(date)}\nMonthly interest: {self.interest(date)/12}\n"


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

    @classmethod
    def from_config(cls, cfg, purchase_price):
        return cls(
            purchase_price,
            cfg["agent"],
            cfg["notary"],
            cfg["land_registry"],
            cfg["property_transfer_tax"]
        )

    def get_total_acquisition_costs(self):
        return self.purchase_price + self.agent_abs + self.notary_abs + self.land_registry_abs + self.property_transfer_tax_abs


class RealEstate:
    def __init__(self, name, address, price, expected_rate, living_space, cold_rent, warm_rent, rent_increase, cost_rate, date = datetime.datetime.now(), parking = 0, parking_price = 0):
        self.name = name
        self.address = address
        self.purchase_price = price + (parking_price if parking > 0 else 0)
        self.purchase_date = date
        self.living_space = living_space  # living space in square meters
        self.initial_cold_rent = cold_rent
        self.initial_warm_rent = warm_rent
        self.annual_rent_increase = rent_increase
        self.annual_cost_increase = cost_rate
        self.parking = parking # number of parking places
        self.parking_price = parking_price
        self.annual_value_increase_rate = expected_rate

    @classmethod
    def from_config(cls, cfg, scenario, date):
        # scenario is a dict with keys: cost_rate, rent_increase, expected_rate
        return cls(
            cfg["name"],
            cfg["address"],
            cfg["price"],
            scenario["expected_rate"],
            cfg["living_space"],
            cfg["cold_rent"],
            cfg["warm_rent"],
            scenario["rent_increase"],
            scenario["cost_rate"],
            date,
            cfg.get("parking", 0),
            cfg.get("parking_price", 0)
        )

    def value(self, date_in=None):
        # This returns the value at start of the year. The excel tool uses end of year / start of next year
        return compound_interest(self.purchase_price,self.annual_value_increase_rate, self.get_ownership_years(date_in))

    def cold_rent(self, date_in=None):
        return compound_interest(self.initial_cold_rent, self.annual_rent_increase, self.get_ownership_years(date_in))

    def warm_rent(self, date_in=None):
        return self.cold_rent(date_in) + compound_interest(self.initial_warm_rent - self.initial_cold_rent, self.annual_cost_increase, self.get_ownership_years(date_in))

    def serialize_stats(self, date):
        return f"\nValue of {self.name} in year {date.year} is: {self.value(date)}\nCold rent: {self.cold_rent(date)}\nWarm rent: {self.warm_rent(date)}\n"

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

    @classmethod
    def from_config(cls, cfg, acquisition_costs, date):
        return cls(
            acquisition_costs.get_total_acquisition_costs(),
            cfg["afa_rate"],
            cfg["afa_percent"],
            date,
            cfg.get("time_frame", 40)
        )

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

    @classmethod
    def from_config(cls, cfg, real_estate):
        return cls(cfg["per_square_meter"], cfg["percent_of_rent"], real_estate)

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
        return f"\nReserve in year {date.year} is: {self.reserve_at_year(date)}\nAccumulated reserve in year {date.year}: {self.reserve_accumulated(date)}\nExpected rent loss in year {date.year}: {self.expected_rent_loss(date)}\n"


class RunningCosts:
    def __init__(self, cottage_deduction_allocatable, cottage_deduction_none_allocatable, property_tax, weg_reserve, real_estate: RealEstate):
        self.cottage_deduction_allocatable = cottage_deduction_allocatable # Hausgeld umlagefähig
        self.cottage_deduction_none_allocatable = cottage_deduction_none_allocatable # Hausgeld nicht umlagefähig
        self.property_tax = property_tax # Grundsteuer
        self.weg_reserve = weg_reserve
        self.real_estate  = real_estate

    @classmethod
    def from_config(cls, cfg, real_estate):
        return cls(
            cfg["cottage_deduction_allocatable"],
            cfg["cottage_deduction_none_allocatable"],
            cfg["property_tax"],
            cfg["weg_reserve"],
            real_estate
        )

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
        return f"\nRunningCosts in year {date.year} is:\nAllocatable: {self.allocatable(date)}\nNon allocatable: {self.none_allocatable(reserve, date)}\nSum: {self.total(reserve, date)}\nCottage deduction: {self.get_cottage_deduction_sum(date)}\nToDo: RunningCosts::allocatable still calculates according to the excel sheet wich is flawed!\n"


class Cashflow:
    def __init__(self, real_estate: RealEstate, credit: Credit, running_cost: RunningCosts, reserves: Reserves, deprecations: Deprecations, tax_rate=42):
        self.real_estate = real_estate
        self.credit = credit
        self.running_cost = running_cost
        self.reserves = reserves
        self.deprecations = deprecations
        self.tax_rate = tax_rate

    @classmethod
    def from_config(cls, cfg, real_estate, credit, running_cost, reserves, deprecations):
        return cls(
            real_estate,
            credit,
            running_cost,
            reserves,
            deprecations,
            cfg.get("tax_rate", 42)
        )

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

    def accumulated_cashflow(self, start_date, end_date):
        acc_cash_flow = 12 * self.post_tax_cash_flow(start_date)
        for i in range(end_date.year - start_date.year):
            acc_cash_flow += 12 * self.post_tax_cash_flow(date_in_years(i+1, start_date))
        return acc_cash_flow

    def serialize_stats(self, date):
        return f"\nCashflow in year {date.year} is:\nOperative: {self.operative_cash_flow(date)}\nTaxed cash flow: {self.taxed_cash_flow(date)}\nTaxes: {self.taxes(date)}\nPost taxes: {self.post_tax_cash_flow(date)}\nAccumulated cash flow: {self.accumulated_cashflow(self.real_estate.purchase_date, date)}\n"

 #ToDo: calculation of retuns
class Returns:
    def __init__(self, acquisition_cost: AcquisitionCosts, real_estate: RealEstate, cash_flow: Cashflow, credit: Credit, ):
        self.acquisition_cost = acquisition_cost
        self.real_estate = real_estate
        self.cash_flow = cash_flow
        self.credit = credit
        self.equity_capital = self.acquisition_cost.get_total_acquisition_costs() - self.credit.rest_volume(None)  # eigenkapital

    @classmethod
    def from_dependencies(cls, acquisition_cost, real_estate, cash_flow, credit):
        return cls(acquisition_cost, real_estate, cash_flow, credit)

    def capital_growth(self, date_in=None):
        date = date_in if date_in else self.real_estate.purchase_date
        acc_cash_flow = self.cash_flow.accumulated_cashflow(self.real_estate.purchase_date, date)
        rest_credit = self.credit.rest_volume(date)
        real_estate_value = self.real_estate.value(date)
        return real_estate_value - rest_credit - self.get_equity_capital() - acc_cash_flow

    def get_equity_capital(self):
        return self.equity_capital

    def serialize_stats(self, date):
        return f"\nCapital growth in year {date.year} is: {self.capital_growth(date)}\n"

class InvestmentPrediction:
    def __init__(self, config, scenario):
        now = datetime.datetime.now()

        self.real_estate = RealEstate.from_config(config["real_estate"], scenario, now)
        self.credit = Credit.from_config(config["credit"], now)
        self.acquisition_costs = AcquisitionCosts.from_config(
            config["acquisition_costs"],
            self.real_estate.purchase_price
        )
        self.reserves = Reserves.from_config(config["reserves"], self.real_estate)
        self.running_costs = RunningCosts.from_config(config["running_costs"], self.real_estate)
        self.deprecations = Deprecations.from_config(config["deprecations"], self.acquisition_costs, now)
        self.cashflow = Cashflow.from_config(
            config["cashflow"],
            self.real_estate,
            self.credit,
            self.running_costs,
            self.reserves,
            self.deprecations
        )
        self.returns = Returns.from_dependencies(
            self.acquisition_costs,
            self.real_estate,
            self.cashflow,
            self.credit
        )
        self.cashflow_break_even = None
        self.acc_cashflow_break_even = None
        self.capital_break_even = None
        self.purchase_price_factor =  round(self.acquisition_costs.purchase_price / (self.real_estate.cold_rent() * 12), 2)

    def get_name(self):
        return self.real_estate.name

    def generate_prediction(self, ax1, ax2, end_date, label=""):
        start_date = self.real_estate.purchase_date
        years = [date_in_years(i, start_date) for i in range(end_date.year - start_date.year)]
        cashflows, self.cashflow_break_even, acc_cashflow, self.acc_cashflow_break_even = self.cashflow_prediction(end_date)
        capital_growth, self.capital_break_even = self.capital_prediction(cashflows, end_date)

        # Plot onto provided axes
        ax1.plot(years, cashflows, label=f"Cashflow ({label})")
        ax1.plot(years, acc_cashflow, label=f"Accumulated cashflow ({label})")
        ax2.plot(years, capital_growth, linestyle="--", label=f"Capital Growth ({label})")
        return dict([["Cashflow" , self.cashflow_break_even], ["Acc Cashflow", self.acc_cashflow_break_even], ["Capital", self.capital_break_even]])

    def cashflow_prediction(self, end_date=None):
        start_date = self.real_estate.purchase_date
        if end_date is None:
            end_date = start_date
        cashflow = []
        acc_cashflow = []
        break_even_date = None
        acc_break_even_date = None
        for i in range(end_date.year - start_date.year):
            date = date_in_years(i, start_date)
            # cashflow and its break even date
            cashflow.append(self.cashflow.post_tax_cash_flow(date))
            if break_even_date is None and cashflow[i] > 0:
                break_even_date = date
            # accumulated cashflow and its break even date
            acc_cashflow.append(cashflow[i] + (acc_cashflow[i-1] if i > 0 else 0))
            if acc_break_even_date is None and acc_cashflow[i] > 0:
                acc_break_even_date = date

        if acc_cashflow[-1] < 0:
            # it is possible that the accumulated cashflow peaks to > 0 and falls below 0 later. Calling that break even is misleading. It most likely occurs when the credit rest volume reaches 0.
            acc_break_even_date = None
        if cashflow[-1] < 0:
            # if the final cash flow is < 0 we don't care for previous peaks > 0
            break_even_date = None
        return cashflow, break_even_date, acc_cashflow, acc_break_even_date

    def capital_prediction(self, cashflow, end_date=None):
        start_date = self.real_estate.purchase_date
        if end_date is None:
            end_date = start_date
        relative_capital_growth = []
        overall_capital_growth = []
        break_even_date = None
        for i in range(end_date.year - start_date.year):
            date = date_in_years(i, start_date)
            relative_capital_growth.append(self.returns.capital_growth(date))
            overall_capital_growth.append(relative_capital_growth[i] - self.returns.get_equity_capital() + cashflow[i])
            if break_even_date is None and overall_capital_growth[i] > 0:
                break_even_date = date
        return overall_capital_growth, break_even_date

    def serialize_stats(self, date_in=None):
        return self.credit.serialize_stats(date_in) + self.real_estate.serialize_stats(date_in) + self.reserves.serialize_stats(date_in) + self.running_costs.serialize_stats(self.reserves, date_in) + self.cashflow.serialize_stats(date_in) + self.returns.serialize_stats(date_in)

def serialize_break_even(date):
    return f"{date.year if date else "Break even not reached!"}"

class CornerCasePrediction:
    def __init__(self, timeframe, investment_config, scenarios):
        self.name = investment_config["real_estate"]["name"]
        self.worst_case = InvestmentPrediction(investment_config, scenarios["worst"])
        self.expected = InvestmentPrediction(investment_config, scenarios["expected"])
        self.best_case = InvestmentPrediction(investment_config, scenarios["best"])
        self.scenario_predictions = [[self.worst_case, "worst case"] , [self.expected, "expected"], [self.best_case, "best case"]]
        self.end_date = date_in_years(timeframe)
        self.evaluation_stats = dict()

    def plot(self):
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        for [predictor, name] in self.scenario_predictions:
            self.evaluation_stats[name] = predictor.generate_prediction(ax1, ax2, self.end_date, name)

        # Labels
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Post-tax cash flow (yearly)")
        ax2.set_ylabel("Capital growth")
        plt.title(f"Cash Flow and Capital Growth Over Time for {self.name}")

        # Legend
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.grid()
        plt.tight_layout()

    def get_evaluation_stats(self):
        return self.evaluation_stats

    def get_evaluation_meta_data(self):
        return dict([["Purchase price", self.expected.real_estate.purchase_price],["Price factor", self.expected.purchase_price_factor]])


def show_break_even_tables(investment_instances: list[CornerCasePrediction]):
    #ToDo: show purchase price
    # Collect scenario names
    table_data = dict()
    table_data.setdefault('column names', [])
    table_data.setdefault('scenarios', dict())
    meta_data = dict()
    for inv in investment_instances:
        # collect meta data for the investment. meta data are case independent performance indicators
        meta_data.setdefault('data', [])
        meta_data['data'].append(inv.get_evaluation_meta_data())
        meta_data.setdefault('names', [])
        meta_data['names'].append(inv.name)
        # reorganize data in rows for table visualization
        stats = inv.get_evaluation_stats()
        table_data['column names'].append(inv.name)
        for scenario_name in stats:
            table_data['scenarios'].setdefault(scenario_name,dict())
            for metric_name in stats[scenario_name]:
                table_data['scenarios'][scenario_name].setdefault(metric_name,[])
                table_data['scenarios'][scenario_name][metric_name].append(serialize_break_even(stats[scenario_name][metric_name]))


    # Create figure with subplots (1 row per scenario, table per subplot)
    fig = plt.figure(constrained_layout=True, figsize=(2 + 2*len(table_data['column names']), 2 + 2*len(table_data['column names'])))
    spec = gridspec.GridSpec(ncols=1, nrows=len(table_data['column names']), figure=fig)

    for i, scenario_name in enumerate(table_data['scenarios']):
        scenario = table_data['scenarios'][scenario_name]
        ax = fig.add_subplot(spec[i, 0])
        ax.axis('off')  # hide axes
        row_labels = [row_label for row_label in scenario]
        row_data = [scenario[metric] for metric in row_labels]

        # Build table with metrics as rows, investments as columns
        table = ax.table(cellText=row_data,
                         rowLabels=row_labels,
                         colLabels=table_data['column names'],
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title(f"Break-even statistics: {scenario_name}", fontweight='bold')

    ax = fig.add_subplot(spec[i+1, 0])
    ax.axis('off')
    metric_names = [inv for inv in meta_data['data'][0]]
    table = ax.table(cellText= numpy.transpose([[inv[metric_names[0]],inv[metric_names[1]]] for i, inv in enumerate(meta_data['data'])]),
                     rowLabels=metric_names,
                     colLabels=meta_data['names'],
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title("Meta data:", fontweight='bold')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--scenario", choices=["worst", "expected", "best"], default="expected")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    scenarios = config["assumptions"]["scenarios"]

    investment_instances =[]
    for investment_cfg in config["investments"]:
        investment_instances.append(CornerCasePrediction(config["timeframe"], investment_cfg, scenarios))

    for investment in investment_instances:
        investment.plot()

    # ToDo Add capital growth at a specific year and cost per qm
    show_break_even_tables(investment_instances)
    plt.show()


if __name__ == "__main__":
    main()