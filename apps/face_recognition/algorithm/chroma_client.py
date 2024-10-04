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
import numpy as np

from .config import CHROMA_SERVICE_HOST, CHROMA_SERVER_PORT

client = chromadb.HttpClient(host=CHROMA_SERVICE_HOST, port=CHROMA_SERVER_PORT)
collection_name = "face_collection"
face_collection = client.get_collection(collection_name)


def save_to_chroma(user_id, embedding, containers, unknown_embeddings):
    if unknown_embeddings is not None and containers is not None:
        inx = next(i for i, e in enumerate(unknown_embeddings) if np.array_equal(e, embedding))
        container = containers[inx]
        container.setParent(None)

    serialized_embedding = embedding

    face_collection.add(embeddings=[serialized_embedding], metadatas=[{'user_id': user_id}], ids=[user_id])
