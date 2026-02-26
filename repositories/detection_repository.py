import uuid
from typing import List
from db.models import Detection
from repositories.base import BaseRepository


class DetectionRepository(BaseRepository):

    def bulk_create(self, job_id: uuid.UUID, detections: List[dict]):
        detection_objects = [
            Detection(
                id=uuid.uuid4(),
                job_id=job_id,
                label=d["label"],
                confidence=d["confidence"],
                bbox_x1=d["bbox"]["x1"],
                bbox_y1=d["bbox"]["y1"],
                bbox_x2=d["bbox"]["x2"],
                bbox_y2=d["bbox"]["y2"],
            )
            for d in detections
        ]

        self.db.add_all(detection_objects)
        self.db.commit()

        return detection_objects

    def get_by_job_id(self, job_id: uuid.UUID):
        return (
            self.db.query(Detection)
            .filter(Detection.job_id == job_id)
            .all()
        )