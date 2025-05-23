# DOG-AI-SERVICE
반려견과 보호자를 위한 AI 비서

---

## 프로젝트의 기능
> 1.구글 계정을 통한 구글 캘린더와의 연동  
>
> 2.LLM을 통한 구글 캘린더에 일정 푸쉬  
>
> 3.AI 챗봇 (DuckDuckGo와 구글엔진을 사용)
>
> 4.강아지 증상 전문 AI챗봇 (라마 인덱스 백터 DB사용한 RAG기반)  
>> 증상 기입 시 구글 드라이브에 증상을 정리한 건강 노트 생성 후 건강노트페이지에 출력  
>> 건강노트 pdf 출력기능  
> 
> 5.LLM을 이용한 추천 스케줄 생성기 (RAG기반)  
>> 유저페이지에 입력된 강아지 정보를 바탕으로 추천 스케줄을 생성  
>> 사용자가 원할 시 구글 캘린더에 푸쉬  
>




---

## 역할 + 기록
### 성한빈
```
역할 : 챗봇(랭체인 에이전트 적용, 히스토리, 콜백 처리), 사용자 정보 페이지(강아지 등록 및 수정 폼), 개인화된 강아지 스케줄링 모듈, 구글 드라이브 연동(부)

```
### 심규상
```
역할 : 강아지 증상 데이터를 벡터 DB에 저장하고, 이를 기반으로 질문에 답하는 전문 챗봇 설계, LLM과 캘린더 연동(주)

--> 5월 19일 : Rag데이터 구축 완료, indexdb 구축 완료


--> 내 캘린더 안되던 원인 
: 병재님 코드에서 이벤트 가져오는 방식을 보면 CalendarID를 primary로 가져오게 되어있음 --> 즉, 계정 생성시 생기는 고유한 캘린더인듯

- 우선 사용자가 증상을 입력하게 되면 자동으로 구글 스프레드 시트에 기입되도록 함.
- 또한, 증상 노트 페이지에서 자동으로 뜨도록 설정함.

--> 5월 20일 증상 챗봇과 강아지 증상 노트 연동 완료

추가하고 싶은 기능 : 3. 강아지 이름 추천 서비스
추가할 기능 : 챗봇에서 먼저 이름을 적고(혹은 견종 목록에서 고르게) 질의 -> 요약 노트에서 자동으로 이름이 기입된 pdf 이름 생성

```
### 오병재
```
역할 : 깃허브 관리, 로그인, 백엔드, LLM과 캘린더 연동(부), 구글 드라이브 연동(주)

1. 캘린더 수정,삭제 기능만 추가하고 마무리
2. 원하는 llm 이용한거 추가해보자 애견관련 호텔이나 매장 서치 챗봇같은거 ㄱㄱ
10. MCP 를 이용한 자동화 시스템


services\AI와 pages/chatbot.py pages/health_note.py가 연동되어있음을 기억하셈



```

---
랭체인 에이전트 이용해서 챗봇 응답처리
## 디렉토리 구조

```
dog_ai_service/
├── app.py                        : 메인 기능 실행 파일
├── .env                          : 환경변수 파일 (Git 예외처리됨, **파일명 절대 변경 금지**)
├── env_config.py                 : 환경변수 로드 모듈
├── requirements.txt              : 패키지 설치 파일
├── test.py                       : 테스트용 파일
├── .gitignore                    : Git 예외 설정
│
├── other_files/                        : 기타 파일 (예: PDF 등)
│   └── 반려견_AI_비서_기획안_최종.pdf
|
├── index_db_backup                     : 증상 데이터를 담은 벡터디비
│
├── components/                   : Streamlit UI 컴포넌트
│   ├── prompt_box.py             : 질문 입력창 컴포넌트
│   ├── sidebar.py                : 사이드바 UI 컴포넌트
│   ├── dog_data.py               : dog_ui 데이터
│   ├── dog_ui.py                 : 강아지 정보 UI
│   ├── dog_schedule.py           : 강아지 스케줄링 모듈
│   ├── schedule_to_calendar.py   : 스케줄 데이터 -> 캘린더 푸쉬 / 일정 최신화 업데이트
│   ├── st_calendar.py            : Streamlit용 캘린더 출력 컴포넌트
|   ├── create_schedulr.py        : 일정 생성 / 일정 요약 출력 컴포넌트트
|   └── symptom_chatbot.py        : 증상 전문 챗봇 컴포넌트
│    
├── pages/                        : Streamlit 내비게이션 페이지들
│   ├── calendar_page.py          : 캘린더 페이지
│   ├── chatbot.py                : 챗봇 페이지
│   └── health_note.py            : 건강 노트 페이지
│
└── services/                     : 서비스 API 모듈
    ├── tasks_api.py              : 구글 Tasks API 처리
    ├── calendar_api.py           : 캘린더 API 처리
    ├── login_api.py              : 로그인 처리 API
    ├── drive_api.py              : 구글 드라이브(시트) API
    ├── get_today_events.py       : 당일 이벤트 리턴해주는 모듈 (필요 없을 지도?)
    └── AI/                       : AI 관련 기능 모듈
        ├── extract_event_info.py : 자연어(사용자 프롬프트)를 json으로 변환하는 모듈
        └── summation.py          : 당일 이벤트를 입력으로 받고, 요약하는 모듈


```

---

## 서버 실행/점검 커멘드
> streamlit run app.py --server.port 8080  
> streamlit hello

---

## Git 커밋명 규칙
```
- **Feat : 신규 기능 추가**
- **Fix : 버그 수정 **
- Build : 빌드 관련 파일 수정
- Chore : 기타 수정
- Ci : 지속적 개발에 따른 수정
- Docs : 문서 수정
- Style : 코드 스타일, 포멧형식 관련
- Refactor : 리팩토링
- Test : 테스트 코드 수정
```

---

## 주의사항
> .env에는 gpt의 api-key 유출 방지로 Git 예외처리를 하여 수동으로 다운로드해줘야함  
> 중요 key가 있다면 유출되지 않도록 주의!  

---

## 각 branch 용도
> ### main(*중요)
>> 메인 branch  
>> main에 대한 모든 업데이트는 **test에서 먼저 시도**하여 이상이 없을 시에 **팀원 모두의 동의**를 구하고한다.
>
> ### test
>> 각자의 개인 branch에서의 업데이트를 먼저 테스트 해보는 곳.
>
> ### backup
>> 만일의 사태를 대비한 백업용 branch  
>> main이나 test에서 이상이 없다면 주기적으로 백업해두자
>
> ### hanbin
>> 성한빈 개인 branch
>> #### hanbin-test
>>> 성한빈 개인 테스트 branch
> ### kyusang
>> 심규상 개인 branch
> ### obj, obj키워드가 들어가는 브랜치
>> 오병재 개인 branch


---

## 초기 설정
> 패키지 설치
>> pip install -r requirements.txt  

## Git 초기설정.
>터미널/cmd/git bash에서 프로젝트를 저장할 위치로 이동 후 아래 코드 입력
>> git clone https://github.com/dog-ai-service/dog-ai-service.git  
>
> vscode에서 해당 프로젝트를 폴더 열기  
> vscode의 터미널에서 아래 코드 입력
>> git switch test  
>> git switch -c [원하는 개인 branch명]  
>
> 좌측 소스 제어(깃)에서 [게시 Branch] 버튼 클릭
> 
> 아래 코드를 입력하여 각 branch가 제대로 추가되었는지 확인  
>> git branch -r
>


---

## GIT 명령어 모음
> branch 새로 생성 후 해당 branch로 즉시 전환
>> git switch -c [branch명]
>
> 로컬(개인컴) branch 목록 조회(*로 강조된 곳이 현재 branch)
>> git branch
>
> 원격(깃허브) branch 목록 조회(*로 강조된 곳이 현재 branch)
>> git branch -r
>
> branch 전환 코드 2가지(최근에는 switch를 더 자주 사용한다고함. checkout은 참고용)
>> git switch [branch명]
>> git checkout [branch명]
>
> branch 병합하기(현재 branch를 대상으로 명령어의 branch를 덮어씌우는 느낌)
>> git merge [branch명]
>
> 해당 커밋의 수정사항'만' 취소하고 새로 커밋하는 명령어
>> git revert <되돌리고 싶은 커밋 id>  
>> ```코드 입력 시 터미널에 이상한 코드가(vi이라고 .txt랑 비슷한 느낌)가 나오면 esc > :q 입력 > 엔터 누르고 깃헙에 푸쉬하면 적용완료```
>
> 병합 도중 병합하기 전으로 되돌리고 싶을 때  
>> git merge --abort  



---

## .gitignore 사용법 예시 (원하는 파일의 커밋제한)
>// 1. '파일명'으로 제외하는 방법 (* 해당 방법은 경로 상관없이 지정한 파일명으로 모두 제외할 수 있다)  
>ignoreFileName.js
>
>// 2. 특정 '파일'만 제외하는 방법 (* 현재 기준을 .ignore파일이 있는 경로라고 생각하면 된다)  
>src/ignoreFileName.js
>
>// 3. 특정 '디렉토리' 기준 이하 파일들 제외 방법  
>node_module/
>
>// 4. 특정 디렉토리 하위의 특정 '확장자' 제외하는 방법  
>src/*.txt
>
>// 5. 특정 디렉토리 하위의 그 하위의 특정 '확장자' 제외하는 방법  
>src/**/*.txt
>
>// 6. 특정 '확장자' 제외하기  
>.txt
>
>// 7. 4번 특정 '확장자'에서 일부 제외 할 파일  
>!manual.txt

---

## ppt 자료 출처
```

2024년 국내 반려동물 양육 비율 약 28.6%…역대 최고
https://www.dailyvet.co.kr/news/policy/234742

반려동물 보호자 ‘건강’에 가장 관심 많아..신뢰하는 정보 채널은 동물병원
https://www.dailyvet.co.kr/news/industry/187304

[트렌드] 동물병원 年 100개씩 늘어도 반려동물 의료비 높아지는 까닭은
https://biz.chosun.com/topics/topics_social/2024/06/09/65V3M3Y6HZD6TFTHX264H5OC34/

```

```