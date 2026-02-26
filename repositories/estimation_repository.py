import uuid
from typing import List, Dict
from db.models import Estimation, EstimationItem
from repositories.base import BaseRepository


class EstimationRepository(BaseRepository):

    def create_estimation(
        self,
        job_id: uuid.UUID,
        total_symbols: int,
        grand_total_cost: int,
        items: List[Dict]
    ) -> Estimation:

        estimation = Estimation(
            id=uuid.uuid4(),
            job_id=job_id,
            total_symbols=total_symbols,
            grand_total_cost=grand_total_cost,
        )

        self.db.add(estimation)
        self.db.flush()  # Get estimation.id before committing

        item_objects = [
            EstimationItem(
                id=uuid.uuid4(),
                estimation_id=estimation.id,
                symbol=item["symbol"],
                count=item["count"],
                unit_cost=item["unit_cost"],
                total_cost=item["total_cost"],
            )
            for item in items
        ]

        self.db.add_all(item_objects)
        self.db.commit()
        self.db.refresh(estimation)

        return estimation