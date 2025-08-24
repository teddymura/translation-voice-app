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
        # 音声生成ボタン
        if st.button("🔊 音声再生"):
            try:
                with st.spinner("音声生成中..."):
                    tts = gtts.gTTS(
                        text=st.session_state.current_translation['translated'], 
                        lang=st.session_state.current_translation['tgt_lang'], 
                        slow=False
                    )
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    
                    # 音声プレイヤー
                    st.audio(mp3_fp.read(), format='audio/mp3', autoplay=True)
                    st.success("🎵 音声を生成しました")
            except Exception as e:
                st.error(f"音声生成エラー: {str(e)}")
        
        # 音声を自動生成するオプション
        if st.checkbox("自動音声生成"):
            try:
                with st.spinner("音声生成中..."):
                    tts = gtts.gTTS(
                        text=st.session_state.current_translation['translated'], 
                        lang=st.session_state.current_translation['tgt_lang'], 
                        slow=False
                    )
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    
                    # 音声プレイヤー
                    st.audio(mp3_fp.read(), format='audio/mp3')
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
            
            with col2:
                st.text_area(
                    f"翻訳 ({item['tgt_lang']})",
                    value=item['translated'],
                    height=60,
                    disabled=True,
                    key=f"trans_{i}"
                )

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
    - 🔊 音声読み上げ
    - 📝 履歴管理（5件）
    - ⚡ 高速翻訳
    """)
    
    if st.button("🗑️ 履歴をクリア"):
        st.session_state.history = []
        st.rerun()
