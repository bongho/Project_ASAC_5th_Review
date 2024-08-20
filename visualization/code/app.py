import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import folium

## DB 관련 함수 import 
from db_functions import find_business_in_db, get_reviews_for_business, get_users_for_review, print_review_table_schema


## 페이지 설정 함수
def setup_page():
    st.set_page_config(page_title="ASAC_5th_Review", page_icon="🛵", layout="wide")
    st.markdown("""
    <style>
        .reportview-container .main .block-container { max-width: 1000px; }
    </style>
    """, unsafe_allow_html=True)


## main 화면 표시 함수
def show_main():
    # 페이지 타이틀 설정
    st.title("Welcome to ASAC-MAP")
    # 프로젝트 설명
    st.write("YELP 데이터셋을 활용한 고객 탐색경험 향상을 위한 키워드 요약 프로젝트")
    st.write("좌측에 가게 이름을 검색해주세요.")


### show result 함수 구성요소 
# ## 지도 표시
# def display_map(business_info):
#     map_center = [business_info[1], business_info[2]]
#     m = folium.Map(location=map_center, zoom_start=15, tiles='cartodbpositron', width='90%', height=200)
#     folium.Marker(location=map_center, popup=f"{business_info[0]}, {business_info[3]}", tooltip="Click for more info").add_to(m)
#     folium_static(m, height=150)


## 대분류 긍/부정 그래프
def display_bar_chart(business_info):
    # namedtuple에서 점수 정보를 가져옴
    data = {
        'Category': ['Service', 'Others', 'Food', 'Price', 'Atmosphere', 'Facilities'],
        'Score': [
            business_info.service_score,
            business_info.others_score,
            business_info.food_score,
            business_info.price_score,
            business_info.atmosphere_score,
            business_info.facility_score
        ]
    }

    # 점수에 따라 Positive/Negative 분류
    df = pd.DataFrame(data)
    df['Type'] = df['Score'].apply(lambda x: 'Positive' if x > 0 else 'Negative')

    # 긍정 및 부정 점수를 각각 정렬(긍정->내림차순 / 부정->오름차순)
    df_positive = df[df['Type'] == 'Positive'].sort_values(by='Score', ascending=False)
    df_negative = df[df['Type'] == 'Negative'].sort_values(by='Score', ascending=False)

    # 데이터프레임 재결합
    df_sorted = pd.concat([df_positive, df_negative])

    # 카테고리별 긍/부정 점수 시각화
    fig, ax = plt.subplots(figsize=(10, 4))  # 그래프 크기 조절 (너비, 높이)
    color_map = {'Positive': 'skyblue', 'Negative': 'orange'}

    # 카테고리별로 바 차트 그리기 및 점수 표시
    for index, row in df_sorted.iterrows():
        bar = ax.bar(row['Category'], row['Score'], color=color_map[row['Type']], width=0.4)
        # 각 막대 위에 점수 표시
        ax.text(bar[0].get_x() + bar[0].get_width() / 2, 
                bar[0].get_height(), 
                f'{row["Score"]:.2f}', 
                ha='center', 
                va='bottom' if row['Score'] < 0 else 'bottom', 
                color='black')
    
    # 중앙선 추가 및 바깥선 제거
    ax.axhline(0, color='lightgrey', linewidth=0.8)
    ax.spines['top'].set_visible(False)  # 상단 바깥선 제거
    ax.spines['right'].set_visible(False)  # 우측 바깥선 제거
    ax.spines['left'].set_visible(False)  # 좌측 바깥선 제거
    ax.spines['bottom'].set_visible(False)  # 하단 바깥선 제거

    ax.set_ylabel('Scores')
    ax.set_title('Category Scores')

    # 스트림릿으로 플롯 출력
    st.pyplot(fig)

    
## 가게 정보 표시
def display_store_info(business_info):
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        st.image("assets/sample_img.jpg", caption='Store Image', width=300)
    with col2:
        #display_map(business_info)
        display_bar_chart(business_info)
        display_additional_info(business_info)


## 가게 추가 정보 표시
def display_additional_info(business_info):
    with st.container(height=142):
        category_string = ' > '.join(eval(business_info.category)) if isinstance(business_info.category, str) else ' > '.join(business_info.category)
        st.write("⭐", round(business_info.average_stars_biz, 2))
        st.write("🍽️", category_string)
        st.write("🏡", f"{business_info.address}, {business_info.region}")


## 리뷰 요약 표시
def display_review_keywords(business_info):
    # @@ 예외처리) 가게 리뷰가 10개 미만인 경우 - 수집중 안내
    if business_info.review_count_biz < 10:
        st.info("가게 리뷰 수집중입니다.")
        return

    # 긍정 및 부정 키워드를 저장할 리스트
    good_keywords = []
    bad_keywords = []

    # 각 점수에 따라 긍정/부정 키워드 분류 및 저장
    if business_info.service_score != 0:
        score_keyword_pair = (business_info.service_score, business_info.service_keyword)
        if business_info.service_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    if business_info.others_score != 0:
        score_keyword_pair = (business_info.others_score, business_info.others_keyword)
        if business_info.others_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    if business_info.food_score != 0:
        score_keyword_pair = (business_info.food_score, business_info.food_keyword)
        if business_info.food_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    if business_info.price_score != 0:
        score_keyword_pair = (business_info.price_score, business_info.price_keyword)
        if business_info.price_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    if business_info.atmosphere_score != 0:
        score_keyword_pair = (business_info.atmosphere_score, business_info.atmosphere_keyword)
        if business_info.atmosphere_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    if business_info.facility_score != 0:
        score_keyword_pair = (business_info.facility_score, business_info.facility_keyword)
        if business_info.facility_score > 0:
            good_keywords.append(score_keyword_pair)
        else:
            bad_keywords.append(score_keyword_pair)

    # 긍정 및 부정 키워드 리스트를 점수 기준으로 정렬
    good_keywords.sort(reverse=True, key=lambda x: x[0])  # 점수 높은 순으로 정렬
    bad_keywords.sort(reverse=False, key=lambda x: x[0])  # 점수 낮은 순으로 정렬

    # 컬럼 레이아웃 정의
    col1, col2 = st.columns(2)
    
    # 첫 번째 컬럼에 긍정 키워드 추가
    with col1:
        st.subheader("Good")
        if good_keywords:
            for score, keyword in good_keywords:
                st.write(f"- {keyword}")
        else:
            st.write()
            #st.write("No positive feedback.")

    # 두 번째 컬럼에 부정 키워드 추가
    with col2:
        st.subheader("Bad")
        if bad_keywords:
            for score, keyword in bad_keywords:
                st.write(f"- {keyword} ")
        else:
            st.write()
            #st.write("No negative feedback.")


    # 리뷰 스키마 확인
    # 메인 스크립트 또는 특정 함수 내에서 호출
    # if __name__ == "__main__":
    #     print_review_table_schema()  # review 테이블의 스키마를 출력

    # 리뷰 데이터 가져오기 및 처리
    print("--------")
    business_id = int(business_info.business_id)
    print("business_id :", business_id)
    reviews = get_reviews_for_business(business_id)
    print("Number of reviews:", len(reviews))

    if reviews:
        review_df = pd.DataFrame(reviews)
        print(review_df.head())
    else:
        print("No reviews found for this business ID.")
        st.write("No reviews found for this business ID.")
        return
    
    # 모든 사용자 정보 가져오기 및 DataFrame 생성
    user_ids = review_df.user_id.tolist()
    print("user_ids : ", user_ids)
    # Check if user_ids are correctly formatted as integers
    print("User IDs are of type:", type(user_ids))

    users = get_users_for_review(user_ids)  # 모든 사용자 정보를 한 번에 가져옴
    print("users : ", users)
    user_df = pd.DataFrame(users, columns=['user_id', 'average_stars_user', 'name', 'most_visited_region'])
    print("user_df : ", user_df.head())
    
    # 리뷰 데이터와 사용자 데이터 병합
    merged_df = pd.merge(review_df, user_df, on='user_id', how='left')
    print("merged_df : ", merged_df.head())
    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.date
    merged_df = merged_df.sort_values(by='date', ascending=False)
    
    # 리뷰 데이터 시각적으로 표시
    st.subheader("Reviews...")
    st.markdown("---")
    for index, row in merged_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"**{row['name']}**")
            with col2:
                st.markdown(f"**⭐{row['stars']}**")
            with col3:
                st.markdown(f"**{row['date']}**")
            st.markdown(f"{row['text']}")
            st.markdown(f"📍 Most visited region: {row['most_visited_region']}")
            st.markdown("---")  # 각 리뷰 사이에 구분선 추가

## 결과 화면 표시
def show_result(business_name):
    business_info = find_business_in_db(business_name)
    # @@ 예외처리) 가게 이름이 DB에 없을 경우 - 가게명 없음 error 메세지
    if not business_info:
        st.error("해당하는 가게가 없습니다. 가게 이름을 확인해주세요.")
        return

    st.title(f"{business_name}")
    display_store_info(business_info)
    display_review_keywords(business_info)


        

###### 페이지 설정 변경
st.set_page_config(
    page_title="ASAC_5th_Review",
    page_icon="🛵",
    layout="wide",  # 'wide' layout 사용
)
####### sidebar #########
# CSS를 이용해 커스텀 스타일 적용
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1000px;  /* 최대 너비 설정 */
    }
</style>
""", unsafe_allow_html=True)


# 앱 실행
with st.sidebar :
    # 사이드바에 타이틀 추가
    st.sidebar.title("ASAC-MAP")
    # 검색창 (* business_name 기준)
    input_name = st.text_input("Search...")

    btn_submit = st.button("Go to Review", key='submit_btn', disabled=(input_name is False))


        
####### main page #########
if not btn_submit:
    show_main()
else:
    ## submit 버튼 onclick 이벤트

    # @@ 예외처리) 입력이 없을 경우 - 에러 메시지
    if not input_name:
        st.error("Please enter the store name.")
    else:
        # 결과 표시
        show_result(input_name)