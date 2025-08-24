import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from googletrans import Translator

app = Flask(__name__)

# Google Translateのインスタンス
translator = Translator()

# 翻訳履歴を保存するリスト（最大5件）
translation_history = []

def add_to_history(original, translated, src_lang, tgt_lang):
    """翻訳履歴に追加（最大5件まで保持）"""
    global translation_history
    
    history_item = {
        'id': datetime.now().isoformat(),
        'original': original,
        'translated': translated,
        'src_lang': src_lang,
        'tgt_lang': tgt_lang,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 新しい項目を先頭に追加
    translation_history.insert(0, history_item)
    
    # 5件を超えた場合、古いものを削除
    if len(translation_history) > 5:
        translation_history = translation_history[:5]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        src = data.get("src", "en")
        tgt = data.get("tgt", "ja")
        
        if not text:
            return jsonify({"error": "テキストが入力されていません"}), 400
            
        if src == tgt:
            add_to_history(text, text, src, tgt)
            return jsonify({
                "translated": text,
                "audio": None
            })
            
        # Google Translateで翻訳実行
        result = translator.translate(text, src=src, dest=tgt)
        translated_text = result.text
        
        # 履歴に追加
        add_to_history(text, translated_text, src, tgt)
        
        return jsonify({
            "translated": translated_text,
            "audio": None  # 音声は無効
        })
        
    except Exception as e:
        print(f"翻訳エラー: {e}")
        return jsonify({"error": "翻訳中にエラーが発生しました"}), 500

@app.route("/history", methods=["GET"])
def get_history():
    """翻訳履歴を取得"""
    return jsonify({"history": translation_history})

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """翻訳履歴をクリア"""
    global translation_history
    translation_history = []
    return jsonify({"message": "履歴をクリアしました"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
