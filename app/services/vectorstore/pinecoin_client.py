import os
from typing import Optional

from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings


_client: Optional[Pinecone] = None
_index = None  # type: ignore


def _parse_cloud_region(env_str: str) -> tuple[str, str]:
    # Expected format: "us-east-1-aws" => (region="us-east-1", cloud="aws")
    parts = env_str.split("-")
    if len(parts) >= 3:
        cloud = parts[-1]
        region = "-".join(parts[:-1])
        return region, cloud
    # Fallback to defaults if format unexpected
    return env_str, "aws"


def _init_if_needed() -> None:
    global _client, _index
    if _index is not None:
        return

    api_key = settings.PINECONE_API_KEY or os.getenv("PINECONE_API_KEY")
    environment = settings.PINECONE_ENVIRONMENT or os.getenv("PINECONE_ENVIRONMENT")
    index_name = settings.PINECONE_PUBMED_INDEX or os.getenv("PINECONE_PUBMED_INDEX")
    dimension = int(os.getenv("PINECONE_PUBMED_DIM", settings.PINECONE_PUBMED_DIM))
    metric = (os.getenv("PINECONE_PUBMED_METRIC") or settings.PINECONE_PUBMED_METRIC).lower()

    if not api_key or not environment or not index_name:
        raise RuntimeError(
            "Pinecone configuration missing. Ensure PINECONE_API_KEY, "
            "PINECONE_ENVIRONMENT, and PINECONE_PUBMED_INDEX are set."
        )

    region, cloud = _parse_cloud_region(environment)

    _client = Pinecone(api_key=api_key)

    # Create index if it doesn't exist
    existing = set(_client.list_indexes().names())
    if index_name not in existing:
        _client.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=cloud, region=region),
        )

    _index = _client.Index(index_name)


def get_index():
    """Return a singleton Pinecone Index instance, creating index if missing."""
    _init_if_needed()
    return _index