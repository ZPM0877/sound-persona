import streamlit as st
import google.generativeai as genai
import re
import os
import urllib.parse  # Twitterシェア用に必要

# ==========================================
# ⚙️ 設定エリア（ここだけ書き換えてください）
# ==========================================

# ★重要★
# アプリを一度「Run」して、右上の「新しいタブで開く」を押したときのURLをここに貼ってください。
# (例: "https://sound-persona-username.replit.app")
# これがないと、Twitterからアプリに戻ってこれません！
YOUR_APP_URL = "https://あなたのアプリのURL.replit.app"

# ==========================================
# 🎧 ページ設定 & デザイン
# ==========================================
st.set_page_config(
    page_title="Sound Persona",
    page_icon="🎧",
    layout="centered"
)

# カスタムCSS（見た目を整える）
st.markdown("""
<style>
    .stTextInput > label {font-size:105%; font-weight:bold; color:#4a4a4a;}
    .stTextArea > label {font-size:105%; font-weight:bold; color:#4a4a4a;}
    .reportview-container {background: #f0f2f6;}
    .big-font {font-size:20px !important;}
</style>
""", unsafe_allow_html=True)

# タイトル
st.title("🎧 Sound Persona")
st.caption("Music Personality Analysis AI / 音楽性格診断")
st.markdown("あなたの**「人生の3曲」**から、隠された人格と魂の色を分析します。")

# ==========================================
# 📘 辞書・説明エリア
# ==========================================
with st.expander("📊 分析軸とタイプ一覧を見る"):
    st.markdown("""
    ### 4つの分析軸
    | 軸 | 説明 | 日本語イメージ |
    |---|---|---|
    | **L** (Lyric) vs **S** (Sound) | 歌詞 ↔ 音響 | 言葉の力 ↔ 音の響き |
    | **E** (Emotional) vs **T** (Technical) | 感情 ↔ 技術 | エモさ・衝動 ↔ 構成・テク |
    | **M** (Mainstream) vs **U** (Underground) | 王道 ↔ 個性 | 時代の寵児 ↔ 孤高のカリスマ |
    | **D** (Dark) vs **B** (Bright) | 内省 ↔ 発散 | 夜・憂い ↔ 光・祝祭 |
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🖊️ 歌詞重視 (L)**
        * **LEMD** : 感傷的な詩人
        * **LEMB** : 希望の語り部
        * **LEUD** : 孤独な哲学者
        * **LEUB** : 孤高の吟遊詩人
        * **LTMD** : 社会を憂う代弁者
        * **LTMB** : 王道のヒットメーカー
        * **LTUD** : 前衛的な言葉の魔術師
        * **LTUB** : 知性派の表現者
        """)
    with col2:
        st.markdown("""
        **🎹 サウンド重視 (S)**
        * **SEMD** : 感情を彩る音の画家
        * **SEMB** : 旋律を愛する夢想家
        * **SEUD** : 静寂と響きの探求者
        * **SEUB** : 癒やしの音使い
        * **STMD** : 鼓動を刻むリズム職人
        * **STMB** : 熱狂の支配者
        * **STUD** : 未踏の音を求む実験者
        * **STUB** : 技巧を極めし達人
        """)

# ==========================================
# 🤖 API設定
# ==========================================
try:
    # Replit Secrets から取得
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # ローカル実行用（Streamlit Cloudなど）
        api_key = st.secrets.get("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ APIキーが見つかりません。Replitの'Secrets'に'GOOGLE_API_KEY'を設定してください。")
        st.stop()

    genai.configure(api_key=api_key)
    # モデル設定（Flash推奨、だめならPro）
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        model.generate_content("test")
    except:
        model = genai.GenerativeModel('gemini-pro')

except Exception as e:
    st.error(f"接続エラー: {e}")
    st.stop()


# ==========================================
# 📝 入力フォーム
# ==========================================
with st.form("music_form"):
    st.markdown("### 💿 Step 1: 人生の3曲")
    
    col1, col2 = st.columns([1.5, 1])
    with col1: s1_name = st.text_input("1曲目: タイトル", placeholder="例: Creep", key="s1n")
    with col2: s1_artist = st.text_input("アーティスト", placeholder="Radiohead", key="s1a")
    
    col3, col4 = st.columns([1.5, 1])
    with col3: s2_name = st.text_input("2曲目: タイトル", key="s2n")
    with col4: s2_artist = st.text_input("アーティスト", key="s2a")

    col5, col6 = st.columns([1.5, 1])
    with col5: s3_name = st.text_input("3曲目: タイトル", key="s3n")
    with col6: s3_artist = st.text_input("アーティスト", key="s3a")

    st.markdown("---")
    st.markdown("### 🔍 Step 2: 音楽の価値観")
    
    q_element = st.text_input(
        "Q1. 音楽で一番重視するのは？",
        placeholder="例: 歌詞の言葉選び、メロディの哀愁、ベースの重低音...",
        help="歌詞、メロディ、リズム、世界観、演奏技術など"
    )

    q_situation = st.text_input(
        "Q2. どんな時に聴きたくなりますか？",
        placeholder="例: 深夜のドライブ、失恋した時、通勤中...",
        help="具体的なシチュエーション"
    )

    q_value = st.text_input(
        "Q3. あなたにとって「音楽」とは？",
        placeholder="例: 逃避場所、エネルギー源、酸素...",
        help="直感で答えてください"
    )

    submitted = st.form_submit_button("Sound Persona を解析する", use_container_width=True)


# ==========================================
# 🚀 診断実行ロジック
# ==========================================
if submitted:
    if not (s1_name and q_value):
        st.warning("⚠️ 精度を高めるため、少なくとも「1曲目」と「音楽とは」は入力してください。")
    else:
        with st.spinner('🎧 波形を解析中... 深層心理にダイブしています...'):
            
            # こだわりの最強プロンプト
            prompt = f"""
            あなたは音楽心理診断AI「Sound Persona」です。
            以下のデータからユーザーを分析し、指定のフォーマットで出力してください。

            【入力データ】
            1. {s1_name} (Artist: {s1_artist})
            2. {s2_name} (Artist: {s2_artist})
            3. {s3_name} (Artist: {s3_artist})
            * 重視: {q_element}
            * 状況: {q_situation}
            * 定義: {q_value}

            【分析ロジックと用語定義】
            以下の4軸で判定し、必ず指定の日本語名称を使用すること。

            1. **L** (Lyric/言葉) vs **S** (Sound/音響)
            2. **E** (Emotional/感情) vs **T** (Technical/技巧)
            3. **M** (Mainstream/王道) vs **U** (Underground/個性)
            4. **D** (Dark/内省) vs **B** (Bright/発散)

            [タイプ名リスト]
            LEMD:感傷的な詩人 / LEMB:希望の語り部 / LEUD:孤独な哲学者 / LEUB:孤高の吟遊詩人
            LTMD:社会を憂う代弁者 / LTMB:王道のヒットメーカー / LTUD:前衛的な言葉の魔術師 / LTUB:知性派の表現者
            SEMD:感情を彩る音の画家 / SEMB:旋律を愛する夢想家 / SEUD:静寂と響きの探求者 / SEUB:癒やしの音使い
            STMD:鼓動を刻むリズム職人 / STMB:熱狂の支配者 / STUD:未踏の音を求む実験者 / STUB:技巧を極めし達人

            【出力フォーマット（厳守）】
            (Markdown形式)
            ## 🎧 Type: **[4文字]**
            ### 『 [タイプ名リストから該当する日本語] 』

            **🎨 Soul Color (魂の色)**
            * カラー名: [色名]
            * カラーコード: **[#RRGGBB]**

            **🧠 Persona Analysis**
            (ユーザーの回答「{q_value}」などを踏まえ、なぜその音楽を必要としているのか？心の隙間や渇望を鋭く言い当てること。300文字程度)

            **👗 Fashion & Spot**
            * Fashion: [似合うスタイル]
            * Spot: [聖域となる場所]

            **🤝 Soulmate Connection**
            * 最高の相性: **[逆の4文字]** 型
            * (理由を一言で)
            """

            try:
                # AI実行
                response = model.generate_content(prompt)
                
                # 結果表示
                st.success("Analysis Complete.")
                st.markdown(response.text)
                
                # --- 演出：カラーカード表示 ---
                color_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', response.text)
                if color_match:
                    hex_color = color_match.group(0)
                    st.markdown(f"""
                    <div style="background-color: {hex_color}; color: #fff; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #eee; text-shadow: 0 0 5px rgba(0,0,0,0.5); margin-bottom: 20px;">
                        <h3 style="margin:0;">Your Soul Color</h3>
                        <p style="margin:0; font-size: 1.2em;">{hex_color}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # --- Twitterシェア機能（修正版）---
                # 1. 結果を抜き出す
                type_match = re.search(r"Type:\s*\*\*([A-Z]{4})\*\*", response.text)
                title_match = re.search(r"『\s*(.*?)\s*』", response.text)
                color_match_text = re.search(r"カラー名:\s*(.*)", response.text)

                res_type = type_match.group(1) if type_match else "分析完了"
                res_title = title_match.group(1) if title_match else ""
                # カラー名はMarkdownの*などを除去して綺麗にする
                res_color = color_match_text.group(1).replace("*","").strip() if color_match_text else ""

                # 2. シェア用テキスト作成
                share_text = f"""【Sound Persona 音楽診断】
私のタイプ：{res_type}
『 {res_title} 』
魂の色：{res_color}

私にとって音楽とは「{q_value}」である。
#SoundPersona"""

                # 3. URLエンコード（日本語対応）
                share_text_encoded = urllib.parse.quote(share_text)
                share_url_encoded = urllib.parse.quote(YOUR_APP_URL)

                # 4. リンク生成
                tweet_url = f"https://twitter.com/intent/tweet?text={share_text_encoded}&url={share_url_encoded}"

                st.link_button("🐦 結果をX(Twitter)でポストする", tweet_url)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
