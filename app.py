from flask import Flask, render_template, request, jsonify, session
from googletrans import Translator
from gtts import gTTS
import os
import uuid
import glob
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
translator = Translator()

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
        
        # 翻訳（エラーハンドリング強化）
        try:
            translated = translator.translate(text, dest=target_lang)
            translated_text = translated.text
        except Exception as trans_error:
            print(f"翻訳サービスエラー: {trans_error}")
            return jsonify({"error": "翻訳サービスが利用できません"}), 503
        
        # gTTS 音声生成
        try:
            tts_lang = LANG_MAP.get(target_lang, "en")
            audio_filename = f"{uuid.uuid4()}.mp3"
            tts_path = os.path.join(STATIC_FOLDER, audio_filename)
            
            tts = gTTS(translated_text, lang=tts_lang)
            tts.save(tts_path)
            
            # 音声ファイルのクリーンアップ
            cleanup_audio_files()
        except Exception as tts_error:
            print(f"音声生成エラー: {tts_error}")
            # 音声生成が失敗しても翻訳結果は返す
            audio_filename = None
        
        # 履歴に追加
        audio_path = f"/static/{audio_filename}" if audio_filename else None
        add_to_history(text, translated_text, audio_path)
        
        response_data = {
            "translated": translated_text
        }
        if audio_filename:
            response_data["audio"] = f"/static/{audio_filename}"
        
        return jsonify(response_data)
        
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
