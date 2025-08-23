from flask import Flask, render_template, request, jsonify, session
from deep_translator import GoogleTranslator, MicrosoftTranslator, LibreTranslator
import os
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

def get_history():
    """セッションから履歴を取得"""
    return session.get('translation_history', [])

def add_to_history(original, translated):
    """履歴に新しい翻訳結果を追加（重複チェック付き）"""
    history = get_history()
    
    # 既に同じ翻訳結果が存在するかチェック
    for existing_entry in history:
        if (existing_entry['original'] == original and 
            existing_entry['translated'] == translated):
            return
    
    # 新しいエントリを先頭に追加
    new_entry = {
        'original': original,
        'translated': translated,
        'timestamp': datetime.now().isoformat()
    }
    history.insert(0, new_entry)
    
    # 最新5件のみ保持
    history = history[:5]
    
    # セッションに保存
    session['translation_history'] = history
    session.permanent = True

def translate_with_fallback(text, target_lang):
    """複数の翻訳サービスを試行"""
    
    # 1. Google翻訳を試行（少し待機時間を入れる）
    try:
        time.sleep(0.5)  # レート制限回避
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        if result and result.strip():
            return result, "Google"
    except Exception as e:
        print(f"Google翻訳エラー: {e}")
    
    # 2. Microsoft翻訳を試行
    try:
        translator = MicrosoftTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        if result and result.strip():
            return result, "Microsoft"
    except Exception as e:
        print(f"Microsoft翻訳エラー: {e}")
    
    # 3. LibreTranslate を試行
    try:
        # 言語コード変換（LibreTranslateの形式に合わせる）
        lang_mapping = {
            'zh': 'zh-cn',
            'ko': 'ko',
            'ja': 'ja',
            'en': 'en',
            'fr': 'fr',
            'de': 'de',
            'es': 'es',
            'it': 'it'
        }
        libre_lang = lang_mapping.get(target_lang, target_lang)
        
        translator = LibreTranslator(source='auto', target=libre_lang)
        result = translator.translate(text)
        if result and result.strip():
            return result, "LibreTranslate"
    except Exception as e:
        print(f"LibreTranslate翻訳エラー: {e}")
    
    # 4. 簡易翻訳（辞書ベース）- 最後の手段
    simple_translations = {
        ('hello', 'ja'): 'こんにちは',
        ('hello', 'fr'): 'bonjour',
        ('hello', 'de'): 'hallo',
        ('hello', 'es'): 'hola',
        ('thank you', 'ja'): 'ありがとう',
        ('good morning', 'ja'): 'おはよう',
    }
    
    simple_key = (text.lower(), target_lang)
    if simple_key in simple_translations:
        return simple_translations[simple_key], "Simple"
    
    return None, None

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>翻訳アプリ</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            input, select, button { padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 5px; }
            input[type="text"] { width: 300px; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: #e9f7ef; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .history { background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }
            .history-item { border-bottom: 1px solid #eee; padding: 10px 0; }
            .history-item:last-child { border-bottom: none; }
            .service-info { font-size: 0.8em; color: #666; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🌐 翻訳アプリ</h1>
        
        <div class="warning">
            <strong>注意:</strong> 翻訳サービスが一時的に不安定な場合があります。エラーが出る場合は少し時間をおいて再試行してください。
        </div>
        
        <div class="container">
            <h3>翻訳する</h3>
            <form id="translateForm">
                <input type="text" id="textInput" placeholder="翻訳したいテキストを入力" required>
                <select id="langSelect">
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="es">Español</option>
                    <option value="it">Italiano</option>
                    <option value="ko">한국어</option>
                    <option value="zh">中文</option>
                </select>
                <button type="submit">翻訳</button>
            </form>
            <div id="result"></div>
        </div>

        <div class="history">
            <h3>翻訳履歴</h3>
            <div id="historyList">履歴を読み込み中...</div>
            <button onclick="clearHistory()">履歴をクリア</button>
        </div>
        
        <script>
        // 翻訳フォームの処理
        document.getElementById('translateForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const text = document.getElementById('textInput').value;
            const lang = document.getElementById('langSelect').value;
            
            document.getElementById('result').innerHTML = '<p>翻訳中... （複数のサービスを試行中）</p>';
            
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'text=' + encodeURIComponent(text) + '&lang=' + lang
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('result').innerHTML = 
                        '<p style="color: red;">エラー: ' + data.error + '</p>';
                } else {
                    document.getElementById('result').innerHTML = 
                        '<div class="result">' +
                        '<h4>翻訳結果:</h4>' +
                        '<p>' + data.translated + '</p>' +
                        '<div class="service-info">翻訳元: ' + data.service + '</div>' +
                        '</div>';
                    loadHistory(); // 履歴を更新
                }
            })
            .catch(error => {
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">通信エラーが発生しました</p>';
            });
        });

        // 履歴を読み込む
        function loadHistory() {
            fetch('/get_history')
            .then(response => response.json())
            .then(data => {
                const historyList = document.getElementById('historyList');
                if (data.history.length === 0) {
                    historyList.innerHTML = '<p>履歴がありません</p>';
                } else {
                    historyList.innerHTML = data.history.map(item => 
                        '<div class="history-item">' +
                        '<strong>原文:</strong> ' + item.original + '<br>' +
                        '<strong>翻訳:</strong> ' + item.translated +
                        '</div>'
                    ).join('');
                }
            });
        }

        // 履歴をクリア
        function clearHistory() {
            fetch('/clear_history', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadHistory();
                }
            });
        }

        // ページ読み込み時に履歴を表示
        loadHistory();
        </script>
    </body>
    </html>
    '''

@app.route("/get_history")
def get_history_json():
    """履歴をJSON形式で返す"""
    return jsonify({"history": get_history()})

@app.route("/translate", methods=["POST"])
def translate_ajax():
    """Ajax用の翻訳エンドポイント"""
    try:
        target_lang = request.form.get("lang", "en")
        text = request.form.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "テキストが入力されていません"}), 400
        
        # 複数サービスで翻訳を試行
        translated_text, service = translate_with_fallback(text, target_lang)
        
        if not translated_text:
            return jsonify({"error": "すべての翻訳サービスが利用できません。しばらくしてから再試行してください。"}), 503
        
        # 履歴に追加
        add_to_history(text, translated_text)
        
        return jsonify({
            "translated": translated_text,
            "service": service
        })
        
    except Exception as e:
        print(f"翻訳エラー: {e}")
        return jsonify({"error": "翻訳中にエラーが発生しました"}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """履歴をクリア"""
    session['translation_history'] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
