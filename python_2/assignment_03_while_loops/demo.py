"""New bounded queue example; never executes the production process supervisor."""
import json


def process_questions(questions):
    pending_questions = list(questions)
    processed_questions = []
    iterations = 0
    has_pending_questions = bool(pending_questions)
    while has_pending_questions:
        question = pending_questions.pop(0)
        processed_questions.append(question.strip())
        iterations += 1
        has_pending_questions = bool(pending_questions)
    return {"processed": processed_questions, "iterations": iterations, "pending": pending_questions}


def run_demo():
    return {"populated": process_questions([" Data handling? ", " Remote access? "]),
            "initially_empty": process_questions([])}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
