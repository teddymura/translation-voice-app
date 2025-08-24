import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import gtts
import io
import base64

app = Flask(__name__)

# より軽量なモデルを使用
MODEL_NAME = "facebook/nllb-200-distilled-600M"

# 言語コードマッピング（HTMLの短縮形 → NLLBの正式コード）
LANG_MAPPING = {
    'en': 'eng_Latn',
    'ja': 'jpn_Jpan',
    'fr': 'fra_Latn',
    'de': 'deu_Latn', 
    'it': 'ita_Latn',
    'zh': 'zho_Hans',
    'ko': 'kor_Hang'
}

# gTTSでサポートされている言語コード
GTTS_LANG_MAPPING = {
    'en': 'en',
    'ja': 'ja',
    'fr': 'fr',
    'de': 'de',
    'it': 'it',
    'zh': 'zh',
    'ko': 'ko'
}

# 翻訳パイプライン（動的に作成するため、ここでは定義しない）
translators = {}

# 翻訳履歴を保存するリスト（最大5件）
translation_history = []

def get_translator(src_lang, tgt_lang):
    """翻訳パイプラインを取得（キャッシュ機能付き）"""
    key = f"{src_lang}-{tgt_lang}"
    if key not in translators:
        translators[key] = pipeline(
            "translation", 
            model=MODEL_NAME,
            src_lang=LANG_MAPPING[src_lang],
            tgt_lang=LANG_MAPPING[tgt_lang],
            max_length=512,  # メモリ使用量を制限
            device=-1  # CPUを強制使用
        )
    return translators[key]

def generate_speech(text, lang_code):
    """音声データを生成してBase64エンコード"""
    try:
        if lang_code not in GTTS_LANG_MAPPING:
            return None
            
        gtts_lang = GTTS_LANG_MAPPING[lang_code]
        tts = gtts.gTTS(text=text, lang=gtts_lang, slow=False)
        
        # メモリ上でMP3データを生成
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Base64エンコード
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        return audio_base64
        
    except Exception as e:
        print(f"音声生成エラー: {e}")
        return None

def add_to_history(original, translated, src_lang, tgt_lang, audio_data):
    """翻訳履歴に追加（最大5件まで保持）"""
    global translation_history
    
    history_item = {
        'id': datetime.now().isoformat(),
        'original': original,
        'translated': translated,
        'src_lang': src_lang,
        'tgt_lang': tgt_lang,
        'audio': audio_data,
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
            
        if src not in LANG_MAPPING or tgt not in LANG_MAPPING:
            return jsonify({"error": "サポートされていない言語です"}), 400
            
        if src == tgt:
            audio_data = generate_speech(text, src)
            add_to_history(text, text, src, tgt, audio_data)
            return jsonify({
                "translated": text,
                "audio": audio_data
            })
            
        # 翻訳実行
        translator = get_translator(src, tgt)
        result = translator(text)
        translated_text = result[0]['translation_text']
        
        # 音声生成
        audio_data = generate_speech(translated_text, tgt)
        
        # 履歴に追加
        add_to_history(text, translated_text, src, tgt, audio_data)
        
        return jsonify({
            "translated": translated_text,
            "audio": audio_data
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
