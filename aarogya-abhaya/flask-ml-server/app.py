from flask import Flask, redirect

app = Flask(__name__)

@app.route("/image-check")
def image_check():
    return redirect("http://localhost:8501")

if __name__ == "__main__":
    app.run(port=5000, debug=True)