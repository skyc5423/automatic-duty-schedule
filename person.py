import random


class Person:
    def __init__(self, name, seniority, fixed_duties=None, unavailable_dates=None, can_work_consecutive=False):
        self.name = name
        self.seniority = seniority
        self.fixed_duties = fixed_duties or []
        self.unavailable_dates = unavailable_dates or []
        self.can_work_consecutive = can_work_consecutive
        self.duty_count = {'평일A': 0, '평일B': 0, '휴일A': 0, '휴일B': 0, '휴일C': 0}
        self.random_seed = random.random()

    def reset_duty_count(self):
        self.duty_count = {'평일A': 0, '평일B': 0, '휴일A': 0, '휴일B': 0, '휴일C': 0}
        self.random_seed = random.random()

    def get_total_ac_count(self):
        return self.duty_count['휴일A'] + self.duty_count['휴일C']

    def get_total_duty_count(self):
        return sum(self.duty_count.values())

    def __repr__(self):
        return f"{self.name}\n고정 당직: {self.fixed_duties}\n불가능한 날짜: {self.unavailable_dates}"

    def get_fixed_duties_as_string(self):
        return [f"{date} {duty}" for date, duty in self.fixed_duties]

    def get_unavailable_dates_as_string(self):
        return [f"{date} {duty}" for date, duty in self.unavailable_dates]
