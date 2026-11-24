"""New indexed-list exercise using fictional display titles, not stored policies."""
import json


def normalize_titles(titles):
    normalized_titles = list(titles)
    for index, title in enumerate(normalized_titles):
        normalized_titles[index] = title.strip().title()
    return normalized_titles


def run_demo():
    original_titles = [" data handling ", "ACCOUNT access"]
    first_before = original_titles[0]
    prepared_titles = normalize_titles(original_titles)
    first_after = prepared_titles[0]
    prepared_titles.append("Incident Response")
    return {"original": original_titles, "first_before": first_before,
            "first_after": first_after, "prepared": prepared_titles}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
