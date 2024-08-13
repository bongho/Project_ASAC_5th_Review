import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import folium

## DB 관련 함수 import 
from db_functions import find_business_in_db, get_reviews_for_business, get_users_for_review


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
    # 임시 데이터 생성 (실제 환경에서는 business_info 데이터 사용)
    data = {
        'Category': ['Food', 'Service', 'Facilities', 'Price', 'Atmosphere', 'Others'],
        'Score': [0.8, -0.25, 0.6, -0.35, 0.7, -0.4],
        'Type': ['Positive', 'Negative', 'Positive', 'Negative', 'Positive', 'Negative']
    }
    df = pd.DataFrame(data)

    # 긍정 및 부정 점수를 각각 정렬(긍정->내림차순 / 부정->오름차순)
    df_positive = df[df['Type'] == 'Positive'].sort_values(by='Score', ascending=False)
    df_negative = df[df['Type'] == 'Negative'].sort_values(by='Score', ascending=False)

    # 데이터프레임 재결합
    df_sorted = pd.concat([df_positive, df_negative])

    # 카테고리별 긍/부정 점수 시각화
    fig, ax = plt.subplots(figsize=(10, 1.5))  # 그래프 크기 조절 (너비, 높이)
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
        category_string = ' > '.join(eval(business_info[5])) if isinstance(business_info[5], str) else ' > '.join(business_info[5])
        st.write("⭐", business_info[8])
        st.write("🍽️", category_string)
        st.write("🏡", f"{business_info[3]}, {business_info[6]}")


## 리뷰 요약 표시
def display_review_keywords(business_info):
    # @@ 예외처리) 가게 리뷰가 10개 미만인 경우 - 수집중 안내
    if business_info[7] < 10:
        st.info("가게 리뷰 수집중입니다.")
        return
    

    # 컬럼 레이아웃 정의
    col1, col2 = st.columns(2)
    # && 동적 구현 + 시각화 추가 필요
    # 첫 번째 컬럼에 긍정 키워드 추가
    with col1:
        st.subheader("Good")
        st.write("- Tasty Pasta")
        st.write("- Kind Waitress")
        st.write("- Cozy Atmosphere")

    # 두 번째 컬럼에 부정 키워드 추가
    with col2:
        st.subheader("Bad")
        st.write("- Awful Location")
        st.write("- High Cost")
        st.write("- No Parking")


    # 리뷰 데이터 가져오기 및 처리
    business_id = business_info[-1]
    reviews = get_reviews_for_business(business_id)
    review_df = pd.DataFrame(reviews, columns=['text', 'user_id', 'stars', 'date', 'business_id'])
    review_df['date'] = pd.to_datetime(review_df['date'])
    review_df = review_df.sort_values(by='date', ascending=False)

    # 모든 사용자 정보 가져오기 및 DataFrame 생성
    users = get_users_for_review(reviews[1])  # 모든 사용자 정보를 한 번에 가져옴
    user_df = pd.DataFrame(users, columns=['user_id', 'average_stars_user', 'name', 'most_visited_region'])

    # 리뷰 데이터와 사용자 데이터 병합
    merged_df = pd.merge(review_df, user_df, on='user_id', how='left')

    # 리뷰 데이터 시각적으로 표시
    st.subheader("Reviews...")
    st.markdown("---")
    for index, row in merged_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"**{row['name']}**")
            with col2:
                st.markdown(f"**{row['stars']}⭐**")
            with col3:
                st.markdown(f"**{row['date'].strftime('%Y-%m-%d')}**")
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


