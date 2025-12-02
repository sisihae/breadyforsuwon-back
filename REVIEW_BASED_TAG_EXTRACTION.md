# 태그 추출 제거 안내

프로젝트에서 더 이상 리뷰 텍스트로부터 `bread_tags`를 자동 추출하지 않습니다.

- 이유: 태그는 데이터 수집(크롤링) 단계나 별도의 DB 파이프라인에서 제공됩니다.
- 영향: 서버(백엔드)는 태그를 생성하지 않으며, `bread_tags`는 CSV나 DB에 미리 채워져 있어야 합니다.

예: `bakery_list.csv`에서의 `bread_tags` 컬럼 예시

```csv
name,address,bread_tags
SweetBakery,Seoul,"[""크로아상"", ""식빵""]"
ToastShop,Seoul,"크로아상,마카롱"
```

지원되는 형식:

- JSON 배열 문자열 (예: `"[""크로아상"", ""식빵""]"`)
- 콤마로 구분된 문자열 (예: `"크로아상,마카롱"`)

참고: `app/utils.data_loader.py`의 로더는 `bread_tags`를 위 형식으로 읽어들입니다.

만약 이전에 `app.services.bread_tag_extractor`를 사용하던 코드가 있다면, 해당 임포트를 제거하거나
`bread_tags`를 외부에서 주입하도록 변경해 주세요.
