import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import random
import time
import requests
import os
from io import StringIO
import base64

# Set locale to French for date formatting
# locale.setlocale(locale.LC_TIME, 'french')  # Adjust if needed for your system

# Path to your Excel file
EXCEL_FILE_PATH = "Annivs.xlsx"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

CSV_FILE = "boite_a_idees.csv"
RAW_URL = f"https://raw.githubusercontent.com/Xuoner/birthdays/main/boite_a_idees.csv"
API_URL = f"https://api.github.com/repos/Xuoner/birthdays/contents/boite_a_idees.csv"

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
    "Attention, la fête approche, prépare les bougies ! 🕯️",
    "Joyeux anniversaire en avance, on espère que le gâteau sera énorme ! 🎉",
    "L’équipe te souhaite une journée mémorable ! 🎁",
    "C’est l’heure de souffler les bougies et de faire un vœu ! 🕯️🎈",
    "Que ta journée soit aussi brillante que toi ! 🌟🎉",
    "Prêt(e) pour la fête ? 🎉",
    "Que les ballons volent dans les airs ! 🎈",
    "Un an de plus, et toujours aussi fabuleux(se) ! 🎉✨",
    "Joyeux anniversaire ! On espère que cette année sera pleine de surprises (les bonnes, bien sûr !) 🎂🎁",
    "Le temps passe, mais toi, tu restes indémodable ! Bon anniversaire ! 🕰️🎉",
    "Un jour de fête, une tonne de gâteaux, et encore plus de bonheur ! 🎂❤️",
    "Tu sais que tu vieillis quand les bougies coûtent plus cher que le gâteau… mais on t’aime quand même ! 🎂🔥",
    "Pas de panique, l'âge c'est comme le vin : tu ne fais que te bonifier ! 🍷🎉",
    "Joyeux anniversaire ! N’oublie pas, on ne compte pas les années mais les souvenirs ! 🕰️✨",
    "Fête bien, ris beaucoup, et surtout, mange tout le gâteau ! 🎂🎈",
    "Tu ne vieillis pas, tu montes juste en niveau ! 🎮🆙",
    "Rappelle-toi : plus de bougies = plus de vœux à faire. Alors, souffle bien fort ! 🕯️🎂",
    "Aujourd’hui, c’est ton jour ! Que le monde tourne autour de toi (au moins jusqu’à minuit) ! 🌟🎁",
]

def load_ideas():
    return pd.read_csv(CSV_FILE, sep = "\t")

def save_idea(idea):
    df = load_ideas()
    new_entry = pd.DataFrame([[idea]], columns=["Idée"])
    df = pd.concat([df, new_entry], ignore_index=True)
    csv_content = df.to_csv(index=False, sep="\t")
    # Récupérer le SHA du fichier (nécessaire pour l'update)
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    get_response = requests.get(API_URL, headers=headers)
    
    if get_response.status_code == 200:
        sha = get_response.json()["sha"]
    else:
        sha = None  # Si le fichier n'existe pas encore
    csv_base64 = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    # Mise à jour sur GitHub
    data = {
        "message": "Mise à jour des idées",
        "content": csv_base64,
        "sha": sha,
        "branch": "main"
    }
    put_response = requests.put(API_URL, headers=headers, json=data)
        
    if put_response.status_code == 200:
        print("File updated successfully!")
    else:
        print(f"Error updating file: {put_response.status_code}, {put_response.text}")

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
st.set_page_config(
    page_title="Anniversaires L&D",  # This sets the name of the app
    page_icon="🎉",
    initial_sidebar_state="collapsed"               # Optional: Set a custom icon for the app                # Optional: Set the layout to "centered" or "wide"
)
st.sidebar.title("Pages disponibles")
page = st.sidebar.radio("Naviguer vers:", ["Anniversaires", "Boite à idées", "Petit-déjeuner", "Carte des Déjeuners", "Chatbot ACL"])


# Page: Anniversaires
if page == "Anniversaires":
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
                next_birthday_date = format_date_in_french(next_birthday['Next Birthday'].strftime('%A %d %B'))
                
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
                
                if num_birthdays_excluding_next > 0:
                    st.markdown(f"<div style='text-align: center;'>🎂 Il y a {num_birthdays_excluding_next} autres anniversaires ce mois-ci !</div>", unsafe_allow_html=True)
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
                else: 
                    st.markdown(f"<div style='text-align: center;'>🎂 Il n'y a pas d'autres anniversaires ce mois-ci !</div>", unsafe_allow_html=True)
                # Now, find the next birthday after the one currently displayed
                next_birthday_after_next = data[data['Next Birthday'] > next_birthday['Next Birthday']].sort_values(by='Next Birthday').iloc[0]
                st.markdown("<br>" * 3, unsafe_allow_html=True)  # Adds 5 line breaks (adjust as needed)
                # Display the message for the birthday after the next one
                next_birthday_after_next_date = format_date_in_french(next_birthday_after_next['Next Birthday'].strftime('%A %d %B'))
                st.markdown(
                    f"<div style='font-size: 18px; text-align: center;'>🎂 Mais {next_birthday_after_next['PRENOM']} arrive juste derrière (le {next_birthday_after_next_date}) ! 🎉</div>", 
                    unsafe_allow_html=True
                )


            except Exception as e:
                st.error("Erreur lors du traitement des données : " + str(e))
        else:
            st.error("Le fichier doit contenir les colonnes `PRENOM` et `DATE NAISSANCE`.")

# Page : Boite à Idées:
if page == "Boite à idées":

    st.title("💡 Boîte à Idées")

    # Saisie de l'idée par l'utilisateur
    new_idea = st.text_area("Déposez votre idée ici :", "")

    if st.button("Soumettre"):
        if new_idea.strip():
            save_idea(new_idea.strip())
            st.success("Votre idée a été ajoutée avec succès !")
            st.rerun()

    # Affichage des idées enregistrées sous forme de tableau
    st.subheader("📜 Idées précédentes")
    df = load_ideas()
    if df.empty:
        st.info("Aucune idée n'a encore été soumise.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)   

# Page: Petits-Déjeuners
if page == "Petit-déjeuner":
    EXCEL_FILE_PATH = "Petits_Dejs.xlsx"

    df = load_data(EXCEL_FILE_PATH)
    # Streamlit App
    st.markdown(
        """
        <style>
        .header {
            text-align: center;
            color: #FF5733;
            font-family: 'Lucida Console', Monaco, monospace;
        }
        .subheader {
            color: #FFBD33;
            font-family: Arial, sans-serif;
        }
        .table {
            font-size: 1.2em;
            color: #2C3E50;
            font-family: 'Courier New', Courier, monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Custom Header
    st.markdown('<h1 class="header">🍳 C\'est l\'heure du Petit-Déjeuner ! 🥐</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Organisez votre petit-déjeuner avec vos viennoiseries préférées. ☕</p>', unsafe_allow_html=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    # Step 1: Select attendees
    st.subheader("👥 Qui vient pour le petit-déjeuner ?")
    selected_people = st.multiselect(
        "Sélectionnez les participants :",
        df["Prénom"],
    )

    if selected_people:
        # Step 2: Retrieve "Choix de cœur" for selected individuals
        selected_df = df[df["Prénom"].isin(selected_people)]
        unique_choices = selected_df["Choix de cœur"].unique()

        st.subheader("🧐 Vérifions les choix de cœur :")
        availability = {}
        for choice in unique_choices:
            availability[choice] = st.checkbox(f"Y a-t-il des {choice} ?", value=True)

        # Step 3: Replace unavailable choices with "En viennoiserie"
        final_choices = []
        for _, row in selected_df.iterrows():
            if availability[row["Choix de cœur"]]:
                final_choices.append(row["Choix de cœur"])
            else:
                final_choices.append(row["En viennoiserie"])

        # Step 4: Summarize and display results
        st.subheader("📊 Résumé des besoins pour le petit-déjeuner :")
        summary = pd.DataFrame(final_choices, columns=["Choix final"]).value_counts().reset_index()
        summary.columns = ["Choix final", "Quantité"]

        # Add emojis to table rows for better visualization
        st.markdown('<p class="table">Voici ce qu’il vous faut :</p>', unsafe_allow_html=True)
        for _, row in summary.iterrows():
            st.write(f"{row['Choix final']} : {row['Quantité']}")


    else:
        st.info("Veuillez sélectionner au moins une personne. 😊")


# Page: Petits-Déjeuners
if page == "Chatbot ACL":
    st.title("🤖 Chatbot ACL")

    # Custom CSS for styling the chat
    st.markdown(
        """
        <style>
            /* General App Background */
            body {
                background-color: #f3f4f6;
                font-family: 'Arial', sans-serif;
            }

            /* Chat Container Styling */
            .stChatMessage {
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
            }

            /* User Message */
            .stChatMessage[data-baseweb="chat-user"] {
                background-color: #e0f7fa;
                color: #006064;
                text-align: right;
                border: 1px solid #b2ebf2;
            }

            /* Assistant Message */
            .stChatMessage[data-baseweb="chat-assistant"] {
                background-color: #ffecb3;
                color: #795548;
                border: 1px solid #ffe082;
            }

            /* Add subtle transitions */
            .stChatMessage {
                animation: fadeIn 0.5s ease-in-out;
            }

            /* Fade-in animation */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }

            /* Chat Input Customization */
            .stTextInput {
                border-radius: 20px;
                border: 2px solid #ff8a65;
            }

            /* Title Styling */
            h1 {
                color: #ff7043;
                font-size: 2.5rem;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Quelle est ta question?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    # Streamed response emulator
    def response_generator(option):
        if option == 0:
            response = "Salut ! Comment puis-je t'aider aujourd'hui ? 😊"
        elif option == 2:
            response = "Malheureusement, je ne suis pas encore capable de générer du code ACL. 🤔"
        elif option == 4:
            response = "À une prochaine fois ! 👋"
        else:
            response = "C'est l'heure de ma pause clope, reviens plus tard. 🚬😄"

        for word in response.split():
            yield word + " "
            time.sleep(0.05)
    # Display assistant response in chat message container
    if len(st.session_state.messages) > 1:
        with st.spinner('Patience, je réfléchis...'):
            time.sleep(2.5)
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(len(st.session_state.messages)))

        # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
