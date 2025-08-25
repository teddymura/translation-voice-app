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
        
        # iOS対策：より厳しい制限
        text = text.strip()
        # 英数字、基本的な句読点、ひらがな、カタカナ、漢字のみ許可
        import re
        if lang_code == 'ja':
            text = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\w\s\.\,\!\?\-]', '', text)
        else:
            text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        # より短い制限
        if len(text) > 100:
            text = text[:100] + "..."
        
        if not text.strip():
            raise Exception("有効なテキストがありません")
        
        # 音声生成（より安全な設定）
        tts = gtts.gTTS(
            text=text, 
            lang=tts_lang, 
            slow=False, 
            lang_check=False,
            tld='com'  # トップレベルドメインを明示的に指定
        )
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return mp3_fp, len(text)
    except Exception as e:
        raise Exception(f"音声生成に失敗: {str(e)}")

# デバイス判定とフォールバック
def show_audio_alternative(text, lang_code):
    """音声が生成できない場合の代替案を表示"""
    st.warning("🔧 音声生成に問題があります。以下の代替案をお試しください：")
    
    # Google翻訳のリンク
    lang_map = {
        'ja': 'ja', 'en': 'en', 'fr': 'fr', 'de': 'de', 
        'it': 'it', 'zh': 'zh-CN', 'ko': 'ko'
    }
    google_lang = lang_map.get(lang_code, 'en')
    
    import urllib.parse
    encoded_text = urllib.parse.quote(text[:100])
    google_url = f"https://translate.google.com/?sl=auto&tl={google_lang}&text={encoded_text}&op=translate"
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🔗 [Google翻訳で音声を聞く]({google_url})")
        st.caption("外部リンクでGoogle翻訳の音声機能を使用")
    
    with col2:
        # テキストをコピー用に表示
        st.text_input("📋 コピー用テキスト", value=text, key=f"copy_{hash(text)}")
        st.caption("テキストをコピーして他の音声アプリで使用")

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
        # 音声機能の状態表示
        st.info("🔊 音声機能")
        
        # 音声生成ボタン
        if st.button("🔊 音声再生"):
            try:
                with st.spinner("音声生成中..."):
                    mp3_fp, text_length = generate_audio(
                        st.session_state.current_translation['translated'],
                        st.session_state.current_translation['tgt_lang']
                    )
                    
                    # 音声ファイル情報を表示
                    audio_data = mp3_fp.read()
                    st.success(f"✅ 音声生成成功 (文字数: {text_length})")
                    
                    # 音声プレイヤー
                    st.audio(audio_data, format='audio/mp3')
                    st.caption("▶️ 上の再生ボタンをタップしてください")
                    
            except Exception as e:
                st.error(f"❌ 音声生成失敗: {str(e)}")
                # 代替案を表示
                show_audio_alternative(
                    st.session_state.current_translation['translated'],
                    st.session_state.current_translation['tgt_lang']
                )
        
        # 簡易音声生成（短いテキストのみ）
        if st.button("🎵 簡易音声（短縮版）"):
            try:
                # より短いテキストで試行
                short_text = st.session_state.current_translation['translated'][:50] + "..."
                with st.spinner("簡易音声生成中..."):
                    mp3_fp, text_length = generate_audio(
                        short_text,
                        st.session_state.current_translation['tgt_lang']
                    )
                    
                    audio_data = mp3_fp.read()
                    st.success(f"✅ 簡易音声生成成功")
                    st.audio(audio_data, format='audio/mp3')
                    st.caption(f"📝 短縮テキスト: {short_text}")
                    
            except Exception as e:
                st.error(f"❌ 簡易音声も失敗: {str(e)}")
                show_audio_alternative(short_text, st.session_state.current_translation['tgt_lang'])

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
                            mp3_fp, text_length = generate_audio(item['original'], item['src_lang'])
                            audio_data = mp3_fp.read()
                            st.audio(audio_data, format='audio/mp3')
                            st.success(f"✅ 原文音声生成成功")
                    except Exception as e:
                        st.error(f"❌ 音声生成失敗")
                        show_audio_alternative(item['original'], item['src_lang'])
            
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
                            mp3_fp, text_length = generate_audio(item['translated'], item['tgt_lang'])
                            audio_data = mp3_fp.read()
                            st.audio(audio_data, format='audio/mp3')
                            st.success(f"✅ 翻訳音声生成成功")
                    except Exception as e:
                        st.error(f"❌ 音声生成失敗")
                        show_audio_alternative(item['translated'], item['tgt_lang'])

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
