import tkinter as tk
from tkinter import ttk
from utils import display
from utils import db
import time

class Window(tk.Toplevel):

    treeview = False
    timelabel = False

    def __init__(self, parent):
        super().__init__(parent)

        # Définition de la taille de la fenêtre, du titre et des lignes/colonnes de l'affichage grid
        display.centerWindow(900, 600, self)
        self.title('Q5 : températures (moyennes, min, max) par département et par année (version optimisée)')
        display.defineGridDisplay(self, 4, 2)
        self.grid_rowconfigure(3, weight=10)
        ttk.Label(self,
                  text="On a repris le code de F3. Modifier le code pour optimiser l'algorithme à la fois en "
                             "terme de temps d'exécution mais aussi de nombre de requêtes exécutées (éco-conception).",
                  wraplength=500,
                  anchor="center",
                  font=('Helvetica', '10', 'bold')
                  ).grid(sticky="we", row=0, columnspan=2)
        # On prépare les éléments à afficher
        ttk.Label(self,
                  text="Lancer l'extraction des données :",
                  anchor="center"
                  ).grid(row=1, column=0)
        ttk.Button(self,
                   text='Go !',
                   command=self.extract_data
                   ).grid(column=1, row=1)
        self.timelabel = ttk.Label(self, anchor="center")
        self.timelabel.grid(row=2, columnspan=2)
        columns = ('code_departement', 'nom_departement', 'annee_mesure', 'moyenne', 'minimum', 'maximum')
        self.treeview = display.createTreeViewDisplay(self, columns, [], 150)
        self.treeview.grid(row=3, columnspan=2, sticky="nswe")

    # Fonction permettant de récupérer les données et de les afficher
    def extract_data(self):

        # On vide la treeview
        self.treeview.delete(*self.treeview.get_children())

        # On démarre le chrono et initialise à 0 le nombre de requêtes exécutées
        start = time.time()
        nbquery = 0
        # 1. Requête
        query = """
            SELECT D.code_departement, D.nom_departement, strftime('%Y', M.date_mesure) as annee,
                   ROUND(avg(M.temperature_moy_mesure), 2) AS moyenne,
                   min(M.temperature_min_mesure) AS minimum,
                   max(M.temperature_max_mesure) AS maximum
            FROM Departements D
            JOIN Mesures M 
                ON D.code_departement = M.code_departement
            WHERE M.date_mesure 
            GROUP BY D.code_departement, annee
            ORDER BY D.code_departement, annee;
        """
        try:
            cursor = db.data.cursor()
            result = cursor.execute(query)
            nbquery += 1  # Une seule requête pour récupérer toutes les données
        except Exception as e:
            print("Erreur : " + repr(e))
        else:
            tab = []
            # 2. Traitement des résultats pour afficher dans la treeview
            for row in result:
                tab.append([row[0], row[1], row[2], row[3], row[4], row[5]])

        # On affiche les données du tableau dans la treeview
        for row in tab:
            self.treeview.insert('', tk.END, values=row)

        # On arrête le chrono et on calcule puis affiche le temps passé à l'extraction des données
        end = time.time()
        self.timelabel.configure(text="Le calcul ("+str(len(tab))+ " lignes) a pris " + str(round(end - start, 3)) + " secondes et exécuté " + str(nbquery) + " requêtes.")
