import pytest
from uuid import uuid4
from src.repositories.comment import CommentRepository
from src.schemas.comment import CommentCreateModel
from src.database.models import Post, User, Comment


@pytest.mark.asyncio
async def test_add_comment(test_db, test_user: User, test_post: Post):
    repo = CommentRepository(test_db)

    data = CommentCreateModel(message="Hello repo test")
    result = await repo.add_comment(post_id=test_post.id, user_id=test_user.id, comment=data)

    assert result is not None
    assert result.message == "Hello repo test"
    assert result.user.id == test_user.id


@pytest.mark.asyncio
async def test_get_comments(test_db, test_user: User, test_post: Post):
    repo = CommentRepository(test_db)

    # Add a comment
    await repo.add_comment(post_id=test_post.id, user_id=test_user.id, comment=CommentCreateModel(message="Another comment"))

    comments = await repo.get_comments(test_post.id)
    assert isinstance(comments, list)
    assert len(comments) >= 1
    assert comments[0].post_id == test_post.id


@pytest.mark.asyncio
async def test_get_comment(test_db, test_user: User, test_post: Post):
    repo = CommentRepository(test_db)

    comment = await repo.add_comment(post_id=test_post.id, user_id=test_user.id, comment=CommentCreateModel(message="To get"))
    found = await repo.get_comment(comment.id)

    assert found is not None
    assert found.id == comment.id

    missing = await repo.get_comment(uuid4())
    assert missing is None


@pytest.mark.asyncio
async def test_update_comment(test_db, test_user: User, test_post: Post):
    repo = CommentRepository(test_db)

    comment = await repo.add_comment(post_id=test_post.id, user_id=test_user.id, comment=CommentCreateModel(message="Before update"))
    updated = await repo.update(comment.id, "After update")

    assert updated is not None
    assert updated.message == "After update"


@pytest.mark.asyncio
async def test_delete_comment(test_db, test_user: User, test_post: Post):
    repo = CommentRepository(test_db)

    comment = await repo.add_comment(post_id=test_post.id, user_id=test_user.id, comment=CommentCreateModel(message="To delete"))
    success = await repo.delete(comment.id)

    assert success is True

    # Try deleting again (should be false)
    success_again = await repo.delete(comment.id)
    assert success_again is False
