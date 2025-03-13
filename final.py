import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")


# 벡터 저장소 디렉토리 설정
VECTOR_STORE_DIR = "vectorstore"

def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.getvalue())
        temp_file_path = temp_file.name

    doc = fitz.open(temp_file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
        
    # 파일 닫기
    doc.close()

    # 임시 파일 삭제
    os.unlink(temp_file_path)
    return text
def create_vectorstore(text, embeddings):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    documents = text_splitter.create_documents([text])

    # 청크 수 반환
    return FAISS.from_documents(documents, embeddings), len(documents)
st.set_page_config(page_title="📚 PDF RAG 시스템", layout="wide")
st.title("📚 PDF 기반 질의응답 시스템")
with st.sidebar:
    st.header("⚙️ 설정")
    user_api_key = st.text_input("OpenAI API 키", value=OPENAI_API_KEY, type="password")
    if user_api_key:
        os.environ["OPENAI_API_KEY"] = user_api_key

    st.markdown("---")
    st.markdown("### 🔍 모델 설정")
    model_name = st.selectbox(
        "OpenAI 모델 선택",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0
    )
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

    st.markdown("---")
    st.markdown("### 📊 청크 설정")
    chunk_size = st.slider("청크 크기", min_value=500, max_value=2000, value=1000, step=100)
    chunk_overlap = st.slider("청크 오버랩", min_value=0, max_value=500, value=100, step=50)
    
tab1, tab2 = st.tabs(["📤 PDF 업로드", "❓ 질의응답"])
with tab1:
    st.header("PDF 파일 업로드")
    uploaded_file = st.file_uploader("PDF 파일을 선택하세요", type="pdf")

    if uploaded_file is not None:
        with st.spinner("PDF 파일 처리 중... 잠시만 기다려주세요."):
            # PDF 텍스트 추출
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.pdf_text = text

            # 텍스트의 일부분 미리보기 표시
            st.subheader("PDF 텍스트 미리보기")
            st.text_area("추출된 텍스트", text[:1000] + ("..." if len(text) > 1000 else ""), height=200)
            # 벡터 저장소 생성
            if st.button("벡터 저장소 생성", use_container_width=True):
                if not user_api_key:
                    st.error("OpenAI API 키를 입력해주세요.")
                else:
                    with st.spinner("벡터 저장소 생성 중... 이 작업은 몇 분 정도 소요될 수 있습니다."):
                        try:
                            embeddings = OpenAIEmbeddings()

                            # 사용자 정의 청크 설정 적용
                            text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap
                            )
                            documents = text_splitter.create_documents([text])

                            # 벡터 저장소 생성
                            vectorstore = FAISS.from_documents(documents, embeddings)

                            # 세션에 저장
                            st.session_state.vectorstore = vectorstore
                            st.session_state.document_chunks = len(documents)

                            # 성공 메시지
                            st.success(f"✅ 벡터 저장소 생성 완료! {len(documents)}개의 청크로 분할되었습니다.")
                            st.info("이제 '질의응답' 탭에서 질문을 해보세요!")
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")
with tab2:
    st.header("PDF 기반 질의응답")

    # 벡터 저장소가 생성되었는지 확인
    if 'vectorstore' not in st.session_state:
        st.warning("먼저 'PDF 업로드' 탭에서 PDF를 업로드하고 벡터 저장소를 생성해주세요.")
    else:
        st.success(f"✅ {st.session_state.get('document_chunks', 0)}개의 청크가 준비되었습니다.")

        # 질문 입력
        query = st.text_input("질문을 입력하세요", placeholder="예: 이 문서의 주요 내용은 무엇인가요?")
        if query:
            # 사용자가 입력한 API 키 확인
            if not user_api_key:
                st.error("OpenAI API 키를 입력해주세요.")
            else:
                with st.spinner("답변 생성 중..."):
                    try:
                        # LLM 및 검색 체인 설정
                        llm = ChatOpenAI(
                            model_name=model_name,
                            temperature=temperature
                        )

                        # 검색기 설정
                        retriever = st.session_state.vectorstore.as_retriever(
                            search_type="similarity",
                            search_kwargs={"k": 3}
                        )

                        # QA 체인 생성
                        qa_chain = RetrievalQA.from_chain_type(
                            llm=llm,
                            chain_type="stuff",
                            retriever=retriever,
                            return_source_documents=True
                        )

                        # 질의응답 실행
                        result = qa_chain({"query": query})

                        # 결과 표시
                        st.subheader("📝 답변")
                        st.write(result["result"])

                        # 참조 문서 표시
                        with st.expander("📚 참조된 문서 청크"):
                            for i, doc in enumerate(result["source_documents"]):
                                st.markdown(f"**청크 {i+1}**")
                                st.text(doc.page_content)
                                st.markdown("---")

                    except Exception as e:
                        st.error(f"오류 발생: {str(e)}")
# 푸터
st.markdown("---")
st.caption("멋쟁이 사자처럼")
