# バックアップされたJSONファイルの構造

{
  "board_info": { ... },
  "items": [ ... ],
  "connectors": [ ... ],
  "metadata": {
    "backup_date": "2024-02-03T12:34:56.789",
    "total_items": 100,
    "total_connectors": 50
  }
}

# 構成の補足

このJSONファイルは以下より構成されている。

## board_info: ボード全体の情報を含むセクション

- 基本情報 (ID, 名前, タイプなど)
- 作成・更新情報
- 権限とポリシー設定
- チーム情報

## items: ボード上のカード要素の配列

- 各カードの基本情報
- スタイル設定
- 位置情報
- コンテンツデータ

## connectors: カード間の接続情報を含む配列

- 接続の始点と終点
- スタイル設定
- 形状情報

## metadata: バックアップ情報など

- バックアップ日時
- 総アイテム数
- 総コネクタ数

---

# JSONファイルのスキーマ

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["board_info", "items", "connectors", "metadata"],
  "properties": {
    "board_info": {
      "type": "object",
      "required": ["id", "type", "name", "links", "createdAt", "createdBy", "modifiedAt", "modifiedBy", "owner", "permissionsPolicy", "picture", "policy", "sharingPolicy", "team", "viewLink"],
      "properties": {
        "id": { "type": "string" },
        "type": { "type": "string", "enum": ["board"] },
        "name": { "type": "string" },
        "description": { "type": "string" },
        "links": {
          "type": "object",
          "required": ["self", "related"],
          "properties": {
            "self": { "type": "string", "format": "uri" },
            "related": { "type": "string", "format": "uri" }
          }
        },
        "createdAt": { "type": "string", "format": "date-time" },
        "createdBy": {
          "type": "object",
          "required": ["id", "type", "name"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string", "enum": ["user"] },
            "name": { "type": "string" }
          }
        },
        "lastOpenedAt": { "type": "string", "format": "date-time" },
        "lastOpenedBy": {
          "type": "object",
          "required": ["id", "type", "name"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string", "enum": ["user"] },
            "name": { "type": "string" }
          }
        },
        "modifiedAt": { "type": "string", "format": "date-time" },
        "modifiedBy": {
          "type": "object",
          "required": ["id", "type", "name"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string", "enum": ["user"] },
            "name": { "type": "string" }
          }
        },
        "owner": {
          "type": "object",
          "required": ["id", "type", "name"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string", "enum": ["user"] },
            "name": { "type": "string" }
          }
        },
        "permissionsPolicy": {
          "type": "object",
          "required": ["collaborationToolsStartAccess", "copyAccess", "copyAccessLevel", "sharingAccess"],
          "properties": {
            "collaborationToolsStartAccess": { "type": "string" },
            "copyAccess": { "type": "string" },
            "copyAccessLevel": { "type": "string" },
            "sharingAccess": { "type": "string" }
          }
        },
        "picture": {
          "type": "object",
          "required": ["id", "type", "imageURL"],
          "properties": {
            "id": { "type": "number" },
            "type": { "type": "string", "enum": ["picture"] },
            "imageURL": { "type": "string", "format": "uri" }
          }
        },
        "policy": {
          "type": "object",
          "required": ["permissionsPolicy", "sharingPolicy"],
          "properties": {
            "permissionsPolicy": {
              "type": "object",
              "properties": {
                "collaborationToolsStartAccess": { "type": "string" },
                "copyAccess": { "type": "string" },
                "copyAccessLevel": { "type": "string" },
                "sharingAccess": { "type": "string" }
              }
            },
            "sharingPolicy": {
              "type": "object",
              "properties": {
                "access": { "type": "string" },
                "inviteToAccountAndBoardLinkAccess": { "type": "string" },
                "organizationAccess": { "type": "string" },
                "teamAccess": { "type": "string" }
              }
            }
          }
        },
        "sharingPolicy": {
          "type": "object",
          "required": ["access", "inviteToAccountAndBoardLinkAccess", "organizationAccess", "teamAccess"],
          "properties": {
            "access": { "type": "string" },
            "inviteToAccountAndBoardLinkAccess": { "type": "string" },
            "organizationAccess": { "type": "string" },
            "teamAccess": { "type": "string" }
          }
        },
        "team": {
          "type": "object",
          "required": ["id", "type", "name"],
          "properties": {
            "id": { "type": "string" },
            "type": { "type": "string", "enum": ["team"] },
            "name": { "type": "string" }
          }
        },
        "viewLink": { "type": "string", "format": "uri" }
      }
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "data", "style", "geometry", "position", "links", "createdAt", "createdBy", "modifiedAt", "modifiedBy"],
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string", "enum": ["card"] },
          "data": {
            "type": "object",
            "required": ["dueDate", "title"],
            "properties": {
              "dueDate": { "type": "string", "format": "date-time" },
              "title": { "type": "string" }
            }
          },
          "style": {
            "type": "object",
            "required": ["cardTheme"],
            "properties": {
              "cardTheme": { "type": "string" }
            }
          },
          "geometry": {
            "type": "object",
            "required": ["width", "height"],
            "properties": {
              "width": { "type": "number" },
              "height": { "type": "number" }
            }
          },
          "position": {
            "type": "object",
            "required": ["x", "y", "origin", "relativeTo"],
            "properties": {
              "x": { "type": "number" },
              "y": { "type": "number" },
              "origin": { "type": "string" },
              "relativeTo": { "type": "string" }
            }
          },
          "links": {
            "type": "object",
            "required": ["self"],
            "properties": {
              "self": { "type": "string", "format": "uri" }
            }
          }
        }
      }
    },
    "connectors": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "links", "startItem", "endItem", "createdAt", "createdBy", "modifiedAt", "modifiedBy", "shape", "style", "type"],
        "properties": {
          "id": { "type": "string" },
          "links": {
            "type": "object",
            "required": ["self"],
            "properties": {
              "self": { "type": "string", "format": "uri" }
            }
          },
          "startItem": {
            "type": "object",
            "required": ["links", "id"],
            "properties": {
              "links": {
                "type": "object",
                "required": ["self"],
                "properties": {
                  "self": { "type": "string", "format": "uri" }
                }
              },
              "id": { "type": "string" },
              "position": {
                "type": "object",
                "properties": {
                  "x": { "type": "string" },
                  "y": { "type": "string" }
                }
              }
            }
          },
          "endItem": {
            "type": "object",
            "required": ["links", "id"],
            "properties": {
              "links": {
                "type": "object",
                "required": ["self"],
                "properties": {
                  "self": { "type": "string", "format": "uri" }
                }
              },
              "id": { "type": "string" },
              "position": {
                "type": "object",
                "properties": {
                  "x": { "type": "string" },
                  "y": { "type": "string" }
                }
              }
            }
          },
          "shape": { "type": "string" },
          "style": {
            "type": "object",
            "required": ["startStrokeCap", "endStrokeCap", "strokeWidth", "strokeStyle", "strokeColor"],
            "properties": {
              "startStrokeCap": { "type": "string" },
              "endStrokeCap": { "type": "string" },
              "strokeWidth": { "type": "string" },
              "strokeStyle": { "type": "string" },
              "strokeColor": { "type": "string" }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["backup_date", "total_items", "total_connectors"],
      "properties": {
        "backup_date": { "type": "string", "format": "date-time" },
        "total_items": { "type": "integer" },
        "total_connectors": { "type": "integer" }
      }
    }
  }
}
