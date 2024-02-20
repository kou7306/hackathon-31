from flask import Blueprint, render_template, request, redirect, session, flash, url_for, get_flashed_messages
from firebaseSetUp import auth, db
from bs4 import BeautifulSoup
import requests

userpage_bp = Blueprint('userpage', __name__)

user_doc_ref = db.collection('user')
review_doc_ref=db.collection('review')

def get_bar_color(ans):
    if ans <= -4:
        return 'bg-red-500'  # 1
    elif ans <= -3:
        return 'bg-red-400'  # 2
    elif ans <= -2:
        return 'bg-red-300'  # 3
    elif ans <= -1:
        return 'bg-orange-400'  # 4
    elif ans < 0:
        return 'bg-yellow-600'  # 5
    elif ans == 0:
        return 'bg-yellow-500'  # 6
    elif ans <= 1:
        return 'bg-lime-400'  # 7
    elif ans <= 2:
        return 'bg-green-400'  # 8
    elif ans <= 3:
        return 'bg-green-500'  # 9
    else:
        return 'bg-green-600'  # 10

def get_bar_width(ans):
    return ((ans + 5) / 10) * 100

# ユーザーページ
@userpage_bp .route('/userpage', methods=['GET', 'POST'])
def user_page():   
    user_id = session.get('user_id')
    if not user_doc_ref.document(user_id).get().exists:
        return redirect("/login?query=userpage")
    if not user_id:
        return redirect('/login?query=userpage')
    user_id = session.get('user_id')
    if user_id:
        logged_in = True
    else:
        logged_in = False   
    user_doc = user_doc_ref.document(user_id)
    user=user_doc.get()
    user_data=user.to_dict()
    username=user_data["username"]
    # 特定のユーザーネームに一致するドキュメントを取得
    query = review_doc_ref.where('username', '==', username).get()

    # アンケート結果の取得・表示
    genre_value=user_data.get("genre")
    start_question = 20 * (int(genre_value) - 1)
    end_question = start_question + 20

    html_file_path=f"templates/question{genre_value}.html"
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_code = file.read()
    result = user_data.get('mangaAnswer')

    #アンケートの設問を格納する配列
    question = []
    soup = BeautifulSoup(html_code, 'html.parser')

    #アンケートの設問を取得
    h2_elems = soup.find_all('h2')
    for h2 in h2_elems:
        question.append(h2.text)
    
    #アンケートの回答を取得
    answer = result[start_question:end_question]

    #設問と回答をタプル化
    combined_list = list(zip(question, answer))

    #選択したジャンルを取得
    genre_list = ["バトル", "スポーツ", "恋愛", "ミステリー", "コメディ", "SF", "歴史"]
    genre_choice = genre_list[int(genre_value)-1]
    
    updated_combined_list = []
    for q, ans in combined_list:
        color = get_bar_color(ans)
        width = get_bar_width(ans)
        updated_combined_list.append((q, ans, color, width))
    
    #ブックマークをデータベースから取得
    favorite_titles = user_data["bookmark"]

    # フォローしたユーザーのIDを取得
    follow_data = []
    for follow_id in user_data["follow"]:
        follow_doc = user_doc_ref.document(follow_id).get()
        if follow_doc.exists:
            follow_name = follow_doc.to_dict()["username"]
            follow_data.append((follow_name, follow_id))

    return render_template("userpage.html", myreview_query=query,username=username, user_id=user_id,favorite_titles=favorite_titles,follow_data=follow_data,result=result, combined_list=updated_combined_list, genre_choice=genre_choice, logged_in=logged_in)

@userpage_bp.route('/userpage/<id>', methods=['GET', 'POST'])
def update(id):
    if 'user' in session:
        name = request.form['username']
        print(name)
        try:
            db.collection('user').document(id).update({'username': name})
            return redirect('/userpage')
        except:
            return redirect('/userpage', code=500)
    else:
        return redirect('/login?query=userpage')