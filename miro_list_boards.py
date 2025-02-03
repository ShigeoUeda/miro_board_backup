import requests
import json
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List
import csv
from dotenv import load_dotenv
import os

class MiroBoardLister:
    """
    Miroの全ボード情報を取得し、リスト化するクラス
    """
    
    def __init__(self, access_token: str):
        """
        初期化
        
        引数:
            access_token (str): Miro APIのアクセストークン
        """
        # トークンにoauth2:プレフィックスがない場合は追加
        if not access_token.startswith('oauth2:'):
            access_token = f'oauth2:{access_token}'

        self.access_token = access_token
        self.base_url = "https://api.miro.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # デバッグ用：認証ヘッダーの内容を確認（トークンの一部を隠す）
        # auth_debug = self.headers["Authorization"]
        # if len(auth_debug) > 20:
        #     auth_debug = f"{auth_debug[:20]}...{auth_debug[-5:]}"
        # print("Debug: Authorization header:", auth_debug)
        
        # ロギングの設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_all_boards(self) -> List[Dict]:
        """
        アクセス可能な全ボードの情報を取得（offsetベースのページネーション）
        
        戻り値:
            List[Dict]: ボード情報のリスト
        """
        boards = []
        offset = 0
        limit = 50
        total = None
        page_count = 1
        
        try:
            while True:
                # クエリパラメータの設定
                params = {
                    "limit": limit,
                    "offset": offset
                }
                
                # APIリクエストの実行
                response = requests.get(
                    f"{self.base_url}/boards",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                # レスポンスの解析
                data = response.json()
                
                # デバッグ情報の出力
                # print(f"\n=== API Response (Page {page_count}) ===")
                # print(json.dumps(data, indent=2, ensure_ascii=False))
                # print("===================================")
                
                # 初回実行時にtotalを取得
                if total is None:
                    total = data.get('total', 0)
                    print(f"\nTotal boards available: {total}")
                
                # 取得したボードを追加
                current_boards = data.get('data', [])
                boards.extend(current_boards)
                
                # 取得状況のログ出力
                # print(f"Current page boards count: {len(current_boards)}")
                # print(f"Total boards retrieved so far: {len(boards)}")
                
                # 次のページがあるかチェック
                if offset + limit >= total or not current_boards:
                    # print("\nNo more pages to fetch")
                    break
                
                offset += limit
                page_count += 1
                # print(f"Moving to next page with offset: {offset}")
            
            print(f"\n=== Summary ===")
            print(f"Total pages retrieved: {page_count}")
            print(f"Total boards retrieved: {len(boards)}")
            
            return boards
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"ボード情報の取得に失敗しました: {str(e)}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"エラーの詳細: {e.response.text}")
            raise
        
    def save_board_list(self, boards: List[Dict], output_format: str = 'csv') -> None:
        """
        ボードリストを保存
        
        引数:
            boards: ボード情報のリスト
            output_format: 出力形式 ('csv' または 'both')
        """
        # CSVとして保存
        csv_path = "board_list.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 指定された順序でヘッダーを書き込み
            writer.writerow(['ボード名', 'boardID', '作成日時', 'アクセスURL'])
            
            # データを書き込み
            for board in sorted(boards, key=lambda x: x.get('name', '')):  # ボード名でソート
                writer.writerow([
                    board.get('name', ''),           # ボード名
                    board.get('id', ''),             # boardID
                    board.get('createdAt', ''),      # 作成日時
                    board.get('viewLink', '')        # アクセスURL
                ])
        
        self.logger.info(f"CSVファイルを保存しました: {csv_path}")
        print(f"\n保存したボードの総数: {len(boards)}")
        
        # JSONも保存する場合（'both'が指定された場合）
        if output_format == 'both':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"miro_boards_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "boards": boards,
                    "metadata": {
                        "total_boards": len(boards),
                        "generated_at": datetime.now().isoformat()
                    }
                }, f, indent=2, ensure_ascii=False)
            self.logger.info(f"JSONファイルを保存しました: {json_path}")

def read_token_from_env() -> str:
    """
    .envファイルからトークンを読み出す
    
    戻り値:
        str: アクセストークン
    """
    try:
        env_path = Path('.') / '.env'
        if not env_path.exists():
            raise FileNotFoundError(".envファイルが見つかりません")

        # .envファイルの内容をログ出力（トークンは一部のみ表示）
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
            logging.info(f".envファイルの内容:\n{env_content.replace(env_content.strip(), '***[masked]***')}")

        # .envファイルを読み込み
        load_dotenv(env_path)
        
        # 環境変数からトークンを取得
        access_token = os.getenv('MIRO_ACCESS_TOKEN')
        if not access_token:
            raise ValueError(".envファイル内にMIRO_ACCESS_TOKENが設定されていないか、値が空です")
        
        # トークンの最初の10文字のみをログ出力
        # print(f"Debug: Token format check:")
        # print(f"Token length: {len(access_token)}")
        # print(f"Token starts with: {access_token[:10]}...")
        # print(f"Raw token: {repr(access_token)}")
            
        return access_token.strip()  # 余分な空白を除去

    except Exception as e:
        logging.error(f".envファイルの読み込みエラー: {str(e)}")
        raise

def main():
    """
    メイン実行関数
    """
    try:
        # .envファイルからトークンを読み出し
        access_token = read_token_from_env()
        
        # ボードリスト取得の実行
        lister = MiroBoardLister(access_token)
        boards = lister.get_all_boards()
        
        # CSVとして保存（必要に応じて'both'を指定してJSONも保存）
        lister.save_board_list(boards)
        
    except Exception as e:
        logging.error(f"プロセスが失敗しました: {str(e)}")

if __name__ == "__main__":
    main()