import streamlit as st
from deep_translator import GoogleTranslator
import gtts
import io
import base64

# ページ設定
st.set_page_config(
    page_title="🌍 翻訳アプリ",
    page_icon="🌍",
    layout="wide"
)

# タイトル
st.title("🌍 多言語翻訳アプリ")

# 翻訳関数
def translate_text(text, src_lang, tgt_lang):
    try:
        translator = GoogleTranslator(source=src_lang, target=tgt_lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        raise Exception(f"翻訳エラー: {str(e)}")

# gTTS用の言語コード変換
def get_tts_lang_code(lang_code):
    """gTTSで使用する言語コードに変換"""
    lang_mapping = {
        'zh': 'zh-cn',  # 中国語（簡体字）
        'ja': 'ja',
        'en': 'en', 
        'fr': 'fr',
        'de': 'de',
        'it': 'it',
        'ko': 'ko'
    }
    return lang_mapping.get(lang_code, 'en')  # デフォルトは英語

# 安全な音声生成関数
def generate_audio(text, lang_code):
    """安全に音声を生成する"""
    try:
        # 空文字チェック
        if not text or not text.strip():
            raise Exception("音声生成するテキストが空です")
        
        # 言語コード変換
        tts_lang = get_tts_lang_code(lang_code)
        
        # iOS対策：文字数制限とテキスト正規化
        text = text.strip()
        if len(text) > 200:  # より短く制限
            text = text[:200] + "..."
        
        # 特殊文字の処理（iOS対策）
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        if not text.strip():
            raise Exception("有効なテキストがありません")
        
        # 音声生成
        tts = gtts.gTTS(text=text, lang=tts_lang, slow=False, lang_check=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return mp3_fp
    except Exception as e:
        raise Exception(f"音声生成に失敗しました: {str(e)}")

# iOS判定関数
def is_ios_device():
    """ユーザーエージェントからiOSデバイスかどうか判定（簡易版）"""
    return False  # サーバーサイドでは正確な判定が困難なため、常にFalseを返す

# 言語選択
col1, col2 = st.columns(2)

with col1:
    src_lang = st.selectbox(
        "翻訳元の言語",
        ["en", "ja", "fr", "de", "it", "zh", "ko"],
        format_func=lambda x: {
            "en": "🇺🇸 English", 
            "ja": "🇯🇵 日本語",
            "fr": "🇫🇷 Français", 
            "de": "🇩🇪 Deutsch",
            "it": "🇮🇹 Italiano", 
            "zh": "🇨🇳 中文",
            "ko": "🇰🇷 한국어"
        }[x]
    )

with col2:
    tgt_lang = st.selectbox(
        "翻訳先の言語",
        ["ja", "en", "fr", "de", "it", "zh", "ko"],
        format_func=lambda x: {
            "en": "🇺🇸 English", 
            "ja": "🇯🇵 日本語",
            "fr": "🇫🇷 Français", 
            "de": "🇩🇪 Deutsch",
            "it": "🇮🇹 Italiano", 
            "zh": "🇨🇳 中文",
            "ko": "🇰🇷 한국語"
        }[x]
    )

# 入力テキスト
input_text = st.text_area(
    "翻訳したいテキストを入力してください",
    height=100,
    placeholder="例: Hello, how are you today?"
)

# 翻訳ボタン
if st.button("🔄 翻訳する", type="primary"):
    if input_text.strip():
        if src_lang != tgt_lang:
            try:
                # 翻訳実行
                with st.spinner("翻訳中..."):
                    translated_text = translate_text(input_text, src_lang, tgt_lang)
                
                # セッション状態に結果を保存
                st.session_state.current_translation = {
                    'original': input_text,
                    'translated': translated_text,
                    'src_lang': src_lang,
                    'tgt_lang': tgt_lang
                }
                
                # 履歴に追加
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                # 新しい翻訳を履歴の先頭に追加
                history_item = {
                    'original': input_text,
                    'translated': translated_text,
                    'src_lang': src_lang,
                    'tgt_lang': tgt_lang
                }
                st.session_state.history.insert(0, history_item)
                
                # 5件まで保持
                if len(st.session_state.history) > 5:
                    st.session_state.history = st.session_state.history[:5]
                    
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("⚠️ 同じ言語が選択されています")
    else:
        st.warning("⚠️ テキストを入力してください")

# 翻訳結果の表示
if 'current_translation' in st.session_state:
    st.success("✅ 翻訳完了！")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_area(
            "翻訳結果",
            value=st.session_state.current_translation['translated'],
            height=100,
            disabled=True
        )
    
    with col2:
        # iOS対策：音声機能の説明を追加
        st.info("📱 iOS端末をご利用の場合、音声再生にはブラウザの制限があります")
        
        # 音声生成ボタン
        if st.button("🔊 音声再生"):
            try:
                with st.spinner("音声生成中..."):
                    mp3_fp = generate_audio(
                        st.session_state.current_translation['translated'],
                        st.session_state.current_translation['tgt_lang']
                    )
                    
                    # 音声ファイル情報を表示
                    audio_data = mp3_fp.read()
                    st.success(f"🎵 音声を生成しました ({len(audio_data)} bytes)")
                    
                    # 音声プレイヤー（iOS対策：autoplayを削除）
                    st.audio(audio_data, format='audio/mp3')
                    
                    # iOS用の追加説明
                    st.caption("🔸 iOS端末の場合は、音声プレイヤーの再生ボタンを手動でタップしてください")
                    
            except Exception as e:
                st.error(f"音声生成エラー: {str(e)}")
                # デバッグ情報を表示
                st.caption(f"エラー詳細: 言語={st.session_state.current_translation['tgt_lang']}, テキスト長={len(st.session_state.current_translation['translated'])}")
        
        # 音声を自動生成するオプション（iOS対策で名称変更）
        if st.checkbox("翻訳時に音声も生成"):
            try:
                with st.spinner("音声生成中..."):
                    mp3_fp = generate_audio(
                        st.session_state.current_translation['translated'],
                        st.session_state.current_translation['tgt_lang']
                    )
                    
                    # 音声プレイヤー
                    audio_data = mp3_fp.read()
                    st.audio(audio_data, format='audio/mp3')
                    st.caption("🔸 音声プレイヤーの再生ボタンをタップしてください")
            except Exception as e:
                st.error(f"音声生成エラー: {str(e)}")

# 履歴表示
if 'history' in st.session_state and st.session_state.history:
    st.markdown("---")
    st.subheader("📝 翻訳履歴（最新5件）")
    
    for i, item in enumerate(st.session_state.history):
        with st.expander(f"{i+1}. {item['original'][:30]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_area(
                    f"原文 ({item['src_lang']})",
                    value=item['original'],
                    height=60,
                    disabled=True,
                    key=f"orig_{i}"
                )
                # 原文の音声ボタン
                if st.button(f"🔊 原文音声", key=f"orig_audio_{i}"):
                    try:
                        with st.spinner("音声生成中..."):
                            mp3_fp = generate_audio(item['original'], item['src_lang'])
                            audio_data = mp3_fp.read()
                            st.audio(audio_data, format='audio/mp3')
                            st.success("🎵 原文音声を生成しました")
                            st.caption("🔸 再生ボタンをタップしてください")
                    except Exception as e:
                        st.error(f"音声生成エラー: {str(e)}")
            
            with col2:
                st.text_area(
                    f"翻訳 ({item['tgt_lang']})",
                    value=item['translated'],
                    height=60,
                    disabled=True,
                    key=f"trans_{i}"
                )
                # 翻訳文の音声ボタン
                if st.button(f"🔊 翻訳音声", key=f"trans_audio_{i}"):
                    try:
                        with st.spinner("音声生成中..."):
                            mp3_fp = generate_audio(item['translated'], item['tgt_lang'])
                            audio_data = mp3_fp.read()
                            st.audio(audio_data, format='audio/mp3')
                            st.success("🎵 翻訳音声を生成しました")
                            st.caption("🔸 再生ボタンをタップしてください")
                    except Exception as e:
                        st.error(f"音声生成エラー: {str(e)}")

# サイドバー
with st.sidebar:
    st.markdown("## 📱 使い方")
    st.markdown("""
    1. 翻訳元と翻訳先の言語を選択
    2. テキストを入力
    3. 「翻訳する」ボタンをクリック
    4. 音声再生も可能！
    """)
    
    st.markdown("## ✨ 特徴")
    st.markdown("""
    - 🌍 7言語対応
    - 🔊 音声読み上げ（現在の翻訳＆履歴）
    - 📝 履歴管理（5件）
    - ⚡ 高速翻訳
    - 🎵 原文・翻訳文両方の音声対応
    """)
    
    if st.button("🗑️ 履歴をクリア"):
        st.session_state.history = []
        st.rerun()
