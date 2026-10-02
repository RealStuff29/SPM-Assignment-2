import math
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ---------- Programme tables ----------

FARE_CLASS_EARNING = {
    "First": 2.0,
    "Business": 1.5,
    "PremiumEconomy": 1.1,
    "EconomyFlex": 1.0,
    "EconomyStandard": 0.75,
    "EconomyLite": 0.25,
    "EconomySaver": 0.0,
}

TIER_BONUS = {
    "Blue": 0.0,
    "Silver": 0.25,
    "Gold": 0.5,
    "Solitaire": 1.0,
}

# Fare classes that earn nothing at all when the sector is flown on a partner airline
PARTNER_ZERO_CLASSES = {"EconomyLite", "EconomySaver"}


# ---------- Domain model ----------

@dataclass
class Accrual:
    """Miles earned by a single sector: redeemable miles, and status-qualifying elite miles."""
    miles: float
    elite_miles: float


class Sector:
    def __init__(self, distance_miles: int, fare_class: str, partner_operated=False):
        if distance_miles <= 0:
            raise ValueError(f"distance_miles must be positive, got {distance_miles}")
        if fare_class not in FARE_CLASS_EARNING:
            raise ValueError(f"unknown fare_class: {fare_class}")

        self.distance_miles = distance_miles
        self.fare_class = fare_class
        self.partner_operated = partner_operated


class Member:
    def __init__(self, name: str, tier="Blue", miles_balance=0, elite_miles_balance=0):
        if tier not in TIER_BONUS:
            raise ValueError(f"unknown tier: {tier}")

        self.name = name
        self.tier = tier
        self.miles_balance = miles_balance
        self.elite_miles_balance = elite_miles_balance


# ---------- Accrual Rules ----------

class AccrualRule(ABC):
    """Abstract base for all rules."""
    @abstractmethod
    def apply(self, sector: Sector, member: Member, current: Accrual) -> Accrual:
        pass # pragma: no cover


class DistanceRule(AccrualRule):
    """Miles flown, subject to a minimum sector distance."""
    def __init__(self, minimum_sector: int):
        self.minimum_sector = minimum_sector

    def apply(self, sector, member, current):
        credited = max(sector.distance_miles, self.minimum_sector)
        return Accrual(credited, credited)


class FareClassRule(AccrualRule):
    """Earning percentage determined by the fare class booked."""
    def apply(self, sector, member, current):
        rate = FARE_CLASS_EARNING[sector.fare_class]
        return Accrual(current.miles * rate, current.elite_miles * rate)


class PartnerAirlineRule(AccrualRule):
    """Partner-operated sectors earn at a reduced rate; the cheapest fare classes earn nothing."""
    def __init__(self, partner_rate: float):
        self.partner_rate = partner_rate

    def apply(self, sector, member, current):
        if not sector.partner_operated:
            return current
        if sector.fare_class in PARTNER_ZERO_CLASSES:
            return Accrual(0.0, 0.0)
        return Accrual(current.miles * self.partner_rate,
                       current.elite_miles * self.partner_rate)


class TierBonusRule(AccrualRule):
    """Tier bonus, awarded on redeemable miles only."""
    def apply(self, sector, member, current):
        bonus = TIER_BONUS[member.tier]
        return Accrual(current.miles * (1 + bonus), current.elite_miles)


class MilestoneBonusRule(AccrualRule):
    """One-off bonus for crossing the elite mile milestone in this membership year."""
    def __init__(self, threshold: int, bonus: int):
        self.threshold = threshold
        self.bonus = bonus

    def apply(self, sector, member, current):
        before = member.elite_miles_balance
        after = before + current.elite_miles
        if before < self.threshold <= after:
            return Accrual(current.miles + self.bonus, current.elite_miles)
        return current


class RoundingRule(AccrualRule):
    """Accruals are always rounded down to whole miles."""
    def apply(self, sector, member, current):
        return Accrual(math.floor(current.miles), math.floor(current.elite_miles))


# ---------- Miles Calculator ----------

class MilesCalculator:
    def __init__(self):
        self.rules = [
        DistanceRule(minimum_sector=500),
        FareClassRule(),
        PartnerAirlineRule(partner_rate=0.5),
        TierBonusRule(),
        MilestoneBonusRule(threshold=25000, bonus=5000),
        RoundingRule()
    ]

    def calculate_accrual(self, sector: Sector, member: Member) -> Accrual:
        accrual = Accrual(0.0, 0.0)
        # First rule sets a base accrual; others adjust it.
        for i, rule in enumerate(self.rules):
            accrual = rule.apply(sector, member, accrual if i else Accrual(0.0, 0.0))
        member.miles_balance += accrual.miles
        member.elite_miles_balance += accrual.elite_miles
        return accrual
