from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>翻訳アプリ（テスト版）</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>翻訳アプリ（最小構成テスト）</h1>
        <form id="translateForm">
            <input type="text" id="textInput" placeholder="翻訳したいテキストを入力" required>
            <select id="langSelect">
                <option value="en">English</option>
                <option value="ja">日本語</option>
                <option value="fr">Français</option>
            </select>
            <button type="submit">翻訳</button>
        </form>
        <div id="result"></div>
        
        <script>
        document.getElementById('translateForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const text = document.getElementById('textInput').value;
            const lang = document.getElementById('langSelect').value;
            
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'text=' + encodeURIComponent(text) + '&lang=' + lang
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = 
                    '<h3>結果:</h3><p>' + data.message + '</p>';
            })
            .catch(error => {
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">エラーが発生しました</p>';
            });
        });
        </script>
    </body>
    </html>
    '''

@app.route("/translate", methods=["POST"])
def translate_test():
    """テスト用翻訳エンドポイント"""
    try:
        target_lang = request.form.get("lang", "en")
        text = request.form.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "テキストが入力されていません"}), 400
        
        # 翻訳機能は一時的に無効化し、テキストをそのまま返す
        message = f"入力: '{text}' → {target_lang} (翻訳機能はテスト中のため無効)"
        
        return jsonify({"message": message})
        
    except Exception as e:
        print(f"エラー: {e}")
        return jsonify({"error": "処理中にエラーが発生しました"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
