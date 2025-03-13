import streamlit as st
import pandas as pd
import numpy as np
import json

# 페이지 설정
st.set_page_config(
    page_title="학생 성적 관리 대시보드",
    page_icon="📚",
    layout="wide"
)

# 앱 제목
st.title("📚 학생 성적 관리 대시보드")
st.markdown("학생들의 성적을 관리하고 분석하는 대시보드입니다.")

# 학생 데이터프레임 생성 (요구사항 1)
@st.cache_data
def create_student_data():
    data = {
        '학생 이름': ['김민준', '이서연', '박지호', '최수아', '정도윤', '한예은', '황현우', '송지은'],
        '학년': [1, 2, 3, 1, 2, 3, 2, 1],
        '국어': [85, 92, 78, 96, 88, 77, 82, 94],
        '영어': [92, 88, 76, 94, 85, 75, 79, 91],
        '수학': [78, 95, 65, 92, 90, 68, 85, 79],
        '과학': [90, 84, 72, 88, 95, 70, 78, 86]
    }
    
    # 데이터프레임 생성
    df = pd.DataFrame(data)
    
    # 총점과 평균 점수 계산 (요구사항 3)
    df['총점'] = df['국어'] + df['영어'] + df['수학'] + df['과학']
    df['평균'] = df['총점'] / 4
    
    return df

# 데이터프레임 로드
df = create_student_data()

# 사이드바 - 검색 및 필터링 옵션 (도전 과제)
st.sidebar.header("검색 및 필터링")

# 학생 검색 기능 (도전 과제)
search_name = st.sidebar.text_input("학생 이름 검색")

# 과목 필터링 (도전 과제)
st.sidebar.subheader("과목별 필터링")
selected_subject = st.sidebar.selectbox("과목 선택", ['국어', '영어', '수학', '과학'])

# 평균 기준 필터링 (도전 과제)
filter_option = st.sidebar.radio(
    "필터링 기준",
    ["전체 학생", f"{selected_subject} 평균 이상", f"{selected_subject} 평균 이하"]
)

# 학년 필터링
selected_grade = st.sidebar.multiselect("학년 선택", [1, 2, 3], default=[1, 2, 3])

# 데이터 필터링 적용
filtered_df = df.copy()

# 학년 필터 적용
filtered_df = filtered_df[filtered_df['학년'].isin(selected_grade)]

# 이름 검색 필터 적용
if search_name:
    filtered_df = filtered_df[filtered_df['학생 이름'].str.contains(search_name)]

# 과목 평균 필터 적용
if filter_option != "전체 학생":
    subject_avg = df[selected_subject].mean()
    if "이상" in filter_option:
        filtered_df = filtered_df[filtered_df[selected_subject] >= subject_avg]
    else:
        filtered_df = filtered_df[filtered_df[selected_subject] < subject_avg]

# 메인 컨텐츠 탭나누기
tab1, tab2 = st.tabs(["📋 학생 성적", "📊 데이터 분석"])

with tab1:
    # 기본 데이터프레임 표시 (요구사항 2)
    st.subheader("학생 성적 데이터")
    
    # 정렬 옵션
    sort_options = st.radio(
        "정렬 기준",
        ["정렬 없음", "평균 높은 순", "평균 낮은 순"],
        horizontal=True
    )
    
    # 데이터 정렬 (요구사항 4)
    display_df = filtered_df.copy()
    if sort_options == "평균 높은 순":
        display_df = display_df.sort_values(by='평균', ascending=False)
    elif sort_options == "평균 낮은 순":
        display_df = display_df.sort_values(by='평균', ascending=True)
    
    # 데이터프레임 표시
    st.dataframe(display_df, use_container_width=True)
    
    # 필터링 결과 요약
    if len(filtered_df) < len(df):
        st.info(f"검색 결과: 총 {len(filtered_df)}명의 학생이 필터링 조건에 일치합니다.")
    
    # 메트릭 표시 (요구사항 5)
    st.subheader("주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="전체 평균 점수",
            value=f"{df['평균'].mean():.2f}"
        )
    
    with col2:
        st.metric(
            label="가장 높은 평균 점수",
            value=f"{df['평균'].max():.2f}",
            delta=f"+ {df['평균'].max() - df['평균'].mean():.2f}"
        )
    
    with col3:
        st.metric(
            label="가장 낮은 평균 점수",
            value=f"{df['평균'].min():.2f}",
            delta=f"- {df['평균'].mean() - df['평균'].min():.2f}"
        )
    
    with col4:
        st.metric(
            label=f"{selected_subject} 과목 평균",
            value=f"{df[selected_subject].mean():.2f}"
        )
    
    # 학생별 총점 데이터 표시 (요구사항 6)
    st.subheader("학생별 총점 데이터")
    
    # 총점 데이터용 데이터프레임 생성
    total_scores_df = df[['학생 이름', '학년', '총점', '평균']].copy()
    
    # 평균 점수 소수점 두 자리까지 표시
    total_scores_df['평균'] = total_scores_df['평균'].round(2)
    
    # 데이터프레임을 테이블로 표시
    st.dataframe(
        total_scores_df,
        column_config={
            "학생 이름": st.column_config.TextColumn("학생 이름"),
            "학년": st.column_config.NumberColumn("학년", format="%d학년"),
            "총점": st.column_config.NumberColumn("총점", format="%d점"),
            "평균": st.column_config.NumberColumn("평균", format="%.2f점"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # JSON 형식으로도 볼 수 있는 옵션 제공
    with st.expander("JSON 형식으로 보기"):
        total_scores = []
        for index, row in df.iterrows():
            total_scores.append({
                "id": f"student_{index}",
                "name": row['학생 이름'],
                "grade": int(row['학년']),
                "total_score": int(row['총점']),
                "average": float(row['평균'])
            })
        st.json(total_scores)

with tab2:
    st.subheader("성적 분석")
    
    # 과목별 평균 점수
    st.subheader("과목별 평균 점수")
    subject_means = pd.DataFrame({
        '과목': ['국어', '영어', '수학', '과학'],
        '평균 점수': [
            df['국어'].mean(),
            df['영어'].mean(),
            df['수학'].mean(),
            df['과학'].mean()
        ]
    })
    st.bar_chart(subject_means.set_index('과목'), use_container_width=True)
    
    # 학년별 평균 분석
    st.subheader("학년별 평균 성적")
    grade_analysis = df.groupby('학년')[['국어', '영어', '수학', '과학', '평균']].mean().reset_index()
    st.dataframe(grade_analysis.style.highlight_max(axis=0), use_container_width=True)
    
    # 학년별 평균 점수 차트
    st.line_chart(grade_analysis.set_index('학년')[['국어', '영어', '수학', '과학']], use_container_width=True)
    
    # 성적 분포 히스토그램
    st.subheader("성적 분포")
    hist_subject = st.selectbox("과목 선택", ['평균', '국어', '영어', '수학', '과학'])
    
    # 점수 범위를 나누어 히스토그램 데이터 생성 (matplotlib 없이)
    score_ranges = ["0-59", "60-69", "70-79", "80-89", "90-100"]
    score_counts = []
    
    # 각 점수 범위에 속하는 학생 수 계산
    for score_range in score_ranges:
        if score_range == "0-59":
            count = len(df[df[hist_subject] < 60])
        elif score_range == "60-69":
            count = len(df[(df[hist_subject] >= 60) & (df[hist_subject] < 70)])
        elif score_range == "70-79":
            count = len(df[(df[hist_subject] >= 70) & (df[hist_subject] < 80)])
        elif score_range == "80-89":
            count = len(df[(df[hist_subject] >= 80) & (df[hist_subject] < 90)])
        else:  # "90-100"
            count = len(df[df[hist_subject] >= 90])
        score_counts.append(count)
    
    # 히스토그램 표시 (streamlit의 차트 사용)
    hist_df = pd.DataFrame({
        '점수 범위': score_ranges,
        '학생 수': score_counts
    })
    st.bar_chart(hist_df.set_index('점수 범위'))
    
    # 성적 구간별 학생 수
    st.subheader("성적 구간별 학생 수")
    
    # 성적 구간 분류
    def get_grade(score):
        if score >= 90:
            return 'A (90-100)'
        elif score >= 80:
            return 'B (80-89)'
        elif score >= 70:
            return 'C (70-79)'
        elif score >= 60:
            return 'D (60-69)'
        else:
            return 'F (0-59)'
    
    # 각 과목별 성적 등급 계산
    grade_counts = {}
    for subject in ['국어', '영어', '수학', '과학']:
        grade_counts[subject] = df[subject].apply(get_grade).value_counts().to_dict()
    
    # 평균 성적 등급
    grade_counts['평균'] = df['평균'].apply(get_grade).value_counts().to_dict()
    
    # 과목 선택
    grade_subject = st.selectbox("과목 선택", ['평균', '국어', '영어', '수학', '과학'], key='grade_chart')
    
    # 성적 등급 차트 데이터 준비
    grade_labels = ['A (90-100)', 'B (80-89)', 'C (70-79)', 'D (60-69)', 'F (0-59)']
    grade_data = []
    
    for label in grade_labels:
        if label in grade_counts[grade_subject]:
            grade_data.append(grade_counts[grade_subject][label])
        else:
            grade_data.append(0)
    
    # 차트 표시
    grade_chart_data = pd.DataFrame({
        '등급': grade_labels,
        '학생 수': grade_data
    })
    st.bar_chart(grade_chart_data.set_index('등급'), use_container_width=True)

# 푸터
st.markdown("---")
st.caption("© 2023 학생 성적 관리 대시보드 | Streamlit으로 제작되었습니다")