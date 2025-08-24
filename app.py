from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# 基本的な翻訳辞書（フォールバック用）
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
        'cat': {'ja': '猫', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'},
        'dog': {'ja': '犬', 'fr': 'chien', 'de': 'hund', 'es': 'perro', 'it': 'cane', 'ko': '개', 'zh': '狗'}
    },
    'ja': {
        'こんにちは': {'en': 'hello', 'fr': 'bonjour', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕하세요', 'zh': '你好'},
        'ありがとう': {'en': 'thank you', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '감사합니다', 'zh': '谢谢'},
        'おはよう': {'en': 'good morning', 'fr': 'bonjour', 'de': 'guten morgen', 'es': 'buenos días', 'it': 'buongiorno', 'ko': '좋은 아침', 'zh': '早上好'},
        'はい': {'en': 'yes', 'fr': 'oui', 'de': 'ja', 'es': 'sí', 'it': 'sì', 'ko': '네', 'zh': '是'},
        'いいえ': {'en': 'no', 'fr': 'non', 'de': 'nein', 'es': 'no', 'it': 'no', 'ko': '아니오', 'zh': '不'},
        '愛': {'en': 'love', 'fr': 'amour', 'de': 'liebe', 'es': 'amor', 'it': 'amore', 'ko': '사랑', 'zh': '爱'},
        '猫': {'en': 'cat', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'}
    }
}

def get_history():
    """セッションから履歴を取得"""
    return session.get('translation_history', [])

def add_to_history(original, translated, service):
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
    history = history[:10]
    
    session['translation_history'] = history
    session.permanent = True

def try_api_translation(text, target_lang):
    """API翻訳を試行"""
    try:
        from deep_translator import GoogleTranslator
        time.sleep(0.5)  # レート制限対策
        
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        
        if result and result.strip() and result.lower() != text.lower():
            return result, "Google Translate API"
        else:
            return None, None
            
    except ImportError:
        print("deep-translator が見つかりません")
        return None, None
    except Exception as e:
        print(f"API翻訳エラー: {e}")
        return None, None

def offline_translate(text, target_lang):
    """オフライン辞書翻訳"""
    text_lower = text.lower().strip()
    
    # 英語から他言語
    if text_lower in TRANSLATION_DICT.get('en', {}):
        translation = TRANSLATION_DICT['en'][text_lower].get(target_lang)
        if translation:
            return translation, "Dictionary (EN→" + target_lang.upper() + ")"
    
    # 日本語から他言語
    if text in TRANSLATION_DICT.get('ja', {}):
        translation = TRANSLATION_DICT['ja'][text].get(target_lang)
        if translation:
            return translation, "Dictionary (JA→" + target_lang.upper() + ")"
    
    return None, None

def smart_translate(text, target_lang):
    """スマート翻訳: API優先、辞書フォールバック"""
    
    # 1. まずAPI翻訳を試行
    api_result, api_service = try_api_translation(text, target_lang)
    if api_result:
        return api_result, api_service
    
    # 2. APIが失敗したら辞書翻訳
    dict_result, dict_service = offline_translate(text, target_lang)
    if dict_result:
        return dict_result, dict_service + " (API unavailable)"
    
    # 3. どちらも失敗
    return None, None

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>翻訳アプリ (ハイブリッド版)</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            input, select, button { padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 5px; }
            input[type="text"] { width: 350px; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: #e9f7ef; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .result.api { background: #e3f2fd; }
            .result.dictionary { background: #fff3e0; }
            .history { background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }
            .history-item { border-bottom: 1px solid #eee; padding: 10px 0; }
            .history-item:last-child { border-bottom: none; }
            .service-info { font-size: 0.8em; color: #666; margin-top: 5px; }
            .info { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .status { text-align: center; margin: 10px 0; font-weight: bold; }
            .loading { color: #007bff; }
        </style>
    </head>
    <body>
        <h1>🌐 翻訳アプリ (ハイブリッド版)</h1>
        
        <div class="info">
            <strong>🚀 ハイブリッド翻訳システム</strong><br>
            ① まずGoogle翻訳APIを試行<br>
            ② APIが利用できない場合は内蔵辞書を使用<br>
            → どんな単語でも安心して翻訳できます！
        </div>
        
        <div class="container">
            <h3>翻訳する</h3>
            <form id="translateForm">
                <input type="text" id="textInput" placeholder="翻訳したいテキストを入力 (単語でも文でもOK)" required>
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
            <div id="status" class="status"></div>
            <div id="result"></div>
        </div>

        <div class="history">
            <h3>翻訳履歴</h3>
            <div id="historyList">履歴を読み込み中...</div>
            <button onclick="clearHistory()">履歴をクリア</button>
        </div>
        
        <script>
        document.getElementById('translateForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const text = document.getElementById('textInput').value;
            const lang = document.getElementById('langSelect').value;
            
            document.getElementById('status').innerHTML = '<span class="loading">🔄 Google翻訳APIを試行中...</span>';
            document.getElementById('result').innerHTML = '';
            
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'text=' + encodeURIComponent(text) + '&lang=' + lang
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = '';
                
                if (data.error) {
                    document.getElementById('result').innerHTML = 
                        '<p style="color: red;">エラー: ' + data.error + '</p>';
                } else {
                    let resultClass = 'result';
                    if (data.service.includes('API')) {
                        resultClass += ' api';
                    } else if (data.service.includes('Dictionary')) {
                        resultClass += ' dictionary';
                    }
                    
                    document.getElementById('result').innerHTML = 
                        '<div class="' + resultClass + '">' +
                        '<h4>翻訳結果:</h4>' +
                        '<p style="font-size: 1.2em;">' + data.translated + '</p>' +
                        '<div class="service-info">🔧 ' + data.service + '</div>' +
                        '</div>';
                    loadHistory();
                }
            })
            .catch(error => {
                document.getElementById('status').innerHTML = '';
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">通信エラーが発生しました</p>';
            });
        });

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
                        '<strong>翻訳:</strong> ' + item.translated + '<br>' +
                        '<div class="service-info">🔧 ' + item.service + '</div>' +
                        '</div>'
                    ).join('');
                }
            });
        }

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
        
        # スマート翻訳を実行
        translated_text, service = smart_translate(text, target_lang)
        
        if not translated_text:
            return jsonify({"error": f"「{text}」を翻訳できませんでした。APIが利用できず、辞書にも登録されていません。"}), 404
        
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
