import tkinter as tk
from utils import display
from utils import db
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Window(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Définition de la taille de la fenêtre, du titre et des lignes/colonnes de l'affichage grid
        display.centerWindow(1500, 800, self)
        self.title('Q6 : Records de températures historiques pour la zone H1 en 2018')
        display.defineGridDisplay(self, 1, 1)

        """
        ttk.Label(
            self,
            text=(
                "On souhaite tracer un graphique pour comparer les températures des départements de la zone "
                "climatique H1 en 2018 avec les records de températures historiques enregistrés dans notre base "
                "de données pour l’ensemble du pays, pour chaque jour de l’année.\n\n"
                "Pour l’ensemble de cet exercice, seules les données de la colonne temperature_moy_mesure de "
                "la table Mesures seront prises en compte.\n\n"
                "On souhaite afficher ces données sur le même graphique, avec les 4 courbes suivantes :\n"
                "    - Les records de fraîcheur historiques pour chaque jour de l’année (toutes années confondues, toutes zones climatiques confondues).\n"
                "    - Les records de chaleur historiques pour chaque jour de l’année (toutes années confondues, toutes zones climatiques confondues).\n"
                "    - Les températures du département le plus froid de la zone H1 pour chaque jour de l’année 2018.\n"
                "    - Les températures du département le plus chaud de la zone H1 pour chaque jour de l’année 2018.\n\n"
                "Les départements les plus froids et les plus chauds de la zone H1 sont ceux pour lesquels la "
                "moyenne de leurs températures sur l’année 2018 est respectivement la plus basse et la plus élevée.\n\n"
                "Pour tracer le graphique, basez-vous sur le code fourni en exemple dans F4. Attention, seule la "
                "requête SQL doit être modifiée dans le code que vous reprendrez de F4. Vous ne devez pas modifier "
                "le code de génération du graphique.\n\n"
                "Indication : travaillez indépendamment sur chaque courbe demandée. Le plus difficile sera de rassembler "
                "les données nécessaires pour tracer les 4 courbes dans une même requête."
            ),
            wraplength=700,
            anchor="center",
            font=('Helvetica', '10', 'bold')
        ).grid(sticky="we", row=0)
        """

        # Récupération des données depuis la base de données
        cursor = db.data.cursor()
        query = """
            WITH RecordFroid AS (
                SELECT 
                    strftime('%m-%d', date_mesure) AS jour,
                    MIN(temperature_moy_mesure) AS record_froid,
                    MAX(temperature_moy_mesure) AS record_chaleur
                FROM Mesures
                GROUP BY jour
                ORDER BY jour
            ),
            A AS (
                SELECT D.code_departement, AVG(M.temperature_moy_mesure) AS moy
                FROM Departements D
                JOIN Mesures M ON D.code_departement = M.code_departement
                WHERE D.zone_climatique = 'H1'
                AND strftime('%Y', M.date_mesure) = '2018'
                GROUP BY D.code_departement
            ),
            DepartementLePlusFroid AS (
                SELECT code_departement
                FROM A
                WHERE moy = (SELECT MIN(moy) FROM A)
            ),
            Requetetrois AS (
                SELECT strftime('%m-%d', M.date_mesure) AS jour, M.temperature_moy_mesure
                FROM Mesures M
                JOIN DepartementLePlusFroid D ON M.code_departement = D.code_departement
                WHERE strftime('%Y', M.date_mesure) = '2018'
                ORDER BY M.date_mesure
            ),
            DepartementLePlusChaud AS (
                SELECT code_departement
                FROM A
                WHERE moy = (SELECT MAX(moy) FROM A)
            ),
            Requetequatre AS (
                SELECT strftime('%m-%d', M.date_mesure) AS jour, M.temperature_moy_mesure
                FROM Mesures M
                JOIN DepartementLePlusChaud D ON M.code_departement = D.code_departement
                WHERE strftime('%Y', M.date_mesure) = '2018'
                ORDER BY M.date_mesure
            )
            -- Requête principale qui fait le JOIN des trois sous-requêtes
            SELECT 
                RF.jour, 
                RF.record_froid, 
                RF.record_chaleur, 
                R3.temperature_moy_mesure AS temp_froid_departement, 
                R4.temperature_moy_mesure AS temp_chaud_departement
            FROM 
                RecordFroid RF
            JOIN Requetetrois R3 ON RF.jour = R3.jour
            JOIN Requetequatre R4 ON RF.jour = R4.jour
            ORDER BY RF.jour
        """
        result = []
        try:
            result = cursor.execute(query).fetchall()  # Utilisation de fetchall() pour récupérer tous les résultats
        except Exception as e:
            print("Erreur : " + repr(e))

        # Extraction et préparation des valeurs à mettre sur le graphique
        graph1 = []
        graph2 = []
        graph3 = []
        graph4 = []
        tabx = []
        for row in result:
            tabx.append(row[0])
            graph1.append(row[1])
            graph2.append(row[2])
            graph3.append(row[3])
            graph4.append(row[4])

        # Formatage des dates pour l'affichage sur l'axe x
        #datetime_dates = [datetime.strptime(date, '%m-%d') for date in tabx]

        # Formatage des dates pour l'affichage sur l'axe x
        datetime_dates = [datetime.strptime('2018-' + date, '%Y-%m-%d') for date in tabx]

        # Ajout de la figure et du subplot qui contiendront le graphique
        fig = Figure(figsize=(15, 8), dpi=100)
        plot1 = fig.add_subplot(111)

        # Affichage des courbes
        plot1.plot(range(len(datetime_dates)), graph1, color='#00FFFF', label='températures minimales historiques')
        plot1.plot(range(len(datetime_dates)), graph2, color='#FF8300', label='températures maximales historiques')
        plot1.plot(range(len(datetime_dates)), graph3, color='#0000FF', label='Températures département le plus froid (H1)')
        plot1.plot(range(len(datetime_dates)), graph4, color='#FF0000', label='Températures département le plus chaud (H1)')

        # Configuration de l'axe x pour n'afficher que le premier jour de chaque mois
        xticks = [i for i, date in enumerate(datetime_dates) if date.day == 1]
        xticklabels = [date.strftime('%Y-%m-%d') for date in datetime_dates if date.day == 1]
        plot1.set_xticks(xticks)
        plot1.set_xticklabels(xticklabels, rotation=45)
        plot1.legend()


        # Affichage du graphique
        canvas = FigureCanvasTkAgg(fig,  master=self)
        canvas.draw()
        canvas.get_tk_widget().pack()