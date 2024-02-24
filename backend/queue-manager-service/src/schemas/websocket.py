import uuid

from pydantic import BaseModel


class BasePushPayload(BaseModel):
    consumer_id: uuid.UUID
    producer_id: uuid.UUID


class InputLikeCommentMessage(BasePushPayload):
    comment_id: uuid.UUID
