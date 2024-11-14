# Dictionary specifying column names and desired data types
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

# Dictionary of data frames and their corresponding currencies
currency_mapping = {
    'SWE': 'SEK',  # Swedish Krona
    'FRA': 'EUR',  # Euro
    'ITA': 'EUR',  # Euro
    'USA': 'USD'   # US Dollar
}

# Dictionary with common software/programming tools keywords 
software_keywords = {
    'Programming Languages': [
        'python', ' r ', 'sql', 'javascript', 'java', 'c++', 'c#', 'ruby', 'swift', 'kotlin', 'scala', 'matlab', 'sas', 'stata', ' go ', 'php', 'typescript', 'rust', 'bash'
    ],
    'Data Analysis and Manipulation': [
        'excel', 'pandas', 'numpy', 'dplyr', 'tidyverse', 'julia', 'matlab', 'stata'
    ],
    'Machine Learning and Statistical Modeling': [
        'scikit-learn', 'tensorflow', 'keras', 'pytorch', 'xgboost', 'catboost', 'lightgbm', 'mlpack', 'caret', 'mlr', 'weka', 'statsmodels'
    ],
    'Data Visualization and Business Intelligence (BI) Tools': [
        'tableau', 'power bi', 'matplotlib', 'seaborn', 'd3.js', 'looker', 'plotly', 'ggplot2', 'qlik', 'sap', 'looker studio', 'superset', 'metabase'
    ],
    'Big Data Technologies': [
        'spark', 'hadoop', 'bigquery', 'redshift', 'snowflake', 'databricks', 'hive', 'kafka', 'hdfs', 'flink', 'storm'
    ],
    'Database Management Systems (DBMS)': [
        'mysql', 'postgresql', 'mongodb', 'cassandra', 'oracle', 'microsoft sql server', 'firebase', 'db2', 'couchbase', 'neo4j', 'redis', 'couchdb', 'mariadb'
    ],
    'Cloud Computing': [
        'aws', 'azure', 'google cloud', 'gcp', 'ibm cloud', 'oracle cloud', 'digitalocean', 'heroku'
    ],
    'Development Tools': [
        'git', 'docker', 'vscode', 'jupyter', 'pycharm', 'rstudio', 'eclipse', 'netbeans', 'intellij idea', 'notepad++', 'sublime text', 'atom'
    ],
    'Version Control and Collaboration': [
        'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'trello', 'microsoft teams', 'asana', 'notion'
    ],
    'Containerization and Orchestration': [
        'docker', 'kubernetes', 'openshift', 'mesos', 'rancher', 'nomad'
    ],
    'Workflow Management': [
        'airflow', 'luigi', 'prefect', 'kubeflow'
    ],
    'Data Science Platforms': [
        'databricks', 'knime', 'h2o.ai', 'rapidminer', 'datarobot', 'mlflow'
    ]
}