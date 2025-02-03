import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
import requests
import logging
import argparse
import pandas as pd
import time

class MiroBoardBackup:
    """Miroボードのアイテムとコネクターをバックアップするクラス"""
    
    def __init__(self, access_token: str):
        """
        初期化
        
        Args:
            access_token (str): Miro APIのアクセストークン
        """
        if not access_token.startswith('oauth2:'):
            access_token = f'oauth2:{access_token}'
            
        self.access_token = access_token
        self.base_url = "https://api.miro.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        self.logger = logging.getLogger(__name__)

    def get_board_info(self, board_id: str) -> Dict[str, Any]:
        """ボード基本情報を取得"""
        response = requests.get(
            f"{self.base_url}/boards/{board_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_paginated_data(self, url: str, resource_type: str) -> List[Dict[str, Any]]:
        """
        ページネーション対応でデータを取得
        
        Args:
            url (str): APIエンドポイントのURL
            resource_type (str): 取得するリソースの種類（'items' または 'connectors'）
            
        Returns:
            List[Dict[str, Any]]: 取得したデータのリスト
        """
        items = []
        limit = 50
        cursor = ""

        while True:
            params = {"limit": limit}
            if cursor:
                params["cursor"] = cursor

            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            current_items = data.get('data', [])
            if not current_items:
                break

            items.extend(current_items)
            total_items = data.get('total', 0)
            self.logger.info(f"{resource_type}: {total_items}個中{len(items)}個を取得しました")

            links = data.get('links', {})
            if 'next' not in links:
                break

            next_url = links['next']
            from urllib.parse import urlparse, parse_qs
            query_params = parse_qs(urlparse(next_url).query)
            cursor = query_params.get('cursor', [''])[0]

        return items

    def get_board_items(self, board_id: str) -> List[Dict[str, Any]]:
        """ボード内のすべてのアイテムを取得"""
        url = f"{self.base_url}/boards/{board_id}/items"
        return self.get_paginated_data(url, "アイテム")

    def get_board_connectors(self, board_id: str) -> List[Dict[str, Any]]:
        """ボード内のすべてのコネクターを取得"""
        url = f"{self.base_url}/boards/{board_id}/connectors"
        return self.get_paginated_data(url, "コネクター")

    def backup_board(self, board_id: str, board_name: str = "") -> str:
        """
        ボードの情報をバックアップ（アイテムとコネクターを含む）
        
        Args:
            board_id (str): バックアップ対象のボードID
            board_name (str): ボード名（CSVから取得した場合）
            
        Returns:
            str: バックアップファイルのパス
        """
        try:
            board_info = self.get_board_info(board_id)
            self.logger.info(f"ボード情報を取得しました: {board_name or board_info.get('name', board_id)}")
            
            items = self.get_board_items(board_id)
            self.logger.info(f"ボードから{len(items)}個のアイテムを取得しました")

            connectors = self.get_board_connectors(board_id)
            self.logger.info(f"ボードから{len(connectors)}個のコネクターを取得しました")
            
            backup_data = {
                'board_info': board_info,
                'items': items,
                'connectors': connectors,
                'metadata': {
                    'backup_date': datetime.now().isoformat(),
                    'total_items': len(items),
                    'total_connectors': len(connectors)
                }
            }
            
            # バックアップディレクトリの作成
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = backup_dir / f"backup_{board_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"バックアップが完了しました: {filename}")
            return str(filename)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"APIリクエストが失敗しました: {str(e)}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"エラー詳細: {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"バックアップが失敗しました: {str(e)}")
            raise

def read_token_from_env() -> str:
    """環境変数からトークンを読み出す"""
    try:
        env_path = Path('.') / '.env'
        if not env_path.exists():
            raise FileNotFoundError(".envファイルが見つかりません")

        load_dotenv(env_path)
        access_token = os.getenv('MIRO_ACCESS_TOKEN')
        
        if not access_token:
            raise ValueError(".envファイル内にMIRO_ACCESS_TOKENが設定されていないか、値が空です")
            
        return access_token.strip()

    except Exception as e:
        logging.error(f".envファイルの読み込みエラー: {str(e)}")
        raise

def read_board_ids_from_csv(csv_path: str) -> pd.DataFrame:
    """CSVファイルからボードIDを読み込む"""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        if 'boardID' not in df.columns:
            raise ValueError("CSVファイルに'boardID'列が存在しません")
        return df
    except Exception as e:
        logging.error(f"CSVファイルの読み込みエラー: {str(e)}")
        raise

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='Miroボードのアイテムとコネクターをバックアップするツール')
    parser.add_argument('-c', '--csv-file', help='ボードIDが記載されたCSVファイルのパス')
    parser.add_argument('-b', '--board-id', help='単一のボードIDをバックアップする場合に指定')
    parser.add_argument('-i', '--interval', type=int, default=1, help='バックアップ間隔（秒）。デフォルト: 1秒')
    args = parser.parse_args()

    if not args.csv_file and not args.board_id:
        parser.error("--csv-file または --board-id のいずれかを指定してください")

    try:
        access_token = read_token_from_env()
        backup = MiroBoardBackup(access_token)

        if args.csv_file:
            df = read_board_ids_from_csv(args.csv_file)
            total_boards = len(df)
            logging.info(f"CSVファイルから{total_boards}個のボードを読み込みました")

            for index, row in df.iterrows():
                board_id = row['boardID']
                board_name = row['ボード名'] if 'ボード名' in df.columns else ""
                
                logging.info(f"バックアップ進捗: {index + 1}/{total_boards}")
                logging.info(f"ボード '{board_name or board_id}' のバックアップを開始します")
                
                try:
                    backup.backup_board(board_id, board_name)
                except Exception as e:
                    logging.error(f"ボード '{board_name or board_id}' のバックアップ中にエラーが発生しました: {str(e)}")
                    continue
                
                if index < total_boards - 1:  # 最後のボード以外は待機
                    time.sleep(args.interval)
        
        else:
            backup_file = backup.backup_board(args.board_id)
            print(f"\nバックアップが完了しました: {backup_file}")
        
    except Exception as e:
        logging.error(f"エラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()