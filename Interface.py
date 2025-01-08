import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import random

# Set locale to French for date formatting
# locale.setlocale(locale.LC_TIME, 'french')  # Adjust if needed for your system

# Path to your Excel file
EXCEL_FILE_PATH = "Annivs.xlsx"

MONTHS_EN_TO_FR = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre",
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche"
}


# Funny comments pool
FUNNY_COMMENTS = [
    "Une année de plus, une ride de sagesse en plus ! 🎂",
    "Attention, la fête approche, prépare les bougies ! 🕯️",
    "Joyeux anniversaire en avance, on espère que le gâteau sera énorme ! 🎉",
    "L’équipe te souhaite une journée mémorable ! 🎁",
    "C’est l’heure de souffler les bougies et de faire un vœu ! 🕯️🎈",
    "L’âge, ce n’est qu’un nombre… sauf quand on parle des anniversaires ! 😜",
    "En vieillissant, on devient plus sage… mais est-ce vraiment le cas ? 🤔🎉",
    "Que ta journée soit aussi brillante que toi ! 🌟🎉",
    "Joyeux anniversaire à l’esprit jeune et au cœur grand ! ❤️🎂"
    "Prêt(e) pour la fête ? 🎉",
    "Que les ballons volent dans les airs ! 🎈"
]

def format_date_in_french(formatted_date):
    for en, fr in MONTHS_EN_TO_FR.items():
        formatted_date = formatted_date.replace(en, fr)  # Replace with French
    return formatted_date

def count_birthdays_in_month(data):
    today = datetime.today()
    current_month = today.month
    # Filter rows where the birthday is in the current month
    birthdays_this_month = data[data['DATE NAISSANCE'].dt.month == current_month]
    return len(birthdays_this_month), birthdays_this_month

# Load data from Excel
def load_data(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        st.error("Erreur lors du chargement du fichier : " + str(e))
        return None

# Find the next upcoming birthday
def find_next_birthday(data):
    today = datetime.today()
    # Create a 'Next Birthday' column by combining birth year with current year
    data['Next Birthday'] = data['DATE NAISSANCE'].apply(lambda x: x.replace(year=today.year))
    data['Next Birthday'] = data['Next Birthday'].apply(
        lambda x: x + timedelta(days=365) if x < today else x
    )
    # Calculate the age on the next birthday
    data['Age'] = data['Next Birthday'].dt.year - data['DATE NAISSANCE'].dt.year
    # Find the person with the soonest upcoming birthday
    data = data.sort_values(by='Next Birthday')
    next_birthday = data.iloc[0]
    return next_birthday

# Streamlit interface
st.title("🎉 Anniversaire L&D 🎂")
# Custom CSS for birthday theme
st.markdown(
    """
    <style>
        body {
            background-color: #fdf2e9;
            color: #4f4f4f;
        }
        h1 {
            color: #ff67a5;
            font-family: 'Comic Sans MS', sans-serif;
        }
        .birthday-box {
            background-color: #ffe0e0;
            border: 2px solid #ff67a5;
            border-radius: 40px;
            padding: 5px;
            text-align: center;
        }
        .birthday-box h2 {
            color: #ff67a5;
            font-size: 28px;
        }
        .birthday-box p {
            font-size: 20px;
        }
        .birthday-box .emoji {
            font-size: 30px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Load your Excel file
data = load_data(EXCEL_FILE_PATH)

if data is not None:
    # Ensure required columns exist
    if 'PRENOM' in data.columns and 'DATE NAISSANCE' in data.columns:
        try:
            data['DATE NAISSANCE'] = pd.to_datetime(data['DATE NAISSANCE'])
            next_birthday = find_next_birthday(data)
            funny_comment = random.choice(FUNNY_COMMENTS)
            
            # Format the date in French
            next_birthday_date = format_date_in_french(next_birthday['Next Birthday'].strftime('%A %d %B %Y'))
            
            # Display the joyful birthday information
            st.markdown(f"<div class='birthday-box'>", unsafe_allow_html=True)
            # Display a bigger line for the birthday message with neutral text color
            st.markdown(
                f"<h2 style='font-size: 36px;'>🎉 {next_birthday['PRENOM']} aura {next_birthday['Age']} ans le {next_birthday_date}.</h2>", 
                unsafe_allow_html=True
            )

            st.write(f"🤪 {funny_comment}")
            st.markdown("</div>", unsafe_allow_html=True)
             # Count how many other birthdays are in the current month
            # Count how many other birthdays are in the current month
                        # Add spacing to move the button lower on the page



            num_birthdays, birthdays_this_month = count_birthdays_in_month(data)
            next_birthday_date = next_birthday['Next Birthday']

            # Filter out the next birthday from the list of birthdays this month
            birthdays_this_month_excluding_next = birthdays_this_month[birthdays_this_month['Next Birthday'] != next_birthday_date]

            # Now, display the number of other birthdays (excluding the next birthday)
            num_birthdays_excluding_next = len(birthdays_this_month_excluding_next)
            st.markdown("<br>" * 4, unsafe_allow_html=True)  # Adds 5 line breaks (adjust as needed)
            st.markdown(f"<div style='text-align: center;'>🎂 Il y a {num_birthdays_excluding_next} autres anniversaires ce mois-ci !</div>", unsafe_allow_html=True)
            if num_birthdays_excluding_next > 0:
           # Display the button to toggle the list of other birthdays
                if 'show_birthdays' not in st.session_state:
                    st.session_state.show_birthdays = False  # Default to not show birthdays list

                if st.button('Voir/ Masquer les autres anniversaires de ce mois'):
                    st.session_state.show_birthdays = not st.session_state.show_birthdays  # Toggle the state

                # Display the other birthdays (excluding the next birthday) if the button was clicked
                if st.session_state.show_birthdays:
                    st.subheader("Anniversaires ce mois-ci")
                    # Display the list of birthdays with smaller font
                    for index, row in birthdays_this_month_excluding_next.iterrows():
                        birthday_date = row['DATE NAISSANCE'].replace(year=datetime.today().year)
                        st.markdown(f"🎉 **{row['PRENOM']}** : {format_date_in_french(birthday_date.strftime('%d %B'))}", unsafe_allow_html=True)
            # Now, find the next birthday after the one currently displayed
            next_birthday_after_next = data[data['Next Birthday'] > next_birthday['Next Birthday']].sort_values(by='Next Birthday').iloc[0]
            st.markdown("<br>" * 3, unsafe_allow_html=True)  # Adds 5 line breaks (adjust as needed)
            # Display the message for the birthday after the next one
            next_birthday_after_next_date = format_date_in_french(next_birthday_after_next['Next Birthday'].strftime('%A %d %B %Y'))
            st.markdown(
                f"<div style='font-size: 18px; text-align: center;'>🎂 Mais {next_birthday_after_next['PRENOM']} arrive juste derrière (le {next_birthday_after_next_date}) ! 🎉</div>", 
                unsafe_allow_html=True
            )


        except Exception as e:
            st.error("Erreur lors du traitement des données : " + str(e))
    else:
        st.error("Le fichier doit contenir les colonnes `PRENOM` et `DATE NAISSANCE`.")
