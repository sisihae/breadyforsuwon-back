# BreadyForSuwon Backend

## 프로젝트 개요

**수원 빵집 투어 RAG 챗봇 백엔드**

- FastAPI 기반 REST API
- RDB (PostgreSQL) + Vector DB (Pinecone/Weaviate) 하이브리드 구조
- OpenAI GPT-4 + Embeddings를 이용한 RAG 챗봇
- CSV 데이터 자동 로드

## 빠른 시작

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 입력

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 데이터베이스 실행 (Docker)
docker-compose up -d

# 4. 데이터 로드
python scripts/load_data.py

# 5. 서버 실행
python -m uvicorn app.main:app --reload
```

## API 사용 예시

### 1. 챗봇 사용

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "분위기 좋은 카페 같은 빵집 추천해줄래?",
    "district": "영통구",
    "context_count": 5
  }'
```

### 2. 검색

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "달콤한 빵",
    "top_k": 5
  }'
```

### 3. 빵집 조회

```bash
curl "http://localhost:8000/api/v1/bakeries"
```

## 아키텍처

```
┌─ Frontend ─┐
     │
┌─ FastAPI ─┐
     │
     ├─ RAG Service ─┐
     │              ├─ LLM (GPT-4)
     │              ├─ Embeddings
     │
     ├─ PostgreSQL (구조화된 데이터)
     │
     └─ Vector DB (임베딩 데이터)
```

## 주요 기능

✅ **RAG 챗봇**: 사용자 질문에 대해 관련 빵집 정보를 바탕으로 응답
✅ **스마트 검색**: 분위기, 맛, 용도 등을 고려한 의미 있는 검색
✅ **하이브리드 DB**: 정성적 정보는 Vector DB, 정량적 정보는 RDB에 저장
✅ **CSV 임포트**: 빵집 데이터 자동 로드 및 임베딩 생성

## 확장 계획

- 🔜 사용자 인증 (JWT)
- 🔜 즐겨찾기/방문 기록
- 🔜 리뷰/평점 시스템
- 🔜 추천 알고리즘 고도화
- 🔜 모바일 앱 연동
