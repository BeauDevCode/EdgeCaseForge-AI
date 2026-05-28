import json
import subprocess
import sys
import tempfile
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "data" / "challenges.json"
PROJECT_NAME = "EdgeCaseForge AI"

st.set_page_config(page_title=PROJECT_NAME, page_icon="🧠", layout="wide")

def load_challenges():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_solution(user_code: str, tests: list[dict], timeout_seconds: int = 3):
    """
    Runs user code locally. This is for demo/portfolio use only.
    Do not run untrusted code on a real server without sandboxing.
    """
    tests_json = json.dumps(tests)
    runner = f"""
import json

USER_TESTS = json.loads({tests_json!r})

{user_code}

results = []
for test in USER_TESTS:
    try:
        actual = solve(test["input"])
        if actual is None:
            actual = ""
        actual = str(actual).strip()
        expected = str(test["expected"]).strip()
        results.append({
            "name": test["name"],
            "passed": actual == expected,
            "expected": expected,
            "actual": actual
        })
    except Exception as e:
        results.append({
            "name": test["name"],
            "passed": False,
            "expected": test["expected"],
            "actual": "ERROR: " + repr(e)
        })
print(json.dumps(results))
"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "runner.py"
        path.write_text(runner, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
        except subprocess.TimeoutExpired:
            return [{"name": "timeout", "passed": False, "expected": "finish quickly", "actual": "TIMEOUT"}]

        if completed.returncode != 0:
            return [{"name": "runtime", "passed": False, "expected": "no crash", "actual": completed.stderr[-2000:]}]

        try:
            return json.loads(completed.stdout.strip())
        except Exception:
            return [{"name": "output parse", "passed": False, "expected": "JSON test results", "actual": completed.stdout[-2000:]}]

def build_pitch(challenge):
    failure_traps = "\n".join("- " + item for item in challenge["why_llms_fail"])
    return f"""
# Project Pitch: {PROJECT_NAME}

{PROJECT_NAME} is a coding-benchmark builder for evaluating AI coding models.

The selected demo challenge is **{challenge['title']}**, a {challenge['difficulty']} {challenge['category']} problem.

## What the app demonstrates

- Problem-design skill
- Golden-solution thinking
- Hidden-test engineering
- Model-failure analysis
- Python app development
- Streamlit UI development

## Why this matters

AI coding models often pass simple examples but fail edge cases. This project shows how to design tasks that test real reasoning, not just pattern matching.

## Example model-failure traps

{failure_traps}
"""

challenges = load_challenges()

st.title("🧠 " + PROJECT_NAME)
st.caption("AI coding benchmark builder: challenge design, hidden tests, golden-solution notes, and sample validation.")

with st.sidebar:
    st.header("Choose a challenge")
    categories = ["All"] + sorted(set(c["category"] for c in challenges))
    selected_category = st.selectbox("Category", categories)
    filtered = challenges if selected_category == "All" else [c for c in challenges if c["category"] == selected_category]
    titles = [c["title"] for c in filtered]
    title = st.selectbox("Challenge", titles)
    challenge = next(c for c in filtered if c["title"] == title)

    st.divider()
    st.write("**Difficulty:**", challenge["difficulty"])
    st.write("**Category:**", challenge["category"])

tab1, tab2, tab3, tab4 = st.tabs(["Challenge", "AI Failure Analysis", "Test Runner", "Portfolio Pitch"])

with tab1:
    st.subheader(challenge["title"])
    st.write(challenge["statement"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Input format")
        st.write(challenge["input_format"])
        st.markdown("### Constraints")
        st.write(challenge["constraints"])
    with col2:
        st.markdown("### Output format")
        st.write(challenge["output_format"])
        st.markdown("### Golden solution hint")
        st.info(challenge["golden_solution_hint"])

    st.markdown("### Sample tests")
    for test in challenge["sample_tests"]:
        with st.expander(test["name"]):
            st.markdown("**Input**")
            st.code(test["input"])
            st.markdown("**Expected output**")
            st.code(test["expected"])

with tab2:
    st.subheader("Why this can make AI models fail")
    for item in challenge["why_llms_fail"]:
        st.markdown(f"- {item}")

    st.subheader("Hidden test ideas")
    for item in challenge["hidden_test_ideas"]:
        st.markdown(f"- {item}")

    st.warning("Portfolio note: do not claim this guarantees model failure. Say it is a benchmark-design tool for finding likely failure cases.")

with tab3:
    st.subheader("Run a Python solution against sample tests")
    st.caption("Paste code that defines solve(input_data: str) -> str. This local demo runner is not a secure sandbox.")

    starter = """def solve(input_data: str) -> str:
    # Write your solution here.
    return ""
"""
    user_code = st.text_area("Your solution", value=starter, height=260)

    if st.button("Run sample tests"):
        results = run_solution(user_code, challenge["sample_tests"])
        passed = sum(1 for r in results if r["passed"])
        st.write(f"Passed {passed}/{len(results)} tests")

        for result in results:
            if result["passed"]:
                st.success(f"PASS: {result['name']}")
            else:
                st.error(f"FAIL: {result['name']}")
                st.markdown("**Expected**")
                st.code(result["expected"])
                st.markdown("**Actual**")
                st.code(result["actual"])

with tab4:
    st.subheader("Portfolio / Handshake showcase text")
    pitch = build_pitch(challenge)
    st.code(pitch, language="markdown")
    st.markdown("### Short version")
    st.write(PROJECT_NAME + " is a Python/Streamlit tool for creating coding-benchmark tasks, hidden tests, golden-solution notes, and AI model failure analysis.")
