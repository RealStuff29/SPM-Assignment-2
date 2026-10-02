from accrual import *

print("")

# EXAMPLE 1: Chris flies London to Los Angeles in Business
calc = MilesCalculator()

s = Sector(distance_miles=5400, fare_class="Business",
           partner_operated=False)

m = Member("Chris", tier="Gold")

a = calc.calculate_accrual(s, m)
print(f"Chris' accrual for London to Los Angeles: {a.miles} miles, {a.elite_miles} elite miles")
print(f"Chris' balances: {m.miles_balance} miles, {m.elite_miles_balance} elite miles\n")


# EXAMPLE 2: Ada takes a short hop from London to Edinburgh
calc = MilesCalculator()

s = Sector(distance_miles=330, fare_class="EconomyStandard",
           partner_operated=False)

m = Member("Ada", tier="Blue")

a = calc.calculate_accrual(s, m)
print(f"Ada's accrual for London to Edinburgh: {a.miles} miles, {a.elite_miles} elite miles")
print(f"Ada's balances: {m.miles_balance} miles, {m.elite_miles_balance} elite miles\n")


# EXAMPLE 3: Boudicca flies two sectors, having already earned 22,000 elite miles this year
calc = MilesCalculator()

s1 = Sector(distance_miles=3200, fare_class="EconomyLite",
            partner_operated=True)

s2 = Sector(distance_miles=6800, fare_class="Business",
            partner_operated=False)

m = Member("Boudicca", tier="Silver", miles_balance=0, elite_miles_balance=22000)

a = calc.calculate_accrual(s1, m)
print(f"Boudicca's accrual for London to Boston: {a.miles} miles, {a.elite_miles} elite miles")

a = calc.calculate_accrual(s2, m)
print(f"Boudicca's accrual for London to Singapore: {a.miles} miles, {a.elite_miles} elite miles")
print(f"Boudicca's balances: {m.miles_balance} miles, {m.elite_miles_balance} elite miles\n")
