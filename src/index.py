"""
Cloudflare Workers Python - Pixel Pirates API
Adapted from FastAPI backend for Workers runtime
"""

from js import Response, Headers, fetch
import json


async def on_fetch(request, env):
    """
    Main entry point for Cloudflare Worker

    Args:
        request: Incoming HTTP request
        env: Environment bindings (DB, CACHE, secrets)
    """

    # Parse URL and method
    url = request.url
    method = request.method

    # CORS headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }

    # Handle CORS preflight
    if method == "OPTIONS":
        return Response.new(
            None,
            status=204,
            headers=Headers.new(cors_headers)
        )

    # Route handling
    path = url.split('?')[0].split('/')[-1] if '/' in url else ''

    try:
        # Health check endpoint
        if "health" in url:
            return json_response({"status": "healthy", "service": "Pixel Pirates API"}, cors_headers)

        # Root endpoint
        if path == "" or "api" not in url:
            return json_response({
                "name": env.APP_NAME,
                "version": env.APP_VERSION,
                "status": "running",
                "docs": "/docs",
                "health": "/api/v1/health"
            }, cors_headers)

        # Authentication endpoints
        if "auth" in url:
            return await handle_auth(request, env, cors_headers)

        # Analysis endpoints
        if "analyze" in url:
            return await handle_analysis(request, env, cors_headers)

        # Posts endpoints
        if "posts" in url:
            return await handle_posts(request, env, cors_headers)

        # Default 404
        return json_response({"error": "Not found"}, cors_headers, 404)

    except Exception as e:
        return json_response(
            {"error": "Internal server error", "detail": str(e)},
            cors_headers,
            500
        )


async def handle_auth(request, env, headers):
    """Handle authentication endpoints"""
    method = request.method

    if "register" in request.url and method == "POST":
        # User registration
        data = await request.json()

        # Simple validation
        if not data.get("email") or not data.get("password"):
            return json_response({"error": "Email and password required"}, headers, 400)

        # Hash password (simplified - use proper hashing in production)
        # In production, use a proper bcrypt library

        # Insert into D1
        try:
            result = await env.DB.prepare(
                "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)"
            ).bind(
                data.get("username", data["email"]),
                data["email"],
                f"hashed_{data['password']}"  # REPLACE WITH PROPER HASHING
            ).run()

            return json_response({
                "message": "User registered successfully",
                "user_id": result.meta.last_row_id
            }, headers)
        except Exception as e:
            return json_response({"error": f"Registration failed: {str(e)}"}, headers, 400)

    elif "login" in request.url and method == "POST":
        # User login
        data = await request.json()

        # Query user from D1
        try:
            result = await env.DB.prepare(
                "SELECT * FROM users WHERE email = ?"
            ).bind(data["email"]).first()

            if not result:
                return json_response({"error": "Invalid credentials"}, headers, 401)

            # Verify password (simplified)
            # In production, use proper password verification

            # Generate token (simplified - use JWT in production)
            token = f"token_{result['id']}"

            return json_response({
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": result["id"],
                    "email": result["email"],
                    "username": result["username"]
                }
            }, headers)
        except Exception as e:
            return json_response({"error": f"Login failed: {str(e)}"}, headers, 500)

    return json_response({"error": "Method not allowed"}, headers, 405)


async def handle_analysis(request, env, headers):
    """Handle content analysis endpoints"""
    method = request.method

    if method == "POST":
        data = await request.json()

        # Get content to analyze
        content = data.get("content", "")
        if not content:
            return json_response({"error": "Content required"}, headers, 400)

        # Simple analysis (replace with actual AI/ML analysis)
        credibility_score = 0.75  # Placeholder
        is_misinformation = credibility_score < 0.5

        # Cache result in KV
        cache_key = f"analysis_{hash(content)}"
        await env.CACHE.put(
            cache_key,
            json.dumps({
                "credibility_score": credibility_score,
                "is_misinformation": is_misinformation
            }),
            expiration_ttl=3600  # 1 hour
        )

        # Store in D1
        user_id = data.get("user_id", 1)  # Get from auth token in production

        # Insert post
        post_result = await env.DB.prepare(
            "INSERT INTO posts (user_id, content) VALUES (?, ?)"
        ).bind(user_id, content).run()

        post_id = post_result.meta.last_row_id

        # Insert analysis
        await env.DB.prepare(
            """INSERT INTO analysis_results
            (post_id, user_id, credibility_score, is_misinformation, confidence, analysis_type)
            VALUES (?, ?, ?, ?, ?, ?)"""
        ).bind(
            post_id,
            user_id,
            credibility_score,
            1 if is_misinformation else 0,
            0.85,
            "basic"
        ).run()

        return json_response({
            "post_id": post_id,
            "credibility_score": credibility_score,
            "is_misinformation": is_misinformation,
            "confidence": 0.85,
            "recommendation": "Verify with additional sources" if is_misinformation else "Content appears credible"
        }, headers)

    return json_response({"error": "Method not allowed"}, headers, 405)


async def handle_posts(request, env, headers):
    """Handle posts endpoints"""
    method = request.method

    if method == "GET":
        # Get user's posts with analysis
        user_id = 1  # Get from auth token in production

        try:
            result = await env.DB.prepare(
                """SELECT p.*, a.credibility_score, a.is_misinformation
                FROM posts p
                LEFT JOIN analysis_results a ON p.id = a.post_id
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
                LIMIT 20"""
            ).bind(user_id).all()

            posts = result.results if hasattr(result, 'results') else []

            return json_response({
                "posts": posts,
                "count": len(posts)
            }, headers)
        except Exception as e:
            return json_response({"error": f"Failed to fetch posts: {str(e)}"}, headers, 500)

    return json_response({"error": "Method not allowed"}, headers, 405)


def json_response(data, headers, status=200):
    """Helper to create JSON response"""
    return Response.new(
        json.dumps(data),
        status=status,
        headers=Headers.new(headers)
    )
