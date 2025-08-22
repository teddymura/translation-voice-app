from flask import Flask, render_template, request, jsonify, session
from googletrans import Translator
from gtts import gTTS
import os
import whisper
import uuid
import glob
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # セッション用のシークレットキー

translator = Translator()
model = whisper.load_model("base")  # CPUでもOK

LANG_MAP = {
    "en": "en", "ja": "ja", "fr": "fr", "de": "de",
    "it": "it", "es": "es", "ko": "ko", "zh-cn": "zh-CN"
}

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

def cleanup_audio_files():
    """staticフォルダ内の音声ファイルを5件まで残して削除"""
    try:
        # static フォルダ内の .mp3 ファイルを取得
        audio_files = glob.glob(os.path.join(STATIC_FOLDER, "*.mp3"))
        
        # ファイルを作成日時でソート（新しい順）
        audio_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        
        # 5件を超える古いファイルを削除
        if len(audio_files) > 5:
            for file_path in audio_files[5:]:
                try:
                    os.remove(file_path)
                    print(f"削除しました: {file_path}")
                except OSError as e:
                    print(f"ファイル削除エラー: {file_path}, {e}")
    except Exception as e:
        print(f"音声ファイルクリーンアップエラー: {e}")

def get_history():
    """セッションから履歴を取得"""
    return session.get('translation_history', [])

def add_to_history(original, translated, audio_path=None):
    """履歴に新しい翻訳結果を追加（重複チェック付き）"""
    history = get_history()
    
    # 既に同じ翻訳結果が存在するかチェック
    for existing_entry in history:
        if (existing_entry['original'] == original and 
            existing_entry['translated'] == translated):
            # 同じ内容が既に存在する場合は追加しない
            return
    
    # 新しいエントリを先頭に追加
    new_entry = {
        'original': original,
        'translated': translated,
        'audio': audio_path,
        'timestamp': datetime.now().isoformat()
    }
    history.insert(0, new_entry)
    
    # 最新5件のみ保持
    history = history[:5]
    
    # セッションに保存
    session['translation_history'] = history
    session.permanent = True  # セッションを永続化

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    return render_template("index.html", history=get_history())

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
        
        # 翻訳
        translated = translator.translate(text, dest=target_lang)
        translated_text = translated.text

        # gTTS 音声生成
        tts_lang = LANG_MAP.get(target_lang, "en")
        audio_filename = f"{uuid.uuid4()}.mp3"
        tts_path = os.path.join(STATIC_FOLDER, audio_filename)
        
        tts = gTTS(translated_text, lang=tts_lang)
        tts.save(tts_path)
        
        # 音声ファイルのクリーンアップ
        cleanup_audio_files()
        
        # 履歴に追加
        add_to_history(text, translated_text, f"/{tts_path}")
        
        return jsonify({
            "translated": translated_text,
            "audio": f"/{tts_path}"
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
    app.run(debug=True, host="0.0.0.0", port=5000)