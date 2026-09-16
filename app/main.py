import json
from pathlib import Path
from dotenv import load_dotenv

from agents import Runner

from app.agent_nodes.profile_agent import profile_agent
load_dotenv()


def load_candidate_profile():
    profile_path = Path("data/candidate/profile.json")

    with open(profile_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    profile = load_candidate_profile()

    prompt = f"""
Analyze the following candidate profile.

CANDIDATE PROFILE:

{json.dumps(profile, indent=2)}

Produce:

1. Candidate positioning
2. Strongest Customer Success capabilities
3. Transferable experience
4. Career gaps
5. Best target Customer Success roles
6. Biggest risks in the current career transition
7. Three recommendations for improving the candidate's positioning

Do not invent anything.
"""

    result = Runner.run_sync(profile_agent, prompt)

    print("\n")
    print("=" * 70)
    print("CUSTOMER SUCCESS CANDIDATE ANALYSIS")
    print("=" * 70)
    print(result.final_output)


if __name__ == "__main__":
    main()
