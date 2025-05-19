import os
import io
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# 1) .env 로드
load_dotenv()  

# 2) 권한 범위
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

def get_drive_service():
    creds = None
    # (1) 저장된 토큰 있으면 로드
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # (2) 없거나 만료됐으면 OAuth 플로우
    if not creds or not creds.valid:
        # .env 에서 불러온 클라이언트 정보
        client_config = {
            "installed": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)

        # 발급받은 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    # Drive API 서비스 객체 반환
    return build('drive', 'v3', credentials=creds)


def upload_db_to_drive(local_path: str, drive_filename: str):
    service = get_drive_service()
    # 동일 이름 파일 검색
    query = f"name = '{drive_filename}' and trashed = false"
    resp = service.files().list(q=query, spaces='drive',
                                fields='files(id)').execute()
    files = resp.get('files', [])

    media = MediaFileUpload(local_path, mimetype='application/x-sqlite3', resumable=True)
    if files:
        # 기존 파일 업데이트
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated '{drive_filename}' (ID: {file_id})")
    else:
        # 새로 업로드
        file_metadata = {'name': drive_filename}
        created = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Uploaded new '{drive_filename}' (ID: {created['id']})")


def download_db_from_drive(drive_filename: str, local_path: str):
    service = get_drive_service()
    # 파일 검색
    query = f"name = '{drive_filename}' and trashed = false"
    resp = service.files().list(q=query, spaces='drive',
                                fields='files(id)').execute()
    files = resp.get('files', [])
    if not files:
        raise FileNotFoundError(f"Drive에서 '{drive_filename}' 파일을 찾을 수 없습니다.")
    file_id = files[0]['id']

    # 다운로드
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(local_path, mode='wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    print(f"Downloaded '{drive_filename}' to {local_path}")


if __name__ == "__main__":
    LOCAL_DB = "chat.db"
    DRIVE_NAME = "user_chat_history.db"

    # 앱 시작 시
    download_db_from_drive(DRIVE_NAME, LOCAL_DB)

    # ... SQLite 열어서 메모리 초기화 등 처리 ...

    # 세션 종료 직전 또는 저장할 때
    upload_db_to_drive(LOCAL_DB, DRIVE_NAME)
