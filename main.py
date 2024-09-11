from scheduler import Scheduler
from person import Person
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
st.set_page_config(layout="wide")


# Step 1: Setting up the date period and holidays
st.title("Scheduling App")

# Allow users to pick the period
start_date = st.date_input("시작 날짜", value=datetime.today())
end_date = st.date_input(
    "종료 날짜", value=datetime.today() + timedelta(days=20))

# Ensure that end date is after start date
if start_date >= end_date:
    st.error("종료 날짜가 시작 날짜보다 빠릅니다. 다시 설정해주세요.")

# Allow users to input holidays
holidays = st.multiselect("공휴일 선택하기 (주말은 따로 추가하지 않아도 됨)", pd.date_range(
    start_date, end_date).strftime("%Y-%m-%d"))

# Step 2: Initialize session state for persons
if 'persons_data' not in st.session_state:
    st.session_state.persons_data = [
        Person("박민수", 1),
        Person("은호선", 1),
        Person("신정은", 1),
        Person("송인규", 1),
        Person("한정호", 1),
        Person("백승환", 1),
        Person("이수민", 1),
        Person("심성보", 1),
        Person("임청욱", 1),
        Person("정윤미", 1),
        Person("김벼리", 1),
        Person("조희승", 1),
    ]


# Function to add a new blank person form


def add_person_form():
    st.session_state.persons_data.append(Person(**{
        'name': '',
        'seniority': 1,
        'fixed_duties': [],
        'unavailable_dates': [],
        'can_work_consecutive': False
    }))

# Function to remove a person form by index


def remove_person_form(index):
    del st.session_state.persons_data[index]
    # Update page to reflect changes
    st.rerun()


# Add a new form button
if st.button("Add Person"):
    add_person_form()

# Generate the duty options for selection
date_range = pd.date_range(start_date, end_date).strftime("%Y-%m-%d").tolist()

all_duty = []
for date in date_range:
    if datetime.strptime(date, "%Y-%m-%d").weekday() >= 5 or date in holidays:
        all_duty.append(f"{date} 휴일A")
        all_duty.append(f"{date} 휴일B")
        all_duty.append(f"{date} 휴일C")
    else:
        all_duty.append(f"{date} 평일A")
        all_duty.append(f"{date} 평일B")

# Display dynamic forms for each person

for idx, person in enumerate(st.session_state.persons_data):
    with st.form(key=f"person_form_{idx}"):
        st.text_input("이름", value=person.name, key=f"name_{idx}")
        st.number_input("연차 (연차가 낮을수록 우선순위가 높음)",
                        value=person.seniority, min_value=1, key=f"seniority_{idx}")
        st.multiselect(
            "고정 당직", all_duty, default=person.get_fixed_duties_as_string(), key=f"fixed_duties_{idx}")
        st.multiselect("불가능한 스케쥴", all_duty,
                       default=person.get_unavailable_dates_as_string(), key=f"unavailable_dates_{idx}")
        st.checkbox(
            "연속 당직 가능", value=person.can_work_consecutive, key=f"can_work_consecutive_{idx}")

        # Delete button for the form
        if st.form_submit_button("Remove"):
            remove_person_form(idx)

# Step 3: Generating Results


def generate_schedules(persons_data, start_date, end_date, holidays):
    for person in persons_data:
        person.reset_duty_count()
    scheduler = Scheduler(persons_data, start_date, end_date, holidays)
    scheduler.schedule_duty()
    schedule = scheduler.create_calendar_df()
    person = scheduler.create_person_df()

    return schedule, person


# Button to generate schedules
if st.button("Generate Schedule"):
    if st.session_state.persons_data:
        schedules, persons = generate_schedules(
            st.session_state.persons_data, start_date, end_date, holidays)

        st.subheader("Schedule Options")

        custom_css = """
        <style>
            .stDataFrame table {
                width: 150%;
                table-layout: fixed;
            }
            .stDataFrame th, .stDataFrame td {
                text-align: center;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
        </style>
        """

        # Apply the custom CSS
        st.markdown(custom_css, unsafe_allow_html=True)

        html_table = schedules.to_html(
            classes='stDataFrame', escape=False, index=False)
        st.markdown(html_table, unsafe_allow_html=True)

        html_table = persons.to_html(
            classes='stDataFrame', escape=False, index=False)
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.error("Please add at least one person to generate the schedule.")
