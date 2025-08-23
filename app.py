from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# 基本的な翻訳辞書
TRANSLATION_DICT = {
    'en': {
        'hello': {'ja': 'こんにちは', 'fr': 'bonjour', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕하세요', 'zh': '你好'},
        'thank you': {'ja': 'ありがとう', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '감사합니다', 'zh': '谢谢'},
        'good morning': {'ja': 'おはよう', 'fr': 'bonjour', 'de': 'guten morgen', 'es': 'buenos días', 'it': 'buongiorno', 'ko': '좋은 아침', 'zh': '早上好'},
        'good night': {'ja': 'おやすみ', 'fr': 'bonne nuit', 'de': 'gute nacht', 'es': 'buenas noches', 'it': 'buonanotte', 'ko': '좋은 밤', 'zh': '晚安'},
        'yes': {'ja': 'はい', 'fr': 'oui', 'de': 'ja', 'es': 'sí', 'it': 'sì', 'ko': '네', 'zh': '是'},
        'no': {'ja': 'いいえ', 'fr': 'non', 'de': 'nein', 'es': 'no', 'it': 'no', 'ko': '아니오', 'zh': '不'},
        'please': {'ja': 'お願いします', 'fr': 's\'il vous plaît', 'de': 'bitte', 'es': 'por favor', 'it': 'per favore', 'ko': '제발', 'zh': '请'},
        'sorry': {'ja': 'すみません', 'fr': 'désolé', 'de': 'entschuldigung', 'es': 'lo siento', 'it': 'scusa', 'ko': '미안해요', 'zh': '对不起'},
        'love': {'ja': '愛', 'fr': 'amour', 'de': 'liebe', 'es': 'amor', 'it': 'amore', 'ko': '사랑', 'zh': '爱'},
        'water': {'ja': '水', 'fr': 'eau', 'de': 'wasser', 'es': 'agua', 'it': 'acqua', 'ko': '물', 'zh': '水'},
        'food': {'ja': '食べ物', 'fr': 'nourriture', 'de': 'essen', 'es': 'comida', 'it': 'cibo', 'ko': '음식', 'zh': '食物'},
        'beautiful': {'ja': '美しい', 'fr': 'beau', 'de': 'schön', 'es': 'hermoso', 'it': 'bello', 'ko': '아름다운', 'zh': '美丽'},
        'happy': {'ja': '幸せ', 'fr': 'heureux', 'de': 'glücklich', 'es': 'feliz', 'it': 'felice', 'ko': '행복한', 'zh': '快乐'},
        'cat': {'ja': '猫', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'},
        'dog': {'ja': '犬', 'fr': 'chien', 'de': 'hund', 'es': 'perro', 'it': 'cane', 'ko': '개', 'zh': '狗'},
        'house': {'ja': '家', 'fr': 'maison', 'de': 'haus', 'es': 'casa', 'it': 'casa', 'ko': '집', 'zh': '房子'},
        'friend': {'ja': '友達', 'fr': 'ami', 'de': 'freund', 'es': 'amigo', 'it': 'amico', 'ko': '친구', 'zh': '朋友'},
        'family': {'ja': '家族', 'fr': 'famille', 'de': 'familie', 'es': 'familia', 'it': 'famiglia', 'ko': '가족', 'zh': '家庭'},
        'time': {'ja': '時間', 'fr': 'temps', 'de': 'zeit', 'es': 'tiempo', 'it': 'tempo', 'ko': '시간', 'zh': '时间'},
        'money': {'ja': 'お金', 'fr': 'argent', 'de': 'geld', 'es': 'dinero', 'it': 'denaro', 'ko': '돈', 'zh': '钱'},
        'work': {'ja': '仕事', 'fr': 'travail', 'de': 'arbeit', 'es': 'trabajo', 'it': 'lavoro', 'ko': '일', 'zh': '工作'},
        'school': {'ja': '学校', 'fr': 'école', 'de': 'schule', 'es': 'escuela', 'it': 'scuola', 'ko': '학교', 'zh': '学校'}
    },
    'ja': {
        'こんにちは': {'en': 'hello', 'fr': 'bonjour', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕하세요', 'zh': '你好'},
        'ありがとう': {'en': 'thank you', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '감사합니다', 'zh': '谢谢'},
        'おはよう': {'en': 'good morning', 'fr': 'bonjour', 'de': 'guten morgen', 'es': 'buenos días', 'it': 'buongiorno', 'ko': '좋은 아침', 'zh': '早上好'},
        'はい': {'en': 'yes', 'fr': 'oui', 'de': 'ja', 'es': 'sí', 'it': 'sì', 'ko': '네', 'zh': '是'},
        'いいえ': {'en': 'no', 'fr': 'non', 'de': 'nein', 'es': 'no', 'it': 'no', 'ko': '아니오', 'zh': '不'},
        '愛': {'en': 'love', 'fr': 'amour', 'de': 'liebe', 'es': 'amor', 'it': 'amore', 'ko': '사랑', 'zh': '爱'},
        '猫': {'en': 'cat', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'},
        '犬': {'en': 'dog', 'fr': 'chien', 'de': 'hund', 'es': 'perro', 'it': 'cane', 'ko': '개', 'zh': '狗'},
    }
}

def get_history():
    """セッションから履歴を取得"""
    return session.get('translation_history', [])

def add_to_history(original, translated, service="Dictionary"):
    """履歴に新しい翻訳結果を追加"""
    history = get_history()
    
    for existing_entry in history:
        if (existing_entry['original'] == original and 
            existing_entry['translated'] == translated):
            return
    
    new_entry = {
        'original': original,
        'translated': translated,
        'service': service,
        'timestamp': datetime.now().isoformat()
    }
    history.insert(0, new_entry)
    history = history[:10]  # 10件まで保持
    
    session['translation_history'] = history
    session.permanent = True

def offline_translate(text, target_lang):
    """オフライン辞書を使用した翻訳"""
    text_lower = text.lower().strip()
    
    # 英語から他言語への翻訳
    if text_lower in TRANSLATION_DICT.get('en', {}):
        translation = TRANSLATION_DICT['en'][text_lower].get(target_lang)
        if translation:
            return translation, "Dictionary (EN→" + target_lang.upper() + ")"
    
    # 日本語から他言語への翻訳
    if text in TRANSLATION_DICT.get('ja', {}):
        translation = TRANSLATION_DICT['ja'][text].get(target_lang)
        if translation:
            return translation, "Dictionary (JA→" + target_lang.upper() + ")"
    
    # 部分マッチを試行
    for lang in ['en', 'ja']:
        for key, translations in TRANSLATION_DICT.get(lang, {}).items():
            if text_lower in key or key in text_lower:
                translation = translations.get(target_lang)
                if translation:
                    return f"{translation} (部分マッチ)", f"Dictionary ({lang.upper()}→{target_lang.upper()})"
    
    return None, None

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    # 利用可能な単語リストを生成
    available_words = []
    for lang_dict in TRANSLATION_DICT.values():
        available_words.extend(list(lang_dict.keys())[:10])  # 各言語から10個ずつ
    
    word_examples = ", ".join(available_words[:15])  # 最初の15個を表示
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>翻訳アプリ (オフライン版)</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            input, select, button {{ padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 5px; }}
            input[type="text"] {{ width: 300px; }}
            button {{ background: #007bff; color: white; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            .result {{ background: #e9f7ef; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .history {{ background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }}
            .history-item {{ border-bottom: 1px solid #eee; padding: 10px 0; }}
            .history-item:last-child {{ border-bottom: none; }}
            .service-info {{ font-size: 0.8em; color: #666; }}
            .info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .examples {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>🌐 翻訳アプリ (オフライン辞書版)</h1>
        
        <div class="info">
            <strong>📘 現在オフライン辞書モードで動作中</strong><br>
            インターネット翻訳サービスが一時的に利用できないため、内蔵辞書を使用しています。<br>
            基本的な単語や挨拶の翻訳が可能です。
        </div>
        
        <div class="examples">
            <strong>利用可能な単語例:</strong><br>
            {word_examples}... など
        </div>
        
        <div class="container">
            <h3>翻訳する</h3>
            <form id="translateForm">
                <input type="text" id="textInput" placeholder="翻訳したい単語を入力 (例: hello, ありがとう)" required>
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
        document.getElementById('translateForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const text = document.getElementById('textInput').value;
            const lang = document.getElementById('langSelect').value;
            
            document.getElementById('result').innerHTML = '<p>辞書を検索中...</p>';
            
            fetch('/translate', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded',
                }},
                body: 'text=' + encodeURIComponent(text) + '&lang=' + lang
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.error) {{
                    document.getElementById('result').innerHTML = 
                        '<p style="color: red;">エラー: ' + data.error + '</p>';
                }} else {{
                    document.getElementById('result').innerHTML = 
                        '<div class="result">' +
                        '<h4>翻訳結果:</h4>' +
                        '<p>' + data.translated + '</p>' +
                        '<div class="service-info">翻訳元: ' + data.service + '</div>' +
                        '</div>';
                    loadHistory();
                }}
            }})
            .catch(error => {{
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">通信エラーが発生しました</p>';
            }});
        }});

        function loadHistory() {{
            fetch('/get_history')
            .then(response => response.json())
            .then(data => {{
                const historyList = document.getElementById('historyList');
                if (data.history.length === 0) {{
                    historyList.innerHTML = '<p>履歴がありません</p>';
                }} else {{
                    historyList.innerHTML = data.history.map(item => 
                        '<div class="history-item">' +
                        '<strong>原文:</strong> ' + item.original + '<br>' +
                        '<strong>翻訳:</strong> ' + item.translated + '<br>' +
                        '<div class="service-info">' + item.service + '</div>' +
                        '</div>'
                    ).join('');
                }}
            }});
        }}

        function clearHistory() {{
            fetch('/clear_history', {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    loadHistory();
                }}
            }});
        }}

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
        
        # オフライン辞書で翻訳
        translated_text, service = offline_translate(text, target_lang)
        
        if not translated_text:
            return jsonify({"error": f"「{text}」は辞書に登録されていません。利用可能な単語例を参照してください。"}), 404
        
        # 履歴に追加
        add_to_history(text, translated_text, service)
        
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
