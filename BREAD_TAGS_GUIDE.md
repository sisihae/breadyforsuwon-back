# 빵 종류 태그 (Bread Tags) 설계

## 개요

빵집에서 판매하는 빵의 종류를 태그 형태로 저장하여 효율적으로 관리하고 검색할 수 있습니다.

## 데이터베이스 필드 정의

### PostgreSQL 배열 타입 사용

```python
# models/bakery.py
from sqlalchemy.dialects.postgresql import ARRAY

class Bakery(Base):
    __tablename__ = "bakeries"

    # 배열 타입으로 정의 (PostgreSQL 최적화)
    bread_tags = Column(ARRAY(String), nullable=True, default=list)
```

### 왜 배열 타입인가?

| 방식                | 장점           | 단점               |
| ------------------- | -------------- | ------------------ |
| **배열 (ARRAY)**    | ✅ 성능 좋음   | ❌ PostgreSQL 특화 |
|                     | ✅ 간단한 쿼리 |                    |
| JSON                | ✅ DB 이식성   | ⚠️ 쿼리 복잡도     |
| Many-to-Many 테이블 | ✅ 정규화      | ❌ 조인 오버헤드   |
| 텍스트 (쉼표 구분)  | ✅ 간단        | ❌ 쿼리 어려움     |

**추천**: PostgreSQL 사용 시 **ARRAY 타입** 사용

## 지원하는 빵 종류 (태그)

```python
# 현재 지원하는 빵 종류
BREAD_TAGS = [
    "크로아상",      # Croissant
    "식빵",          # Bread loaf
    "파이",          # Pie
    "케이크",        # Cake
    "슈",            # Choux (슈, 에클레어, 샹틸리)
    "마카롱",        # Macaron
    "도넛",          # Doughnut
    "베이글",        # Bagel
    "브리오슈",      # Brioche
    "바게트",        # Baguette
    "라운드빵",      # Round bread, rolls
]
```

## API 사용 예시

### 1. 빵집 생성 (빵 종류 지정)

```bash
curl -X POST "http://localhost:8000/api/v1/bakeries" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "파리바게뜨",
    "address": "수원시 영통구 영통로 123",
    "rating": 4.5,
    "bread_tags": ["크로아상", "식빵", "파이", "바게트"]
  }'
```

### 2. 빵집 업데이트 (빵 종류 수정)

```bash
curl -X PUT "http://localhost:8000/api/v1/bakeries/{bakery_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "bread_tags": ["크로아상", "케이크", "도넛"]
  }'
```

### 3. 특정 빵 종류로 검색

```bash
# POST /api/v1/search - bread_tags 필터링
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "맛있는 빵집",
    "bread_tags": ["크로아상", "식빵"],
    "top_k": 10
  }'
```

응답 예시:

```json
[
  {
    "id": "uuid-1",
    "name": "파리바게뜨",
    "address": "수원시 영통구...",
    "rating": 4.5,
    "bread_tags": ["크로아상", "식빵", "파이"],
    "similarity_score": 0.92
  },
  {
    "id": "uuid-2",
    "name": "플렁드",
    "address": "수원시 장안구...",
    "rating": 4.2,
    "bread_tags": ["크로아상", "케이크"],
    "similarity_score": 0.87
  }
]
```

### 4. 챗봇에서 빵 종류로 필터링

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "크로아상이 맛있는 빵집 추천해줄래?",
    "district": "영통구",
    "bread_tags": ["크로아상"],
    "context_count": 5
  }'
```

응답 예시:

```json
{
  "response": "영통구에서 크로아상이 유명한 빵집 3곳을 추천해드립니다...",
  "recommendations": [
    {
      "name": "파리바게뜨 영통점",
      "bread_tags": ["크로아상", "식빵", "바게트"],
      "similarity_score": 0.95
    },
    ...
  ],
  "sources_used": ["파리바게뜨 영통점", "플렁드", "베이콜로지"]
}
```

## 데이터베이스 쿼리

### PostgreSQL 배열 쿼리

```python
# 특정 태그를 포함하는 빵집 찾기
bakeries = db.query(Bakery).filter(
    Bakery.bread_tags.contains(["크로아상"])
).all()

# 여러 태그 중 하나라도 포함
bakeries = db.query(Bakery).filter(
    or_(
        Bakery.bread_tags.contains(["크로아상"]),
        Bakery.bread_tags.contains(["케이크"]),
    )
).all()

# 모든 태그 포함 (AND 로직)
bakeries = db.query(Bakery).filter(
    Bakery.bread_tags.contains(["크로아상", "식빵"])
).all()
```

### ORM 메서드

```python
# BakeryRepository의 메서드 사용
repo = BakeryRepository(db)

# 특정 빵 종류만 검색
bakeries = repo.get_by_bread_tags(
    tags=["크로아상", "파이"],
    limit=10
)

# 복합 필터링
bakeries = repo.get_by_filters(
    district="영통구",
    bread_tags=["크로아산"],
    min_rating=4.0,
    limit=20
)
```

## CSV 데이터 로드

CSV에서 `bread_tags`는 더 이상 서버에서 자동으로 생성되지 않습니다. 크롤링 또는 데이터 준비 단계에서
`bread_tags` 컬럼을 미리 채워서 저장해 주세요. 예제 형식은 `REVIEW_BASED_TAG_EXTRACTION.md`와
`app/utils/data_loader.py`를 참조하면 됩니다.

만약 프로젝트 초기 버전에서 사용하던 자동 추출 로직(패턴 기반)이 남아 있다면, 해당 코드는 제거되었으므로
관련 임포트를 삭제하고 `bread_tags`를 외부에서 주입하도록 변경해야 합니다.

## 마이그레이션 (기존 프로젝트)

### Alembic으로 마이그레이션

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Add bread_tags to bakery"

# 마이그레이션 적용
alembic upgrade head
```

### 마이그레이션 파일 예시

```python
# migrations/versions/xxx_add_bread_tags.py
def upgrade():
    op.add_column('bakeries',
        sa.Column('bread_tags',
            postgresql.ARRAY(sa.String()),
            nullable=True
        )
    )

def downgrade():
    op.drop_column('bakeries', 'bread_tags')
```

## 벡터 DB 임베딩

bread_tags는 LLM 응답 생성 시 컨텍스트로 사용됩니다.

```python
# LLM 컨텍스트에 포함
context = f"""
빵집: {bakery.name}
평점: {bakery.rating}
빵 종류: {', '.join(bakery.bread_tags) if bakery.bread_tags else '정보 없음'}
특징: {bakery.ai_summary}
"""
```

## 성능 최적화

### 인덱싱

```python
# GIN 인덱스 추가 (배열 검색 최적화)
class Bakery(Base):
    __table_args__ = (
        Index('idx_bread_tags', 'bread_tags',
              postgresql_using='gin'),
    )
```

SQL:

```sql
CREATE INDEX idx_bread_tags ON bakeries USING GIN (bread_tags);
```

### 쿼리 성능

- 배열 `contains` 쿼리: **O(1)** (인덱스 사용 시)
- 일반 문자열 검색: **O(n)**

## 향후 확장

- [ ] 태그 별 평점 집계
- [ ] 인기 빵 종류 순위
- [ ] 사용자 선호도 기반 추천
- [ ] 빵 종류별 가격 평균
- [ ] 계절별 특별 빵 정보
