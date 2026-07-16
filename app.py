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
<link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,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">

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
