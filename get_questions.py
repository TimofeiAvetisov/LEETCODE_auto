import requests
import json

def get_questions(session):
    """
    Получает список вопросов с LeetCode, которые не были решены.
    Возвращает список вопросов, которые не были решены.
    """
    print("Starting to fetch questions from LeetCode...")
    #with open("Query_params/LEETCODE_SESSION.txt", "r") as f:
    #    session = f.read().strip()

    with open("Query_params/leetcode_query.graphql", "r", encoding="utf-8") as f:
        query = f.read()

    with open("Query_params/leetcode_variables.json", "r", encoding="utf-8") as f:
        variables = json.load(f)

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "Cookie": f"LEETCODE_SESSION={session}"
    }

    payload = {
        "operationName": "problemsetQuestionList",
        "query": query,
        "variables": variables
    }

    response = requests.post("https://leetcode.com/graphql/", headers=headers, json=payload)
    data = response.json()

    all_questions = data["data"]["problemsetQuestionList"]["questions"]
    print(f"Total questions fetched: {len(all_questions)}")
    print(f"Total questions not accepted: {len(all_questions)}")
    print("Questions query executed successfully.")
    print()
    print()


    return all_questions


def save_not_solved_questions(questions, user_id):
    """
    Сохраняет список вопросов в файл.
    """
    not_accepted = [q for q in questions if q["status"] != "ac" and not q["isPaidOnly"]]

    print("Starting to save questions to not_accepted_questions.json...")
    with open("Data/not_accepted_questions.json", "w", encoding="utf-8") as f:
        json.dump({str(user_id): not_accepted}, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(not_accepted)} questions to not_accepted_questions.json")
    print("Questions saved successfully.")
    print()
    print()
    return not_accepted

def save_solved_questions(questions, user_id):
    """
    Сохраняет список решенных вопросов в файл.
    """
    print("Starting to save solved questions to solved_questions.json...")
    solved_questions = [q for q in questions if q["status"] == "ac"]
    with open("Data/solved_questions.json", "w", encoding="utf-8") as f:
        json.dump({str(user_id) : solved_questions}, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(solved_questions)} solved questions to solved_questions.json")
    print("Solved questions saved successfully.")
    print()
    print()
    return solved_questions

if __name__ == "__main__":
    questions = get_questions()
    save_not_solved_questions(questions)
    save_solved_questions(questions)
    print("Script executed successfully.")

