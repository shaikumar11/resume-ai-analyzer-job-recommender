# A curated whitelist of real technical/professional skills.
# Only words in this set will be shown as "matched" or "missing" keywords.

TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "rust",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "nosql", "redis",
    "html", "css", "react", "angular", "vue", "node", "nodejs", "express",
    "flask", "django", "fastapi", "spring", "dotnet",
    "rest", "api", "apis", "graphql", "soap", "microservices",
    "pyspark", "spark", "hadoop", "kafka", "airflow", "etl",
    "delta", "lake", "databricks", "snowflake", "bigquery",
    "aws", "azure", "gcp", "oci", "cloud", "docker", "kubernetes",
    "git", "github", "gitlab", "ci", "cd", "jenkins", "terraform",
    "machine", "learning", "tensorflow", "keras", "pytorch", "sklearn",
    "scikit", "opencv", "nlp", "cnn", "rnn", "deep",
    "pandas", "numpy", "matplotlib", "tableau", "powerbi", "excel",
    "dbms", "oop", "algorithm", "algorithms", "data", "structures",
    "agile", "scrum", "linux", "unix", "bash", "shell",
    "testing", "junit", "pytest", "selenium", "postman",
}


def filter_skills(word_set):
    """Keep only words that are recognized technical skills."""
    return {word for word in word_set if word in TECH_SKILLS}