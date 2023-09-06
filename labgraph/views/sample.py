from datetime import datetime
from typing import Dict, List, Literal, Optional, Union, cast

import pymongo
from labgraph.data import Action, Analysis, Material, Measurement, Sample
from labgraph.data.nodes import BaseNode
from labgraph.utils.data_objects import LabgraphDefaultMongoDB, LabgraphMongoDB
from labgraph.views.nodes import (
    ActionView,
    MaterialView,
    AnalysisView,
    MeasurementView,
)
from .base import BaseView, NotFoundInDatabaseError, AlreadyInDatabaseError
from bson import ObjectId


class SampleView(BaseView):
    def __init__(self, labgraph_mongodb_instance: Optional[LabgraphMongoDB] = None):
        super().__init__(
            "samples", Sample, labgraph_mongodb_instance=labgraph_mongodb_instance
        )
        self.actionview = ActionView(
            labgraph_mongodb_instance=labgraph_mongodb_instance
        )
        self.materialview = MaterialView(
            labgraph_mongodb_instance=labgraph_mongodb_instance
        )
        self.analysisview = AnalysisView(
            labgraph_mongodb_instance=labgraph_mongodb_instance
        )
        self.measurementview = MeasurementView(
            labgraph_mongodb_instance=labgraph_mongodb_instance
        )

    def add(
        self,
        entry: Sample,
        additional_incoming_node_ids: Optional[List[ObjectId]] = None,
        if_already_in_db: Literal["raise", "skip", "update"] = "raise",
    ) -> ObjectId:
        if not isinstance(entry, self._entry_class):
            raise ValueError(f"Entry must be of type {self._entry_class.__name__}")

        if not entry.has_valid_graph:
            raise ValueError(
                "Sample graph is not valid! Check for isolated nodes or graph cycles."
            )

        try:
            self.get_by_id(id=entry.id)
            found_in_db = True
        except NotFoundInDatabaseError:
            found_in_db = False
        if found_in_db:
            if if_already_in_db == "raise":
                raise AlreadyInDatabaseError(
                    f"{self._entry_class.__name__} (name={entry.name}, id={entry.id}) already exists in the database!"
                )
            elif if_already_in_db == "skip":
                return entry.id
            elif if_already_in_db == "update":
                self.update(entry)
                return entry.id
        self._check_if_nodes_are_valid(
            entry
        )  # will throw error if any nodes cannot be encoded to BSON

        if not self._has_valid_graph_in_db(
            entry, additional_incoming_node_ids=additional_incoming_node_ids
        ):
            raise ValueError(
                "Sample graph is not valid! Check for isolated nodes, graph cycles, or node dependencies that are not covered by either 1. existing database entries 2. nodes in this Sample or 3. nodes in the `additional_incoming_nodes` list."
            )

        for node in entry.nodes:
            if isinstance(node, Action):
                self.actionview.add(node, if_already_in_db="update")
            elif isinstance(node, Material):
                self.materialview.add(node, if_already_in_db="update")
            elif isinstance(node, Analysis):
                self.analysisview.add(node, if_already_in_db="update")
            elif isinstance(node, Measurement):
                self.measurementview.add(node, if_already_in_db="update")
            else:
                raise ValueError(f"Node {node} is not a valid node type")
        created_at = datetime.now().replace(
            microsecond=0
        )  # remove microseconds, they get lost in MongoDB anyways
        result = self._collection.insert_one(
            {
                **entry.to_dict(),
                "created_at": created_at,
                "updated_at": created_at,  # same as created_at on first version in db
            }
        )

        # update local copy of entry to reflect database changes
        entry._created_at = created_at
        entry._updated_at = created_at
        return cast(ObjectId, result.inserted_id)

    def add_many_samples(self, samples: List[Sample]):
        """Adds a batch of samples together. Useful when defining samples that depend on each other.

        Args:
            samples (List[Sample]): List of samples whose tasks share edges, yet the samples do not each contain all connected nodes.
        """
        master_sample = Sample(
            name="temporary_batch_sample",
            description="This is a wrapper Sample to batch add nodes from multiple new, correlated samples. This should be deleted almost instantly after the contained samples are defined in the database.",
        )
        for sample in samples:
            for node in sample.nodes:
                master_sample.add_node(node)

        self.add(
            entry=master_sample,
            if_already_in_db="raise",
            additional_incoming_node_ids=[node.id for node in master_sample.nodes],
        )
        try:
            for sample in samples:
                self.add(sample)
        except Exception as e:
            raise e
        finally:
            self.remove(id=master_sample.id, remove_nodes=False)

    def _check_if_nodes_are_valid(self, sample: Sample) -> bool:
        """ensure that all nodes contained within the sample can be encoded to BSON and added to the database. This will fail if user supplies data formats that cannot be encoded to BSON."""
        bad_nodes = []
        for node in sample.nodes:
            node: BaseNode
            node.raise_if_invalid()
            if not node.is_valid_for_mongodb():
                bad_nodes.append(node)
        if len(bad_nodes) > 0:
            raise ValueError(
                f"Some nodes cannot be added to the mongodb. This is because some values contained in the nodes are in a format that cannot be encoded to BSON. Affected nodes: {str(bad_nodes)}."
            )

    def _has_valid_graph_in_db(
        self,
        sample: Sample,
        additional_incoming_node_ids: Optional[List[ObjectId]] = None,
    ) -> bool:
        # we need to check the graph in the db to make sure it is valid.

        upcoming_nodes = [
            node.id for node in sample.nodes
        ]  # all nodes that will be added along with this sample

        if additional_incoming_node_ids is not None:
            upcoming_nodes += additional_incoming_node_ids  # other nodes that should be considered valid (ie are guaranteed to be added).

        # checkifvalid_methods = {
        #     Action: self._is_valid_action,
        #     Material: self._is_valid_material,
        #     Measurement: self._is_valid_measurement,
        #     Analysis: self._is_valid_analysis,
        # }

        checkifvalid_methods = {
            "Action": self.actionview.get_by_id,
            "Material": self.materialview.get_by_id,
            "Measurement": self.measurementview.get_by_id,
            "Analysis": self.analysisview.get_by_id,
        }

        for node in sample.nodes:
            for related_node in node.upstream + node.downstream:
                if related_node["node_id"] in upcoming_nodes:
                    continue
                try:
                    checkifvalid = checkifvalid_methods[related_node["node_type"]]
                    checkifvalid(id=related_node["node_id"])
                except NotFoundInDatabaseError as e:
                    return False
        return True

    def _entry_to_object(self, entry: dict):
        id = entry.pop("_id")
        created_at = entry.pop("created_at")
        updated_at = entry.pop("updated_at")
        version_history = entry.pop("version_history", [])
        nodes = entry.pop("nodes")
        contents = entry.pop("contents")

        s = Sample(**entry)
        s._id = id

        for nodetype, nodeids in nodes.items():
            for nodeid in nodeids:
                if nodetype == "Action":
                    node = self.actionview.get_by_id(id=nodeid)
                elif nodetype == "Material":
                    node = self.materialview.get_by_id(id=nodeid)
                elif nodetype == "Measurement":
                    node = self.measurementview.get_by_id(id=nodeid)
                elif nodetype == "Analysis":
                    node = self.analysisview.get_by_id(id=nodeid)
                s.add_node(node)
        s._sort_nodes()

        s._created_at = created_at
        s._updated_at = updated_at
        s._version_history = version_history
        s._contents = contents

        return s

    def get_by_id(self, id: ObjectId) -> Sample:
        entry = self._collection.find_one({"_id": id})
        if entry is None:
            raise NotFoundInDatabaseError(
                f"{self._entry_class.__name__} with id {id} not found in database!"
            )
        return self._entry_to_object(entry)

    def get_by_contents(self, contents: dict) -> List[Sample]:
        """Return all Sample(s) that contain the given key-value pairs in their document.

        Args:
            contents (dict): Dictionary of contents to match against. Samples which contain all of the provided key-value pairs will be returned.

        Raises:
            NotFoundInDatabaseError: No Sample found with specified contents

        Returns:
            List[Sample]: List of Sample(s) with the specified contents. List is sorted from most recent to oldest.
        """
        result = self._collection.find(contents).sort("created_at", pymongo.DESCENDING)
        entries = [self._entry_to_object(entry) for entry in entries]
        if len(entries) == 0:
            raise NotFoundInDatabaseError(
                f"No Sample found that contains the following key-value pairs: {contents}!"
            )
        return entries

    def get_by_node(self, node: BaseNode) -> List[Sample]:
        """Return any Sample(s) that contain the given node

        Args:
            node (BaseNode): A Node object (Action, Material, Measurement, or Analysis)

        Raises:
            ValueError: Invalid node type
            NotFoundInDatabaseError: No Sample found containing specified node

        Returns:
            List[Sample]: List of Sample(s) containing the specified node. List is sorted from most recent to oldest.
        """
        node_type = node.__class__.__name__
        node_id = node.id
        return self.get_by_node_info(node_type, node_id)

    def get_by_node_info(self, node_type: str, node_id: ObjectId) -> List[Sample]:
        """Return any Sample(s) that contain a node of the given type and ID

        Args:
            node_type (str): Type (Action, Material, Measurement, or Analysis) of node
            node_id (ObjectId): ObjectId of node

        Raises:
            ValueError: Invalid node type
            NotFoundInDatabaseError: No Sample found containing specified node

        Returns:
            List[Sample]: List of Sample(s) containing the specified node. List is sorted from most recent to oldest.
        """
        if node_type not in ["Action", "Material", "Measurement", "Analysis"]:
            raise ValueError(
                f"node_type must be one of 'Action', 'Material', 'Measurement', 'Analysis'"
            )

        result = self._collection.find({f"nodes.{node_type}": node_id}).sort(
            "created_at", pymongo.DESCENDING
        )
        entries = [self._entry_to_object(entry) for entry in result]
        if len(entries) == 0:
            raise NotFoundInDatabaseError(
                f"No Sample found containing node of type {node_type} with id {node_id}!"
            )
        return entries

    def get_by_action_node(self, action_id: ObjectId) -> List[Sample]:
        return self.get_by_node_info("Action", action_id)

    def get_by_material_node(self, material_id: ObjectId) -> List[Sample]:
        return self.get_by_node_info("Material", material_id)

    def get_by_measurement_node(self, measurement_id: ObjectId) -> List[Sample]:
        return self.get_by_node_info("Measurement", measurement_id)

    def get_by_analysis_node(self, analysis_id: ObjectId) -> List[Sample]:
        return self.get_by_node_info("Analysis", analysis_id)

    def update(self, entry: Sample):
        """Updates an entry in the database. The previous entry will be placed in a `version_history` field of the entry.

        Args:
            entry (Sample): Sample object to be updated

        Raises:
            TypeError: Node is of wrong type
            NotFoundInDatabaseError: Node does not exist in the database
            ValueError: Upstream nodes can only be added, not removed! Removing can break the graph.
            ValueError: Downstream nodes can only be added, not removed! Removing can break the graph.
        """
        if not isinstance(entry, Sample):
            raise TypeError(f"Entry must be of type Sample!")

        if not entry.has_valid_graph:
            raise ValueError(
                "Sample graph is not valid! Check for isolated nodes or graph cycles."
            )
        old_entry = self._collection.find_one({"_id": entry.id})
        if old_entry is None:
            raise NotFoundInDatabaseError(
                f"Cannot update Sample with id {entry.id} because it does not exist in the database."
            )

        self._check_if_nodes_are_valid(
            entry
        )  # will throw error if any nodes cannot be encoded to BSON

        for node in entry.nodes:
            if isinstance(node, Action):
                self.actionview.add(node, if_already_in_db="update")
            elif isinstance(node, Material):
                self.materialview.add(node, if_already_in_db="update")
            elif isinstance(node, Analysis):
                self.analysisview.add(node, if_already_in_db="update")
            elif isinstance(node, Measurement):
                self.measurementview.add(node, if_already_in_db="update")
            else:
                raise ValueError(f"Node {node} is not a valid node type")

        new_entry = entry.to_dict()

        # If we are only adding new nodes, we won't consider this a version update. Will instead update the current version in place.
        only_changing_nodes = True
        for key in new_entry:
            if key == "nodes":
                continue
            if key not in old_entry:
                only_changing_nodes = False
                break
            if new_entry[key] != old_entry[key]:
                only_changing_nodes = False
                break

        if only_changing_nodes:
            # no need for version history if we are only adding nodes
            updated_at = datetime.now().replace(microsecond=0)
            self._collection.update_one(
                {"_id": entry.id},
                {
                    "$set": {
                        "nodes": new_entry["nodes"],
                        "updated_at": updated_at,  # remove microseconds, they get lost in MongoDB anyways,
                    }
                },
            )
            entry._updated_at = updated_at

        else:
            # if other things are changing, lets keep a version history
            new_entry["created_at"] = old_entry["created_at"]
            new_entry["updated_at"] = (
                datetime.now().replace(microsecond=0),
            )  # remove microseconds, they get lost in MongoDB anyways
            new_entry["version_history"] = old_entry.get("version_history", [])
            old_entry.pop(
                "version_history", None
            )  # dont nest version histories, instead append to the new entry's version history
            new_entry["version_history"].append(old_entry)
            self._collection.replace_one({"_id": entry.id}, new_entry)

            # update local copy of entry to reflect database changes
            entry._created_at = new_entry["created_at"]
            entry._updated_at = new_entry["updated_at"]

            if "version_history" in new_entry:
                entry._version_history = new_entry["version_history"]

    def remove(
        self, id: ObjectId, remove_nodes: bool = False, _force_dangerous: bool = False
    ):
        """Removes an entry from the database

        Args:
            entry (Sample): Sample object to be removed

        Raises:
            TypeError: Entry is of wrong type
            NotFoundInDatabaseError: Entry does not exist in the database
        """
        if remove_nodes and self._labgraph_mongodb_instance != LabgraphDefaultMongoDB():
            raise NotImplementedError("Sample deletion with node removal is not supported when using a LabgraphMongoDB instance. If you need to do this, please set this DB as the default using a labgraph config file (`labgraph.utils.make_config()`), in which case deletion with node removal is supported. Sorry!")
        if not self._exists(id):
            if _force_dangerous:
                return
            else:
                raise NotFoundInDatabaseError(
                    f"Cannot remove Sample with id {id} because it does not exist in the database."
                )
        sample = self.get_by_id(id)
        if remove_nodes:
            VIEWS = {
                "Action": self.actionview,
                "Material": self.materialview,
                "Measurement": self.measurementview,
                "Analysis": self.analysisview,
            }
            for node in sample.nodes:
                VIEWS[node.__class__.__name__].remove(
                    node.id, _force_dangerous=_force_dangerous
                )

        result = self._collection.delete_one({"_id": id})
        if result.deleted_count == 0 and not remove_nodes:
            # if removing nodes, this sample may have been deleted in the node removal sequence, so no error raise is needed
            raise NotFoundInDatabaseError(
                f"Cannot remove Sample with id {id} because it does not exist in the database."
            )
