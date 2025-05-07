from httpx import AsyncClient

import asyncio
import pytest

@pytest.mark.asyncio
async def test_add_comment_success(async_client: AsyncClient, get_token: str, test_post_id):
    payload = {
        "text": "This is a test comment"
    }

    headers = {
        "Authorization": f"Bearer {get_token}"
    }

    response = await async_client.post(
        f"/posts/{test_post_id}/comments",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == payload["text"]

@pytest.mark.asyncio
async def test_get_comments(async_client: AsyncClient, get_token: str):
    headers={"Authorization": f"Bearer {get_token}"}

    get_posts = await async_client.get("/posts/", headers=headers)
    posts = get_posts.json()
    post_id = posts[0]["id"]

    response = await async_client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_comment_by_id(async_client: AsyncClient, get_token: str):
    headers={"Authorization": f"Bearer {get_token}"}

    get_posts = await async_client.get("/posts/", headers=headers)
    posts = get_posts.json()
    post_id = posts[0]["id"]

    get_comments = await async_client.get(
        f"/posts/{post_id}/comments", headers=headers
    )
    
    comment_id = get_comments.json()[0]["id"]

    # get comment
    response = await async_client.get(f"/posts/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == comment_id

@pytest.mark.asyncio
async def test_update_comment(async_client: AsyncClient, get_token: str):
    headers={"Authorization": f"Bearer {get_token}"}

    get_posts = await async_client.get("/posts/", headers=headers)
    posts = get_posts.json()
    post_id = posts[0]["id"]

    get_comments = await async_client.get(
        f"/posts/{post_id}/comments", headers=headers
    )
    
    comment_id = get_comments.json()[0]["id"]

    # Update
    update_data = {"text": "Updated comment"}
    response = await async_client.put(
        f"/posts/comments/{comment_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Updated comment"

@pytest.mark.asyncio
async def test_delete_comment_as_admin(async_client: AsyncClient, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}

    get_posts = await async_client.get("/posts/", headers=headers)
    posts = get_posts.json()
    post_id = posts[0]["id"]

    get_comments = await async_client.get(
        f"/posts/{post_id}/comments", headers=headers
    )
    comments = get_comments.json()
    comment_id = comments[0]["id"]

    await asyncio.sleep(0)

    # Now delete it
    response = await async_client.delete(
        f"/posts/comments/{comment_id}",
        headers=headers
    )

    print(f"resp text: {response.text}")
    assert response.status_code == 200
    assert response.json()['success'] is True
