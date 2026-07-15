from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)


def check_password(password: str) -> dict:
    length = len(password) >= 8
    upper = bool(re.search(r"[A-Z]", password))
    lower = bool(re.search(r"[a-z]", password))
    digit = bool(re.search(r"[0-9]", password))
    special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};:,.<>?]", password))

    score = length + upper + lower + digit + special

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    suggestions = []
    if not length:
        suggestions.append("Make the password at least 8 characters long")
    if not upper:
        suggestions.append("Add an uppercase letter (A-Z)")
    if not lower:
        suggestions.append("Add a lowercase letter (a-z)")
    if not digit:
        suggestions.append("Add a number (0-9)")
    if not special:
        suggestions.append("Add a special character (e.g. ! @ # $ % ^ & * ( ) _ + - =)")

    return {
        "length": length,
        "upper": upper,
        "lower": lower,
        "digit": digit,
        "special": special,
        "score": score,
        "strength": strength,
        "suggestions": suggestions,
    }


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Password Strength Checker</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    color: #222;
  }

  section {
    padding: 50px 20px;
  }

  /* --- TOP: Tips section (dark navy) --- */
  .tips {
    background: #10192e;
    color: #f1f3f8;
    text-align: center;
  }

  .tips h1 {
    margin: 0 0 8px;
    font-size: 30px;
  }

  .tips p.subtitle {
    color: #9aa5c1;
    margin: 0 0 30px;
  }

  .tips-grid {
    max-width: 700px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    text-align: left;
  }

  .tip-item {
    background: #1a2440;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 14px;
    border-left: 3px solid #4da6ff;
  }

  /* --- MIDDLE: Checker card (white, pops against dark sections) --- */
  .checker-wrap {
    background: #eef1f6;
    display: flex;
    justify-content: center;
  }

  .checker-card {
    background: #fff;
    max-width: 420px;
    width: 100%;
    padding: 32px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    margin-top: -40px;
  }

  .checker-card h2 {
    margin-top: 0;
    text-align: center;
    color: #10192e;
  }

  .checker-card label {
    font-size: 14px;
    font-weight: bold;
    display: block;
    margin-bottom: 6px;
  }

  .checker-card input {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    margin-bottom: 16px;
    border: 1px solid #ccc;
    border-radius: 6px;
  }

  .bar-bg {
    height: 8px;
    background: #e6e9ef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 6px;
  }

  .bar-fill {
    height: 100%;
    width: 0%;
    background: #ccc;
    transition: width 0.2s, background 0.2s;
  }

  .strength-text {
    font-weight: bold;
    margin-bottom: 16px;
    font-size: 14px;
  }

  .checklist {
    list-style: none;
    padding: 0;
    margin: 0 0 8px;
    font-size: 14px;
  }

  .checklist li {
    padding: 3px 0;
  }

  .checklist li.pass { color: #1b9e5a; }
  .checklist li.fail { color: #c0392b; }

  .suggestions {
    font-size: 14px;
    margin-top: 10px;
  }

  /* --- BOTTOM: Importance section (dark teal) --- */
  .importance {
    background: #0b2b2b;
    color: #eafaf5;
    text-align: center;
  }

  .importance h2 {
    margin-top: 0;
    font-size: 26px;
  }

  .importance-grid {
    max-width: 800px;
    margin: 30px auto 0;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .stat {
    background: #123c3c;
    border-radius: 8px;
    padding: 20px 14px;
  }

  .stat .num {
    font-size: 26px;
    font-weight: bold;
    color: #4de8b8;
    margin-bottom: 6px;
  }

  .stat .label {
    font-size: 13px;
    color: #b6e6d8;
  }

  @media (max-width: 600px) {
    .tips-grid, .importance-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<section class="tips">
  <h1>How to Set a Strong Password</h1>
  <p class="subtitle">A few simple habits make a big difference</p>
  <div class="tips-grid">
    <div class="tip-item">Use at least 8-12 characters — longer is stronger.</div>
    <div class="tip-item">Mix uppercase, lowercase, numbers, and symbols.</div>
    <div class="tip-item">Avoid common words, names, or birthdays.</div>
    <div class="tip-item">Never reuse the same password across sites.</div>
  </div>
</section>

<section class="checker-wrap">
  <div class="checker-card">
    <h2>Password Checker</h2>

    <label for="password">Enter your password</label>
    <input type="text" id="password" placeholder="Type your password here" oninput="checkPassword()">

    <div class="bar-bg">
      <div class="bar-fill" id="barFill"></div>
    </div>
    <div class="strength-text" id="strengthText">&nbsp;</div>

    <ul class="checklist" id="checklist"></ul>

    <div class="suggestions" id="suggestions"></div>
  </div>
</section>

<section class="importance">
  <h2>Why a Strong Password Matters</h2>
  <p>Weak passwords are one of the most common ways accounts get hacked. A strong, unique password is one of the simplest ways to protect your data.</p>
  <div class="importance-grid">
    <div class="stat">
      <div class="num">81%</div>
      <div class="label">of breaches involve weak or stolen passwords</div>
    </div>
    <div class="stat">
      <div class="num">&lt;1 sec</div>
      <div class="label">to crack a common short password</div>
    </div>
    <div class="stat">
      <div class="num">Years</div>
      <div class="label">to crack a long, complex password</div>
    </div>
  </div>
</section>

<script>
let timeout = null;

function checkPassword() {
  clearTimeout(timeout);
  timeout = setTimeout(runCheck, 200);
}

async function runCheck() {
  const password = document.getElementById('password').value;
  const barFill = document.getElementById('barFill');
  const strengthText = document.getElementById('strengthText');
  const checklist = document.getElementById('checklist');
  const suggestions = document.getElementById('suggestions');

  if (!password) {
    barFill.style.width = "0%";
    barFill.style.background = "#ccc";
    strengthText.innerHTML = "&nbsp;";
    checklist.innerHTML = "";
    suggestions.innerHTML = "";
    return;
  }

  const res = await fetch('/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password })
  });

  const data = await res.json();

  const pct = (data.score / 5) * 100;
  let color = "#c0392b";
  if (data.strength === "Medium") color = "#e0a800";
  if (data.strength === "Strong") color = "#1b9e5a";

  barFill.style.width = pct + "%";
  barFill.style.background = color;
  strengthText.textContent = "Strength: " + data.strength;
  strengthText.style.color = color;

  const items = [
    { label: "At least 8 characters", pass: data.length },
    { label: "Uppercase letter", pass: data.upper },
    { label: "Lowercase letter", pass: data.lower },
    { label: "Number", pass: data.digit },
    { label: "Special character", pass: data.special }
  ];

  checklist.innerHTML = items.map(i =>
    `<li class="${i.pass ? 'pass' : 'fail'}">${i.pass ? '✔' : '✘'} ${i.label}</li>`
  ).join('');

  if (data.suggestions.length > 0) {
    let html = "<b>Suggestions:</b><ul>";
    data.suggestions.forEach(s => html += `<li>${s}</li>`);
    html += "</ul>";
    suggestions.innerHTML = html;
  } else {
    suggestions.innerHTML = "";
  }
}
</script>

</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "Password is required"}), 400

    result = check_password(password)
    return jsonify(result)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
