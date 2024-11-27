import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3  # Pour gérer la base de données
from utils import display

# Pointeur sur la base de données
data = sqlite3.connect("data/climat_france.db")
data.execute("PRAGMA foreign_keys = 1")  # Activation des clés étrangères


class Window(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Définition de la taille de la fenêtre, du titre et des lignes/colonnes de l'affichage grid
        display.centerWindow(600, 400, self)
        self.title('Q7 : gérer les travaux de rénovation')
        display.defineGridDisplay(self, 2, 1)
        ttk.Label(self,
                  text="Proposer des fonctionnalités permettant de gérer l'ajout, modification et suppression pour un "
                       "type de travaux",
                  wraplength=500,
                  anchor="center",
                  font=('Helvetica', '10', 'bold')
                  ).grid(sticky="we", row=0)

        # Formulaire d'ajout
        self.create_form()

    def create_form(self):
        """Crée un formulaire pour ajouter des travaux photovoltaïques."""
        # Variables des champs
        self.id_travaux = tk.StringVar()
        self.cout_total_ht = tk.StringVar()
        self.cout_induit_ht = tk.StringVar()
        self.date_travaux = tk.StringVar()  # Année (INTEGER, peut être vide)
        self.annee_construction = tk.StringVar()  # Année (INTEGER, peut être vide)
        self.type_logement = tk.StringVar()
        self.code_region = tk.StringVar()  # Utilisé dans la combobox (obligatoire)
        self.code_departement = tk.StringVar()  # Utilisé dans la combobox (facultatif)

        self.puissance_installee = tk.StringVar()
        self.type_panneaux = tk.StringVar()

        # Grille du formulaire
        fields = [
            ("ID Travail (Rechercher)", self.id_travaux),  # Ajouté pour la recherche par ID
            ("Coût total HT", self.cout_total_ht),
            ("Coût induit HT", self.cout_induit_ht),
            ("Année des travaux (YYYY)", self.date_travaux),
            ("Année de construction (YYYY)", self.annee_construction),
            ("Type de logement", self.type_logement),
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i + 1, column=0, sticky="w", padx=10, pady=5)
            ttk.Entry(self, textvariable=var).grid(row=i + 1, column=1, sticky="we", padx=10, pady=5)

        # Combobox pour les régions (obligatoire)
        ttk.Label(self, text="Code Région").grid(row=len(fields) + 1, column=0, sticky="w", padx=10, pady=5)
        self.region_combobox = ttk.Combobox(self, textvariable=self.code_region, state="readonly")
        self.region_combobox['values'] = self.get_regions()  # Remplit les valeurs depuis la base
        self.region_combobox.grid(row=len(fields) + 1, column=1, sticky="we", padx=10, pady=5)

        # Combobox pour les départements (facultatif)
        ttk.Label(self, text="Code Département").grid(row=len(fields) + 2, column=0, sticky="w", padx=10, pady=5)
        self.departement_combobox = ttk.Combobox(self, textvariable=self.code_departement)
        self.departement_combobox['values'] = self.get_departements()  # Remplit les valeurs depuis la base
        self.departement_combobox.grid(row=len(fields) + 2, column=1, sticky="we", padx=10, pady=5)

        # Champ spécifique : Puissance installée
        ttk.Label(self, text="Puissance installée (kW)").grid(row=len(fields) + 3, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(self, textvariable=self.puissance_installee).grid(row=len(fields) + 3, column=1, sticky="we", padx=10, pady=5)

        # Combobox pour le Type de panneaux
        ttk.Label(self, text="Type de panneaux").grid(row=len(fields) + 4, column=0, sticky="w", padx=10, pady=5)
        self.type_panneaux_combobox = ttk.Combobox(
            self, textvariable=self.type_panneaux, state="readonly"
        )
        self.type_panneaux_combobox['values'] = ['MONOCRISTALLIN', 'POLYCRISTALLIN']
        self.type_panneaux_combobox.grid(row=len(fields) + 4, column=1, sticky="we", padx=10, pady=5)

        # Bouton pour soumettre
        ttk.Button(self, text="Ajouter", command=self.add_photovoltaic_work).grid(
            row=len(fields) + 5, column=0, columnspan=2, pady=10
        )

        # Bouton pour rechercher par ID
        ttk.Button(self, text="Rechercher par ID", command=self.search_work_by_id).grid(
            row=len(fields) + 6, column=0, columnspan=2, pady=10
        )

        # Bouton pour modifier
        ttk.Button(self, text="Modifier", command=self.modify_work_by_id).grid(
            row=len(fields) + 7, column=0, columnspan=2, pady=10
        )

        # Bouton pour supprimer
        ttk.Button(self, text="Supprimer", command=self.delete_work_by_id).grid(
            row=len(fields) + 8, column=0, columnspan=2, pady=10
        )

    def add_photovoltaic_work(self):
        """Ajoute un travail photovoltaïque dans les tables Travaux et Photovoltaiques."""
        try:
            # Vérification : région obligatoire
            if not self.code_region.get():
                messagebox.showerror("Erreur", "La région est obligatoire.")
                return

            # Extraire le code région
            code_region = int(self.code_region.get().split(" - ")[0])

            # Vérification : si département est saisi, il doit appartenir à la région sélectionnée
            code_departement = None
            if self.code_departement.get():
                # Extraire uniquement le code département depuis le format "code - nom"
                code_departement = self.code_departement.get().split(" - ")[0]

            # Vérification explicite de la région
            cursor = data.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")  # Activer les clés étrangères
            cursor.execute("SELECT COUNT(*) FROM Regions WHERE code_region = ?", (code_region,))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Erreur", "La région sélectionnée n'existe pas.")
                return

            # Vérification explicite du département
            if code_departement:
                cursor.execute(
                    "SELECT COUNT(*) FROM Departements WHERE code_departement = ? AND code_region = ?",
                    (code_departement, code_region)
                )
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Erreur",
                                         "Le département saisi n'est pas valide ou n'appartient pas à la région.")
                    return

            # Vérification : date_travaux > annee_construction_logement_travaux si les deux champs sont remplis
            if self.date_travaux.get() and self.annee_construction.get():
                if int(self.date_travaux.get()) <= int(self.annee_construction.get()):
                    messagebox.showerror(
                        "Erreur",
                        "L'année des travaux doit être supérieure à l'année de construction."
                    )
                    return

            # Préparation des valeurs à insérer (None pour les champs vides)
            cout_total_ht = float(self.cout_total_ht.get()) if self.cout_total_ht.get() else None
            cout_induit_ht = float(self.cout_induit_ht.get()) if self.cout_induit_ht.get() else None
            date_travaux = int(self.date_travaux.get()) if self.date_travaux.get() else None
            annee_construction = int(self.annee_construction.get()) if self.annee_construction.get() else None
            type_logement = self.type_logement.get() if self.type_logement.get() else None
            code_departement = code_departement if code_departement else None
            puissance_installee = int(self.puissance_installee.get()) if self.puissance_installee.get() else None
            type_panneaux = self.type_panneaux.get() if self.type_panneaux.get() else None

            # Insertion dans la table Travaux
            cursor.execute(
                """
                INSERT INTO Travaux (
                    cout_total_ht_travaux, cout_induit_ht_travaux, date_travaux, 
                    type_logement_travaux, annee_construction_logement_travaux, 
                    code_region, code_departement
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (cout_total_ht, cout_induit_ht, date_travaux, type_logement, annee_construction, code_region,
                 code_departement)
            )
            id_travaux = cursor.lastrowid  # Récupérer l'ID du travail inséré

            # Insertion dans la table Photovoltaiques (uniquement si un champ est rempli)

            cursor.execute(
                """
                INSERT INTO Photovoltaiques (
                    id_travaux, puissance_installee_photovoltaique, 
                    type_panneaux_photovoltaique
                ) VALUES (?, ?, ?)
                """,
                (id_travaux, puissance_installee, type_panneaux)
            )

            # Validation des modifications
            data.commit()

            # Message de confirmation
            messagebox.showinfo("Succès", "Travail photovoltaïque ajouté avec succès !")

            # Réinitialisation des champs
            self.reset_form()

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
            data.rollback()

    def search_work_by_id(self):
        """Recherche un travail par ID et remplit le formulaire."""
        try:
            # Vérification : ID requis pour la recherche
            if not self.id_travaux.get():
                messagebox.showerror("Erreur", "Veuillez entrer un ID de travail.")
                return

            # Récupérer les données depuis la base
            cursor = data.cursor()
            cursor.execute("""
                SELECT 
                    cout_total_ht_travaux, cout_induit_ht_travaux, date_travaux,
                    type_logement_travaux, annee_construction_logement_travaux, 
                    code_region, code_departement, puissance_installee_photovoltaique, 
                    type_panneaux_photovoltaique
                FROM Travaux
                LEFT JOIN Photovoltaiques ON Travaux.id_travaux = Photovoltaiques.id_travaux
                WHERE Travaux.id_travaux = ?
            """, (self.id_travaux.get(),))
            result = cursor.fetchone()

            if not result:
                messagebox.showerror("Erreur", "Aucun travail trouvé avec cet ID.")
                return

            # Remplir le formulaire avec les données
            (
                cout_total_ht, cout_induit_ht, date_travaux, type_logement,
                annee_construction, code_region, code_departement,
                puissance_installee, type_panneaux
            ) = result

            self.cout_total_ht.set(cout_total_ht if cout_total_ht is not None else "")
            self.cout_induit_ht.set(cout_induit_ht if cout_induit_ht is not None else "")
            self.date_travaux.set(date_travaux if date_travaux is not None else "")
            self.type_logement.set(type_logement if type_logement is not None else "")
            self.annee_construction.set(annee_construction if annee_construction is not None else "")
            self.code_region.set(f"{code_region} - Région Correspondante")  # Ajuster si nécessaire
            self.code_departement.set(f"{code_departement} - Département Correspondant" if code_departement else "")
            self.puissance_installee.set(puissance_installee if puissance_installee is not None else "")
            self.type_panneaux.set(type_panneaux if type_panneaux is not None else "")

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def modify_work_by_id(self):
        """Modifie un travail existant dans les tables Travaux et Photovoltaiques par ID."""
        try:
            # Vérification : ID requis pour modifier
            if not self.id_travaux.get():
                messagebox.showerror("Erreur", "Veuillez entrer un ID de travail.")
                return

            # Récupérer l'ID
            id_travaux = int(self.id_travaux.get())

            # Vérification : l'entrée doit exister
            cursor = data.cursor()
            cursor.execute("SELECT COUNT(*) FROM Travaux WHERE id_travaux = ?", (id_travaux,))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Erreur", "Aucun travail trouvé avec cet ID.")
                return

            # Préparer les valeurs à mettre à jour
            cout_total_ht = float(self.cout_total_ht.get()) if self.cout_total_ht.get() else None
            cout_induit_ht = float(self.cout_induit_ht.get()) if self.cout_induit_ht.get() else None
            date_travaux = int(self.date_travaux.get()) if self.date_travaux.get() else None
            annee_construction = int(self.annee_construction.get()) if self.annee_construction.get() else None
            type_logement = self.type_logement.get() if self.type_logement.get() else None
            code_region = int(self.code_region.get().split(" - ")[0]) if self.code_region.get() else None
            code_departement = (
                self.code_departement.get().split(" - ")[0] if self.code_departement.get() else None
            )
            puissance_installee = int(self.puissance_installee.get()) if self.puissance_installee.get() else None
            type_panneaux = self.type_panneaux.get() if self.type_panneaux.get() else None

            # Vérification explicite de la région
            if code_region:
                cursor.execute("SELECT COUNT(*) FROM Regions WHERE code_region = ?", (code_region,))
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Erreur", "La région sélectionnée n'existe pas.")
                    return

            # Vérification explicite du département
            if code_departement:
                cursor.execute(
                    "SELECT COUNT(*) FROM Departements WHERE code_departement = ? AND code_region = ?",
                    (code_departement, code_region)
                )
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Erreur",
                                         "Le département saisi n'est pas valide ou n'appartient pas à la région.")
                    return

            # Vérification : date_travaux > annee_construction_logement_travaux si les deux champs sont remplis
            if date_travaux and annee_construction:
                if date_travaux <= annee_construction:
                    messagebox.showerror(
                        "Erreur",
                        "L'année des travaux doit être supérieure à l'année de construction."
                    )
                    return

            # Mise à jour de la table Travaux
            cursor.execute(
                """
                UPDATE Travaux
                SET cout_total_ht_travaux = ?, 
                    cout_induit_ht_travaux = ?, 
                    date_travaux = ?, 
                    type_logement_travaux = ?, 
                    annee_construction_logement_travaux = ?, 
                    code_region = ?, 
                    code_departement = ?
                WHERE id_travaux = ?
                """,
                (
                    cout_total_ht, cout_induit_ht, date_travaux, type_logement,
                    annee_construction, code_region, code_departement, id_travaux
                )
            )

            # Mise à jour de la table Photovoltaiques (uniquement si un champ spécifique est rempli)
            cursor.execute(
                """
                UPDATE Photovoltaiques
                SET puissance_installee_photovoltaique = ?, 
                    type_panneaux_photovoltaique = ?
                WHERE id_travaux = ?
                """,
                (puissance_installee, type_panneaux, id_travaux)
            )

            # Validation des modifications
            data.commit()

            # Message de confirmation
            messagebox.showinfo("Succès", "Travail photovoltaïque modifié avec succès !")

            # Réinitialisation des champs
            self.reset_form()

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
            data.rollback()

    def delete_work_by_id(self):
        """Supprime un travail et ses données associées dans les tables Travaux et Photovoltaiques par ID."""
        try:
            # Vérification : ID requis pour supprimer
            if not self.id_travaux.get():
                messagebox.showerror("Erreur", "Veuillez entrer un ID de travail.")
                return

            # Récupérer l'ID
            id_travaux = int(self.id_travaux.get())

            # Vérification : l'entrée doit exister
            cursor = data.cursor()
            cursor.execute("SELECT COUNT(*) FROM Travaux WHERE id_travaux = ?", (id_travaux,))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Erreur", "Aucun travail trouvé avec cet ID.")
                return

            # Confirmation de suppression
            confirmation = messagebox.askyesno(
                "Confirmation",
                f"Êtes-vous sûr de vouloir supprimer le travail avec ID {id_travaux} ?"
            )
            if not confirmation:
                return

            # Suppression des données dans la table Photovoltaiques
            cursor.execute("DELETE FROM Photovoltaiques WHERE id_travaux = ?", (id_travaux,))

            # Suppression des données dans la table Travaux
            cursor.execute("DELETE FROM Travaux WHERE id_travaux = ?", (id_travaux,))

            # Validation des modifications
            data.commit()

            # Message de confirmation
            messagebox.showinfo("Succès", f"Le travail avec ID {id_travaux} a été supprimé avec succès !")

            # Réinitialisation des champs
            self.reset_form()

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
            data.rollback()

    def check_departement_region(self, code_departement, code_region):
        """Vérifie si un département appartient bien à une région."""
        cursor = data.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Departements WHERE code_departement = ? AND code_region = ?",
            (code_departement, code_region)
        )
        return cursor.fetchone()[0] > 0

    def reset_form(self):
        """Réinitialise les champs du formulaire."""
        self.cout_total_ht.set("")
        self.cout_induit_ht.set("")
        self.date_travaux.set("")
        self.annee_construction.set("")
        self.type_logement.set("")
        self.code_region.set("")
        self.code_departement.set("")
        self.puissance_installee.set("")
        self.type_panneaux.set("")

    def get_regions(self):
        """Récupère les régions depuis la base de données."""
        cursor = data.cursor()
        cursor.execute("SELECT code_region, nom_region FROM Regions")
        regions = cursor.fetchall()
        return [f"{code} - {nom}" for code, nom in regions]


    def get_departements(self):
        """Récupère les départements avec leurs noms depuis la base de données."""
        cursor = data.cursor()
        cursor.execute("SELECT code_departement, nom_departement FROM Departements ORDER BY code_departement ")
        departements = cursor.fetchall()
        # Retourne une liste au format "code - nom"
        return [f"{code} - {nom}" for code, nom in departements]

