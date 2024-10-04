# -*- coding: utf-8 -*-
"""
File: chroma_client.py
Description: Manages interactions with the CHROMA service for face recognition data storage.
Author: Wang Zhiwei, Zhao Zheyun
Date: 2024.07.03

Copyright (C) 2024 Wang Zhiwei, Zhao Zheyun. All rights reserved.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
Contact: zhaozy@example.com
"""

import chromadb

from config.settings import CHROMA_CONFIG

CHROMA_SERVICE_HOST = CHROMA_CONFIG['HOST']
CHROMA_SERVER_PORT = CHROMA_CONFIG['PORT']

client = chromadb.HttpClient(host=CHROMA_SERVICE_HOST, port=CHROMA_SERVER_PORT)
collection_name = "face_collection"
face_collection = client.get_collection(collection_name)


def save_to_chroma(user_id, embedding):
    serialized_embedding = embedding

    face_collection.add(embeddings=[serialized_embedding], metadatas=[{'user_id': user_id}], ids=[user_id])


def delete_from_chroma(user_id):
    try:
        # 尝试从 CHROMA 中删除指定的 user_id
        face_collection.delete(ids=[user_id])
    except KeyError:
        # 如果 user_id 不存在于 CHROMA 数据库中，抛出 KeyError
        raise KeyError(f"User ID '{user_id}' does not exist in CHROMA.")
