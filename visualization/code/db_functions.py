## DB 관련 함수 저장

import sqlite3

## DB 연결
def get_connection(db_path='DB/ASAC_MAP.db'):
    """데이터베이스 연결을 반환합니다."""
    return sqlite3.connect(db_path)

## business table 정보 불러오기
def find_business_in_db(business_name):
    # DB에서 business_name을 검색
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, latitude, longitude, address, postal_code, category, region, review_count_biz, bined_stars, business_id FROM business WHERE name = ?", (business_name,))
    result = c.fetchone()
    return result

## reveiw table 정보 불러오기
def get_reviews_for_business(business_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT text, user_id, business_id, stars, date FROM review WHERE business_id =?",(business_id,))
    return c.fetchall()

# ## user table 정보 불러오기
# def get_users_for_review(user_id):
#     conn = get_connection()
#     c = conn.cursor()
#     c.execute("SELECT user_id, name, average_stars_user, most_visited_region FROM user WHERE user_id=?",(user_id,))
#     return c.fetchone()

def get_users_for_review(user_ids):
    conn = get_connection()
    try:
        c = conn.cursor()
        query = "SELECT user_id, average_stars_user, name, most_visited_region FROM user WHERE user_id IN ({})"
        format_strings = ','.join(['?']*len(user_ids))  # user_ids 개수만큼 '?'를 생성
        query = query.format(format_strings)
        c.execute(query, user_ids)
        return c.fetchall()
    finally:
        conn.close()
