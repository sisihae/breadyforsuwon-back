from typing import List, Optional, Dict, Any
import weaviate
from weaviate.classes.query import MetadataQuery
from app.config.settings import settings


class VectorRepository:
    """Repository for Vector DB (Weaviate) operations"""

    def __init__(self):
        # Validate configuration
        if not settings.weaviate_url:
            raise ValueError(
                "WEAVIATE_URL is not configured. "
                "Please set it in your .env file or environment variables."
            )

        try:
            # Connect to Weaviate
            self.client = weaviate.connect_to_custom(
                http_host=settings.weaviate_url.replace("http://", "").replace("https://", ""),
                http_port=8080,
                http_secure=False,
                grpc_host=settings.weaviate_url.replace("http://", "").replace("https://", ""),
                grpc_port=50051,
                grpc_secure=False,
            )
            self.class_name = settings.weaviate_class_name

            # Create class if it doesn't exist
            self._ensure_class_exists()
        except Exception as e:
            raise ValueError(f"Failed to initialize Weaviate: {str(e)}")

    def _ensure_class_exists(self):
        """Ensure the Bakery class exists in Weaviate"""
        try:
            # Check if class exists
            schema = self.client.schema.get()
            class_names = [c["class"] for c in schema.get("classes", [])]

            if self.class_name not in class_names:
                # Create class
                class_obj = {
                    "class": self.class_name,
                    "description": "Bakery information with embeddings",
                    "vectorizer": "none",  # We provide our own vectors
                    "properties": [
                        {
                            "name": "bakery_id",
                            "dataType": ["string"],
                            "description": "UUID of the bakery"
                        },
                        {
                            "name": "name",
                            "dataType": ["string"],
                            "description": "Name of the bakery"
                        },
                        {
                            "name": "district",
                            "dataType": ["string"],
                            "description": "District location"
                        },
                        {
                            "name": "address",
                            "dataType": ["string"],
                            "description": "Full address"
                        },
                        {
                            "name": "bread_tags",
                            "dataType": ["string[]"],
                            "description": "Types of bread available"
                        }
                    ]
                }
                self.client.schema.create_class(class_obj)
        except Exception as e:
            # If error is about class already existing, ignore it
            if "already exists" not in str(e).lower():
                raise

    def upsert_vector(
        self,
        bakery_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Upsert (insert or update) a vector to Weaviate"""
        try:
            collection = self.client.collections.get(self.class_name)

            # Prepare properties
            properties = {
                "bakery_id": bakery_id,
                "name": metadata.get("name", ""),
                "district": metadata.get("district", ""),
                "address": metadata.get("address", ""),
                "bread_tags": metadata.get("bread_tags", [])
            }

            # Insert with custom vector
            collection.data.insert(
                properties=properties,
                vector=embedding,
                uuid=bakery_id
            )
        except Exception as e:
            raise ValueError(f"Failed to upsert vector: {str(e)}")

    def upsert_vectors(
        self,
        vectors: List[tuple]
    ) -> None:
        """Upsert multiple vectors to Weaviate

        Args:
            vectors: List of (id, embedding, metadata) tuples
        """
        for bakery_id, embedding, metadata in vectors:
            self.upsert_vector(bakery_id, embedding, metadata)

    def query(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query similar vectors from Weaviate

        Args:
            embedding: Query embedding vector
            top_k: Number of top results to return
            filters: Optional metadata filters

        Returns:
            List of results with scores and metadata
        """
        try:
            collection = self.client.collections.get(self.class_name)

            # Build filter if provided
            where_filter = None
            if filters:
                # Build Weaviate filter
                # Example: {"district": "영통구"}
                if "district" in filters:
                    from weaviate.classes.query import Filter
                    where_filter = Filter.by_property("district").equal(filters["district"])

            # Perform vector search
            response = collection.query.near_vector(
                near_vector=embedding,
                limit=top_k,
                return_metadata=MetadataQuery(distance=True),
                filters=where_filter
            )

            # Format results
            results = []
            for item in response.objects:
                results.append({
                    "bakery_id": item.properties.get("bakery_id"),
                    "score": 1 - item.metadata.distance,  # Convert distance to similarity
                    "metadata": {
                        "name": item.properties.get("name"),
                        "district": item.properties.get("district"),
                        "address": item.properties.get("address"),
                        "bread_tags": item.properties.get("bread_tags", [])
                    }
                })

            return results
        except Exception as e:
            raise ValueError(f"Failed to query vectors: {str(e)}")

    def get_vector(self, bakery_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID"""
        try:
            collection = self.client.collections.get(self.class_name)
            result = collection.query.fetch_object_by_id(bakery_id)

            if result:
                return {
                    "id": bakery_id,
                    "values": result.vector,
                    "metadata": result.properties
                }
            return None
        except Exception:
            return None

    def delete_vector(self, bakery_id: str) -> None:
        """Delete a vector by ID"""
        try:
            collection = self.client.collections.get(self.class_name)
            collection.data.delete_by_id(bakery_id)
        except Exception as e:
            raise ValueError(f"Failed to delete vector: {str(e)}")

    def delete_vectors(self, bakery_ids: List[str]) -> None:
        """Delete multiple vectors by IDs"""
        for bakery_id in bakery_ids:
            self.delete_vector(bakery_id)

    def update_metadata(
        self,
        bakery_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update metadata for a vector"""
        try:
            collection = self.client.collections.get(self.class_name)
            collection.data.update(
                uuid=bakery_id,
                properties=metadata
            )
        except Exception as e:
            raise ValueError(f"Failed to update metadata: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = self.client.collections.get(self.class_name)
            aggregate = collection.aggregate.over_all(total_count=True)

            return {
                "total_count": aggregate.total_count
            }
        except Exception as e:
            return {"error": str(e)}

    def __del__(self):
        """Close Weaviate connection"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except:
            pass
