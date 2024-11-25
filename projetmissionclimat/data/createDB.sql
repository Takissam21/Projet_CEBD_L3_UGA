create table Regions (
    code_region INTEGER,
    nom_region TEXT,
    constraint pk_regions primary key (code_region)
);

create table Departements (
    code_departement INTEGER,
    nom_departement TEXT,
    code_region INTEGER,
    zone_climatique TEXT,
    constraint pk_departements primary key (code_departement),
    constraint fk_region foreign key (code_region) references Regions(code_region),
    constraint zone_climatique_valide CHECK (zone_climatique IN ('H1', 'H2', 'H3'))
);

create table Mesures (
    code_departement INTEGER,
    date_mesure DATE,
    temperature_min_mesure FLOAT,
    temperature_max_mesure FLOAT,
    temperature_moy_mesure FLOAT,
    constraint pk_mesures primary key (code_departement, date_mesure),
    constraint fk_mesures foreign key (code_departement) references Departements(code_departement) ON DELETE CASCADE
);

--TODO Q4 Ajouter les créations des nouvelles tables

create table Communes (
    code_commune INTEGER,
    nom_commune TEXT,
    status TEXT,
    altitude_moyenne INTEGER,
    population INTEGER,
    superficie INTEGER,
    code_canton INTEGER,
    code_arrondissement INTEGER,

    code_departement INTEGER,

    constraint pk_commune primary key (code_commune,code_departement),
    constraint fk_commune foreign key (code_departement) references Departements(code_departement) ON DELETE CASCADE
);

CREATE TABLE Isolation (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- ID auto-incrémenté
    cout_total_ht FLOAT,
    cout_induit_ht FLOAT,
    annee_travaux INTEGER,
    type_logement TEXT,
    annee_construction INTEGER,
    poste_isolation TEXT, --Type
    isolant TEXT, --Type
    epaisseur INTEGER,
    surface FLOAT,

    code_departement INTEGER,             -- Code du département (clé étrangère)
    code_region INTEGER,                  -- Code de la région (clé étrangère)

    FOREIGN KEY (code_region) REFERENCES Regions(code_region),
    FOREIGN KEY (code_departement) REFERENCES Departements(code_departement),
    CONSTRAINT type_poste_valide CHECK (poste_isolation IN (
        'COMBLES PERDUES', 'ITI', 'ITE', 'RAMPANTS',
        'SARKING', 'TOITURE TERRASSE', 'PLANCHER BAS')),
    CONSTRAINT type_isolant_valide CHECK (isolant IN (
        'AUTRES','LAINE VEGETALE','LAINE MINERALE','PLASTIQUES'))
);

CREATE TABLE Chauffage (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- ID auto-incrémenté
    cout_total_ht FLOAT,
    cout_induit_ht FLOAT,
    annee_travaux INTEGER,
    type_logement TEXT,
    annee_construction INTEGER,

    energie_chauffage_avt_travaux TEXT,
    energie_chauffage_installee TEXT ,
    generateur TEXT,
    type_chaudiere TEXT,

    code_departement INTEGER,             -- Code du département (clé étrangère)
    code_region INTEGER,                  -- Code de la région (clé étrangère)

    FOREIGN KEY (code_region) REFERENCES Regions(code_region),

    FOREIGN KEY (code_departement) REFERENCES Departements(code_departement),

    CONSTRAINT type_energie_valide CHECK (energie_chauffage_avt_travaux IN (
        'AUTRES', 'BOIS', 'ELECTRICITE', 'FIOUL', 'GAZ')),

    CONSTRAINT type_energie_validee CHECK (energie_chauffage_installee IN (
        'AUTRES', 'BOIS', 'ELECTRICITE', 'FIOUL', 'GAZ')),

    CONSTRAINT type_generateur_valide CHECK (generateur IN (
        'AUTRES', 'CHAUDIERE', 'INSERT', 'PAC', 'POELE', 'RADIATEUR')),

    CONSTRAINT type_chaudiere_valide CHECK (type_chaudiere IN (
        'STANDARD',
        'AIR-EAU',
        'A CONDENSATION',
        'AUTRES',
        'AIR-AIR',
        'GEOTHERMIE',
        'HPE'
    ))
);

CREATE TABLE Photovoltaique (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- ID auto-incrémenté
    cout_total_ht FLOAT,
    cout_induit_ht FLOAT,
    annee_travaux INTEGER,
    type_logement TEXT,
    annee_construction INTEGER,

    puissance_installee TEXT,
    type_panneaux TEXT ,

    code_departement INTEGER,             -- Code du département (clé étrangère)
    code_region INTEGER,                  -- Code de la région (clé étrangère)

    FOREIGN KEY (code_region) REFERENCES Regions(code_region),
    FOREIGN KEY (code_departement) REFERENCES Departements(code_departement),

    CONSTRAINT type_panneaux_valide CHECK (type_panneaux IN (
        'MONOCRISTALLIN',
        'POLYCRISTALLIN'
    ))
);
