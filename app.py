from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# 拡張翻訳辞書（フォールバック用）
TRANSLATION_DICT = {
    'en': {
        # 基本挨拶・返事
        'hello': {'ja': 'こんにちは', 'fr': 'bonjour', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕하세요', 'zh': '你好'},
        'hi': {'ja': 'やあ', 'fr': 'salut', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕', 'zh': '嗨'},
        'thank you': {'ja': 'ありがとう', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '감사합니다', 'zh': '谢谢'},
        'thanks': {'ja': 'ありがとう', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '고마워', 'zh': '谢谢'},
        'good morning': {'ja': 'おはよう', 'fr': 'bonjour', 'de': 'guten morgen', 'es': 'buenos días', 'it': 'buongiorno', 'ko': '좋은 아침', 'zh': '早上好'},
        'good night': {'ja': 'おやすみ', 'fr': 'bonne nuit', 'de': 'gute nacht', 'es': 'buenas noches', 'it': 'buonanotte', 'ko': '좋은 밤', 'zh': '晚安'},
        'goodbye': {'ja': 'さよなら', 'fr': 'au revoir', 'de': 'auf wiedersehen', 'es': 'adiós', 'it': 'arrivederci', 'ko': '안녕히 가세요', 'zh': '再见'},
        'bye': {'ja': 'バイバイ', 'fr': 'salut', 'de': 'tschüss', 'es': 'adiós', 'it': 'ciao', 'ko': '바이', 'zh': '拜拜'},
        'yes': {'ja': 'はい', 'fr': 'oui', 'de': 'ja', 'es': 'sí', 'it': 'sì', 'ko': '네', 'zh': '是'},
        'no': {'ja': 'いいえ', 'fr': 'non', 'de': 'nein', 'es': 'no', 'it': 'no', 'ko': '아니요', 'zh': '不'},
        'please': {'ja': 'お願いします', 'fr': 's\'il vous plaît', 'de': 'bitte', 'es': 'por favor', 'it': 'per favore', 'ko': '제발', 'zh': '请'},
        'sorry': {'ja': 'すみません', 'fr': 'désolé', 'de': 'entschuldigung', 'es': 'lo siento', 'it': 'scusa', 'ko': '미안해요', 'zh': '对不起'},
        'excuse me': {'ja': 'すみません', 'fr': 'excusez-moi', 'de': 'entschuldigen sie', 'es': 'disculpe', 'it': 'mi scusi', 'ko': '실례합니다', 'zh': '打扰一下'},
        
        # 感情・感覚
        'love': {'ja': '愛', 'fr': 'amour', 'de': 'liebe', 'es': 'amor', 'it': 'amore', 'ko': '사랑', 'zh': '爱'},
        'like': {'ja': '好き', 'fr': 'aimer', 'de': 'mögen', 'es': 'gustar', 'it': 'piacere', 'ko': '좋아하다', 'zh': '喜欢'},
        'happy': {'ja': '幸せ', 'fr': 'heureux', 'de': 'glücklich', 'es': 'feliz', 'it': 'felice', 'ko': '행복한', 'zh': '快乐'},
        'sad': {'ja': '悲しい', 'fr': 'triste', 'de': 'traurig', 'es': 'triste', 'it': 'triste', 'ko': '슬픈', 'zh': '伤心'},
        'angry': {'ja': '怒り', 'fr': 'en colère', 'de': 'wütend', 'es': 'enojado', 'it': 'arrabbiato', 'ko': '화난', 'zh': '愤怒'},
        'tired': {'ja': '疲れた', 'fr': 'fatigué', 'de': 'müde', 'es': 'cansado', 'it': 'stanco', 'ko': '피곤한', 'zh': '累'},
        'beautiful': {'ja': '美しい', 'fr': 'beau', 'de': 'schön', 'es': 'hermoso', 'it': 'bello', 'ko': '아름다운', 'zh': '美丽'},
        'good': {'ja': 'いい', 'fr': 'bon', 'de': 'gut', 'es': 'bueno', 'it': 'buono', 'ko': '좋은', 'zh': '好'},
        'bad': {'ja': '悪い', 'fr': 'mauvais', 'de': 'schlecht', 'es': 'malo', 'it': 'cattivo', 'ko': '나쁜', 'zh': '坏'},
        
        # 動物
        'cat': {'ja': '猫', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'},
        'dog': {'ja': '犬', 'fr': 'chien', 'de': 'hund', 'es': 'perro', 'it': 'cane', 'ko': '개', 'zh': '狗'},
        'bird': {'ja': '鳥', 'fr': 'oiseau', 'de': 'vogel', 'es': 'pájaro', 'it': 'uccello', 'ko': '새', 'zh': '鸟'},
        'fish': {'ja': '魚', 'fr': 'poisson', 'de': 'fisch', 'es': 'pez', 'it': 'pesce', 'ko': '물고기', 'zh': '鱼'},
        
        # 食べ物・飲み物
        'water': {'ja': '水', 'fr': 'eau', 'de': 'wasser', 'es': 'agua', 'it': 'acqua', 'ko': '물', 'zh': '水'},
        'food': {'ja': '食べ物', 'fr': 'nourriture', 'de': 'essen', 'es': 'comida', 'it': 'cibo', 'ko': '음식', 'zh': '食物'},
        'bread': {'ja': 'パン', 'fr': 'pain', 'de': 'brot', 'es': 'pan', 'it': 'pane', 'ko': '빵', 'zh': '面包'},
        'rice': {'ja': '米', 'fr': 'riz', 'de': 'reis', 'es': 'arroz', 'it': 'riso', 'ko': '쌀', 'zh': '米饭'},
        'coffee': {'ja': 'コーヒー', 'fr': 'café', 'de': 'kaffee', 'es': 'café', 'it': 'caffè', 'ko': '커피', 'zh': '咖啡'},
        'tea': {'ja': '茶', 'fr': 'thé', 'de': 'tee', 'es': 'té', 'it': 'tè', 'ko': '차', 'zh': '茶'},
        
        # 家族・人間関係
        'family': {'ja': '家族', 'fr': 'famille', 'de': 'familie', 'es': 'familia', 'it': 'famiglia', 'ko': '가족', 'zh': '家庭'},
        'friend': {'ja': '友達', 'fr': 'ami', 'de': 'freund', 'es': 'amigo', 'it': 'amico', 'ko': '친구', 'zh': '朋友'},
        'mother': {'ja': '母', 'fr': 'mère', 'de': 'mutter', 'es': 'madre', 'it': 'madre', 'ko': '어머니', 'zh': '妈妈'},
        'father': {'ja': '父', 'fr': 'père', 'de': 'vater', 'es': 'padre', 'it': 'padre', 'ko': '아버지', 'zh': '爸爸'},
        'child': {'ja': '子供', 'fr': 'enfant', 'de': 'kind', 'es': 'niño', 'it': 'bambino', 'ko': '아이', 'zh': '孩子'},
        
        # 場所・建物
        'house': {'ja': '家', 'fr': 'maison', 'de': 'haus', 'es': 'casa', 'it': 'casa', 'ko': '집', 'zh': '房子'},
        'school': {'ja': '学校', 'fr': 'école', 'de': 'schule', 'es': 'escuela', 'it': 'scuola', 'ko': '학교', 'zh': '学校'},
        'hospital': {'ja': '病院', 'fr': 'hôpital', 'de': 'krankenhaus', 'es': 'hospital', 'it': 'ospedale', 'ko': '병원', 'zh': '医院'},
        'store': {'ja': '店', 'fr': 'magasin', 'de': 'geschäft', 'es': 'tienda', 'it': 'negozio', 'ko': '상점', 'zh': '商店'},
        'park': {'ja': '公園', 'fr': 'parc', 'de': 'park', 'es': 'parque', 'it': 'parco', 'ko': '공원', 'zh': '公园'},
        
        # 時間・数字
        'time': {'ja': '時間', 'fr': 'temps', 'de': 'zeit', 'es': 'tiempo', 'it': 'tempo', 'ko': '시간', 'zh': '时间'},
        'today': {'ja': '今日', 'fr': 'aujourd\'hui', 'de': 'heute', 'es': 'hoy', 'it': 'oggi', 'ko': '오늘', 'zh': '今天'},
        'tomorrow': {'ja': '明日', 'fr': 'demain', 'de': 'morgen', 'es': 'mañana', 'it': 'domani', 'ko': '내일', 'zh': '明天'},
        'yesterday': {'ja': '昨日', 'fr': 'hier', 'de': 'gestern', 'es': 'ayer', 'it': 'ieri', 'ko': '어제', 'zh': '昨天'},
        'one': {'ja': '一', 'fr': 'un', 'de': 'eins', 'es': 'uno', 'it': 'uno', 'ko': '하나', 'zh': '一'},
        'two': {'ja': '二', 'fr': 'deux', 'de': 'zwei', 'es': 'dos', 'it': 'due', 'ko': '둘', 'zh': '二'},
        
        # 抽象概念
        'money': {'ja': 'お金', 'fr': 'argent', 'de': 'geld', 'es': 'dinero', 'it': 'denaro', 'ko': '돈', 'zh': '钱'},
        'work': {'ja': '仕事', 'fr': 'travail', 'de': 'arbeit', 'es': 'trabajo', 'it': 'lavoro', 'ko': '일', 'zh': '工作'},
        'study': {'ja': '勉強', 'fr': 'étude', 'de': 'studium', 'es': 'estudio', 'it': 'studio', 'ko': '공부', 'zh': '学习'},
        'help': {'ja': '助け', 'fr': 'aide', 'de': 'hilfe', 'es': 'ayuda', 'it': 'aiuto', 'ko': '도움', 'zh': '帮助'},
        'problem': {'ja': '問題', 'fr': 'problème', 'de': 'problem', 'es': 'problema', 'it': 'problema', 'ko': '문제', 'zh': '问题'},
        
        # よく使う文
        'i love you': {'ja': '愛してる', 'fr': 'je t\'aime', 'de': 'ich liebe dich', 'es': 'te amo', 'it': 'ti amo', 'ko': '사랑해', 'zh': '我爱你'},
        'how are you': {'ja': '元気ですか', 'fr': 'comment allez-vous', 'de': 'wie geht es ihnen', 'es': '¿cómo estás?', 'it': 'come stai', 'ko': '어떻게 지내세요', 'zh': '你好吗'},
        'what is your name': {'ja': '名前は何ですか', 'fr': 'comment vous appelez-vous', 'de': 'wie heißen sie', 'es': '¿cómo te llamas?', 'it': 'come ti chiami', 'ko': '이름이 뭐예요', 'zh': '你叫什么名字'},
        'i am fine': {'ja': '元気です', 'fr': 'je vais bien', 'de': 'mir geht es gut', 'es': 'estoy bien', 'it': 'sto bene', 'ko': '잘 지내요', 'zh': '我很好'}
    },
    'ja': {
        'こんにちは': {'en': 'hello', 'fr': 'bonjour', 'de': 'hallo', 'es': 'hola', 'it': 'ciao', 'ko': '안녕하세요', 'zh': '你好'},
        'ありがとう': {'en': 'thank you', 'fr': 'merci', 'de': 'danke', 'es': 'gracias', 'it': 'grazie', 'ko': '감사합니다', 'zh': '谢谢'},
        'おはよう': {'en': 'good morning', 'fr': 'bonjour', 'de': 'guten morgen', 'es': 'buenos días', 'it': 'buongiorno', 'ko': '좋은 아침', 'zh': '早上好'},
        'おやすみ': {'en': 'good night', 'fr': 'bonne nuit', 'de': 'gute nacht', 'es': 'buenas noches', 'it': 'buonanotte', 'ko': '좋은 밤', 'zh': '晚安'},
        'さようなら': {'en': 'goodbye', 'fr': 'au revoir', 'de': 'auf wiedersehen', 'es': 'adiós', 'it': 'arrivederci', 'ko': '안녕히 가세요', 'zh': '再见'},
        'はい': {'en': 'yes', 'fr': 'oui', 'de': 'ja', 'es': 'sí', 'it': 'sì', 'ko': '네', 'zh': '是'},
        'いいえ': {'en': 'no', 'fr': 'non', 'de': 'nein', 'es': 'no', 'it': 'no', 'ko': '아니요', 'zh': '不'},
        'すみません': {'en': 'sorry', 'fr': 'désolé', 'de': 'entschuldigung', 'es': 'lo siento', 'it': 'scusa', 'ko': '미안해요', 'zh': '对不起'},
        '愛': {'en': 'love', 'fr': 'amour', 'de': 'liebe', 'es': 'amor', 'it': 'amore', 'ko': '사랑', 'zh': '爱'},
        '猫': {'en': 'cat', 'fr': 'chat', 'de': 'katze', 'es': 'gato', 'it': 'gatto', 'ko': '고양이', 'zh': '猫'},
        '犬': {'en': 'dog', 'fr': 'chien', 'de': 'hund', 'es': 'perro', 'it': 'cane', 'ko': '개', 'zh': '狗'},
        '水': {'en': 'water', 'fr': 'eau', 'de': 'wasser', 'es': 'agua', 'it': 'acqua', 'ko': '물', 'zh': '水'},
        '家': {'en': 'house', 'fr': 'maison', 'de': 'haus', 'es': 'casa', 'it': 'casa', 'ko': '집', 'zh': '房子'},
        '学校': {'en': 'school', 'fr': 'école', 'de': 'schule', 'es': 'escuela', 'it': 'scuola', 'ko': '학교', 'zh': '学校'},
        '友達': {'en': 'friend', 'fr': 'ami', 'de': 'freund', 'es': 'amigo', 'it': 'amico', 'ko': '친구', 'zh': '朋友'},
        '時間': {'en': 'time', 'fr': 'temps', 'de': 'zeit', 'es': 'tiempo', 'it': 'tempo', 'ko': '시간', 'zh': '时间'},
        '今日': {'en': 'today', 'fr': 'aujourd\'hui', 'de': 'heute', 'es': 'hoy', 'it': 'oggi', 'ko': '오늘', 'zh': '今天'},
        '明日': {'en': 'tomorrow', 'fr': 'demain', 'de': 'morgen', 'es': 'mañana', 'it': 'domani', 'ko': '내일', 'zh': '明天'},
        '愛してる': {'en': 'i love you', 'fr': 'je t\'aime', 'de': 'ich liebe dich', 'es': 'te amo', 'it': 'ti amo', 'ko': '사랑해', 'zh': '我爱你'},
        '元気ですか': {'en': 'how are you', 'fr': 'comment allez-vous', 'de': 'wie geht es ihnen', 'es': '¿cómo estás?', 'it': 'come stai', 'ko': '어떻게 지내세요', 'zh': '你好吗'}
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
    """改良されたオフライン辞書翻訳"""
    text_lower = text.lower().strip()
    
    # 完全一致を優先
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
    
    # 部分マッチ（単語を含む場合）
    for lang in ['en', 'ja']:
        for key, translations in TRANSLATION_DICT.get(lang, {}).items():
            # 入力テキストに辞書の単語が含まれる場合
            if key in text_lower or (lang == 'ja' and key in text):
                translation = translations.get(target_lang)
                if translation:
                    return f"[{translation}]が含まれています", f"Dictionary ({lang.upper()}→{target_lang.upper()}) - 部分マッチ"
    
    # 単語分割マッチ（スペースで区切られた場合）
    words = text_lower.split()
    if len(words) > 1:
        translations = []
        for word in words:
            if word in TRANSLATION_DICT.get('en', {}):
                trans = TRANSLATION_DICT['en'][word].get(target_lang)
                if trans:
                    translations.append(trans)
                else:
                    translations.append(f"[{word}]")
            else:
                translations.append(f"[{word}]")
        
        if len(translations) > 0 and any('[' not in t for t in translations):
            return " ".join(translations), f"Dictionary (EN→{target_lang.upper()}) - 単語別翻訳"
    
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
