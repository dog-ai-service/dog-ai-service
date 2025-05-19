# ui
import streamlit as st
# 구글 권한 사용을 위한 패키지
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
# 환경변수
from env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET



def drive_creds():
    client_id=GOOGLE_CLIENT_ID
    client_secret=GOOGLE_CLIENT_SECRET

    # 세션 상태에 token이 없으면 로그인 버튼 표시
    # 사용할 계정의 Google Calendar API를 사용 상태로 바꾸어야 사용가능
    if "token" not in st.session_state:
        pass
    else:
        token = st.session_state.token
        # 드라이브(스프레드시트) 사용을 위한 구글계정 정보를 세션에서 가져오기
        creds = Credentials(
            token=token["token"]["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/drive"]
        )


        return creds

# 저장용 폴더 만들고 폴거의 id값 반환
def create_folder():
    service = build("drive", "v3", credentials=drive_creds())
    folder_name='dog_ai_service'

    # 이미 존재하는 폴더가 있는지 확인
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])

    if files:
        st.info(f"📁 기존 폴더 '{folder_name}' 사용")
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        st.success(f"✅ 폴더 '{folder_name}' 생성 완료")
        return folder.get('id')

# 시트 생성
def sheet_create():
    creds = drive_creds()
    if not creds:
        st.error("❌ 먼저 로그인하세요")
        return
    folder_name='dog_ai_service'
    title="강아지 정보"

    sheet_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 이미 존재하는 폴더가 있는지 확인
    query = f"name = '{title}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
#
    if files:
        st.info(f"기존 파일 '{title}' 사용")
        spreadsheet_id=files[0]['id']
        return spreadsheet_id
    else:
        # 시트 만들기
        spreadsheet = {'properties': {'title': title}}
        try:
            sheet = sheet_service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = sheet['spreadsheetId']
            st.success(f"{title}")
        except Exception as e:
            st.error(f"오류 : {e}")
            return
#

    # 시트를 이동
    try:
        folder_id = create_folder()

        file = drive_service.files().get(fileId=spreadsheet_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))

        drive_service.files().update(
            fileId=spreadsheet_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        st.info(f"'{folder_name}' 폴더로 이동됨")
    except Exception as e:
        st.error(f"폴더 이동 오류: {e}")

    return spreadsheet_id

def sheet_read():
    pass

def sheet_update():
    pass

def sheet_delete():
    pass