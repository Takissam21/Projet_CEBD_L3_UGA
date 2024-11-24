import tkinter as tk
from tkinter import ttk
from utils import display
from utils import db

class Window(tk.Toplevel):
    treeView = None
    comboBox = None
    errorLabel = None

    def __init__(self, parent):
        super().__init__(parent)

        # Définition de la fenêtre
        display.centerWindow(600, 450, self)
        self.title('Q3 : nombre de mesures prises et moyenne des temperatures [...] (version dynamique)')
        display.defineGridDisplay(self, 3, 3)
        self.grid_rowconfigure(3, weight=10)

        ttk.Label(self,
                  text="On a repris le code de F2. Modifier l'interface pour proposer un choix de la région sans "
                       "saisie manuelle (par exemple un proposer un menu déroulant avec les valeurs extraites de la "
                       "base, ou toute autre idée). Changez la requête fournie pour afficher le nombre de mesures prises"
                       " et la moyenne des températures moyennes par département pour la région choisie.",
                  wraplength=500,
                  anchor="center",
                  font=('Helvetica', '10', 'bold')
                  ).grid(sticky="we", row=0, columnspan=3)

        # Affichage du label et du Combobox
        ttk.Label(self,
                  text='Veuillez sélectionner une région :',
                  anchor="center",
                  font=('Helvetica', '10', 'bold')
                  ).grid(row=1, column=0)

        # Création d'un Combobox pour la sélection de la région
        self.comboBox = ttk.Combobox(self, state='readonly', font=('Helvetica', '10'))
        self.comboBox.grid(row=1, column=1)
        self.loadRegions()  # Charger les régions dans le Combobox
        ttk.Button(self,
                   text='Valider',
                   command=self.searchRegion
                   ).grid(row=1, column=2)

        # Label pour les messages d'erreur ou de confirmation
        self.errorLabel = ttk.Label(self, anchor="center", font=('Helvetica', '10', 'bold'))
        self.errorLabel.grid(columnspan=3, row=2, sticky="we")

        # Préparer un Treeview pour afficher les résultats
        columns = ('code_departement', 'nom_departement', 'num_mesures', 'moy_temp_moyenne')
        self.treeView = ttk.Treeview(self, columns=columns, show='headings')
        for column in columns:
            self.treeView.column(column, anchor=tk.CENTER, width=15)
            self.treeView.heading(column, text=column)
        self.treeView.grid(columnspan=3, row=3, sticky='nswe')

    def loadRegions(self):
        """Récupère les noms des régions depuis la base de données et les charge dans le Combobox."""
        try:
            cursor = db.data.cursor()
            cursor.execute("SELECT DISTINCT nom_region FROM Regions")
            regions = [row[0] for row in cursor.fetchall()]
            self.comboBox['values'] = regions
        except Exception as e:
            self.errorLabel.config(foreground='red', text=f"Erreur lors du chargement des régions : {e}")

    def searchRegion(self, event=None):
        """
        # On vide le treeView (pour rafraichir les données si quelque chose était déjà présent)
        self.treeView.delete(*self.treeView.get_children())

        # On récupère la valeur saisie dans la case
        region = self.input.get()

        # Si la saisie est vide, on affiche une erreur
        if len(region) == 0:
            self.errorLabel.config(foreground='red', text="Veuillez saisir une région !")

        # Si la saisie contient quelque chose
        else :
        """
        """Recherche les départements pour la région sélectionnée et affiche les résultats."""
        self.treeView.delete(*self.treeView.get_children())  # Vider le tableau
        region = self.comboBox.get()  # Récupérer la région sélectionnée

        if not region:  # Si aucune région n'est sélectionnée
            self.errorLabel.config(foreground='red', text="Veuillez sélectionner une région !")
            return

        try:
            cursor = db.data.cursor()
            result = cursor.execute("""
                SELECT code_departement, nom_departement, COUNT(*) AS num_mesures, AVG(temperature_moy_mesure) AS temperature_moy
                FROM Departements
                JOIN Regions USING (code_region)
                JOIN Mesures USING (code_departement)
                WHERE nom_region = ?
                GROUP BY code_departement, nom_departement
            """, [region])

            i = 0
            for row in result:
                self.treeView.insert('', tk.END, values=row)
                i += 1

            if i == 0:
                self.errorLabel.config(foreground='orange', text=f"Aucun résultat pour la région \"{region}\" !")
            else:
                self.errorLabel.config(foreground='green', text=f"Voici les résultats pour la région \"{region}\" :")
        except Exception as e:
            self.errorLabel.config(foreground='red', text=f"Erreur : {e}")
