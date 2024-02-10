from flask import Blueprint, render_template, request, redirect, session, flash, url_for, get_flashed_messages,jsonify
from firebaseSetUp import auth, db

bookmark_bp = Blueprint('bookmark', __name__)

comics_doc_ref=db.collection('comics')

# ブックマーク機能
@bookmark_bp.route("/<user_id>/bookmark", methods=["POST"])
def toggle_bookmark(user_id):
    data = request.get_json()

    # 漫画のタイトルを取得
    title = data.get("title")

    # データベースでブックマークの状態をトグル

    comics_doc = comics_doc_ref.document(title)
    
    # ブックマークの状態を取得
    comics_data = comics_doc.get()
    
    if comics_data.exists:
        current_bookmark = comics_data.to_dict().get("bookmark", [])
    else:
        current_bookmark = []


    # 新しいユーザーIDをブックマークリストに追加
    if user_id not in current_bookmark:
        current_bookmark.append(user_id)
        comics_doc.update({"bookmark": current_bookmark})
        new_bookmark_value = len(current_bookmark) # ブックマーク数を取得
    else:
        current_bookmark.remove(user_id)
        comics_doc.update({"bookmark": current_bookmark})
        new_bookmark_value = len(current_bookmark)

    return jsonify({"bookmarked": new_bookmark_value})

