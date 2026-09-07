"""
The command-line entry point: run the full four-agent evaluation for one
application and print what each agent decided.

    cd backend
    .\venv\Scripts\python.exe -m multi_agent.main
    Enter application ID to evaluate: 1
"""

from dotenv import load_dotenv

load_dotenv()

from multi_agent.graph import evaluate_loan_application  # noqa: E402


def main() -> None:
    application_id = input("Enter application ID to evaluate: ").strip()

    print(f"\n{'=' * 60}")
    print(f"Evaluating Loan Application #{application_id}")
    print("=" * 60)

    result = evaluate_loan_application(application_id)

    print("\nAGENT MESSAGES:")
    for msg in result.get("messages", []):
        print(f"  [{msg['agent'].upper()}]: {msg['message']}")

    print(f"\n{'=' * 60}")
    print(f"FINAL DECISION: {result.get('final_decision', 'NOT REACHED')}")
    reasoning = result.get("reasoning", "N/A")
    print(f"\nREASONING:\n{reasoning[:500]}{'...' if len(reasoning) > 500 else ''}")

    if result.get("errors"):
        print(f"\nERRORS: {result['errors']}")


if __name__ == "__main__":
    main()
