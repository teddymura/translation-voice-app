from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import time
import re

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
        'horse': {'ja': '馬', 'fr': 'cheval', 'de': 'pferd', 'es': 'caballo', 'it': 'cavallo', 'ko': '말', 'zh': '马'},
        'cow': {'ja': '牛', 'fr': 'vache', 'de': 'kuh', 'es': 'vaca', 'it': 'mucca', 'ko': '소', 'zh': '牛'},
        
        # 食べ物・飲み物
        'water': {'ja': '水', 'fr': 'eau', 'de': 'wasser', 'es': 'agua', 'it': 'acqua', 'ko': '물', 'zh': '水'},
        'food': {'ja': '食べ物', 'fr': 'nourriture', 'de': 'essen', 'es': 'comida', 'it': 'cibo', 'ko': '음식', 'zh': '食物'},
        'bread': {'ja': 'パン', 'fr': 'pain', 'de': 'brot', 'es': 'pan', 'it': 'pane', 'ko': '빵', 'zh': '面包'},
        'rice': {'ja': '米', 'fr': 'riz', 'de': 'reis', 'es': 'arroz', 'it': 'riso', 'ko': '쌀', 'zh': '米饭'},
        'coffee': {'ja': 'コーヒー', 'fr': 'café', 'de': 'kaffee', 'es': 'café', 'it': 'caffè', 'ko': '커피', 'zh': '咖啡'},
        'tea': {'ja': '茶', 'fr': 'thé', 'de': 'tee', 'es': 'té', 'it': 'tè', 'ko': '차', 'zh': '茶'},
        'milk': {'ja': 'ミルク', 'fr': 'lait', 'de': 'milch', 'es': 'leche', 'it': 'latte', 'ko': '우유', 'zh': '牛奶'},
        'juice': {'ja': 'ジュース', 'fr': 'jus', 'de': 'saft', 'es': 'jugo', 'it': 'succo', 'ko': '주스', 'zh': '果汁'},
        
        # 家族・人間関係
        'family': {'ja': '家族', 'fr': 'famille', 'de': 'familie', 'es': 'familia', 'it': 'famiglia', 'ko': '가족', 'zh': '家庭'},
        'friend': {'ja': '友達', 'fr': 'ami', 'de': 'freund', 'es': 'amigo', 'it': 'amico', 'ko': '친구', 'zh': '朋友'},
        'mother': {'ja': '母', 'fr': 'mère', 'de': 'mutter', 'es': 'madre', 'it': 'madre', 'ko': '어머니', 'zh': '妈妈'},
        'father': {'ja': '父', 'fr': 'père', 'de': 'vater', 'es': 'padre', 'it': 'padre', 'ko': '아버지', 'zh': '爸爸'},
        'child': {'ja': '子供', 'fr': 'enfant', 'de': 'kind', 'es': 'niño', 'it': 'bambino', 'ko': '아이', 'zh': '孩子'},
        'brother': {'ja': '兄弟', 'fr': 'frère', 'de': 'bruder', 'es': 'hermano', 'it': 'fratello', 'ko': '형제', 'zh': '兄弟'},
        'sister': {'ja': '姉妹', 'fr': 'sœur', 'de': 'schwester', 'es': 'hermana', 'it': 'sorella', 'ko': '자매', 'zh': '姐妹'},
        
        # 場所・建物
        'house': {'ja': '家', 'fr': 'maison', 'de': 'haus', 'es': 'casa', 'it': 'casa', 'ko': '집', 'zh': '房子'},
        'school': {'ja': '学校', 'fr': 'école', 'de': 'schule', 'es': 'escuela', 'it': 'scuola', 'ko': '학교', 'zh': '学校'},
        'hospital': {'ja': '病院', 'fr': 'hôpital', 'de': 'krankenhaus', 'es': 'hospital', 'it': 'ospedale', 'ko': '병원', 'zh': '医院'},
        'store': {'ja': '店', 'fr': 'magasin', 'de': 'geschäft', 'es': 'tienda', 'it': 'negozio', 'ko': '상점', 'zh': '商店'},
        'park': {'ja': '公園', 'fr': 'parc', 'de': 'park', 'es': 'parque', 'it': 'parco', 'ko': '공원', 'zh': '公园'},
        'restaurant': {'ja': 'レストラン', 'fr': 'restaurant', 'de': 'restaurant', 'es': 'restaurante', 'it': 'ristorante', 'ko': '식당', 'zh': '餐厅'},
        'hotel': {'ja': 'ホテル', 'fr': 'hôtel', 'de': 'hotel', 'es': 'hotel', 'it': 'hotel', 'ko': '호텔', 'zh': '酒店'},
        
        # 時間・数字
        'time': {'ja': '時間', 'fr': 'temps', 'de': 'zeit', 'es': 'tiempo', 'it': 'tempo', 'ko': '시간', 'zh': '时间'},
        'today': {'ja': '今日', 'fr': 'aujourd\'hui', 'de': 'heute', 'es': 'hoy', 'it': 'oggi', 'ko': '오늘', 'zh': '今天'},
        'tomorrow': {'ja': '明日', 'fr': 'demain', 'de': 'morgen', 'es': 'mañana', 'it': 'domani', 'ko': '내일', 'zh': '明天'},
        'yesterday': {'ja': '昨日', 'fr': 'hier', 'de': 'gestern', 'es': 'ayer', 'it': 'ieri', 'ko': '어제', 'zh': '昨天'},
        'now': {'ja': '今', 'fr': 'maintenant', 'de': 'jetzt', 'es': 'ahora', 'it': 'ora', 'ko': '지금', 'zh': '现在'},
        'one': {'ja': '一', 'fr': 'un', 'de': 'eins', 'es': 'uno', 'it': 'uno', 'ko': '하나', 'zh': '一'},
        'two': {'ja': '二', 'fr': 'deux', 'de': 'zwei', 'es': 'dos', 'it': 'due', 'ko': '둘', 'zh': '二'},
        'three': {'ja': '三', 'fr': 'trois', 'de': 'drei', 'es': 'tres', 'it': 'tre', 'ko': '셋', 'zh': '三'},
        
        # 色
        'red': {'ja': '赤', 'fr': 'rouge', 'de': 'rot', 'es': 'rojo', 'it': 'rosso', 'ko': '빨간색', 'zh': '红色'},
        'blue': {'ja': '青', 'fr': 'bleu', 'de': 'blau', 'es': 'azul', 'it': 'blu', 'ko': '파란색', 'zh': '蓝色'},
        'green': {'ja': '緑', 'fr': 'vert', 'de': 'grün', 'es': 'verde', 'it': 'verde', 'ko': '초록색', 'zh': '绿色'},
        'yellow': {'ja': '黄色', 'fr': 'jaune', 'de': 'gelb', 'es': 'amarillo', 'it': 'giallo', 'ko': '노란색', 'zh': '黄色'},
        'black': {'ja': '黒', 'fr': 'noir', 'de': 'schwarz', 'es': 'negro', 'it': 'nero', 'ko': '검은색', 'zh': '黑色'},
        'white': {'ja': '白', 'fr': 'blanc', 'de': 'weiß', 'es': 'blanco', 'it': 'bianco', 'ko': '흰색', 'zh': '白色'},
        
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
        'i am fine': {'ja': '元気です', 'fr': 'je vais bien', 'de': 'mir geht es gut', 'es': 'estoy bien', 'it': 'sto bene', 'ko': '잘 지내요', 'zh': '我很好'},
        'see you later': {'ja': 'また後で', 'fr': 'à plus tard', 'de': 'bis später', 'es': 'hasta luego', 'it': 'a dopo', 'ko': '나중에 봐요', 'zh': '回头见'},
        'nice to meet you': {'ja': 'はじめまして', 'fr': 'ravi de vous rencontrer', 'de': 'freut mich', 'es': 'mucho gusto', 'it': 'piacere di conoscerti', 'ko': '만나서 반가워요', 'zh': '很高兴认识你'}
    },
    'ja': {
        # 基本的な単語・フレーズを逆引きで追加
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
        '元気ですか': {'en': 'how are you', 'fr': 'comment allez-vous', 'de': 'wie geht es ihnen', 'es': '¿cómo estás?', 'it': 'come stai', 'ko': '어떻게 지내세요', 'zh': '你好吗'},
        # 色
        '赤': {'en': 'red', 'fr': 'rouge', 'de': 'rot', 'es': 'rojo', 'it': 'rosso', 'ko': '빨간색', 'zh': '红色'},
        '青': {'en': 'blue', 'fr': 'bleu', 'de': 'blau', 'es': 'azul', 'it': 'blu', 'ko': '파란색', 'zh': '蓝色'},
        '緑': {'en': 'green', 'fr': 'vert', 'de': 'grün', 'es': 'verde', 'it': 'verde', 'ko': '초록색', 'zh': '绿色'},
        '食べ物': {'en': 'food', 'fr': 'nourriture', 'de': 'essen', 'es': 'comida', 'it': 'cibo', 'ko': '음식', 'zh': '食物'},
        'お金': {'en': 'money', 'fr': 'argent', 'de': 'geld', 'es': 'dinero', 'it': 'denaro', 'ko': '돈', 'zh': '钱'},
        '仕事': {'en': 'work', 'fr': 'travail', 'de': 'arbeit', 'es': 'trabajo', 'it': 'lavoro', 'ko': '일', 'zh': '工作'}
    }
}

# API状態管理
API_STATUS = {
    'available': False,
    'last_check': None,
    'error_count': 0
}

def get_history():
    """セッションから履歴を取得"""
    return session.get('translation_history', [])

def add_to_history(original, translated, service):
    """履歴に新しい翻訳結果を追加"""
    history = get_history()
    
    # 重複チェック
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
    history = history[:15]  # 履歴数を15に増加
    
    session['translation_history'] = history
    session.permanent = True

def check_api_availability():
    """API利用可能性をチェック"""
    try:
        from deep_translator import GoogleTranslator
        # 簡単なテスト翻訳を実行
        translator = GoogleTranslator(source='en', target='ja')
        test_result = translator.translate('test')
        
        if test_result and test_result != 'test':
            API_STATUS['available'] = True
            API_STATUS['error_count'] = 0
            return True
    except Exception as e:
        API_STATUS['error_count'] += 1
        print(f"API利用不可: {e}")
    
    API_STATUS['available'] = False
    API_STATUS['last_check'] = datetime.now()
    return False

def try_api_translation(text, target_lang):
    """改良されたAPI翻訳"""
    # エラーが多すぎる場合はスキップ
    if API_STATUS['error_count'] > 3:
        return None, None
    
    try:
        from deep_translator import GoogleTranslator
        time.sleep(0.3)  # レート制限対策を強化
        
        # 言語自動検出で翻訳
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        
        if result and result.strip() and result.lower() != text.lower():
            API_STATUS['available'] = True
            API_STATUS['error_count'] = 0
            return result, "Google Translate API"
        else:
            return None, None
            
    except ImportError:
        print("deep-translator が見つかりません")
        return None, None
    except Exception as e:
        API_STATUS['error_count'] += 1
        print(f"API翻訳エラー: {e}")
        return None, None

def enhanced_offline_translate(text, target_lang):
    """強化されたオフライン辞書翻訳"""
    text_lower = text.lower().strip()
    original_text = text.strip()
    
    # 1. 完全一致を優先（英語）
    if text_lower in TRANSLATION_DICT.get('en', {}):
        translation = TRANSLATION_DICT['en'][text_lower].get(target_lang)
        if translation:
            return translation, "Dictionary (EN→" + target_lang.upper() + ")"
    
    # 2. 完全一致を優先（日本語）
    if original_text in TRANSLATION_DICT.get('ja', {}):
        translation = TRANSLATION_DICT['ja'][original_text].get(target_lang)
        if translation:
            return translation, "Dictionary (JA→" + target_lang.upper() + ")"
    
    # 3. 部分マッチ（フレーズ内の単語検索）
    best_matches = []
    
    # 英語の部分マッチ
    for key, translations in TRANSLATION_DICT.get('en', {}).items():
        if key in text_lower:
            translation = translations.get(target_lang)
            if translation:
                confidence = len(key) / len(text_lower)  # マッチ度合い
                best_matches.append((key, translation, confidence, 'en'))
    
    # 日本語の部分マッチ
    for key, translations in TRANSLATION_DICT.get('ja', {}).items():
        if key in original_text:
            translation = translations.get(target_lang)
            if translation:
                confidence = len(key) / len(original_text)
                best_matches.append((key, translation, confidence, 'ja'))
    
    # 最も信頼度の高いマッチを選択
    if best_matches:
        best_matches.sort(key=lambda x: x[2], reverse=True)
        best_match = best_matches[0]
        
        if best_match[2] > 0.8:  # 高信頼度
            return best_match[1], f"Dictionary ({best_match[3].upper()}→{target_lang.upper()}) - 高精度マッチ"
        elif best_match[2] > 0.3:  # 中信頼度
            return f"[{best_match[1]}] を含む可能性があります", f"Dictionary ({best_match[3].upper()}→{target_lang.upper()}) - 部分マッチ"
    
    # 4. 単語分割マッチ（スペースまたは句読点で区切り）
    words = re.split(r'[\s\.,;:!?]+', text_lower)
    words = [w for w in words if w]  # 空文字を除去
    
    if len(words) > 1:
        translations = []
        found_translations = 0
        
        for word in words:
            if word in TRANSLATION_DICT.get('en', {}):
                trans = TRANSLATION_DICT['en'][word].get(target_lang)
                if trans:
                    translations.append(trans)
                    found_translations += 1
                else:
                    translations.append(f"[{word}]")
            else:
                translations.append(f"[{word}]")
        
        # 少なくとも半分の単語が翻訳できた場合
        if found_translations >= len(words) * 0.5:
            return " ".join(translations), f"Dictionary (EN→{target_lang.upper()}) - 単語別翻訳 ({found_translations}/{len(words)} 単語)"
    
    return None, None

def smart_translate(text, target_lang):
    """改良されたスマート翻訳システム"""
    
    # 1. まずAPI翻訳を試行（エラーが少ない場合のみ）
    if API_STATUS['error_count'] < 3:
        api_result, api_service = try_api_translation(text, target_lang)
        if api_result:
            return api_result, api_service
    
    # 2. APIが失敗したら強化された辞書翻訳
    dict_result, dict_service = enhanced_offline_translate(text, target_lang)
    if dict_result:
        status_msg = " (API利用不可)" if API_STATUS['error_count'] >= 3 else " (API失敗)"
        return dict_result, dict_service + status_msg
    
    # 3. どちらも失敗
    return None, None

def get_language_stats():
    """辞書内の言語統計を取得"""
    stats = {}
    for source_lang, translations in TRANSLATION_DICT.items():
        stats[source_lang] = len(translations)
    return stats

@app.route("/", methods=["GET"])
def index():
    """メインページ表示"""
    lang_stats = get_language_stats()
    total_words = sum(lang_stats.values())
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>翻訳アプリ (改良版ハイブリッド)</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .main-container {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #333;
                margin: 0;
                font-size: 2.5em;
            }}
            .stats {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
                border-left: 4px solid #007bff;
            }}
            .container {{ 
                background: #f9f9f9; 
                padding: 25px; 
                border-radius: 12px; 
                margin-bottom: 25px; 
                border: 1px solid #e0e0e0;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            input, select, button {{ 
                padding: 12px; 
                margin: 5px; 
                border: 2px solid #ddd; 
                border-radius: 8px; 
                font-size: 16px;
                transition: all 0.3s ease;
            }}
            input[type="text"] {{ 
                width: 400px; 
                max-width: 100%;
            }}
            input[type="text"]:focus {{
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
            }}
            button {{ 
                background: linear-gradient(135deg, #007bff, #0056b3); 
                color: white; 
                cursor: pointer; 
                font-weight: bold;
                min-width: 100px;
            }}
            button:hover {{ 
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,123,255,0.3);
            }}
            .result {{ 
                background: #e9f7ef; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 15px 0; 
                border-left: 4px solid #28a745;
            }}
            .result.api {{ 
                background: #e3f2fd; 
                border-left-color: #2196f3;
            }}
            .result.dictionary {{ 
                background: #fff3e0; 
                border-left-color: #ff9800;
            }}
            .history {{ 
                background: #fff; 
                padding: 20px; 
                border-radius: 10px; 
                border: 2px solid #ddd; 
            }}
            .history-item {{ 
                border-bottom: 1px solid #eee; 
                padding: 15px 0; 
                transition: background-color 0.2s;
            }}
            .history-item:hover {{
                background-color: #f8f9fa;
            }}
            .history-item:last-child {{ 
                border-bottom: none; 
            }}
            .service-info {{ 
                font-size: 0.85em; 
                color: #666; 
                margin-top: 8px; 
                font-style: italic;
            }}
            .info {{ 
                background: linear-gradient(135deg, #d4edda, #c3e6cb); 
                border: 1px solid #c3e6cb; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 15px 0; 
            }}
            .status {{ 
                text-align: center; 
                margin: 15px 0; 
                font-weight: bold; 
                min-height: 24px;
            }}
            .loading {{ 
                color: #007bff; 
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            .clear-btn {{
                background: linear-gradient(135deg, #dc3545, #c82333);
                font-size: 14px;
                padding: 8px 16px;
            }}
            .supported-langs {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 15px;
            }}
            .lang-tag {{
                background: #007bff;
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            @media (max-width: 768px) {{
                body {{ padding: 10px; }}
                .main-container {{ padding: 20px; }}
                input[type="text"] {{ width: 100%; }}
                .header h1 {{ font-size: 2em; }}
            }}
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="header">
                <h1>🌐 翻訳アプリ</h1>
                <p>ハイブリッド翻訳システム (改良版)</p>
            </div>
            
            <div class="stats">
                <strong>📊 辞書統計:</strong> 
                英語→多言語: {lang_stats.get('en', 0)} 単語 | 
                日本語→多言語: {lang_stats.get('ja', 0)} 単語 | 
                合計: {total_words} エントリ
                <div class="supported-langs">
                    <div class="lang-tag">English</div>
                    <div class="lang-tag">日本語</div>
                    <div class="lang-tag">Français</div>
                    <div class="lang-tag">Deutsch</div>
                    <div class="lang-tag">Español</div>
                    <div class="lang-tag">Italiano</div>
                    <div class="lang-tag">한국어</div>
                    <div class="lang-tag">中文</div>
                </div>
            </div>
            
            <div class="info">
                <strong>🚀 翻訳システムの特徴</strong><br>
                ✅ Google翻訳API優先実行 (利用可能時)<br>
                ✅ {total_words}+ 語の多言語辞書でバックアップ<br>
                ✅ 部分マッチ・単語分割で高精度翻訳<br>
                ✅ 翻訳履歴15件まで保存<br>
                → APIが使えない時でも安心して翻訳できます！
            </div>
            
            <div class="container">
                <h3>🔧 API接続テスト</h3>
                <p>Google翻訳APIが利用可能かテストできます</p>
                <button onclick="testAPI()" style="background: linear-gradient(135deg, #28a745, #20c997);">
                    🧪 API接続テスト実行
                </button>
                <div id="apiTestResult"></div>
            </div>
            
            <div class="container">
                <h3>✨ 翻訳する</h3>
                <form id="translateForm">
                    <div class="form-group">
                        <input type="text" id="textInput" placeholder="翻訳したいテキストを入力 (単語・文・フレーズ何でもOK)" required>
                    </div>
                    <div class="form-group">
                        <select id="langSelect">
                            <option value="en">🇺🇸 English</option>
                            <option value="ja" selected>🇯🇵 日本語</option>
                            <option value="fr">🇫🇷 Français</option>
                            <option value="de">🇩🇪 Deutsch</option>
                            <option value="es">🇪🇸 Español</option>
                            <option value="it">🇮🇹 Italiano</option>
                            <option value="ko">🇰🇷 한국어</option>
                            <option value="zh">🇨🇳 中文</option>
                        </select>
                        <button type="submit">🔄 翻訳</button>
                    </div>
                </form>
                <div id="status" class="status"></div>
                <div id="result"></div>
            </div>

            <div class="history">
                <h3>📚 翻訳履歴 (最新15件)</h3>
                <div id="historyList">履歴を読み込み中...</div>
                <button class="clear-btn" onclick="clearHistory()">🗑️ 履歴をクリア</button>
            </div>
        </div>
        
        <script>
        document.getElementById('translateForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const text = document.getElementById('textInput').value;
            const lang = document.getElementById('langSelect').value;
            
            document.getElementById('status').innerHTML = '<span class="loading">🔄 翻訳処理中... (API → 辞書の順で実行)</span>';
            document.getElementById('result').innerHTML = '';
            
            fetch('/translate', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded',
                }},
                body: 'text=' + encodeURIComponent(text) + '&lang=' + lang
            }})
            .then(response => response.json())
            .then(data => {{
                document.getElementById('status').innerHTML = '';
                
                if (data.error) {{
                    document.getElementById('result').innerHTML = 
                        '<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">' +
                        '<strong>❌ エラー:</strong> ' + data.error + '</div>';
                }} else {{
                    let resultClass = 'result';
                    let serviceIcon = '🔧';
                    
                    if (data.service.includes('API')) {{
                        resultClass += ' api';
                        serviceIcon = '🌐';
                    }} else if (data.service.includes('Dictionary')) {{
                        resultClass += ' dictionary';
                        serviceIcon = '📖';
                    }}
                    
                    document.getElementById('result').innerHTML = 
                        '<div class="' + resultClass + '">' +
                        '<h4>✨ 翻訳結果:</h4>' +
                        '<p style="font-size: 1.3em; font-weight: bold; color: #2c3e50;">' + data.translated + '</p>' +
                        '<div class="service-info">' + serviceIcon + ' ' + data.service + '</div>' +
                        '</div>';
                    
                    // 入力欄をクリア
                    document.getElementById('textInput').value = '';
                    document.getElementById('textInput').focus();
                    
                    loadHistory();
                }}
            }})
            .catch(error => {{
                document.getElementById('status').innerHTML = '';
                document.getElementById('result').innerHTML = 
                    '<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px;">' +
                    '<strong>⚠️ 通信エラー:</strong> サーバーとの通信に失敗しました</div>';
                console.error('Error:', error);
            }});
        }});

        function loadHistory() {{
            fetch('/get_history')
            .then(response => response.json())
            .then(data => {{
                const historyList = document.getElementById('historyList');
                if (data.history.length === 0) {{
                    historyList.innerHTML = '<p style="text-align: center; color: #6c757d; font-style: italic;">📝 履歴がありません</p>';
                }} else {{
                    historyList.innerHTML = data.history.map((item, index) => 
                        '<div class="history-item">' +
                        '<div style="display: flex; align-items: center; margin-bottom: 5px;">' +
                        '<span style="background: #007bff; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 10px;">' + (index + 1) + '</span>' +
                        '<strong style="color: #495057;">原文:</strong>' +
                        '</div>' +
                        '<p style="margin: 5px 0 5px 34px; font-size: 16px;">' + item.original + '</p>' +
                        '<strong style="color: #495057; margin-left: 34px;">翻訳:</strong>' +
                        '<p style="margin: 5px 0 10px 34px; font-size: 16px; color: #2c3e50; font-weight: bold;">' + item.translated + '</p>' +
                        '<div class="service-info" style="margin-left: 34px;">🔧 ' + item.service + '</div>' +
                        '</div>'
                    ).join('');
                }}
            }})
            .catch(error => {{
                console.error('履歴読み込みエラー:', error);
                document.getElementById('historyList').innerHTML = 
                    '<p style="color: #dc3545;">❌ 履歴の読み込みに失敗しました</p>';
            }});
        }}

        function clearHistory() {{
            if (confirm('翻訳履歴をすべて削除しますか？')) {{
                fetch('/clear_history', {{
                    method: 'POST'
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        loadHistory();
                    }}
                }})
                .catch(error => {{
                    console.error('履歴クリアエラー:', error);
                    alert('履歴のクリアに失敗しました');
                }});
            }}
        }}

        function testAPI() {
            document.getElementById('apiTestResult').innerHTML = 
                '<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">' +
                '<span class="loading">🔄 API接続テスト中...</span></div>';
            
            fetch('/test_api')
            .then(response => response.json())
            .then(data => {
                let resultHTML = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid ';
                
                if (data.api_available) {
                    resultHTML += '#28a745;"><h4 style="color: #155724;">🎉 API接続テスト結果</h4>';
                } else {
                    resultHTML += '#dc3545;"><h4 style="color: #721c24;">⚠️ API接続テスト結果</h4>';
                }
                
                Object.keys(data).forEach(key => {
                    if (key !== 'api_available') {
                        resultHTML += '<p><strong>' + key + ':</strong> ' + data[key] + '</p>';
                    }
                });
                
                resultHTML += '</div>';
                document.getElementById('apiTestResult').innerHTML = resultHTML;
            })
            .catch(error => {
                document.getElementById('apiTestResult').innerHTML = 
                    '<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin-top: 15px;">' +
                    '<strong>❌ テストエラー:</strong> ' + error + '</div>';
            });
        }

        // 初期化
        loadHistory();
        document.getElementById('textInput').focus();
        
        // Enterキーで翻訳実行
        document.getElementById('textInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                document.getElementById('translateForm').dispatchEvent(new Event('submit'));
            }}
        }});
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
    """Ajax用の翻訳エンドポイント（改良版）"""
    try:
        target_lang = request.form.get("lang", "en")
        text = request.form.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "テキストが入力されていません"}), 400
        
        if len(text) > 500:  # 文字数制限
            return jsonify({"error": "テキストが長すぎます（500文字以内で入力してください）"}), 400
        
        # スマート翻訳を実行
        translated_text, service = smart_translate(text, target_lang)
        
        if not translated_text:
            return jsonify({
                "error": f"「{text}」を翻訳できませんでした。\n" +
                        "・APIが利用できない状態です\n" +
                        "・辞書にも登録されていません\n" +
                        "・より簡単な単語やフレーズでお試しください"
            }), 404
        
        # 履歴に追加
        add_to_history(text, translated_text, service)
        
        return jsonify({
            "translated": translated_text,
            "service": service,
            "api_status": API_STATUS
        })
        
    except Exception as e:
        print(f"翻訳エラー: {e}")
        return jsonify({"error": "翻訳処理中にエラーが発生しました。しばらくしてからお試しください。"}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """履歴をクリア"""
    try:
        session['translation_history'] = []
        return jsonify({"success": True})
    except Exception as e:
        print(f"履歴クリアエラー: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api_status")
def api_status():
    """API状態確認エンドポイント"""
    return jsonify(API_STATUS)

@app.route("/test_api")
def test_api():
    """API接続テスト用エンドポイント"""
    test_results = {}
    
    # 1. deep-translatorのインポートテスト
    try:
        from deep_translator import GoogleTranslator
        test_results['import_status'] = '✅ ライブラリ正常'
    except ImportError as e:
        test_results['import_status'] = f'❌ インポートエラー: {e}'
        return jsonify(test_results)
    
    # 2. 簡単な翻訳テスト
    try:
        translator = GoogleTranslator(source='en', target='ja')
        result = translator.translate('hello')
        if result and result != 'hello':
            test_results['translation_test'] = f'✅ 翻訳成功: hello → {result}'
            test_results['api_available'] = True
        else:
            test_results['translation_test'] = '⚠️ 翻訳結果が不正'
            test_results['api_available'] = False
    except Exception as e:
        test_results['translation_test'] = f'❌ 翻訳エラー: {str(e)}'
        test_results['api_available'] = False
    
    # 3. 接続環境情報
    import socket
    import os
    try:
        hostname = socket.gethostname()
        test_results['hostname'] = hostname
        test_results['environment'] = os.environ.get('RENDER', 'ローカル環境')
    except:
        pass
    
    return jsonify(test_results)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
