import json
import argparse
import random
from get_questions import get_questions, save_not_solved_questions, save_solved_questions

SETTINGS_FILE = "user_settings.json"

def load_settings():
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def choose_random_question(questions, settings):
    print("Choosing random questions based on user settings...")
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

def run(refresh=False):
    print("Starting the script to fetch and process LeetCode questions...")
    if refresh:
        print("Refreshing questions from LeetCode...")
        questions = get_questions()
        if not questions:
            print("No questions retrieved. Check session or query.")
            return []
        save_not_solved_questions(questions)
        save_solved_questions(questions)
    else:
        print("Using cached questions from file...")
        try:
            with open("not_accepted_questions.json", "r", encoding="utf-8") as f:
                questions = json.load(f)
        except FileNotFoundError:
            print("Cache file not found. Please run with --refresh first.")
            return []

    settings = load_settings()
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

def refresh_questions():
    print("Refreshing questions from LeetCode (json only)...")
    questions = get_questions()
    if not questions:
        print("No questions retrieved. Check session or query.")
        return 0
    not_accepted = save_not_solved_questions(questions)
    accepted = save_solved_questions(questions)
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
