from bson import ObjectId
from flask import Blueprint
from labgraph.views import SampleView
import pymongo

sample_view: SampleView = SampleView()
sample_bp = Blueprint("/sample", __name__, url_prefix="/api/sample")


@sample_bp.route("/summary/<count>", methods=["GET"])
def get_sample_summary(count: int):
    """
    Get the summary of the "count" most recent samples. if count==0, returns all samples. samples are returned in reverse chronological order.
    """
    samples = []
    count = int(count)

    kws = dict(
        projection={
            "_id": 1,
            "name": 1,
            "description": 1,
            "nodes": 1,
            "tags": 1,
            "created_at": 1,
            # "updated_at": 1,
        },
        sort=[("created_at", pymongo.DESCENDING)],
    )

    count = int(count)
    if count != 0:
        kws["limit"] = count

    for entry in sample_view._collection.find(
        {},
        **kws,
    ):
        samples.append(
            {
                "_id": str(entry["_id"]),
                "name": entry["name"],
                "description": entry["description"],
                "nodes": {
                    k: [str(oid) for oid in v] for k, v in entry["nodes"].items()
                },
                "tags": entry["tags"],
                "created_at": entry["created_at"],
                # "updated_at": entry["updated_at"],
            }
        )

    return samples


# @sample_bp.route("/submit", methods=["POST"])
# def submit_new_sample():
#     """
#     Submit a new sample to the system
#     """
#     data = request.get_json(force=True)  # type: ignore
#     try:
#         sample = SampleInputFormat(**data)  # type: ignore
#         sample_id = sample_view.add_sample(Sample.from_dict(data))
#     except ValidationError as exception:
#         return {"status": "error", "errors": exception.errors()}, 400
#     except ValueError as exception:
#         return {"status": "error", "errors": exception.args[0]}, 400

#     return {"status": "success", "data": {"sample_id": sample_id}}


@sample_bp.route("/<sample_id>", methods=["GET"])
def get_sample(sample_id):
    """
    Get the status of a sample
    """
    try:
        sample_entry = sample_view._collection.find_one(
            {"_id": ObjectId(sample_id)},
        )
        if sample_entry is None:
            raise ValueError(f"No sample found with id {sample_id}")

    except ValueError as exception:
        return {"status": "error", "errors": exception.args[0]}, 400

    sample_entry["_id"] = str(sample_entry["_id"])
    sample_entry["nodes"] = {
        k: [str(oid) for oid in v] for k, v in sample_entry["nodes"].items()
    }
    return sample_entry
