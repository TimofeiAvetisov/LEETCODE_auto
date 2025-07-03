import json
import argparse
import random
from get_questions import get_questions, save_not_solved_questions, save_solved_questions

SETTINGS_FILE = "user_settings.json"

def load_settings(user_id: str):
    try:
        with open("Data/users_settings.json", "r", encoding="utf-8") as f:
            all_settings = json.load(f)
        return all_settings.get(user_id, None)
    except FileNotFoundError:
        return None

def save_settings(user_id: str, settings: dict):
    try:
        with open("Data/users_settings.json", "r", encoding="utf-8") as f:
            all_settings = json.load(f)
    except FileNotFoundError:
        all_settings = {}

    all_settings[user_id] = settings

    with open("Data/users_settings.json", "w", encoding="utf-8") as f:
        json.dump(all_settings, f, ensure_ascii=False, indent=4)

def choose_random_question(questions, settings):
    print("Choosing random questions based on user settings...")
    print(settings)
    result = []
    by_difficulty = settings["count_by_difficulty"]

    for diff, count in by_difficulty.items():
        candidates = [q for q in questions if q["difficulty"] == diff]
        random.shuffle(candidates)
        result.extend(candidates[:count])

    print(f"Selected {len(result)} questions based on user preferences.\n\n\n")
    return result

def print_questions(questions):
    for q in questions:
        print(f"{q['title']}({q['difficulty']}) - {q['status']}")
        print(f"Link: https://leetcode.com/problems/{q['titleSlug']}/\n")

def run(session, user_id, refresh=False):
    print("Starting the script to fetch and process LeetCode questions...")
    if refresh:
        print("Refreshing questions from LeetCode...")
        questions = get_questions(session)
        if not questions:
            print("No questions retrieved. Check session or query.")
            return []
        save_not_solved_questions(questions, user_id)
        save_solved_questions(questions, user_id)
    else:
        print("Using cached questions from file...")
        try:
            with open("Data/not_accepted_questions.json", "r", encoding="utf-8") as f:
                questions = json.load(f)
        except FileNotFoundError:
            print("Cache file not found. Please run with --refresh first.")
            return []
        questions = questions.get(user_id, [])
        if not questions:
            print("No questions found in cache. Please run with --refresh first.")
            return []

    settings = load_settings(user_id)
    selected = choose_random_question(questions, settings)
    print_questions(selected)
    print("Script completed successfully. Happy coding!\n\n\n")
    return selected

def format_questions(questions):
    lines = []
    for q in questions:
        line = f"<b>{q['title']}</b> ({q['difficulty']})\n🔗 https://leetcode.com/problems/{q['titleSlug']}/"
        lines.append(line)
    return "\n\n".join(lines) if lines else "Нет подходящих задач."

def refresh_questions(session, user_id):
    print("Refreshing questions from LeetCode (json only)...")
    questions = get_questions(session)
    if not questions:
        print("No questions retrieved. Check session or query.")
        return 0

    not_accepted = save_not_solved_questions(questions, user_id)
    accepted = save_solved_questions(questions, user_id)
    print(f"Saved {len(questions)} questions to not_accepted_questions.json")
    print("Questions refreshed and saved successfully.")
    return (len(not_accepted), len(accepted))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", action="store_true", help="Set user settings")
    parser.add_argument("--refresh", action="store_true", help="Refresh questions from LeetCode")

    args = parser.parse_args()
    print("Starting the main script...")
    if args.set:
        print("Use Telegram /set to configure settings now.")
    else:
        run(refresh=args.refresh)
    print("Main script executed successfully.\n\n\n")
