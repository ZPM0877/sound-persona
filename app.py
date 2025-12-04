import streamlit as st
import google.generativeai as genai
import re
import os
import urllib.parse

# ==========================================
# ⚙️ 設定エリア
# ==========================================
# ★重要：ここに「Streamlit Cloudで発行されたURL」を後で貼ってください
# (例: "https://sound-persona-xxxxx.streamlit.app")
YOUR_APP_URL = "https://share.streamlit.io/" 

# ==========================================
# 🎧 ページ設定 & デザイン
# ==========================================
st.set_page_config(
    page_title="Sound Persona",
    page_icon="🎧",
    layout="centered"
)

# スマホでも見やすくするカスタムCSS
st.markdown("""
<style>
    .stTextInput > label {font-size:105%; font-weight:bold; color:#4a4a4a;}
    .big-font {font-size:20px !important;}
    .reportview-container {background: #fcfcfc;}
</style>
""", unsafe_allow_html=True)

st.title("🎧 Sound Persona")
st.caption("Music Personality Analysis AI / 音楽性格診断")
st.markdown("あなたの**「人生の3曲」**から、隠された人格と魂の色を分析します。")

# ==========================================
# 📘 分析軸とタイプ一覧
# ==========================================
with st.expander("📊 4つの分析軸と全16タイプ（クリックで開く）"):
    st.markdown("""
    ### 🔍 4つの分析軸
    | 記号 | 分析軸 | イメージ |
    |:---:|:---|:---|
    | **L** vs **S** | **言葉** ↔ **響き** | 歌詞重視か、音の気持ちよさ重視か |
    | **E** vs **T** | **直感** ↔ **技巧** | エモさ・衝動か、構成・テクニックか |
    | **M** vs **U** | **王道** ↔ **個性** | みんなが知る曲か、知る人ぞ知る曲か |
    | **D** vs **B** | **内省** ↔ **発散** | 一人で浸りたいか、みんなで盛り上がりたいか |
    """)
    
    st.markdown("---")
    st.markdown("### 🎭 全16タイプ一覧")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📝 言葉重視 (Lyric)**
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
        **🎹 響き重視 (Sound)**
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
# 🤖 API設定 (Streamlit Secrets対応)
# ==========================================
try:
    # Streamlit CloudのSecrets、またはローカルの.streamlit/secrets.tomlから取得
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # 環境変数からの取得（バックアップ）
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("⚠️ APIキーが見つかりません。Streamlit Cloudの'Settings' > 'Secrets' に設定してください。")
        st.stop()

    genai.configure(api_key=api_key)

    # モデル自動検出ロジック
    valid_model = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5' in m.name:
                    valid_model = m.name
                    break
        if not valid_model:
             for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_model = m.name
                    break

        if valid_model:
            model = genai.GenerativeModel(valid_model)
        else:
            st.error("⚠️ 使用可能なGeminiモデルが見つかりませんでした。")
            st.stop()

    except Exception as e:
        st.error(f"モデル設定エラー: {e}")
        st.stop()

except Exception as e:
    st.error(f"接続エラー: {e}")
    st.stop()


# ==========================================
# 📝 入力フォーム
# ==========================================
with st.form("music_form"):
    st.markdown("### 💿 Step 1: 人生の3曲")
    
    col1, col2 = st.columns([1.5, 1])
    with col1: s1_name = st.text_input("1曲目: タイトル", placeholder="例: Pretender", key="s1n")
    with col2: s1_artist = st.text_input("アーティスト", placeholder="Official髭男dism", key="s1a")
    
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
        placeholder="例: 歌詞、メロディ、声、リズム、世界観",
        help="直感で「これだ」と思うもの"
    )

    q_situation = st.text_input(
        "Q2. どんな時に聴きたくなりますか？",
        placeholder="例: 通勤中、寝る前、失恋した時、テンション上げたい時",
        help="具体的なシーン"
    )

    q_value = st.text_input(
        "Q3. あなたにとって「音楽」とは？",
        placeholder="例: 救い、エネルギー、酸素、ガソリン、タイムマシン",
        help="一言で表すと？"
    )

    submitted = st.form_submit_button("Sound Persona を解析する", use_container_width=True)


# ==========================================
# 🚀 診断実行ロジック
# ==========================================
if submitted:
    if not (s1_name and q_value):
        st.warning("⚠️ 精度を高めるため、少なくとも「1曲目」と「音楽とは」は入力してください。")
    else:
        with st.spinner('🎧 解析中... あなたのプレイリストから深層心理を読み解いています...'):
            
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

            1. **L** (Lyric) vs **S** (Sound) -> 言葉 vs 響き
            2. **E** (Emotional) vs **T** (Technical) -> 直感 vs 技巧
            3. **M** (Mainstream) vs **U** (Underground) -> 王道 vs 個性
            4. **D** (Dark) vs **B** (Bright) -> 内省 vs 発散

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
                response = model.generate_content(prompt)
                
                # 結果表示
                st.success("Analysis Complete.")
                st.markdown(response.text)
                
                # カラーカード表示
                color_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', response.text)
                if color_match:
                    hex_color = color_match.group(0)
                    st.markdown(f"""
                    <div style="background-color: {hex_color}; color: #fff; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #eee; text-shadow: 0 0 5px rgba(0,0,0
