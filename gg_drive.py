import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# 1. 권한 범위 설정 (드라이브 전체 읽기/쓰기)
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_drive_service():
    creds = None
    # (1) 이전에 발급받은 토큰이 있으면 로드
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # (2) 없거나 만료됐으면 OAuth 플로우
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        # 새 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    # Drive API 서비스 객체 반환
    return build('drive', 'v3', credentials=creds)


def upload_db_to_drive(local_path: str, drive_filename: str):
    """
    1) 로컬의 local_path 파일을
    2) 구글 드라이브 내 파일명 drive_filename 으로 업로드(또는 업데이트)
    """
    service = get_drive_service()

    # (A) 먼저 동일 이름 파일이 있는지 검색
    query = f"name = '{drive_filename}' and trashed = false"
    resp = service.files().list(q=query, spaces='drive',
                                fields='files(id, name)').execute()
    files = resp.get('files', [])

    media = MediaFileUpload(local_path, mimetype='application/x-sqlite3', resumable=True)

    if files:
        # (B) 이미 있으면 update
        file_id = files[0]['id']
        updated = service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"Updated file '{drive_filename}' (ID: {file_id})")
    else:
        # (C) 없으면 새로 생성
        file_metadata = {'name': drive_filename}
        created = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Uploaded new file '{drive_filename}' (ID: {created['id']})")


def download_db_from_drive(drive_filename: str, local_path: str):
    """
    1) 드라이브에서 drive_filename 파일을 찾아
    2) 로컬에 local_path 로 다운로드
    """
    service = get_drive_service()

    # (A) 파일 검색
    query = f"name = '{drive_filename}' and trashed = false"
    resp = service.files().list(q=query, spaces='drive',
                                fields='files(id, name)').execute()
    files = resp.get('files', [])

    if not files:
        raise FileNotFoundError(f"Drive에서 '{drive_filename}' 파일을 찾을 수 없습니다.")
    file_id = files[0]['id']

    # (B) 다운로드 수행
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(local_path, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    print(f"Downloaded '{drive_filename}' to {local_path}")


if __name__ == "__main__":
    LOCAL_DB = "chat.db"
    DRIVE_NAME = "user_chat_history.db"

    # 예: 로그인 시
    download_db_from_drive(DRIVE_NAME, LOCAL_DB)

    # ... (여기서 SQLite 열어서 메모리 초기화 등 처리) ...

    # 예: 세션 종료 직전 또는 메시지 저장 시
    upload_db_to_drive(LOCAL_DB, DRIVE_NAME)
