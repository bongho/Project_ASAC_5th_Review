## DB 관련 함수 저장

import sqlite3
from collections import namedtuple

## DB 연결
def get_connection(db_path='DB/ASAC_MAP.db'):
    return sqlite3.connect(db_path)


## business table tuple 정의
Business = namedtuple(
    'Business', [
    'business_id',
    'name',
    'address',
    'category',
    'region',
    'review_count_biz',
    'average_stars_biz',
    'service_score',
    'others_score',
    'food_score',
    'price_score',
    'atmosphere_score',
    'facility_score',
    'atmosphere_keyword',
    'facility_keyword',
    'food_keyword',
    'others_keyword',
    'price_keyword',
    'service_keyword'
])
## business table 정보 불러오기
def find_business_in_db(business_name):
    # DB에서 business_name을 검색
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM business WHERE name = ?", (business_name,))
        result = c.fetchone()

        if result:
            # NamedTuple 인스턴스를 생성
            business = Business._make(result)
            print("find_business_in_db: Business found.")
            return business
        else:
            print("find_business_in_db: No business found.")
            return None
    except Exception as e:
        print(f"find_business_in_db: An error occurred: {e}")
        return None
    finally:
        conn.close()

## reveiw table 정보 불러오기
# Review namedtuple 정의
Review = namedtuple('Review', [
    'review_id',
    'user_id',
    'business_id',
    'stars',
    'useful',
    'text',
    'date',
    'food',
    'service',
    'atmosphere',
    'facility',
    'price',
    'others'
])
def get_reviews_for_business(business_id):
    conn = get_connection()
    try:
        c = conn.cursor()
        query = "SELECT * FROM review WHERE business_id = ?"
        c.execute(query, (business_id,))
        rows = c.fetchall()
        
        # Review namedtuple을 사용하여 각 행을 변환
        reviews = [Review(*row) for row in rows]
        
        print(f"Fetched {len(reviews)} reviews for business ID {business_id}")
        return reviews
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []
    finally:
        conn.close()




# ## user table 정보 불러오기
# User namedtuple 정의
User = namedtuple('User', [
    'user_id',
    'name',
    'review_count_user',
    'average_stars_user',
    'most_visited_region',
    'visit_cnt',
    'log_visit_cnt'
])
def get_users_for_review(user_ids):
    if not user_ids:
        print("No user_ids provided, returning empty list.")
        return []

    conn = get_connection()
    try:
        c = conn.cursor()
        # IN절에서 사용할 '?'의 개수는 user_ids의 길이에 맞추기
        format_strings = ','.join(['?']*len(user_ids))
        query = f"SELECT * FROM user WHERE user_id IN ({format_strings})"
        c.execute(query, user_ids)
        rows = c.fetchall()
        
        # User namedtuple을 사용하여 각 행을 변환
        users = [User(*row) for row in rows]
        
        print(f"Fetched {len(users)} users.")
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        conn.close()




## 리뷰 스키마 확인 코드
def print_review_table_schema():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("PRAGMA table_info(review)")
        schema = c.fetchall()
        print("Review table schema:")
        for col in schema:
            print(col)
    finally:
        conn.close()
