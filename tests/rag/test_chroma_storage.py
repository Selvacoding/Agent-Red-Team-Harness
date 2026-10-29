import pytest

from targets.rag.storage import ChromaVectorStore


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "targets.rag.storage.create_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )
    return ChromaVectorStore(
        collection_name="test-rag",
        persist_directory=str(tmp_path / "chroma"),
    )


def sample_chunk(chunk_id="policy-chunk-0"):
    return {
        "id": chunk_id,
        "document_id": "policy",
        "content": "Only an administrator can delete a customer.",
        "metadata": {
            "source": "policy.md",
            "section": "Deletion Policy",
            "chunk_index": 0,
        },
    }


def test_add_and_search_chunk(store):
    store.add_chunks([sample_chunk()])

    results = store.search("Who can delete a customer?")

    assert len(results) == 1
    assert results[0]["id"] == "policy-chunk-0"
    assert results[0]["document_id"] == "policy"
    assert results[0]["metadata"]["source"] == "policy.md"
    assert results[0]["score"] == pytest.approx(1.0)


def test_upsert_does_not_duplicate_chunk(store):
    store.add_chunks([sample_chunk()])
    store.add_chunks([sample_chunk()])

    assert store.collection.count() == 1


def test_empty_store_returns_no_results(store):
    assert store.search("customer deletion") == []


def test_reset_removes_collection_data(store):
    store.add_chunks([sample_chunk()])

    store.reset()

    assert store.search("customer deletion") == []
    assert store.collection.count() == 0


def test_data_persists_across_store_instances(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "targets.rag.storage.create_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )
    directory = str(tmp_path / "persistent-chroma")

    first = ChromaVectorStore(
        collection_name="persistent-test",
        persist_directory=directory,
    )
    first.add_chunks([sample_chunk()])

    second = ChromaVectorStore(
        collection_name="persistent-test",
        persist_directory=directory,
    )

    results = second.search("customer deletion")

    assert len(results) == 1
    assert results[0]["id"] == "policy-chunk-0"

def test_delete_document_preserves_other_documents(store):
    original = sample_chunk("original-chunk")
    poisoned = {
        **sample_chunk("poisoned-chunk"),
        "document_id": "poisoned-document",
        "metadata": {"poisoned": True},
    }

    store.add_chunks([original, poisoned])
    store.delete_document("poisoned-document")

    assert store.collection.count() == 1
    results = store.search("customer deletion")
    assert len(results) == 1
    assert results[0]["document_id"] == "policy"

def test_default_stores_use_separate_collections(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "targets.rag.storage.create_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )
    directory = str(tmp_path / "isolated-chroma")

    first = ChromaVectorStore(persist_directory=directory)
    second = ChromaVectorStore(persist_directory=directory)

    first.add_chunks([sample_chunk("first-chunk")])

    assert first.collection_name != second.collection_name
    assert first.collection.count() == 1
    assert second.collection.count() == 0


def test_reset_preserves_other_chunks_in_shared_collection(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "targets.rag.storage.create_embedding",
        lambda text: [1.0, 0.0, 0.0],
    )
    directory = str(tmp_path / "shared-chroma")

    first = ChromaVectorStore(
        collection_name="shared-test",
        persist_directory=directory,
    )
    second = ChromaVectorStore(
        collection_name="shared-test",
        persist_directory=directory,
    )

    first.add_chunks([sample_chunk("first-chunk")])
    second.add_chunks([sample_chunk("second-chunk")])

    first.reset()

    assert first.collection.count() == 1
    assert first.collection.get()["ids"] == ["second-chunk"]
