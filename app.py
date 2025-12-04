import streamlit as st
import google.generativeai as genai
import re
import os

# ==========================================
# 🎧 Sound Persona：Webアプリ版
# ==========================================

# 1. ページの設定（タイトルやアイコン）
st.set_page_config(page_title="Sound Persona",
                   page_icon="🎧",
                   layout="centered")

# 2. スタイルの調整（見た目を少しおしゃれに）
st.markdown("""
<style>
    .stTextInput > label {font-size:105%; font-weight:bold; color:#4a4a4a;}
    .stTextArea > label {font-size:105%; font-weight:bold; color:#4a4a4a;}
    .reportview-container {background: #f0f2f6;}
</style>
""",
            unsafe_allow_html=True)

# 3. タイトル表示
st.title("🎧 Sound Persona")
st.caption("Music Personality Analysis AI / 音楽性格診断")
st.write("あなたの「人生の3曲」から、隠された人格と魂の色を分析します。")

with st.expander("📊 分析軸について"):
    st.markdown("""
    あなたの音楽の好みを4つの軸で分析します：
    
    | 軸 | 説明 |
    |---|---|
    | **L**(Lyric) vs **S**(Sound) | 歌詞重視 ↔ サウンド重視 |
    | **E**(Emotional) vs **T**(Technical) | 感情的 ↔ 技術的 |
    | **M**(Mainstream) vs **U**(Underground) | メインストリーム ↔ アンダーグラウンド |
    | **D**(Dark) vs **B**(Bright) | ダーク ↔ ブライト |
    
    例：**LEMD** = 歌詞重視・感情的・メインストリーム・ダーク
    """)

# 4. APIキーの読み込み（ReplitのSecretsから）
try:
    # ReplitのSecretsからキーを取得
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # 万が一Secretsがない場合（ローカル用）
        api_key = st.secrets["GOOGLE_API_KEY"]

    genai.configure(api_key=api_key)

    # モデル設定
    model = genai.GenerativeModel('gemini-2.0-flash')

except Exception as e:
    st.error("⚠️ APIキーが設定されていません。Replitの'Secrets'に'GOOGLE_API_KEY'を設定してください。")
    st.stop()

# ==========================================
# 入力フォーム（Colabの入力をスマホ用に変換）
# ==========================================

with st.form("music_form"):
    st.markdown("### 💿 Step 1: 人生の3曲")

    # 横並びレイアウト（曲名｜アーティスト）
    col1, col2 = st.columns([1.5, 1])
    with col1:
        s1_name = st.text_input("1曲目: タイトル", placeholder="例: Creep", key="song1_name")
    with col2:
        s1_artist = st.text_input("アーティスト", placeholder="Radiohead", key="song1_artist")

    col3, col4 = st.columns([1.5, 1])
    with col3:
        s2_name = st.text_input("2曲目: タイトル", key="song2_name")
    with col4:
        s2_artist = st.text_input("アーティスト", key="song2_artist")

    col5, col6 = st.columns([1.5, 1])
    with col5:
        s3_name = st.text_input("3曲目: タイトル", key="song3_name")
    with col6:
        s3_artist = st.text_input("アーティスト", key="song3_artist")

    st.markdown("---")
    st.markdown("### 🔍 Step 2: 音楽の価値観")

    # 追加質問（ヘルプテキスト付き）
    q_element = st.text_input("Q1. 音楽で一番重視するのは？",
                              placeholder="例: 歌詞、メロディ、リズム",
                              help="歌詞、メロディ、リズム、演奏技術、世界観など")

    q_situation = st.text_input("Q2. どんな時に聴きたくなりますか？",
                                placeholder="例: 深夜、失恋した時",
                                help="具体的なシチュエーションを書くと分析精度が上がります")

    q_value = st.text_input("Q3. あなたにとって「音楽」とは？",
                            placeholder="例: 逃避場所、エネルギー源",
                            help="直感で答えてください")

    # 送信ボタン
    submitted = st.form_submit_button("Sound Persona を解析する",
                                      use_container_width=True)

# ==========================================
# 診断実行ロジック
# ==========================================
if submitted:
    # 入力チェック
    if not (s1_name and q_value):
        st.warning("⚠️ 少なくとも「1曲目」と「音楽とは」は入力してください。")
    else:
        with st.spinner('🎧 波形を解析中... あなたの深層心理にダイブしています...'):

            # プロンプト（Colabで作った最強版）
            prompt = f"""
            あなたは音楽心理診断AI「Sound Persona」です。
            以下の詳細データからユーザーを分析してください。

            【入力データ】
            1. {s1_name} (Artist: {s1_artist})
            2. {s2_name} (Artist: {s2_artist})
            3. {s3_name} (Artist: {s3_artist})
            * 重視: {q_element}
            * 状況: {q_situation}
            * 定義: {q_value}

            【分析軸】
            L(Lyric) vs S(Sound)
            E(Emotional) vs T(Technical)
            M(Mainstream) vs U(Underground)
            D(Dark) vs B(Bright)

            【出力フォーマット】
            (マークダウン形式)
            ## 🎧 Type: **[4文字]**
            ### 『 [二つ名] 』

            **🎨 Soul Color (魂の色)**
            * カラー名: [色名]
            * カラーコード: **[#RRGGBB]**

            **🧠 Persona Analysis (詳細性格分析)**
            (300文字程度で深く分析)

            **👗 Fashion & Spot**
            * Fashion: [似合うスタイル]
            * Spot: [似合う場所]

            **🤝 Soulmate Connection**
            * 最高の相性: **[逆の4文字]** 型
            * (理由を一言で)

            ---
            **🐦 X(Twitter)シェア用**
            (以下の枠内をそのままコピーできる形で)
            ```
            【Sound Persona 音楽診断】
            私のタイプ：[4文字]『 [二つ名] 』
            魂の色：[カラー名]
            音楽とは「{q_value}」である。
            #SoundPersona
            ```
            """

            try:
                # AI実行
                response = model.generate_content(prompt)

                # 結果表示エリア
                st.success("Analysis Complete.")
                st.markdown(response.text)

                # 色の抽出と表示
                color_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}',
                                        response.text)
                if color_match:
                    hex_color = color_match.group(0)
                    st.markdown(f"""
                    <div style="
                        background-color: {hex_color};
                        color: #ffffff;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        border: 2px solid #ddd;
                        text-shadow: 0px 0px 5px rgba(0,0,0,0.5);
                    ">
                        <h3 style="margin:0;">Your Soul Color</h3>
                        <p style="margin:0; font-size: 1.2em;">{hex_color}</p>
                    </div>
                    """,
                                unsafe_allow_html=True)

                # ツイートボタンの生成（簡易版）
                tweet_text = f"私のSound Persona診断結果！音楽とは「{q_value}」である。 #SoundPersona"
                tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
                st.link_button("🐦 結果をX(Twitter)でポストする", tweet_url)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
