# Column names and desired data types
DTYPE_DICT = {
    'page': 'int64',  
    'country': 'string', 
    'job_link': 'object', 
    'search_keyword': 'category', 
    'search_location': 'string', 
    'job_title': 'string', 
    'company_name': 'string', 
    'company_location': 'object', 
    'salary': 'object', 
    'job_description': 'string'
}


# Monthly conversion factors for salaries 
TIME_PERIOD_MAP = {
        'hour': 160, 
        'year': 1/12, 
        'week': 4,
        'day': 20, 
        'month': 1,
    }

# Language lables mapped to languages 
LANGUAGE_MAP = {
    "en": "english",
    "fr": "french",
    "it": "italian",
    "sv": "swedish"
}

# Check if these ones could be condensed 
# Country codes mapped to languages 
COUNTRIES_LANGUAGES = {
    'SWE': ('Sweden', 'swedish'),
    'FRA': ('France', 'french'),
    'ITA': ('Italy', 'italian'),
    'USA': ('USA', 'english')
}

COUNTRY_CODE_MAP = {
    'Sweden': 'SWE',
    'France': 'FRA', 
    'Italy': 'ITA',
    'USA': 'USA'
}

# Time periods for different languages 
TIME_KEYWORDS = {
    'english': {'day': 'day', 'year': 'year|annual', 'month': 'month', 'hour': 'hour', 'week': 'week'},
    'french': {'day': 'par jour', 'year': r'par\s*an|annuel|année', 'month': r'par\s*mois|mensuel', 'hour': r'par\s*heure|horaire', 'week': r'par\s*semaine|hebdomadaire'},
    'italian': {'day': 'al giorno', 'year': 'anno|annuale', 'month': 'mese|mensile', 'hour': 'ora|orario', 'week': 'settimana|settimanale'},
    'swedish': {'day': 'per dag', 'year': 'år|årlig', 'month': 'månad|mån', 'hour': 'timme|tim|/h', 'week': 'vecka'}
}


SOFTWARE_KEYWORDS = {
    'Programming Languages/Software': [
        'python', 'r', 'sql', 'javascript', 'java', 'c++', 'c#', 'ruby', 
        'swift', 'kotlin', 'scala', 'matlab', 'sas', 'stata', 'go', 
        'php', 'typescript', 'rust', 'bash', 'excel', 'julia'
    ],
    'ML and Statistical Modeling': [
        'scikit-learn', 'tensorflow', 'keras', 'pytorch', 'xgboost', 
        'catboost', 'lightgbm', 'mlpack', 'caret', 'mlr', 'statsmodels', 
        'neptune.ai', 'comet.ml', 'sagemaker', 'vertex ai'
    ],
    'Data Visualization Tools': [
        'matplotlib', 'seaborn', 'plotly', 'ggplot2', 'd3.js'
    ],
    'BI Tools': [
        'tableau', 'power bi', 'looker', 'qlik', 'sap', 
        'superset', 'metabase', 'thoughtspot', 'looker studio'
    ],
    'Big Data Technologies': [
        'spark', 'hadoop', 'bigquery', 'redshift', 'snowflake', 
        'hive', 'kafka', 'hdfs', 'flink', 'storm', 'apache nifi', 
        'spark streaming'
    ],
    'DBMS': [
        'mysql', 'postgresql', 'mongodb', 'cassandra', 'oracle', 
        'microsoft sql server', 'firebase', 'db2', 'couchbase', 
        'neo4j', 'redis', 'couchdb', 'mariadb'
    ],
    'Cloud Computing': [
        'aws', 'azure', 'google cloud', 'gcp', 'ibm cloud', 'oracle cloud', 
        'digitalocean', 'heroku'
    ],
    'Development Tools': [
        'docker', 'vscode', 'jupyter', 'pycharm', 'rstudio', 
        'eclipse', 'netbeans', 'intellij idea', 'notepad++', 
        'sublime text', 'atom'
    ],
    'Version Control': [
        'git', 'github', 'gitlab', 'bitbucket'
    ],
    'Collaboration Tools': [
        'jira', 'confluence', 'slack', 'trello', 'microsoft teams', 
        'asana', 'notion'
    ],
    'Containerization/Orchestration': [
        'kubernetes', 'openshift', 'mesos', 'rancher'
    ],
    'Workflow Management': [
        'airflow', 'luigi', 'prefect', 'kubeflow'
    ],
    'Data Science Platforms': [
        'databricks', 'knime', 'h2o.ai', 'rapidminer', 'datarobot', 
        'mlflow', 'dataiku', 'alteryx', 'talend', 'informatica'
    ]
}



# Context patterns for interview keywords 
CONTEXT_PATTERNS = {
    'english': r'recruitment process|interview process',
    'french': r'processus de recrutement|processus d\'entretien',
    'italian': r'processo di reclutamento|colloquio|selezione del personale',
    'swedish': r'rekryteringsprocess|intervjuprocess'
}

# Interview keywords 
INTERVIEW_STAGES = {
    'phone_screening': r'phone screening|phone interview|video interview|screening call|screening téléphonique|entrevue téléphonique|chiamata di screening|colloquio telefonico|telefonintervju|intervista video|entretien vidéo|visio|entretien en visio',
    'technical_screening': r'technical screening|technical interview|coding screen|technical phone screen|technical evaluation|évaluation technique|entrevue technique|prova tecnica|codice di screening|screening tecnico|teknisk screening|teknisk intervju',
    'case_study': r'case study|take-home assignment|business case|mock project|real-world problem|étude de cas|assignation à domicile|assegnazione a casa|business case|caso studio|fallstudie|business case',
    'coding_assessment': r'coding test|coding interview|programming test|technical assessment|live coding challenge|data challenge|whiteboard interview|SQL test|Python test|test di programmazione|intervista di programmazione|assessment tecnico|test SQL|test Python|kodningsprov|programmeringstest|teknisk bedömning|sfida di codifica',
    'behavioral_interview': r'behavioral interview|cultural interview|HR interview|situational interview|behavioral questions|entretien comportemental|entretien culturel|entrevue RH|entrevue situationnelle|domande comportamentali|colloquio comportamentale|HR-intervju|beteendefrågor',
    'on_site_interview': r'on-site interview|final round|in-person interview|panel interview|group interview|entrevue sur place|dernière ligne droite|entrevue en personne|entrevue en panel|entretien collectif|intervista in sede|colloquio finale|colloquio in presenza|intervista di gruppo|panelintervju|slutintervju|intervista di gruppo',
    'presentation': r'project presentation|technical presentation|mock presentation|présentation de projet|présentation technique|presentazione di progetto|presentazione tecnica'
}

# Location mappings for France 
DEPT_MAPPING_FR = {
    # 75 - Paris
    'Paris': '75 - Paris',
    'France': '75 - Paris',
    'Île-de-France': '75 - Paris',
    
    # 77 - Seine-et-Marne
    'Marne-la-Vallée': '77 - Seine-et-Marne',
    
    # 78 - Yvelines
    'Bougival': '78 - Yvelines',
    'Croissy-sur-Seine': '78 - Yvelines',
    'Guyancourt': '78 - Yvelines',
    'Jouy-en-Josas': '78 - Yvelines',
    'Jouy En Josas': '78 - Yvelines',
    'Le Chesnay': '78 - Yvelines',
    'Le Vésinet': '78 - Yvelines',
    'Magny-les-Hameaux': '78 - Yvelines',
    'Montigny-le-Bretonneux': '78 - Yvelines',
    'Poissy': '78 - Yvelines',
    'Vélizy-Villacoublay': '78 - Yvelines',
    'Versailles': '78 - Yvelines',
    
    # 91 - Essonne
    'Gif-sur-Yvette': '91 - Essonne',
    'Les Ulis': '91 - Essonne',
    'Massy': '91 - Essonne',
    'Orsay': '91 - Essonne',
    'Paray-Vieille-Poste': '91 - Essonne',
    'Saclay': '91 - Essonne',
    'Saint-Michel-sur-Orge': '91 - Essonne',
    
    # 92 - Hauts-de-Seine
    'Antony': '92 - Hauts-de-Seine',
    'Asnières-sur-Seine': '92 - Hauts-de-Seine',
    'Bagneux': '92 - Hauts-de-Seine',
    'Bois-Colombes': '92 - Hauts-de-Seine',
    'Boulogne-Billancourt': '92 - Hauts-de-Seine',
    'Châtillon': '92 - Hauts-de-Seine',
    'Clamart': '92 - Hauts-de-Seine',
    'Clichy': '92 - Hauts-de-Seine',
    'Colombes': '92 - Hauts-de-Seine',
    'Courbevoie': '92 - Hauts-de-Seine',
    'Gennevilliers': '92 - Hauts-de-Seine',
    'Issy-les-Moulineaux': '92 - Hauts-de-Seine',
    'La Défense': '92 - Hauts-de-Seine',
    'Le Plessis-Robinson': '92 - Hauts-de-Seine',
    'Levallois-Perret': '92 - Hauts-de-Seine',
    'Malakoff': '92 - Hauts-de-Seine',
    'Montrouge': '92 - Hauts-de-Seine',
    'Nanterre': '92 - Hauts-de-Seine',
    'Neuilly-sur-Seine': '92 - Hauts-de-Seine',
    'Puteaux': '92 - Hauts-de-Seine',
    'Rueil-Malmaison': '92 - Hauts-de-Seine',
    'Saint-Cloud': '92 - Hauts-de-Seine',
    'Sèvres': '92 - Hauts-de-Seine',
    'Suresnes': '92 - Hauts-de-Seine',
    
    # 93 - Seine-Saint-Denis
    'Aubervilliers': '93 - Seine-Saint-Denis',
    'Épinay-sur-Seine': '93 - Seine-Saint-Denis',
    'La Courneuve': '93 - Seine-Saint-Denis',
    'Montreuil': '93 - Seine-Saint-Denis',
    'Noisy-le-Grand': '93 - Seine-Saint-Denis',
    'Noisy-le-Sec': '93 - Seine-Saint-Denis',
    'Pantin': '93 - Seine-Saint-Denis',
    'Saint-Denis': '93 - Seine-Saint-Denis',
    'Saint-Ouen': '93 - Seine-Saint-Denis',
    'Tremblay-en-France': '93 - Seine-Saint-Denis',
    'Villepinte': '93 - Seine-Saint-Denis',
    
    # 94 - Val-de-Marne
    'Arcueil': '94 - Val-de-Marne',
    'Cachan': '94 - Val-de-Marne',
    'Charenton-le-Pont': '94 - Val-de-Marne',
    'Créteil': '94 - Val-de-Marne',
    'Fontenay-sous-Bois': '94 - Val-de-Marne',
    'Gentilly': '94 - Val-de-Marne',
    'Ivry-sur-Seine': '94 - Val-de-Marne',
    'Le Kremlin-Bicêtre': '94 - Val-de-Marne',
    'Maisons-Alfort': '94 - Val-de-Marne',
    'Rungis': '94 - Val-de-Marne',
    'Saint-Mandé': '94 - Val-de-Marne',
    'Villejuif': '94 - Val-de-Marne',
    'Vitry-sur-Seine': '94 - Val-de-Marne',
    
    # 95 - Val-d'Oise
    'Argenteuil': '95 - Val-d\'Oise',
    'Bezons': '95 - Val-d\'Oise',
    'Roissy-en-France': '95 - Val-d\'Oise',
    
    # 13 - Bouches-du-Rhône
    'Aix-en-Provence': '13 - Bouches-du-Rhône',
    'Aubagne': '13 - Bouches-du-Rhône',
    'Cassis': '13 - Bouches-du-Rhône',
    'Les Milles': '13 - Bouches-du-Rhône',
    'Marignane': '13 - Bouches-du-Rhône',
    'Marseille': '13 - Bouches-du-Rhône',
    'Vitrolles': '13 - Bouches-du-Rhône',
    
    # 69 - Rhône
    'Bron': '69 - Rhône',
    'Craponne': '69 - Rhône',
    'Dardilly': '69 - Rhône',
    'Écully': '69 - Rhône',
    'Genas': '69 - Rhône',
    'Givors': '69 - Rhône',
    'Limonest': '69 - Rhône',
    'Lyon': '69 - Rhône',
    'Marcy-l\'Étoile': '69 - Rhône',
    'Meyzieu': '69 - Rhône',
    'Mions': '69 - Rhône',
    'Saint-Genis-Laval': '69 - Rhône',
    'Saint-Genis-les-Ollières': '69 - Rhône',
    'Saint-Priest': '69 - Rhône',
    'Tassin-la-Demi-Lune': '69 - Rhône',
    'Villeurbanne': '69 - Rhône'
}

REGION_MAPPING_FR = {
   '75': 'Île-de-France',
   '77': 'Île-de-France',
   '78': 'Île-de-France',
   '91': 'Île-de-France',
   '92': 'Île-de-France',
   '93': 'Île-de-France',
   '94': 'Île-de-France',
   '95': 'Île-de-France',
   '69': 'Auvergne-Rhône-Alpes',
   '13': 'Provence-Alpes-Côte d\'Azur'
}

# Location mappings for Sweden
DEPT_MAPPING_SE = {
    'Stockholm': '01 - Stockholm län',
    'Solna': '01 - Stockholm län',
    'Sundbyberg': '01 - Stockholm län',
    'Danderyd': '01 - Stockholm län',
    'Vällingby': '01 - Stockholm län',
    'Bromma': '01 - Stockholm län',
    'Kungsholmen': '01 - Stockholm län',
    'Kista': '01 - Stockholm län',
    'Tumba': '01 - Stockholm län',
    'Tullinge': '01 - Stockholm län',
    'Göteborg': '14 - Västra Götalands län',
    'Mölndal': '14 - Västra Götalands län', 
    'Kungälv': '14 - Västra Götalands län',
    'Malmö': '12 - Skåne län',
    'Lund': '12 - Skåne län'
}

REGION_MAPPING_SE = {
    '01': 'Stockholm',
    '14': 'Västra Götaland',
    '12': 'Skåne'
}

# Location mappings for Italy 
DEPT_MAPPING_IT = {
    'Roma': 'RM - Roma',
    'Milano': 'MI - Milano',
    'Napoli': 'NA - Napoli',
    'Casalnuovo Di Napoli': 'NA - Napoli', 
    'Assago': 'MI - Milano',
    'Sesto San Giovanni': 'MI - Milano',
    'Cernusco sul Naviglio': 'MI - Milano',
    'Rozzano': 'MI - Milano',
    'Monza': 'MB - Monza e Brianza',
    'Vimercate': 'MB - Monza e Brianza',
    'Casalnuovo di Napoli': 'NA - Napoli', 
    'Roma Eur': 'RM - Roma',  # EUR is a business district in Rome
    'Lainate': 'MI - Milano',
    'Verano Brianza': 'MB - Monza e della Brianza',
    'Monza E Della Brianza': 'MB - Monza e della Brianza',
    'Parzialmente Milano': 'MI - Milano',  # This means "Partially Milan"
    'Giussago': 'PV - Pavia',
    'Milano Centro': 'MI - Milano',  # Milan City Center
    'Garbagnate Milanese': 'MI - Milano',
    'Trezzano Sul Naviglio': 'MI - Milano',
    'Basiglio': 'MI - Milano',
    'Vittuone': 'MI - Milano',
    'Cinisello Balsamo': 'MI - Milano',
    'San Donato Milanese': 'MI - Milano',
    'Settimo Milanese': 'MI - Milano',
    'Caponago': 'MB - Monza e della Brianza',
    'Gorgonzola': 'MI - Milano',
    'Villasanta': 'MB - Monza e della Brianza', 
    'Cernusco Sul Naviglio': 'MI - Milano'
}

REGION_MAPPING_IT = {
   'RM': 'Lazio',
   'MI': 'Lombardia', 
   'NA': 'Campania',
   'MB': 'Lombardia', 
   'PV': 'Lombardia'
}

DEPT_MAPPING_US = {
    # Additional New York area cities/variations
    'New York': 'NY - New York State',
    'Manhattan': 'NY - New York State',
    'Brooklyn': 'NY - New York State',
    'Queens': 'NY - New York State',
    'Bronx': 'NY - New York State',
    'New York City': 'NY - New York State',
    'NYC': 'NY - New York State',
    'Staten Island': 'NY - New York State',
    'Forest Hills': 'NY - New York State',
    'Astoria': 'NY - New York State',
    'Flushing': 'NY - New York State',
    'White Plains': 'NY - New York State',
    'Yonkers': 'NY - New York State',
    'Harrison': 'NY - New York State',
    
    # Bay Area
    'San Francisco': 'CA - California',
    'Oakland': 'CA - California',
    'Berkeley': 'CA - California',
    'San Jose': 'CA - California',
    'Palo Alto': 'CA - California',
    'Mountain View': 'CA - California',
    'Sunnyvale': 'CA - California',
    'Santa Clara': 'CA - California',
    'Redwood City': 'CA - California',
    'San Mateo': 'CA - California',
    'Menlo Park': 'CA - California',
    'Cupertino': 'CA - California',
    
    # Seattle area
    'Seattle': 'WA - Washington',
    'Bellevue': 'WA - Washington',
    'Redmond': 'WA - Washington',
    'Kirkland': 'WA - Washington',
    'Tacoma': 'WA - Washington',
    
    # Boston area
    'Boston': 'MA - Massachusetts',
    'Cambridge': 'MA - Massachusetts',
    'Waltham': 'MA - Massachusetts',
    'Somerville': 'MA - Massachusetts',
    'Quincy': 'MA - Massachusetts',
    'Newton': 'MA - Massachusetts',
    'Brookline': 'MA - Massachusetts',
    
    # Additional locations
    'Washington': 'DC - District of Columbia',
    'Arlington': 'VA - Virginia',
    'Alexandria': 'VA - Virginia',
    'McLean': 'VA - Virginia',
    'Reston': 'VA - Virginia',
    'Tysons': 'VA - Virginia',
    'Tysons Corner': 'VA - Virginia',
    'Austin': 'TX - Texas',
    'Houston': 'TX - Texas',
    'Dallas': 'TX - Texas',
    'Fort Worth': 'TX - Texas',
    'Miami': 'FL - Florida',
    'Orlando': 'FL - Florida',
    'Tampa': 'FL - Florida',
    'Atlanta': 'GA - Georgia',
    'Denver': 'CO - Colorado',
    'Boulder': 'CO - Colorado',
    'Portland': 'OR - Oregon',
    'Minneapolis': 'MN - Minnesota',
    'St. Paul': 'MN - Minnesota',
    'Philadelphia': 'PA - Pennsylvania',
    'Pittsburgh': 'PA - Pennsylvania'
}

REGION_MAPPING_US = {
    'NY': 'Northeast',
    'NJ': 'Northeast',
    'MA': 'Northeast',
    'PA': 'Northeast',
    'CT': 'Northeast',
    'RI': 'Northeast',
    'VT': 'Northeast',
    'NH': 'Northeast',
    'ME': 'Northeast',
    'CA': 'West',
    'WA': 'West',
    'OR': 'West',
    'NV': 'West',
    'AZ': 'West',
    'ID': 'West',
    'MT': 'West',
    'WY': 'West',
    'CO': 'West',
    'UT': 'West',
    'IL': 'Midwest',
    'MI': 'Midwest',
    'WI': 'Midwest',
    'MN': 'Midwest',
    'IA': 'Midwest',
    'MO': 'Midwest',
    'ND': 'Midwest',
    'SD': 'Midwest',
    'NE': 'Midwest',
    'KS': 'Midwest',
    'OH': 'Midwest',
    'IN': 'Midwest',
    'TX': 'South',
    'FL': 'South',
    'GA': 'South',
    'AL': 'South',
    'SC': 'South',
    'NC': 'South',
    'VA': 'South',
    'WV': 'South',
    'KY': 'South',
    'TN': 'South',
    'MS': 'South',
    'AR': 'South',
    'LA': 'South',
    'OK': 'South',
    'DC': 'Northeast',
    'DE': 'Northeast',
    'MD': 'South'
}

# Country specific cleaning patterns for location data
CLEANING_PATTERNS = {
    'France': [
        (r'télétravail\s*(?:partiel|à)?\s*(?:à|en)?\s*', ''),
        (r'\b\d{5}\b', ''),
        (r'\(\d{2,3}\)', ''),
        (r'\s\d{1,2}(?:er|ème|e)\s*', ' ')
    ],
    'Sweden': [
        (r'distansjobb\s+(?:i|in)\s+', ''),
        (r'\d{3}\s?\d{2}\s?', '')
    ],
    'Italy': [
        (r'remoto\s+(?:in|a)\s+', ''),
        (r'parzialmente\s+remoto\s+in\s+', ''),
        (r'\d{5}\s?', ''),
        (r',\s*\w+', ''),
        (r'provincia\s+di\s+', '')
    ],
    'USA': [
        (r'hybrid\s+work\s+in\s+|remote\s+in\s+', ''),
        (r'\s+\d{5}(?:-\d{4})?', ''),
        (r',?\s*[a-z]{2}(?:\s+\d{5}(?:-\d{4})?)?$', '')
    ]
}

LOCATION_MAPPINGS = {
    'France': {
        'departments': DEPT_MAPPING_FR,
        'regions': REGION_MAPPING_FR
    },
    'Sweden': {
        'departments': DEPT_MAPPING_SE,
        'regions': REGION_MAPPING_SE
    },
    'Italy': {
        'departments': DEPT_MAPPING_IT,
        'regions': REGION_MAPPING_IT
    },
    'USA': {
        'departments': DEPT_MAPPING_US,
        'regions': REGION_MAPPING_US
    }
}
