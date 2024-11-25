# Column names and desired data types
dtype_dict = {
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

# Countries and corresponding currencies
currency_mapping = {
    'Sweden': 'SEK',  # Swedish Krona
    'France': 'EUR',  # Euro
    'Italy': 'EUR',  # Euro
    'USA': 'USD'   # US Dollar
}

# Time periods with monthly conversion factors
time_period_map = {
    'hour': 160, 'ora': 160, 'heure': 160,
    'year': 1/12, 'anno': 1/12, 'par an': 1/12,
    'week': 4, 'settimana': 4, 'semaine': 4,
    'day': 20, 'giorno': 20, 'jour': 20,
    'month': 1, 'mese': 1, 'mois': 1, 'månad': 1
    }

# Language lables mapped to languages 
language_map = {
    "en": "english",
    "fr": "french",
    "it": "italian",
    "sv": "swedish"
}

# Country codes mapped to languages 
countries_languages = {
    'SWE': ('Sweden', 'swedish'),
    'FRA': ('France', 'french'),
    'ITA': ('Italy', 'italian'),
    'USA': ('USA', 'english')
}

# Time periods for different languages 
time_keywords = {
    'english': {'day': 'day', 'year': 'year|annual', 'month': 'month', 'hour': 'hour', 'week': 'week'},
    'french': {'day': 'par jour', 'year': r'par\s*an|annuel|année', 'month': r'par\s*mois|mensuel', 'hour': r'par\s*heure|horaire', 'week': r'par\s*semaine|hebdomadaire'},
    'italian': {'day': 'al giorno', 'year': 'anno|annuale', 'month': 'mese|mensile', 'hour': 'ora|orario', 'week': 'settimana|settimanale'},
    'swedish': {'day': 'per dag', 'year': 'år|årlig', 'month': 'månad|mån', 'hour': 'timme|tim|/h', 'week': 'vecka'}
}

software_keywords = {
    'Programming Languages/Software': [
        'python', ' r ', 'sql', 'javascript', 'java', 'c++', 'c#', 'ruby', 
        'swift', 'kotlin', 'scala', 'matlab', 'sas', 'stata', 'go ', 
        'php', 'typescript', 'rust', 'bash', 'excel', 'julia'
    ],
    'ML and Statistical Modeling': [
        'scikit-learn', 'tensorflow', 'keras', 'pytorch', 'xgboost', 
        'catboost', 'lightgbm', 'mlpack', 'caret', 'mlr', 'statsmodels', 
        'mlflow', 'neptune.ai', 'comet.ml', 'sagemaker', 'vertex ai'
    ],
    'Data Vis and BI Tools': [
        'tableau', 'power bi', 'matplotlib', 'seaborn', 'd3.js', 'looker', 
        'plotly', 'ggplot2', 'qlik', 'sap', 'looker studio', 'superset', 
        'metabase', 'thoughtspot'
    ],
    'Big Data Technologies': [
        'spark', 'hadoop', 'bigquery', 'redshift', 'snowflake', 'databricks', 
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
        'git', 'docker', 'vscode', 'jupyter', 'pycharm', 'rstudio', 
        'eclipse', 'netbeans', 'intellij idea', 'notepad++', 'sublime text', 
        'atom'
    ],
    'Version Control/Collaboration': [
        'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 
        'trello', 'microsoft teams', 'asana', 'notion'
    ],
    'Containerization/Orchestration': [
        'docker', 'kubernetes', 'openshift', 'mesos', 'rancher'
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
context_patterns = {
    'english': r'recruitment process|interview process',
    'french': r'processus de recrutement|processus d\'entretien',
    'italian': r'processo di reclutamento|processo di colloquio',
    'swedish': r'rekryteringsprocess|intervjuprocess'
}

# Interview keywords 
interview_stages = {
    'phone_screening': r'phone screening|phone interview|video interview|screening call|screening téléphonique|entrevue téléphonique|chiamata di screening|colloquio telefonico|telefonintervju|intervista video|entretien vidéo|visio|entretien en visio',
    'technical_screening': r'technical screening|technical interview|coding screen|technical phone screen|technical evaluation|évaluation technique|entrevue technique|prova tecnica|codice di screening|screening tecnico|teknisk screening|teknisk intervju',
    'case_study': r'case study|take-home assignment|business case|mock project|real-world problem|étude de cas|assignation à domicile|assegnazione a casa|business case|caso studio|fallstudie|business case',
    'coding_assessment': r'coding test|coding interview|programming test|technical assessment|live coding challenge|data challenge|whiteboard interview|SQL test|Python test|test di programmazione|intervista di programmazione|assessment tecnico|test SQL|test Python|kodningsprov|programmeringstest|teknisk bedömning|sfida di codifica',
    'behavioral_interview': r'behavioral interview|cultural interview|HR interview|situational interview|behavioral questions|entretien comportemental|entretien culturel|entrevue RH|entrevue situationnelle|domande comportamentali|colloquio comportamentale|HR-intervju|beteendefrågor',
    'on_site_interview': r'on-site interview|final round|in-person interview|panel interview|group interview|entrevue sur place|dernière ligne droite|entrevue en personne|entrevue en panel|entretien collectif|intervista in sede|colloquio finale|colloquio in presenza|intervista di gruppo|panelintervju|slutintervju|intervista di gruppo',
    'presentation': r'project presentation|technical presentation|mock presentation|présentation de projet|présentation technique|presentazione di progetto|presentazione tecnica'
}