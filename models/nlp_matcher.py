from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(resume_text, job_text):
    """
    Compute cosine similarity between one resume and one job description.
    Returns a float between 0 and 1.
    """

    documents = [resume_text, job_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(float(score), 4)


def rank_jobs_for_resume(resume_text, job_list):
    """
    Rank a list of jobs for a resume.
    """

    results = []

    for job in job_list:
        score = compute_similarity(
            resume_text,
            job.get("description", "")
        )

        results.append({
            "job_id": job.get("id"),
            "title": job.get("title"),
            "similarity_score": score
        })

    results.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return results


def compute_similarities_batch(resume_text, job_texts):
    """
    Compute similarity of one resume against multiple job descriptions.

    Returns:
        list[float]
    """

    if not job_texts:
        return []

    documents = [resume_text] + list(job_texts)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    resume_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(
        resume_vector,
        job_vectors
    )[0]

    return [
        round(float(score), 4)
        for score in similarities
    ]