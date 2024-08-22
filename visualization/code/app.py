import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import folium

## DB 관련 함수 import 
from db_functions import fetch_business_list, find_business_in_db, get_reviews_for_business, get_users_for_review, print_review_table_schema


## 페이지 설정 함수
def setup_page():
    st.set_page_config(page_title="ASAC_5th_Review", page_icon="🛵", layout="wide")
    st.markdown("""
    <style>
        .reportview-container .main .block-container { max-width: 1000px; }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []

if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

## main 화면 표시 함수
def show_main():
    # 페이지 타이틀 설정
    st.title("Welcome to ASAC-MAP")
    # 프로젝트 설명
    st.write("YELP 데이터셋을 활용한 고객 탐색경험 향상을 위한 키워드 요약 프로젝트")
    st.write("아래에서 원하는 가게 이름을 좌측에 입력해주세요.")
    business = fetch_business_list()
    business_df = business[['name', 'category', 'region', 'review_count_biz', 'average_stars_biz']]
    st.dataframe(business_df)


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
    fig, ax = plt.subplots(figsize=(10, 3), constrained_layout=True)  # 높이를 6인치로 고정
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

    #plt.tight_layout()

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
        if business_info.address == None:
            st.write("🏡", f"{business_info.region}")
        else : 
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
        st.subheader("Good Points 👍🏻")
        if good_keywords:
            for score, keyword in good_keywords:
                st.write(f"- {keyword}")
        else:
            st.write()
            #st.write("No positive feedback.")

    # 두 번째 컬럼에 부정 키워드 추가
    with col2:
        st.subheader("Bad Points 👎🏻")
        if bad_keywords:
            for score, keyword in bad_keywords:
                st.write(f"- {keyword} ")
        else:
            st.write()
            #st.write("No negative feedback.")



    
## 리뷰 필터링 기능(대분류 별)
def filter_reviews_by_categories(merged_df, categories):

    if categories:
        filter_condition = merged_df[categories].apply(lambda x: x >= 1).any(axis=1)
        filtered_df = merged_df[filter_condition]
    else:
        filtered_df = merged_df  # 카테고리가 선택되지 않으면 모든 리뷰 반환

    return filtered_df

# 리뷰 별점 찍기
def render_stars(rating):
    full_stars = int(rating)  # 전체 별 개수
    half_star = (rating - full_stars) >= 0.5  # 반 별이 필요한지
    empty_stars = 5 - full_stars - int(half_star)  # 빈 별 개수
    stars_html = '''
    <div style="font-size: 15px; color: orange; text-shadow: 0px 0px 3px orange; margin-top: -10px; margin-left: -8px;">
    '''
    stars_html += '★' * full_stars
    if half_star:
        stars_html += '☆'
    stars_html += '☆' * empty_stars
    stars_html += '</div>'
    return stars_html

# 리뷰 시각화
def display_reviews(business_info):
    # 리뷰 데이터 가져오기 및 처리
    print("--------")
    business_id = int(business_info.business_id)
    print("business_id :", business_id)
    reviews = get_reviews_for_business(business_id)
    print("Number of reviews:", len(reviews))

    if not reviews:
        st.write("No reviews found for this business ID.")
        return
    
    review_df = pd.DataFrame(reviews)
    print(review_df.head())

    # 모든 사용자 정보 가져오기 및 DataFrame 생성
    user_ids = review_df.user_id.tolist()
    users = get_users_for_review(user_ids)  # 모든 사용자 정보를 한 번에 가져옴
    user_df = pd.DataFrame(users)
    print("user_df : ", user_df.head())

    # 리뷰 데이터와 사용자 데이터 병합
    merged_df = pd.merge(review_df, user_df, on='user_id', how='left')
    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.date
    merged_df = merged_df.sort_values(by='date', ascending=False)
    print("merged_df : ", merged_df.head())
    

    # 리뷰 데이터 시각적으로 표시
    st.markdown("---")
    st.subheader(f"Reviews ({len(reviews)}) 💭")
    
    # 사용자에게 필터 선택 옵션 제공
    with st.container(height=250) :
        col1, col2, col3 = st.columns([2, 0.5, 0.5])
        with col1:
            st.markdown(
                """
                <style>
                .lightgray-bg {
                    background-color: lightgray;
                    border-radius: 5px;
                }
                </style>
                """, unsafe_allow_html=True
            )
            st.markdown('<div class="lightgray-bg">', unsafe_allow_html=True)
            # 1. 카테고리 필터
            categories = st.multiselect(
                "카테고리를 선택하세요.",
                ['food', 'service', 'atmosphere', 'facility', 'price', 'others'],
                default=st.session_state.selected_categories
            )
            # 2. 별점 필터
            st.write("별점을 선택하세요.")
            cols = st.columns(6)
            star_ratings = []
            for i, col in enumerate(cols):
                if col.checkbox(f"{i} 점", key=f"star_{i}"):
                    star_ratings.append(i)

            st.markdown('</div>', unsafe_allow_html=True)

        with col3 :
            st.write("")
            st.write("")
            on = st.toggle("Local Reviews")
            if on :
                st.write(f'{business_info.region} 지역 3회 이상 방문객 리뷰 확인')


    # 선택된 카테고리 상태를 세션에 저장 및 필터링 실행
    if categories != st.session_state.selected_categories:
        st.session_state.selected_categories = categories
        st.experimental_rerun()  # 상태가 업데이트된 후 즉시 다시 실행하여 두 번 동작 방지


    print("categories : ", categories)  # 선택된 카테고리 출력
    
    # 선택된 카테고리에 맞게 리뷰 필터링
    filtered_df = filter_reviews_by_categories(merged_df, categories)

    # 선택된 카테고리에 해당하는 리뷰 갯수 출력
    st.write(f'{len(filtered_df)} 개의 리뷰를 찾았습니다.')

    for index, row in filtered_df.iterrows():
        #print("filtered_df : ", filtered_df.head())
        with st.container():
            col1, col2, col3 = st.columns([0.5, 5, 1])
            with col1:
                st.markdown(f"**{row['name']}**")
                
            with col2:
                # 별점 HTML 적용
                stars_html = render_stars(row['stars'])
                components.html(f"""
                    <style>
                    .fa-star {{ color: orange; }}
                    .fa-star-half-alt {{ color: orange; }}
                    .fa-star-o {{ color: grey; }}
                    </style>
                    {stars_html}
                """, height=30)
            with col3:
                st.markdown(f"**{row['date']}**")
            #st.markdown(f"📍 {row['most_visited_region']}")
            st.markdown(f"{row['text']}")
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

    #btn_submit = st.button("Go to Review", key='submit_btn', disabled=(input_name is False))

    # 버튼 클릭 시 검색 상태 유지
    if st.button("Go to Review", key='submit_btn'):
        st.session_state.search_clicked = True
        st.session_state.business_name = input_name

        
####### main page #########
# 메인 페이지 로직
if not st.session_state.search_clicked or not st.session_state.business_name:
    show_main()
## submit 버튼 onclick 이벤트
else: 

    business_name = st.session_state.business_name
    business_info = find_business_in_db(business_name)
    
    # @@ 예외처리) 입력이 없을 경우 - 에러 메시지
    if not business_info:
        st.error("해당하는 가게가 없습니다. 가게 이름을 확인해주세요.")
    else:
        show_result(st.session_state.business_name)
