import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import folium

## DB 관련 함수 import 
from db_functions import find_business_in_db, get_reviews_for_business, get_users_for_reiew


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
## 지도 표시
def display_map(business_info):
    map_center = [business_info[1], business_info[2]]
    m = folium.Map(location=map_center, zoom_start=15, tiles='cartodbpositron', width='90%', height=200)
    folium.Marker(location=map_center, popup=f"{business_info[0]}, {business_info[3]}", tooltip="Click for more info").add_to(m)
    folium_static(m, height=150)

## 가게 정보 표시
def display_store_info(business_info):
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        st.image("assets/sample_img.jpg", caption='Store Image', width=300)
    with col2:
        display_map(business_info)
        display_additional_info(business_info)

## 가게 추가 정보 표시
def display_additional_info(business_info):
    with st.container(height=142):
        category_string = ' > '.join(eval(business_info[5])) if isinstance(business_info[5], str) else ' > '.join(business_info[5])
        st.write("⭐", business_info[8])
        st.write("🍽️", category_string)
        st.write("🏡", f"{business_info[3]}, {business_info[6]}")

## 리뷰 요약 표시
def display_reviews(business_info):
    # @@ 예외처리) 가게 리뷰가 10개 미만인 경우 - 수집중 안내
    if business_info[7] < 10:
        st.info("가게 리뷰 수집중입니다.")
        return

    #reviews = get_reviews_for_business(business_info[-2])

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

## 결과 화면 표시
def show_result(business_name):
    business_info = find_business_in_db(business_name)
    # @@ 예외처리) 가게 이름이 DB에 없을 경우 - 가게명 없음 error 메세지
    if not business_info:
        st.error("해당하는 가게가 없습니다. 가게 이름을 확인해주세요.")
        return

    st.title(f"{business_name}")
    display_store_info(business_info)
    display_reviews(business_info)


        

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


