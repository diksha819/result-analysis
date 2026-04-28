from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ---------- ANALYSIS FUNCTION ----------
def analyze_data(df):

    # Clean column names
    df.columns = df.columns.str.strip()

    # Required columns check
    required_cols = ['RollNo', 'Name', 'Marks', 'Caste']
    for col in required_cols:
        if col not in df.columns:
            return {"error": f"Missing column: {col}"}

    # Convert marks safely
    df['Marks'] = pd.to_numeric(df['Marks'], errors='coerce')
    df = df.dropna(subset=['Marks'])

    total_students = len(df)

    # ==============================
    # PASS/FAIL (OUT OF 500 MARKS)
    # ==============================
    PASS_MARK = 200   # 40% of 500

    df['Result'] = df['Marks'].apply(lambda x: 'Pass' if x >= PASS_MARK else 'Fail')

    passed = len(df[df['Marks'] >= PASS_MARK])
    failed = len(df[df['Marks'] < PASS_MARK])

    avg_marks = round(df['Marks'].mean(), 2)

    # ==============================
    # CLASSIFICATION (OUT OF 500)
    # ==============================
    distinction = len(df[df['Marks'] >= 400])  # 80%+
    first_class = len(df[(df['Marks'] >= 300) & (df['Marks'] < 400)])  # 60-79%
    second_class = len(df[(df['Marks'] >= 250) & (df['Marks'] < 300)])  # 50-59%
    third_class = len(df[(df['Marks'] >= 200) & (df['Marks'] < 250)])  # 40-49%
    fail = len(df[df['Marks'] < 200])

    # ==============================
    # CASTE WISE ANALYSIS
    # ==============================
    caste_data = df.groupby('Caste').apply(
        lambda x: pd.Series({
            'Total': len(x),
            'Passed': len(x[x['Marks'] >= PASS_MARK]),
            'Failed': len(x[x['Marks'] < PASS_MARK]),
            'Pass %': round((len(x[x['Marks'] >= PASS_MARK]) / len(x)) * 100, 2)
        })
    ).reset_index()

    # ==============================
    # TOP 5 STUDENTS
    # ==============================
    top_students = df.sort_values(by='Marks', ascending=False).head(5)

    return {
        "total": total_students,
        "passed": passed,
        "failed": failed,
        "average": avg_marks,
        "pass_mark": PASS_MARK,
        "distinction": distinction,
        "first_class": first_class,
        "second_class": second_class,
        "third_class": third_class,
        "fail": fail,
        "caste_data": caste_data.to_dict(orient='records'),
        "top_students": top_students.to_dict(orient='records'),
        "all_students": df.to_dict(orient='records')
    }


# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")

        if not file:
            return "No file uploaded"

        try:
            df = pd.read_excel(file)
            result = analyze_data(df)

            if "error" in result:
                return result["error"]

            return render_template("dashboard.html", data=result)

        except Exception as e:
            return f"Error reading file: {str(e)}"

    return render_template("index.html")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)