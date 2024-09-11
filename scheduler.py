
from datetime import datetime, timedelta
import pandas as pd
from pandas import DataFrame


class Scheduler:
    def __init__(self, people, start_date, end_date, custom_weekend_list=None):
        self.people = people
        self.start_date = start_date
        self.end_date = end_date
        self.schedule = {}
        self.custom_weekend_list = custom_weekend_list or []
        self.korean_day_names = {
            0: '월요일',
            1: '화요일',
            2: '수요일',
            3: '목요일',
            4: '금요일',
            5: '토요일',
            6: '일요일'
        }

    def get_korean_day_name(self, day_name):
        return self.korean_day_names.get(day_name, day_name)

    def is_weekend(self, date):
        return date.weekday() >= 5 or date in self.custom_weekend_list

    def get_duty_types(self, date):
        return ['휴일A', '휴일B', '휴일C'] if self.is_weekend(date) else ['평일A', '평일B']

    def is_person_available(self, person, date, duty_type):
        if date in person.unavailable_dates:
            return False
        if not person.can_work_consecutive:
            prev_day = date - timedelta(days=1)
            if prev_day in self.schedule and person in [p for d in self.schedule[prev_day] for p in d]:
                return False
        if duty_type in ['평일A', '휴일C'] and person.get_total_ac_count() >= 4:
            return False
        if any(person in self.schedule[date][duty] for duty in self.schedule[date] if duty != duty_type):
            return False
        return True

    def schedule_duty(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            print(f"{current_date.strftime('%Y-%m-%d')} 당직 배정 중...")
            duty_types = self.get_duty_types(current_date)
            self.schedule[current_date] = {duty_type: []
                                           for duty_type in duty_types}

            for duty_type in duty_types:
                print(f"  {duty_type} 당직 배정 중...")
                required_people = 1  # 각 타입당 1명씩 배정

                # 고정 당직 먼저 할당
                assigned_people = [p for p in self.people if (
                    current_date.strftime('%Y-%m-%d'), duty_type) in p.fixed_duties]

                # 나머지 인원 할당
                available_people = [p for p in self.people if p not in assigned_people and self.is_person_available(
                    p, current_date, duty_type)]

                # 총 당직 횟수가 적은 순서로 정렬하고, 같은 경우 연공서열이 낮은 순으로 정렬
                available_people.sort(key=lambda x: (
                    x.get_total_duty_count(), -x.seniority, x.random_seed))
                print(
                    f"  가능한 인원: {', '.join(p.name for p in available_people)}")

                while len(assigned_people) < required_people and available_people:
                    person = available_people.pop(0)
                    assigned_people.append(person)

                for person in assigned_people:
                    person.duty_count[duty_type] += 1
                    print(f"    {person.name} 배정")

                if len(assigned_people) < required_people:
                    print(
                        f"Warning: Not enough people available for {current_date}, {duty_type}")

                self.schedule[current_date][duty_type] = assigned_people

            current_date += timedelta(days=1)

    def print_schedule(self):
        for date, duties in sorted(self.schedule.items()):
            print(
                f"\n{date.strftime('%Y-%m-%d')} ({'휴일' if self.is_weekend(date) else '평일'}):")
            for duty_type, people in duties.items():
                print(f"  {duty_type}: {', '.join(p.name for p in people)}")

    def get_schedule_as_string(self):
        result = []
        for date, duties in sorted(self.schedule.items()):
            result.append(
                f"\n{date.strftime('%Y-%m-%d')} ({'휴일' if self.is_weekend(date) else '평일'})\n")
            for duty_type, people in duties.items():
                result.append(
                    f"  {duty_type}: {', '.join(p.name for p in people)} \t")
        return '\n'.join(result)

    def create_calendar_df(self):
        df = []
        date_dict = {}
        person_dict = {}
        for date, values in self.schedule.items():
            if date.weekday() == 0:
                df.append(date_dict)
                df.append(person_dict)
                date_dict = {}
                person_dict = {}
            date_dict[self.get_korean_day_name(date.weekday())] = str(date)
            person_dict[self.get_korean_day_name(date.weekday())] = '<br>'.join(
                [f"{k}: {v[0].name}" for k, v in values.items()])
        df.append(date_dict)
        df.append(person_dict)
        df = DataFrame(df, columns=list(self.korean_day_names.values()))
        df.fillna('', inplace=True)

        return df

    def create_person_df(self):
        df = []
        for person in sorted(self.people, key=lambda x: x.name):
            df.append({
                '이름': person.name,
                '평일A': person.duty_count['평일A'],
                '평일B': person.duty_count['평일B'],
                '휴일A': person.duty_count['휴일A'],
                '휴일B': person.duty_count['휴일B'],
                '휴일C': person.duty_count['휴일C'],
                '총 당직 횟수': person.get_total_duty_count(),
            })
        df = DataFrame(df)
        return df
